import math 
import numpy as np
import serial
import time

L1 = 10
L2 = 90
L3 = 90
PASSOS_POR_REVOLUCAO = 2048

PORTA_SERIAL = '/dev/ttyUSB0'  
BAUD_RATE = 115200

try:
    arduino = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=20)
    time.sleep(2) # Aguarda o Arduino resetar ao abrir a serial
    print("Conexão serial estabelecida.")
except Exception as e:
    print(f"Erro ao abrir serial: {e}")
    arduino = None

def calc_x(theta1, theta2, theta3):
    return math.cos(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3))
def calc_y(theta1, theta2, theta3):
    return math.sin(theta1) * (L2 * math.cos(theta2) + L3 * math.cos(theta2 + theta3))
def calc_z(theta1, theta2, theta3):
    return L1 + L2 * math.sin(theta2) + L3 * math.sin(theta2 + theta3)

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

def solve(theta1, theta2, theta3, xa, ya, za):
    q0 = np.array([theta1, theta2, theta3])
    X0 = np.array([calc_x(q0[0], q0[1], q0[2]), calc_y(q0[0], q0[1], q0[2]), calc_z(q0[0], q0[1], q0[2])])
    Xa = np.array([xa, ya, za]) 
    iteracoes = 0
    
    while np.linalg.norm(Xa - X0) > 0.1 and iteracoes < 1000:
        q0 = iteracao(q0, X0, Xa)
        X0 = np.array([calc_x(q0[0], q0[1], q0[2]), calc_y(q0[0], q0[1], q0[2]), calc_z(q0[0], q0[1], q0[2])])
        iteracoes += 1
    return q0

def converter_para_passos(angulos_rad):
    """Converte o vetor de ângulos radianos para posição absoluta em passos do motor."""
    passos = []
    for angulo in angulos_rad:
        angulo_normalizado = math.atan2(math.sin(angulo), math.cos(angulo))
        
        graus = math.degrees(angulo_normalizado)
        qtd_passos = int((graus / 360.0) * PASSOS_POR_REVOLUCAO)
        passos.append(qtd_passos)
        
    return passos
def enviar_para_arduino(passos):
    """Envia os passos formatados como uma string: <P1,P2,P3>"""
    if arduino and arduino.is_open:
        comando = f"<{passos[0]},{passos[1]},{passos[2]/2}>\n"
        arduino.write(comando.encode('utf-8'))
        print(f"Enviado: {comando.strip()}")
        
        resposta = arduino.readline().decode('utf-8').strip()
        if resposta:
            print(f"Arduino respondeu: {resposta}")
    else:
        print("Serial inativa. Comando simulado:", f"<{passos[0]},{passos[1]},{passos[2]}>")

# execucao principal
q_atual = [
    math.radians(0), 
    math.radians(45), 
    math.radians(-90)
]
alvo_x, alvo_y, alvo_z = 100, 100, 10

print(f"Calculando cinemática para atingir: X={alvo_x}, Y={alvo_y}, Z={alvo_z}")
q_novo = solve(q_atual[0], q_atual[1], q_atual[2], alvo_x, alvo_y, alvo_z)

print(f"angulos:{q_novo[0]}, {q_novo[1]}, {q_novo[2]}")
passos_alvo = converter_para_passos(q_novo)
print(f"Passos calculados: Base={passos_alvo[0]}, Ombro={passos_alvo[1]}, Cotovelo={passos_alvo[2]}")

enviar_para_arduino(passos_alvo)

q_atual = q_novo
