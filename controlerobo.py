import math
import numpy as np
import serial
import time

L1 = 90.0
L2 = 90.0
OFFSET_R = 30.0
OFFSET_Z = 50.0
PASSOS_POR_REVOLUCAO = 4096
DELAY_LINEAR_SEGUNDOS = 0.15

PORTA_SERIAL = '/dev/ttyUSB0'
BAUD_RATE = 115200





# Conexão serial com o arduino
try:
    arduino = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=20)
    time.sleep(2)
    print("Conexão serial estabelecida.")
except Exception as e:
    print(f"Erro ao abrir serial: {e}")
    arduino = None




# Cálculo das coordenadas x, y, z (feito por Denavit-Hartenberg)
def calc_x(theta1, theta2, theta3):
    return math.cos(theta1) * (L2 * math.cos(theta2+theta3) + L1 * math.cos(theta2) + OFFSET_R)

def calc_y(theta1, theta2, theta3):
    return math.sin(theta1) * (L2 * math.cos(theta2 + theta3) + L1 * math.cos(theta2) + OFFSET_R)

def calc_z(theta1, theta2, theta3):
    return L2 * math.sin(theta2 + theta3) + L1 * math.sin(theta2) + OFFSET_Z




# Cálculo da inversa do jacobiano diretamente (feito em MATLAB)
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


    

# Cálculo iterativo da cinemática inversa
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




# Cálculo da quantidade de passos necessária para atingir os ângulos desejados (conversão direta de graus para passos)
def converter_delta_angulo_para_passos(delta_angulo_rad):
    return int((delta_angulo_rad / 360.0) * PASSOS_POR_REVOLUCAO)

#conversao de theta1, theta2 e theta3 
def converter_delta_para_passos(q_atual_rad, q_novo_rad):
    return [
        converter_delta_angulo_para_passos(q_novo_rad[0] - q_atual_rad[0]),
        converter_delta_angulo_para_passos(q_novo_rad[1] - q_atual_rad[1]),
        converter_delta_angulo_para_passos(q_novo_rad[2] - q_atual_rad[2]),
    ]

# passos absolutos a partir de theta_i = 0deg
def angulo_para_passos_absolutos(angulo_rad):
    return int(round((angulo_rad/(2*math.pi)) * PASSOS_POR_REVOLUCAO))




# Interação com o usuário: definir o ponto alvo
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

# Interação com o usuário: definir o método usado, conforme as fases definidas na especificação do projeto (ou terminar a execução)
def solicitar_modo():
    while True:
        entrada = input("Método 1=sequencial, 2=simultâneo, 3=proporcional, 4=linear, 5=terminar: ").strip()
        if entrada in {"1", "2", "3", "4", "5"}:
            return int(entrada)
        print("Modo inválido. Escolha 1, 2, 3, 4 ou 5.")




# Comunicação com o arduino, envio do número de passos para cada motor
def enviar_para_arduino(modo, passos_delta):
    delta_b = int(passos_delta[0]) # delta base
    delta_o = int(passos_delta[1]) # delta ombro
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




# Execução de movimento para fases 1 a 3
def executar_movimento_cartesiano(q_referencia, alvo_x, alvo_y, alvo_z, modo_arduino):
    print(f"Calculando cinemática para atingir: X={alvo_x}, Y={alvo_y}, Z={alvo_z}")
    q_novo = solve(q_referencia[0], q_referencia[1], q_referencia[2], alvo_x, alvo_y, alvo_z)

    if q_novo is None:
        print("Movimento abortado.")
        return q_referencia

    print(f"Ângulos Finais (Radianos): Base={q_novo[0]:.3f}, Ombro={q_novo[1]:.3f}, Cotovelo={q_novo[2]:.3f}")

    passos_novos = [
        angulo_para_passos_absolutos(q_novo[0]),
        angulo_para_passos_absolutos(q_novo[1]),
        angulo_para_passos_absolutos(q_novo[2])
    ]

    passos_atuais_locais = [
        angulo_para_passos_absolutos(q_referencia[0]),
        angulo_para_passos_absolutos(q_referencia[1]),
        angulo_para_passos_absolutos(q_referencia[2])
    ]

    passos_delta = [
        passos_novos[0] - passos_atuais_locais[0],
        passos_novos[1] - passos_atuais_locais[1],
        passos_novos[2] - passos_atuais_locais[2]
    ]

    print(f"Passos de deslocamento: Base={passos_delta[0]}, Ombro={passos_delta[1]}, Cotovelo={passos_delta[2]}")
    enviar_para_arduino(modo_arduino, passos_delta)

    return q_novo

# Execução para fase 4
def executar_movimento_linear(q_referencia, ponto_final):
    x1 = calc_x(q_referencia[0], q_referencia[1], q_referencia[2])
    y1 = calc_y(q_referencia[0], q_referencia[1], q_referencia[2])
    z1 = calc_z(q_referencia[0], q_referencia[1], q_referencia[2])
    x2, y2, z2 = ponto_final

    dx = (x2 - x1) / 30.0
    dy = (y2 - y1) / 30.0
    dz = (z2 - z1) / 30.0

    print("Executando interpolacao linear em 30 pontos.")

    q_atual_local = q_referencia
    for indice in range(1, 31):
        alvo_x = x1 + dx * indice
        alvo_y = y1 + dy * indice
        alvo_z = z1 + dz * indice

        print(f"Ponto {indice}/30: X={alvo_x:.3f}, Y={alvo_y:.3f}, Z={alvo_z:.3f}")
        q_novo = solve(q_atual_local[0], q_atual_local[1], q_atual_local[2], alvo_x, alvo_y, alvo_z)

        if q_novo is None:
            print("Interpolacao linear abortada.")
            return q_atual_local

        passos_atuais_locais = [
            angulo_para_passos_absolutos(q_atual_local[0]),
            angulo_para_passos_absolutos(q_atual_local[1]),
            angulo_para_passos_absolutos(q_atual_local[2])
        ]
        passos_novos = [
            angulo_para_passos_absolutos(q_novo[0]),
            angulo_para_passos_absolutos(q_novo[1]),
            angulo_para_passos_absolutos(q_novo[2])
        ]

        passos_delta = [
            passos_novos[0] - passos_atuais_locais[0],
            passos_novos[1] - passos_atuais_locais[1],
            passos_novos[2] - passos_atuais_locais[2]
        ]

        print(f"Passos do segmento: Base={passos_delta[0]}, Ombro={passos_delta[1]}, Cotovelo={passos_delta[2]}")
        enviar_para_arduino(3, passos_delta)
        time.sleep(DELAY_LINEAR_SEGUNDOS)
        q_referencia = q_novo
        q_atual_local = q_novo

    return q_atual_local


# ==========================================
#            EXECUÇÃO PRINCIPAL
# ==========================================

# Inicializar o robô na posição de L invertido
q_atual = [
    math.radians(90), #theta1
    math.radians(90), #theta2   
    math.radians(-90) #theta3
]

# Configuração inicial
passos_atuais = [
        angulo_para_passos_absolutos(q_atual[0]),
        angulo_para_passos_absolutos(q_atual[1]),
        angulo_para_passos_absolutos(q_atual[2])
]





# Sequência  de controle interativo
print("Controle interativo iniciado. Digite 'sair' para encerrar.")

while True:
    modo = solicitar_modo()
    if modo == 5:
        print("Encerrando.")
        break

    if modo == 4:
        ponto_final = solicitar_ponto()
        if ponto_final is None:
            print("Encerrando.")
            break

        q_atual = executar_movimento_linear(q_atual, ponto_final)
        continue

    alvo = solicitar_ponto()
    if alvo is None:
        print("Encerrando.")
        break

    alvo_x, alvo_y, alvo_z = alvo
    q_atual = executar_movimento_cartesiano(q_atual, alvo_x, alvo_y, alvo_z, modo)
