const int BASE_P1 = 10;
const int BASE_P2 = 11;
const int BASE_P3 = 12;
const int BASE_P4 = 13;

const int OMBRO_P1 = 2;
const int OMBRO_P2 = 3;
const int OMBRO_P3 = 4;
const int OMBRO_P4 = 5;

const int COTOVELO_P1 = 6;
const int COTOVELO_P2 = 7;
const int COTOVELO_P3 = 8;
const int COTOVELO_P4 = 9;

const byte numChars = 48;
char receivedChars[numChars];
bool newData = false;

int etapaBase = 0;
int etapaOmbro = 0;
int etapaCotovelo = 0;

const double velocidade_rpm = 3.0;

void setup() {
  Serial.begin(115200);

  pinMode(BASE_P1, OUTPUT);
  pinMode(BASE_P2, OUTPUT);
  pinMode(BASE_P3, OUTPUT);
  pinMode(BASE_P4, OUTPUT);

  pinMode(OMBRO_P1, OUTPUT);
  pinMode(OMBRO_P2, OUTPUT);
  pinMode(OMBRO_P3, OUTPUT);
  pinMode(OMBRO_P4, OUTPUT);

  pinMode(COTOVELO_P1, OUTPUT);
  pinMode(COTOVELO_P2, OUTPUT);
  pinMode(COTOVELO_P3, OUTPUT);
  pinMode(COTOVELO_P4, OUTPUT);

  Serial.println("Arduino pronto. Envie <modo,passosBase,passosOmbro,passosCotovelo>");
  Serial.println("modo 1 = sequencial, 2 = simultaneo mesma velocidade, 3 = proporcional");
}

void loop() {
  receberDadosSerial();
  if (newData) {
    processarComando();
    newData = false;
  }
}

void receberDadosSerial() {
  static bool recvInProgress = false;
  static byte ndx = 0;
  const char startMarker = '<';
  const char endMarker = '>';

  while (Serial.available() > 0 && newData == false) {
    char rc = Serial.read();

    if (recvInProgress) {
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

void aplicarEtapa(int etapa, int pin1, int pin2, int pin3, int pin4) {
  switch (etapa) {
    case 1:
      digitalWrite(pin1, HIGH); digitalWrite(pin2, LOW);  digitalWrite(pin3, LOW);  digitalWrite(pin4, LOW);
      break;
    case 2:
      digitalWrite(pin1, HIGH); digitalWrite(pin2, HIGH); digitalWrite(pin3, LOW);  digitalWrite(pin4, LOW);
      break;
    case 3:
      digitalWrite(pin1, LOW);  digitalWrite(pin2, HIGH); digitalWrite(pin3, LOW);  digitalWrite(pin4, LOW);
      break;
    case 4:
      digitalWrite(pin1, LOW);  digitalWrite(pin2, HIGH); digitalWrite(pin3, HIGH); digitalWrite(pin4, LOW);
      break;
    case 5:
      digitalWrite(pin1, LOW);  digitalWrite(pin2, LOW);  digitalWrite(pin3, HIGH); digitalWrite(pin4, LOW);
      break;
    case 6:
      digitalWrite(pin1, LOW);  digitalWrite(pin2, LOW);  digitalWrite(pin3, HIGH); digitalWrite(pin4, HIGH);
      break;
    case 7:
      digitalWrite(pin1, LOW);  digitalWrite(pin2, LOW);  digitalWrite(pin3, LOW);  digitalWrite(pin4, HIGH);
      break;
    default:
      digitalWrite(pin1, HIGH); digitalWrite(pin2, LOW);  digitalWrite(pin3, LOW);  digitalWrite(pin4, HIGH);
      break;
  }
}

void executarUmPasso(int direcao, int pin1, int pin2, int pin3, int pin4, int *etapaMotor) {
  *etapaMotor += direcao;

  if (*etapaMotor > 7) {
    *etapaMotor = 0;
  }
  if (*etapaMotor < 0) {
    *etapaMotor = 7;
  }

  aplicarEtapa(*etapaMotor, pin1, pin2, pin3, pin4);
}

unsigned long calcMotorDelayMicroseconds(double rpm) {
  return 60000000.0 / (4096.0 * rpm);
}

void moverSequencial(long passosBase, long passosOmbro, long passosCotovelo) {
  long totalBase = abs(passosBase);
  long totalOmbro = abs(passosOmbro);
  long totalCotovelo = abs(passosCotovelo);

  int dirBase = (passosBase >= 0) ? 1 : -1;
  int dirOmbro = (passosOmbro >= 0) ? 1 : -1;
  int dirCotovelo = (passosCotovelo >= 0) ? 1 : -1;

  unsigned long delay_us = calcMotorDelayMicroseconds(velocidade_rpm);

  for (long i = 0; i < totalBase; i++) {
    executarUmPasso(dirBase, BASE_P1, BASE_P2, BASE_P3, BASE_P4, &etapaBase);
    delayMicroseconds(delay_us);
  }

  for (long i = 0; i < totalOmbro; i++) {
    executarUmPasso(dirOmbro, OMBRO_P1, OMBRO_P2, OMBRO_P3, OMBRO_P4, &etapaOmbro);
    delayMicroseconds(delay_us);
  }

  for (long i = 0; i < totalCotovelo; i++) {
    executarUmPasso(dirCotovelo, COTOVELO_P1, COTOVELO_P2, COTOVELO_P3, COTOVELO_P4, &etapaCotovelo);
    delayMicroseconds(delay_us);
  }
}

void moverSimultaneoMesmaVelocidade(long passosBase, long passosOmbro, long passosCotovelo) {
  long restanteBase = abs(passosBase);
  long restanteOmbro = abs(passosOmbro);
  long restanteCotovelo = abs(passosCotovelo);

  int dirBase = (passosBase >= 0) ? 1 : -1;
  int dirOmbro = (passosOmbro >= 0) ? 1 : -1;
  int dirCotovelo = (passosCotovelo >= 0) ? 1 : -1;

  unsigned long delay_us = calcMotorDelayMicroseconds(velocidade_rpm);

  while (restanteBase > 0 || restanteOmbro > 0 || restanteCotovelo > 0) {
    if (restanteBase > 0) {
      executarUmPasso(dirBase, BASE_P1, BASE_P2, BASE_P3, BASE_P4, &etapaBase);
      restanteBase--;
    }

    if (restanteOmbro > 0) {
      executarUmPasso(dirOmbro, OMBRO_P1, OMBRO_P2, OMBRO_P3, OMBRO_P4, &etapaOmbro);
      restanteOmbro--;
    }

    if (restanteCotovelo > 0) {
      executarUmPasso(dirCotovelo, COTOVELO_P1, COTOVELO_P2, COTOVELO_P3, COTOVELO_P4, &etapaCotovelo);
      restanteCotovelo--;
    }

    delayMicroseconds(delay_us);
  }
}

void moverProporcional(long passosBase, long passosOmbro, long passosCotovelo) {
  long totalBase = abs(passosBase);
  long totalOmbro = abs(passosOmbro);
  long totalCotovelo = abs(passosCotovelo);

  if (totalBase == 0 && totalOmbro == 0 && totalCotovelo == 0) {
    return;
  }

  int dirBase = (passosBase >= 0) ? 1 : -1;
  int dirOmbro = (passosOmbro >= 0) ? 1 : -1;
  int dirCotovelo = (passosCotovelo >= 0) ? 1 : -1;

  long totalMax = totalBase;
  if (totalOmbro > totalMax) totalMax = totalOmbro;
  if (totalCotovelo > totalMax) totalMax = totalCotovelo;

  double passoBase = (totalBase > 0) ? (double)totalBase / (double)totalMax : 0.0;
  double passoOmbro = (totalOmbro > 0) ? (double)totalOmbro / (double)totalMax : 0.0;
  double passoCotovelo = (totalCotovelo > 0) ? (double)totalCotovelo / (double)totalMax : 0.0;

  double acumuladorBase = 0.0;
  double acumuladorOmbro = 0.0;
  double acumuladorCotovelo = 0.0;

  long restanteBase = totalBase;
  long restanteOmbro = totalOmbro;
  long restanteCotovelo = totalCotovelo;

  unsigned long delay_us = calcMotorDelayMicroseconds(velocidade_rpm);

  for (long i = 0; i < totalMax; i++) {
    acumuladorBase += passoBase;
    acumuladorOmbro += passoOmbro;
    acumuladorCotovelo += passoCotovelo;

    if (acumuladorBase >= 1.0 && restanteBase > 0) {
      executarUmPasso(dirBase, BASE_P1, BASE_P2, BASE_P3, BASE_P4, &etapaBase);
      acumuladorBase -= 1.0;
      restanteBase--;
    }

    if (acumuladorOmbro >= 1.0 && restanteOmbro > 0) {
      executarUmPasso(dirOmbro, OMBRO_P1, OMBRO_P2, OMBRO_P3, OMBRO_P4, &etapaOmbro);
      acumuladorOmbro -= 1.0;
      restanteOmbro--;
    }

    if (acumuladorCotovelo >= 1.0 && restanteCotovelo > 0) {
      executarUmPasso(dirCotovelo, COTOVELO_P1, COTOVELO_P2, COTOVELO_P3, COTOVELO_P4, &etapaCotovelo);
      acumuladorCotovelo -= 1.0;
      restanteCotovelo--;
    }

    delayMicroseconds(delay_us);
  }
}

void processarComando() {
  char *token;
  long modo;
  long passosBase;
  long passosOmbro;
  long passosCotovelo;

  token = strtok(receivedChars, ",");
  if (token == NULL) return;
  modo = atol(token);

  token = strtok(NULL, ",");
  if (token == NULL) return;
  passosBase = atol(token);

  token = strtok(NULL, ",");
  if (token == NULL) return;
  passosOmbro = atol(token);

  token = strtok(NULL, ",");
  if (token == NULL) return;
  passosCotovelo = atol(token);

  if (modo == 1) {
    moverSequencial(passosBase, -passosOmbro, passosCotovelo);
  } else if (modo == 2) {
    moverSimultaneoMesmaVelocidade(passosBase, -passosOmbro, passosCotovelo);
  } else {
    moverProporcional(passosBase, -passosOmbro, passosCotovelo);
  }

  Serial.print("OK ");
  Serial.print(modo);
  Serial.print(",");
  Serial.print(passosBase);
  Serial.print(",");
  Serial.print(passosOmbro);
  Serial.print(",");
  Serial.println(passosCotovelo);
}
