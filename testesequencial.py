import math
import numpy as np
import serial
import time

L1 = 90.0
L2 = 90.0
OFFSET_R = 30.0
OFFSET_Z = 50.0
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
    return math.cos(theta1) * (L2 * math.cos(theta2+theta3) + L1 * math.cos(theta2) + OFFSET_R)

def calc_y(theta1, theta2, theta3):
    return math.sin(theta1) * (L2 * math.cos(theta2 + theta3) + L1 * math.cos(theta2) + OFFSET_R)

def calc_z(theta1, theta2, theta3):
    return L2 * math.sin(theta2 + theta3) + L1 * math.sin(theta2) + OFFSET_Z

def inverse_jacobian(theta1, theta2, theta3):
    alpha1 = L1 * L2 * math.sin(theta3)
    alpha4 = L2 * math.cos(theta2 + theta3)
    alpha2 = OFFSET_R + alpha4 + L1 * math.cos(theta2)
    alpha3 = alpha4 + L1 * math.cos(theta2)

    J11 = -math.sin(theta1) / alpha2
    J12 = math.cos(theta1) / alpha2
    J13 = 0
    J21 = math.cos(theta2 + theta3) * math.cos(theta1) / (L1 * math.sin(theta3))
    J22 = math.cos(theta2 + theta3) * math.sin(theta1) / (L1 * math.sin(theta3))
    J23 = math.sin(theta2 + theta3) / (L1 * math.sin(theta3))
    J31 = -math.cos(theta1) * alpha3 / alpha1
    J32 = -math.sin(theta1) * alpha3 / alpha1
    J33 = - (L2 * math.sin(theta2 + theta3) + L1 * math.sin(theta2)) / alpha1

    return np.array([[J11, J12, J13],
                     [J21, J22, J23],
                     [J31, J32, J33]], dtype=float)

def iteracao(q0, X0, Xa):
    Jinv = inverse_jacobian(q0[0], q0[1], q0[2])
    dX = Xa - X0
    return q0 + 0.5 * (Jinv.dot(dX))


def solve(theta1, theta2, theta3, xa, ya, za):
    q0 = np.array([theta1, theta2, theta3])
    X0 = np.array([calc_x(q0[0], q0[1], q0[2]), calc_y(q0[0], q0[1], q0[2]), calc_z(q0[0], q0[1], q0[2])])

    Xa = np.array([xa, ya, za])

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
    return int((delta_angulo_rad / 360.0) * PASSOS_POR_REVOLUCAO)


def converter_delta_para_passos(q_atual_rad, q_novo_rad):
    return [
        converter_delta_angulo_para_passos(q_novo_rad[0] - q_atual_rad[0]),
        converter_delta_angulo_para_passos(q_novo_rad[1] - q_atual_rad[1]),
        converter_delta_angulo_para_passos(q_novo_rad[2] - q_atual_rad[2]),
    ]

def angulo_para_passos_absolutos(angulo_rad):
    return int(round((angulo_rad/(2*math.pi)) * PASSOS_POR_REVOLUCAO))

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
    delta_c = int(passos_delta[2]) + delta_o  # O cotovelo deve andar junto com o ombro, pois como o motor esta na base ele nao gira junto. Por isso a soma com o delta_o

    if arduino and arduino.is_open:
        arduino.reset_input_buffer()
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
    math.radians(90),
    math.radians(90),
    math.radians(-90)
]

passos_atuais = [
        angulo_para_passos_absolutos(q_atual[0]),
        angulo_para_passos_absolutos(q_atual[1]),
        angulo_para_passos_absolutos(q_atual[2])
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

    passos_novos = [
        angulo_para_passos_absolutos(q_novo[0]),
        angulo_para_passos_absolutos(q_novo[1]),
        angulo_para_passos_absolutos(q_novo[2])
    ]

    # CORRIGIDO: O delta real deve vir estritamente da diferença dos inteiros absolutos calculados
    passos_delta = [
        passos_novos[0] - passos_atuais[0],
        passos_novos[1] - passos_atuais[1],
        passos_novos[2] - passos_atuais[2]
    ]
    
    print(f"Passos de deslocamento: Base={passos_delta[0]}, Ombro={passos_delta[1]}, Cotovelo={passos_delta[2]}")

    enviar_para_arduino(modo, passos_delta)
    
    # Atualiza as referências salvando o ponto para onde o motor de fato foi
    passos_atuais = passos_novos
    q_atual = [
        (passos_atuais[0] / PASSOS_POR_REVOLUCAO) * (2 * math.pi),
        (passos_atuais[1] / PASSOS_POR_REVOLUCAO) * (2 * math.pi),
        (passos_atuais[2] / PASSOS_POR_REVOLUCAO) * (2 * math.pi)
    ]
