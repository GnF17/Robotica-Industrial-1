const int BASE_P1 = 10;
const int BASE_P2 = 12;
const int BASE_P3 = 11;
const int BASE_P4 = 13;

const int OMBRO_P1 = 2;
const int OMBRO_P2 = 4;
const int OMBRO_P3 = 3;
const int OMBRO_P4 = 5;

const int COTOVELO_P1 = 6;
const int COTOVELO_P2 = 8;
const int COTOVELO_P3 = 7;
const int COTOVELO_P4 = 9;

const byte numChars = 40;
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

  Serial.println("Arduino pronto. Envie <passosBase,passosOmbro,passosCotovelo>");
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

void executar_passos_delta(long num_passos, int pin1, int pin2, int pin3, int pin4, int *etapaMotor, unsigned long delay_us) {
  int direcao = (num_passos >= 0) ? 1 : -1;
  long total_passos = abs(num_passos);

  for (long i = 0; i < total_passos; i++) {
    *etapaMotor += direcao;

    if (*etapaMotor > 7) {
      *etapaMotor = 0;
    }
    if (*etapaMotor < 0) {
      *etapaMotor = 7;
    }

    aplicarEtapa(*etapaMotor, pin1, pin2, pin3, pin4);
    delayMicroseconds(delay_us);
  }
}

void processarComando() {
  char *token;
  long passosBase;
  long passosOmbro;
  long passosCotovelo;

  token = strtok(receivedChars, ",");
  if (token == NULL) return;
  passosBase = atol(token);

  token = strtok(NULL, ",");
  if (token == NULL) return;
  passosOmbro = atol(token);

  token = strtok(NULL, ",");
  if (token == NULL) return;
  passosCotovelo = atol(token);

  unsigned long delay_us = calcMotorDelayMicroseconds(velocidade_rpm);

  // Mantem o mesmo sentido físico adotado no sketch com Stepper: ombro invertido.
  executar_passos_delta(passosBase, BASE_P1, BASE_P2, BASE_P3, BASE_P4, &etapaBase, delay_us);
  executar_passos_delta(-passosOmbro, OMBRO_P1, OMBRO_P2, OMBRO_P3, OMBRO_P4, &etapaOmbro, delay_us);
  executar_passos_delta(passosCotovelo, COTOVELO_P1, COTOVELO_P2, COTOVELO_P3, COTOVELO_P4, &etapaCotovelo, delay_us);

  Serial.print("OK ");
  Serial.print(passosBase);
  Serial.print(",");
  Serial.print(passosOmbro);
  Serial.print(",");
  Serial.println(passosCotovelo);
}

unsigned long calcMotorDelayMicroseconds(double rpm) {
  return 60000000.0 / (4096.0 * rpm);
}


