import serial
import time

PORTA = '/dev/ttyUSB0' 
BAUD_RATE = 9600

def mover_motor(passos):
    try:
        print(f"Conectando ao Arduino na porta {PORTA}...")
        arduino = serial.Serial(PORTA, BAUD_RATE, timeout=1)
        
        time.sleep(2) 
        
        print(f"Enviando comando de {passos} passos...")
        comando = f"{passos}\n".encode()
        arduino.write(comando)
        
        arduino.close()
        print("Comando enviado com sucesso.")

    except serial.SerialException as e:
        print(f"Erro na porta serial: {e}")
        print("Verifique se o cabo está conectado e se você tem permissão de leitura/escrita na porta.")

if __name__ == "__main__":
    mover_motor(500)
