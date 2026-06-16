#include <Stepper.h>

const int stepsPerRevolution = 2048; 


Stepper myStepper(stepsPerRevolution, 2, 4, 3, 5);
Stepper leftStepper(stepsPerRevolution,6, 7, 8, 9);
Stepper bottomStepper(stepsPerRevolution, 10, 11, 12, 13);

void setup() {
  Serial.begin(9600);
  myStepper.setSpeed(10); 
  leftStepper.setSpeed(10);
  bottomStepper.setSpeed(10);
}

void loop() {
  if (Serial.available() > 0) {
    int steps = Serial.parseInt(); 
    if (steps != 0) {
      myStepper.step(steps);
      leftStepper.step(steps);
      bottomStepper.step(steps);
    }
  }
}
