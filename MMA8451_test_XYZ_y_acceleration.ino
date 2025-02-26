#include <Wire.h>
#include <Adafruit_MMA8451.h>
#include <Adafruit_Sensor.h>
                                  // testing a new accelerometer
Adafruit_MMA8451 mma = Adafruit_MMA8451();
static int loop_counter = 0;

void setup(void) {
  Serial.begin(9600);
  
  Serial.println("start test");
  

  if (! mma.begin()) {
    Serial.println("Couldnt start");
    while (1);
  }
  
  mma.setRange(MMA8451_RANGE_2_G);    // set the max range of values. lower ranges have higher resolution
  Serial.print("Range = "); Serial.print(2 << mma.getRange());  
  Serial.println("G");
}

int find_avg(int valueArray[]){       
  int avg = 0;
  for(int i = 0; i < 4; i++){
    avg += valueArray[i];
  }
  avg = avg/4.0;
  avg += 0.5;                         // round up the number by adding .5 and floor the result
  avg = int(avg);
  return avg;
}

void loop() {
  // Read the 'raw' data in 14-bit counts
  int myX[4];
  int myY[4];
  int myZ[4];
  while (loop_counter < 4){
    sensors_event_t event; 
    mma.getEvent(&event);

    myX[loop_counter] = event.acceleration.x;
    myY[loop_counter] = event.acceleration.y;
    myZ[loop_counter] = event.acceleration.z;

  
    //acceleration is measured in m/s^2 
  
    //average 4 value reads
  
    delay(50);
    loop_counter++;
  }
  loop_counter = 0;
  Serial.print("x:");
  Serial.println(find_avg(myX));
  Serial.print("y:");
  Serial.println(find_avg(myY));
  Serial.print("z:");
  Serial.println(find_avg(myZ));
  
}
