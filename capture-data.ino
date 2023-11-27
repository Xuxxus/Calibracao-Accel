//Bibliotecas utilizadas
#include <Wire.h>
#include <MPU6050_tockn.h>

MPU6050 mpu6050(Wire);

// Variáveis globais
uint32_t delayPeriod = 1;
uint32_t now, then;
float ax, ay,az; //variaies utilizadas na fucao do acelerometro

void setup() {
  Serial.begin(115200);
  
  Wire.begin();
  mpu6050.begin();
  mpu6050.calcGyroOffsets(true);


  now = 0;
  then = 0;
  ax = 0.0f;
  ay = 0.0f;
  az = 0.0f;
}

void loop() {

  //atualização inicial do imu
  mpu6050.update();

  now = millis();

  if (now - then >= delayPeriod) {
    // Leitura dos dados do MPU6050
    ax = mpu6050.getAccX();
    ay = mpu6050.getAccY();
    az = mpu6050.getAccZ();

    // Imprimir os valores
    Serial.print(ax, 6);
    Serial.print(",");
    Serial.print(ay, 6);
    Serial.print(",");
    Serial.println(az, 6);

    mpu6050.update();
    then = now;
    delay(0.5);

    } else {
      Serial.println("[ERROR]: Erro de leitura do sensor.");
    }
}
