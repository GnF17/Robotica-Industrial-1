import math
import numpy as np
import serial
import time

L2 = 90.0
L3 = 90.0
OFFSET_R = 30.0
OFFSET_Z = 40.0
PASSOS_POR_REVOLUCAO = 4096

PORTA_SERIAL = '/dev/ttyUSB0'
BAUD_RATE = 115200

try:
    arduino = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=20)
    time.sleep(2)
    print("Conexão serial estabelecida.")
except Exception as e:
    print(f"Erro ao abrir serial: {e}")
    arduino = None


def calc_x(theta1, theta2, theta3):
    return math.cos(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3))


def calc_y(theta1, theta2, theta3):
    return math.sin(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3))


def calc_z(theta1, theta2, theta3):
    return L2 * math.sin(theta2) + L3 * math.sin(theta2 + theta3)


def jacobian(theta1, theta2, theta3):
    dxdt1 = -math.sin(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3))
    dxdt2 = -math.cos(theta1) * (L2 * math.sin(theta2) + L3 * math.sin(theta2 + theta3))
    dxdt3 = -math.cos(theta1) * L3 * math.sin(theta2 + theta3)

    dydt1 = math.cos(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3))
    dydt2 = -math.sin(theta1) * (L2 * math.sin(theta2) + L3 * math.sin(theta2 + theta3))
    dydt3 = -math.sin(theta1) * L3 * math.sin(theta2 + theta3)

    dzdt1 = 0
    dzdt2 = L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3)
    dzdt3 = L3 * math.cos(theta2 + theta3)

    return np.array([[dxdt1, dxdt2, dxdt3],
                     [dydt1, dydt2, dydt3],
                     [dzdt1, dzdt2, dzdt3]], dtype=float)


def inverse_jacobian(j):
    return np.linalg.pinv(j)


def iteracao(q0, X0, Xa):
    Jinv = inverse_jacobian(jacobian(q0[0], q0[1], q0[2]))
    dX = Xa - X0
    return q0 + 0.5 * (Jinv.dot(dX))


def calcular_alvo_virtual(xa, ya, za):
    r_alvo = math.sqrt(xa**2 + ya**2)
    theta_base = math.atan2(ya, xa)
    r_virtual = r_alvo - OFFSET_R
    z_virtual = za - OFFSET_Z
    x_virtual = r_virtual * math.cos(theta_base)
    y_virtual = r_virtual * math.sin(theta_base)
    return x_virtual, y_virtual, z_virtual


def solve(theta1, theta2, theta3, xa, ya, za):
    q0 = np.array([theta1, theta2, theta3])
    X0 = np.array([calc_x(q0[0], q0[1], q0[2]), calc_y(q0[0], q0[1], q0[2]), calc_z(q0[0], q0[1], q0[2])])

    v_x, v_y, v_z = calcular_alvo_virtual(xa, ya, za)
    Xa = np.array([v_x, v_y, v_z])

    iteracoes = 0
    max_iter = 1000

    while np.linalg.norm(Xa - X0) > 0.1 and iteracoes < max_iter:
        q0 = iteracao(q0, X0, Xa)
        X0 = np.array([calc_x(q0[0], q0[1], q0[2]), calc_y(q0[0], q0[1], q0[2]), calc_z(q0[0], q0[1], q0[2])])
        iteracoes += 1

    if iteracoes == max_iter:
        print("ALERTA: Solver não convergiu. O alvo pode estar fora de alcance.")
        return None

    return q0


def converter_delta_angulo_para_passos(delta_angulo_rad):
    delta_normalizado = math.atan2(math.sin(delta_angulo_rad), math.cos(delta_angulo_rad))
    return int(round((math.degrees(delta_normalizado) / 360.0) * PASSOS_POR_REVOLUCAO))


def converter_delta_para_passos(q_atual_rad, q_novo_rad):
    return [
        converter_delta_angulo_para_passos(q_novo_rad[0] - q_atual_rad[0]),
        converter_delta_angulo_para_passos(q_novo_rad[1] - q_atual_rad[1]),
        converter_delta_angulo_para_passos(q_novo_rad[2] - q_atual_rad[2]),
    ]


def solicitar_ponto():
    while True:
        entrada = input("Digite o ponto alvo como X Y Z (ou 'sair'): ").strip()
        if entrada.lower() in {"sair", "exit", "quit"}:
            return None

        partes = entrada.replace(",", " ").split()
        if len(partes) != 3:
            print("Entrada inválida. Use três valores: X Y Z")
            continue

        try:
            return float(partes[0]), float(partes[1]), float(partes[2])
        except ValueError:
            print("Entrada inválida. Os valores precisam ser numéricos.")


def solicitar_modo():
    while True:
        entrada = input("Método 1=sequencial, 2=simultâneo, 3=proporcional: ").strip()
        if entrada in {"1", "2", "3"}:
            return int(entrada)
        print("Modo inválido. Escolha 1, 2 ou 3.")


def enviar_para_arduino(modo, passos_delta):
    delta_b = int(passos_delta[0])
    delta_o = int(passos_delta[1])
    delta_c = int(passos_delta[2])

    if arduino and arduino.is_open:
        comando = f"<{modo},{delta_b},{delta_o},{delta_c}>\n"
        arduino.write(comando.encode('utf-8'))
        print(f"Enviado: {comando.strip()}")

        resposta = arduino.readline().decode('utf-8').strip()
        if resposta:
            print(f"Arduino respondeu: {resposta}")
    else:
        print("Serial inativa. Comando simulado:", f"<{modo},{delta_b},{delta_o},{delta_c}>")


# ==========================================
#            EXECUÇÃO PRINCIPAL
# ==========================================

q_atual = [
    math.radians(0),
    math.radians(90),
    math.radians(-90)
]

print("Controle interativo iniciado. Digite 'sair' para encerrar.")

while True:
    alvo = solicitar_ponto()
    if alvo is None:
        print("Encerrando.")
        break

    modo = solicitar_modo()
    alvo_x, alvo_y, alvo_z = alvo

    print(f"Calculando cinemática para atingir: X={alvo_x}, Y={alvo_y}, Z={alvo_z}")
    q_novo = solve(q_atual[0], q_atual[1], q_atual[2], alvo_x, alvo_y, alvo_z)

    if q_novo is None:
        print("Movimento abortado.")
        continue

    print(f"Ângulos Finais (Radianos): Base={q_novo[0]:.3f}, Ombro={q_novo[1]:.3f}, Cotovelo={q_novo[2]:.3f}")

    passos_delta = converter_delta_para_passos(q_atual, q_novo)
    print(f"Passos de deslocamento: Base={passos_delta[0]}, Ombro={passos_delta[1]}, Cotovelo={passos_delta[2]}")

    enviar_para_arduino(modo, passos_delta)
    q_atual = q_novo
