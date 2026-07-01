#include <AccelStepper.h>

const int stepsPerRevolution = 2048; 

// A AccelStepper usa a constante FULL4WIRE. 
// Mantive EXATAMENTE a sua pinagem cruzada (ex: 2, 4, 3, 5).
AccelStepper rightStepper(AccelStepper::FULL4WIRE, 2, 4, 3, 5);
AccelStepper leftStepper(AccelStepper::FULL4WIRE, 6, 8, 7, 9);
AccelStepper bottomStepper(AccelStepper::FULL4WIRE, 10, 12, 11, 13);

const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;
void setup() {
  Serial.begin(115200); 
  
  // 1. Velocidade e Aceleração Conservadoras (O Segredo para não vibrar)
  // Baixamos para 100 passos/s com uma rampa de aceleração bem suave de 30.
  rightStepper.setMaxSpeed(100.0);
  rightStepper.setAcceleration(30.0);
  
  leftStepper.setMaxSpeed(100.0);
  leftStepper.setAcceleration(30.0);
  
  bottomStepper.setMaxSpeed(100.0);
  bottomStepper.setAcceleration(30.0);

    // 2. A Inversão de Hardware
    // O rightStepper é o ombro e sua montagem física está invertida.
    rightStepper.setPinsInverted(true, false, false);

  // 3. O robô nasce sabendo a posição física do "L"
  bottomStepper.setCurrentPosition(0);           
  rightStepper.setCurrentPosition(512);    // 90 graus
  leftStepper.setCurrentPosition(-512);    // -90 graus

  Serial.println("Arduino pronto. Motores simultaneos e estabilizados.");
}

void loop() {
  receberDadosSerial();
  if (newData == true) {
    processarComando();
    newData = false;
  }

  // 4. O MOTOR DA SIMULTANEIDADE
  // Essa função deve rodar livremente no loop. Ela checa se o motor
  // chegou no destino. Se não chegou, ela dá apenas 1 passo e pula pro próximo.
  // IMPORTANTE: Nunca use delay() no seu código com essa biblioteca!
  bottomStepper.run();
  rightStepper.run();
  leftStepper.run();
}

void receberDadosSerial() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; 
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }
        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void processarComando() {
    char * strtokIndx; 
    long alvoBase, alvoOmbro, alvoCotovelo;

    strtokIndx = strtok(receivedChars, ","); 
    alvoBase = atol(strtokIndx);    
 
    strtokIndx = strtok(NULL, ","); 
    alvoOmbro = atol(strtokIndx);

    strtokIndx = strtok(NULL, ","); 
    alvoCotovelo = atol(strtokIndx);

    // 5. ATRIBUIÇÃO DIRETA
    // A AccelStepper trabalha com coordenadas ABSOLUTAS nativamente.
    // Nós não precisamos mais fazer a conta de delta (alvo - posAtual).
    // Basta dizer "vá para a coordenada X" e ela calcula os passos sozinha.
    bottomStepper.moveTo(alvoBase);
    rightStepper.moveTo(alvoOmbro); 
    leftStepper.moveTo(alvoCotovelo);

    Serial.print("Iniciando interpolacao simultanea para: ");
    Serial.print(alvoBase); Serial.print(", ");
    Serial.print(alvoOmbro); Serial.print(", ");
    Serial.println(alvoCotovelo);
}