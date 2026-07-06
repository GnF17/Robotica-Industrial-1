import math
import serial
import time

# --- Dimensões Físicas (mm) ---
L2 = 90.0
L3 = 90.0

# Offsets do paralelogramo mecânico
OFFSET_R = 30.0
OFFSET_Z = 40.0

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


def solve_analitico(xa, ya, za):
    """Calcula a cinemática geométrica exata usando alvos virtuais."""
    theta1 = math.atan2(ya, xa)
    r_alvo = math.sqrt(xa**2 + ya**2)

    r_virtual = r_alvo - OFFSET_R
    z_virtual = za - OFFSET_Z

    R_quadrado = r_virtual**2 + z_virtual**2

    # Trava de segurança física
    if R_quadrado > (L2 + L3)**2 or R_quadrado < (L2 - L3)**2:
        print("ALERTA: Coordenada fora do volume de trabalho do robô!")
        return None

    # Lei dos cossenos
    D = (R_quadrado - L2**2 - L3**2) / (2 * L2 * L3)
    D = max(min(D, 1.0), -1.0) # Evita erro de float próximo a 1.0 ou -1.0

    # Configuração Elbow Up (cotovelo para cima/frente)
    theta3 = math.atan2(-math.sqrt(1 - D**2), D)
    theta2 = math.atan2(z_virtual, r_virtual) - math.atan2(L3 * math.sin(theta3), L2 + L3 * math.cos(theta3))

    return [theta1, theta2, theta3]


def converter_para_passos(angulos_rad):
    """Converte radianos para a posição absoluta teórica em passos."""
    passos = []
    for angulo in angulos_rad:
        graus = math.degrees(angulo)
        qtd_passos = int((graus / 360.0) * PASSOS_POR_REVOLUCAO)
        passos.append(qtd_passos)
    return passos


def enviar_para_arduino(passos):
    """Envia as posições absolutas PURAS. O Arduino cuidará dos offsets e inversões físicas."""
    alvo_b = -int(passos[0])
    alvo_o = int(passos[1])
    alvo_c = int(passos[2])

    if arduino and arduino.is_open:
        comando = f"<{alvo_b},{alvo_o},{alvo_c}>\n"
        arduino.write(comando.encode('utf-8'))
        print(f"Enviado para o Arduino: {comando.strip()}")

        resposta = arduino.readline().decode('utf-8').strip()
        if resposta:
            print(f"Arduino respondeu: {resposta}")
    else:
        print("Serial inativa. Comando simulado:", f"<{alvo_b},{alvo_o},{alvo_c}>")


# ==========================================
#            EXECUÇÃO PRINCIPAL
# ==========================================

# Coordenada alvo da ponta da garra em milímetros
alvo_x, alvo_y, alvo_z = 100, 100, 0

print(f"Calculando cinemática analítica para atingir: X={alvo_x}, Y={alvo_y}, Z={alvo_z}")
q_novo = solve_analitico(alvo_x, alvo_y, alvo_z)

if q_novo is not None:
    print(f"Ângulos Radianos: Base={q_novo[0]:.3f}, Ombro={q_novo[1]:.3f}, Cotovelo={q_novo[2]:.3f}")

    passos_alvo = converter_para_passos(q_novo)
    print(f"Passos absolutos matemáticos: Base={passos_alvo[0]}, Ombro={passos_alvo[1]}, Cotovelo={passos_alvo[2]}")

    enviar_para_arduino(passos_alvo)
else:
    print("Movimento abortado para proteger a estrutura.")
