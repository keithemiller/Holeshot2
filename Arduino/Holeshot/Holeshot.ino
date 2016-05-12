/*
*Holeshot2.0 Arduino Code
*
*The arduino sends the steering and throttle control signals to the motor controller.
*
*There are three modes:
*  1) Serial Mode which sets the throttle/steering to values received through the serial port.
*  2) RC Mode which sets the throttle/steering to the value based on the signal received by the radio receiver.
*  3) Kill_All mode stops the car.
*
*Things to note:
* - Serial Baud Rate = 115200
* - Default Mode is RC_CONTROL_MODE
* 
*Things that need to be done:
* - Add switch to start in RC vs AUTO
* - Add button to tell AUTO to GO
* - Add LCD display for messages
*/

#include <EnableInterrupt.h>

// Pins
#define MOTOR_PIN 10
#define STEERING_PIN 9
#define THROTTLE_INPUT_PIN 3
#define STEERING_INPUT_PIN 2
#define ENCODER_PIN A0

// Car Modes
#define AUTO_DRIVE_MODE -1
#define RC_CONTROL_MODE 1
#define WAIT_MODE 0
#define KILL_ALL_MODE 98

//For serial connection***
#define THROTTLE_FLAG 't'
#define STEERING_FLAG 's'
#define KILLALL_FLAG 'k'
#define HEARTBEAT 'h'
#define NO_SERIAL_AVAL 9
#define HEARTBEAT_THRESHOLD 200
String temp_str = "";
short crt_code = -1;
int crt_value = -1;
int heartbeat_cnt = 0;
//************************

volatile long pwm_value = 0;
volatile long prev_time = 0;

volatile long throtPwmValue = 0;
volatile long throtPrevValue = 0;

volatile long steeringPwmValue = 0;
volatile long steeringPrevValue = 0;

volatile long robotMode = RC_CONTROL_MODE;

int stringReferences[10];
int numReferences = 0;

// ####################### HELPER FUNCTIONS ##########################

void __risingThrottle()
{
  enableInterrupt(THROTTLE_INPUT_PIN, __fallingThrottle, FALLING);
  throtPrevValue = micros();
}

void __fallingThrottle()
{
  enableInterrupt(THROTTLE_INPUT_PIN, __risingThrottle, RISING);
  throtPwmValue = micros() - throtPrevValue;
}

void __risingSteering()
{
  enableInterrupt(STEERING_INPUT_PIN, __fallingSteering, FALLING);
  steeringPrevValue = micros();
}

void __fallingSteering()
{
  enableInterrupt(STEERING_INPUT_PIN, __risingSteering, RISING);
  steeringPwmValue = micros() - steeringPrevValue;
}

void __rising()
{
  enableInterrupt(ENCODER_PIN, __falling, FALLING);
}

void __falling()
{
  enableInterrupt(ENCODER_PIN, __rising, RISING);
  pwm_value = micros() - prev_time;
  prev_time = micros();
  //Serial.println(pwm_value);
}

void __setPWM(int pin, float ms) // 1.5ms = stop, 1ms->2ms is reverse->forward
{
  float msPerPeriod = 8.192; // 256 [from setPwmFrequency(..., 256)] / 31250Hz = 8.192ms
  float maxAnalogValue = 255;
  int analogValue = (ms / msPerPeriod) * maxAnalogValue + 1;
  analogWrite(pin, analogValue);
}

/** 
 *  This code was found here:
 *  http://playground.arduino.cc/Code/PwmFrequency
 */
void setPwmFrequency(int pin, int divisor) {
  byte mode;
  if(pin == 5 || pin == 6 || pin == 9 || pin == 10) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 64: mode = 0x03; break;
      case 256: mode = 0x04; break;
      case 1024: mode = 0x05; break;
      default: return;
    }
    if(pin == 5 || pin == 6) {
      TCCR0B = TCCR0B & 0b11111000 | mode;
    } else {
      TCCR1B = TCCR1B & 0b11111000 | mode;
    }
  } else if(pin == 3 || pin == 11) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 32: mode = 0x03; break;
      case 64: mode = 0x04; break;
      case 128: mode = 0x05; break;
      case 256: mode = 0x06; break;
      case 1024: mode = 0x7; break;
      default: return;
    }
    TCCR2B = TCCR2B & 0b11111000 | mode;
  }
}

int stringToNumber(String thisString) {
  thisString[0] = '0';
  int length = thisString.length();

  return thisString.toInt();
}

/*
 * Serial Baud Rate = 115200
 */
void get_serial_command(){
  
  for (int i = 0; i < 100; i++){
    if (Serial.available() > 0){       
          char b = Serial.read();
          
          if (b != '!'){
              temp_str += b;
          }
          
          else if (b == '!'){
              crt_code = temp_str[0];
              temp_str[0] = '0';
              crt_value = stringToNumber(temp_str);
              temp_str = "";
              return;
          }
      }
  }
  crt_code = NO_SERIAL_AVAL;
}

double normalize_serial_input(int in){
  double normalized = in;
  normalized = normalized / 100.0;
  normalized = normalized + 1;
  return normalized;
}
// ########################## END HELPER FUNCTIONS #########################


void setup() 
{
  setPwmFrequency(MOTOR_PIN, 256);
  setPwmFrequency(STEERING_PIN, 256);

  pinMode(A1, INPUT);
  
  enableInterrupt(ENCODER_PIN, __rising, RISING);
  enableInterrupt(THROTTLE_INPUT_PIN, __risingThrottle, RISING);
  enableInterrupt(STEERING_INPUT_PIN, __risingSteering, RISING);
  prev_time = micros();
  Serial.begin(115200);
}


void loop() 
{

  if (robotMode == WAIT_MODE){
    //TODO
    Serial.println("NOT IMPLEMENTED");
  }
  else if (robotMode == AUTO_DRIVE_MODE)
  {
    // RC takes over if the RC controller sends drive signals
    if ((throtPwmValue < 1700 && throtPwmValue > 1600) || (throtPwmValue < 1400 && throtPwmValue > 1300)){
      robotMode = RC_CONTROL_MODE;
      return; // Continues the main loop
    }
    
    double num = 4.0;
    get_serial_command();
    switch (crt_code)
    {
      case HEARTBEAT:
        heartbeat_cnt = 0;
        break;
      case NO_SERIAL_AVAL:
        heartbeat_cnt++;
        //if (heartbeat_cnt > HEARTBEAT_THRESHOLD) { robotMode = 1; }
        break;
      case THROTTLE_FLAG:
        heartbeat_cnt = 0;
        __setPWM(MOTOR_PIN, normalize_serial_input(crt_value));
        delay(10);
        break;
      case STEERING_FLAG:
        heartbeat_cnt = 0;
        num = normalize_serial_input(crt_value);
        __setPWM(STEERING_PIN, normalize_serial_input(crt_value));
        break;
      case KILLALL_FLAG:
        heartbeat_cnt = 0;
        __setPWM(MOTOR_PIN, 1.5);
        __setPWM(STEERING_PIN, 1.5);
        robotMode = KILL_ALL_MODE;
        break;
    }
  }

  // This is drive by controller mode.  To return back to the previous mode, reset the arduino.
  else 
  {
    if (throtPwmValue > 800 && throtPwmValue < 2200)
    {
      __setPWM(MOTOR_PIN, (float)throtPwmValue/1000.0);
    }
    else
    {
      __setPWM(MOTOR_PIN, 1.5);
    }
  
    if (steeringPwmValue > 800 && steeringPwmValue < 2200)
    {
      __setPWM(STEERING_PIN, (float)steeringPwmValue/1000.0);
    }
    else
    {
      __setPWM(STEERING_PIN, 1.5);
    }
  }
/*
  // KillAll Mode
  else if (robotMode == KILL_ALL_MODE)
  {
    __setPWM(MOTOR_PIN, 1.5);
    __setPWM(STEERING_PIN, 1.5);
    delay(50);
  }
 */
}

