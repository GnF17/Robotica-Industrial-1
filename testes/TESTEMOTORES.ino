#include <Stepper.h>

const int stepsPerRevolution = 2048; 

// A sua pinagem original intocada
Stepper rightStepper(stepsPerRevolution, 2, 4, 3, 5);
Stepper leftStepper(stepsPerRevolution, 6, 8,7, 9);
Stepper bottomStepper(stepsPerRevolution, 10, 12,11, 13);

// 1. O robô nasce sabendo que a posição física do "L" não é o zero matemático
long posAtualBase = 0;           
long posAtualOmbro = 512;        // 90 graus
long posAtualCotovelo = -512;    // -90 graus

const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;

void setup() {
  Serial.begin(115200); 
  
  // Velocidade aumentada para o robô não parecer que está travado
  rightStepper.setSpeed(1); 
  leftStepper.setSpeed(1);
  bottomStepper.setSpeed(1);

  Serial.println("Arduino pronto.");
}

void loop() {
  receberDadosSerial();
  if (newData == true) {
    processarComando();
    newData = false;
  }
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

    // Calcula a diferença real (A Matemática Pura)
    long passosBase = alvoBase - posAtualBase;
    long passosOmbro = alvoOmbro - posAtualOmbro;
    long passosCotovelo = alvoCotovelo - posAtualCotovelo;

    // 2. A INVERSÃO DE HARDWARE
    // Aciona os motores invertendo apenas a polaridade final de execução do motor defeituoso
    bottomStepper.step(passosBase);
    
    // O sinal negativo (-) inverte fisicamente o Ombro, mas não altera a variável "posAtual"
    leftStepper.step(passosCotovelo);
    rightStepper.step(-passosOmbro); 
    
    
    
    // Atualiza a memória com o alvo real (para o próximo movimento não bugar)
    posAtualBase = alvoBase;
    posAtualOmbro = alvoOmbro;
    posAtualCotovelo = alvoCotovelo;

    Serial.print("Chegou nos alvos: ");
    Serial.print(posAtualBase); Serial.print(", ");
    Serial.print(posAtualOmbro); Serial.print(", ");
    Serial.println(posAtualCotovelo);
}