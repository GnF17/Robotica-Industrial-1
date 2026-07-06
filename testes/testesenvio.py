import serial
import time

# Configurações da porta serial - ajuste se necessário
PORTA_SERIAL = '/dev/ttyUSB0'
BAUD_RATE = 115200

try:
    # Inicializa a conexão serial
    arduino = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=2)
    time.sleep(2)  # Tempo necessário para o Arduino reiniciar após abrir a conexão
    print("Conexão serial estabelecida com sucesso!")
except Exception as e:
    print(f"Erro ao abrir a porta serial: {e}")
    arduino = None

print("Digite 'sair' para encerrar o programa.\n")

while True:
    # Solicita a entrada do usuário
    entrada = input("Digite os 4 números separados por espaço (ex: 1 -512 30 100): ").strip()
    
    # Condição de saída
    if entrada.lower() in {'sair', 'exit', 'quit'}:
        print("Encerrando o programa.")
        if arduino and arduino.is_open:
            arduino.close()
        break

    # Substitui vírgulas por espaços e divide a string pelos espaços
    partes = entrada.replace(",", " ").split()

    # Verifica se o usuário realmente digitou 4 valores
    if len(partes) != 4:
        print(f"Erro: Você digitou {len(partes)} valores. É necessário digitar exatamente 4 números.")
        continue

    try:
        # Converte para inteiro para garantir que são números válidos
        n1 = int(partes[0])
        n2 = int(partes[1])
        n3 = int(partes[2])
        n4 = int(partes[3])
    except ValueError:
        print("Erro: Todos os 4 valores precisam ser números inteiros válidos.")
        continue

    # Monta a string no formato de pacote padrão esperado por muitos firmwares
    comando = f"<{n1},{n2},{n3},{n4}>\n"

    # Envia os dados para o Arduino
    if arduino and arduino.is_open:
        arduino.write(comando.encode('utf-8'))
        print(f"Enviado para o Arduino: {comando.strip()}")
        
        # Opcional: Aguarda e lê a resposta imediata do Arduino (eco)
        resposta = arduino.readline().decode('utf-8').strip()
        if resposta:
            print(f"Resposta do Arduino: {resposta}")
    else:
        print(f"Serial inativa. Comando simulado: {comando.strip()}")
    
    print("-" * 40)
