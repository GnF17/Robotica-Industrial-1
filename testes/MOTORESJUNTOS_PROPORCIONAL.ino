#include <AccelStepper.h>
#include <MultiStepper.h>

const int stepsPerRevolution = 2048;

// Mesma pinagem dos outros sketches
AccelStepper rightStepper(AccelStepper::FULL4WIRE, 2, 4, 3, 5);
AccelStepper leftStepper(AccelStepper::FULL4WIRE, 6, 8, 7, 9);
AccelStepper bottomStepper(AccelStepper::FULL4WIRE, 10, 12, 11, 13);

MultiStepper steppers;

const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;

void setup() {
  Serial.begin(115200);

  // Mesmo teto de velocidade para todos: o MultiStepper distribui a velocidade
  // proporcionalmente ao número de passos de cada motor.
  rightStepper.setMaxSpeed(100.0);
  leftStepper.setMaxSpeed(100.0);
  bottomStepper.setMaxSpeed(100.0);

  // O rightStepper é o ombro e está montado com sentido físico invertido.
  rightStepper.setPinsInverted(true, false, false);

  // Posição inicial física do robô em passos
  bottomStepper.setCurrentPosition(0);
  rightStepper.setCurrentPosition(512);
  leftStepper.setCurrentPosition(-512);

  steppers.addStepper(bottomStepper);
  steppers.addStepper(rightStepper);
  steppers.addStepper(leftStepper);

  Serial.println("Arduino pronto. Movimento proporcional e sincronizado.");
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
      } else {
        receivedChars[ndx] = '\0';
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    } else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

void processarComando() {
  char *strtokIndx;
  long alvoBase, alvoOmbro, alvoCotovelo;

  strtokIndx = strtok(receivedChars, ",");
  alvoBase = atol(strtokIndx);

  strtokIndx = strtok(NULL, ",");
  alvoOmbro = atol(strtokIndx);

  strtokIndx = strtok(NULL, ",");
  alvoCotovelo = atol(strtokIndx);

  long alvos[3];
  alvos[0] = alvoBase;
  alvos[1] = alvoOmbro;
  alvos[2] = alvoCotovelo;

  // O MultiStepper calcula velocidades proporcionais para que todos os motores
  // cheguem ao destino ao mesmo tempo.
  steppers.moveTo(alvos);
  steppers.runSpeedToPosition();

  Serial.print("Movimento proporcional concluido em: ");
  Serial.print(alvoBase);
  Serial.print(", ");
  Serial.print(alvoOmbro);
  Serial.print(", ");
  Serial.print(alvoCotovelo);
  Serial.println();
}