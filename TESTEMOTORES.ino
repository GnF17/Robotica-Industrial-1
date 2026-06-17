#include <Stepper.h>

const int stepsPerRevolution = 2048; 

// Mantendo exatamente os pinos que você configurou
Stepper myStepper(stepsPerRevolution, 2, 4, 3, 5);
Stepper leftStepper(stepsPerRevolution, 6, 7, 8, 9);
Stepper bottomStepper(stepsPerRevolution, 10, 11, 12, 13);

// Variáveis para rastrear a posição absoluta atual das juntas
long posAtualBase = 0;
long posAtualOmbro = 0;
long posAtualCotovelo = 0;

// Variáveis de buffer para a comunicação Serial
const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;

void setup() {
  // Ajustado para 115200 para casar com o script Python
  Serial.begin(115200); 
  
  myStepper.setSpeed(10); 
  leftStepper.setSpeed(10);
  bottomStepper.setSpeed(10);

  Serial.println("Arduino com Stepper.h pronto. Aguardando comandos...");
}

void loop() {
  receberDadosSerial();
  
  // Se um pacote completo no formato <P1,P2,P3> chegou, processamos
  if (newData == true) {
    processarComando();
    newData = false;
  }
}

// Função não-bloqueante para ler a string entre '<' e '>'
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
                receivedChars[ndx] = '\0'; // Finaliza a string
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

// Extrai os valores e converte para movimento relativo
void processarComando() {
    char * strtokIndx; 
    long alvoBase, alvoOmbro, alvoCotovelo;

    // Divide a string recebida nas vírgulas
    strtokIndx = strtok(receivedChars, ","); 
    alvoBase = atol(strtokIndx);    
 
    strtokIndx = strtok(NULL, ","); 
    alvoOmbro = atol(strtokIndx);

    strtokIndx = strtok(NULL, ","); 
    alvoCotovelo = atol(strtokIndx);

    // Calcula quantos passos o motor DEVE dar a partir de onde está agora
    long passosBase = alvoBase - posAtualBase;
    long passosOmbro = alvoOmbro - posAtualOmbro;
    long passosCotovelo = alvoCotovelo - posAtualCotovelo;

    // Aciona os motores (Sequencialmente devido ao comportamento do Stepper.h)
    myStepper.step(passosBase);
    leftStepper.step(passosOmbro);
    bottomStepper.step(passosCotovelo);

    // Atualiza o estado interno do robô para os novos alvos
    posAtualBase = alvoBase;
    posAtualOmbro = alvoOmbro;
    posAtualCotovelo = alvoCotovelo;

    // Retorna uma confirmação para o Python ler no console
    Serial.print("Chegou nos alvos: ");
    Serial.print(posAtualBase); Serial.print(", ");
    Serial.print(posAtualOmbro); Serial.print(", ");
    Serial.println(posAtualCotovelo);
}