#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "driver/i2c.h"
#include "mpu9250.h"
#include "ble_module.h"


#define IMUTAG "MPU9250"

char blename[]="open-ring";

void app_main(void)
{
    ble_init(blename);
    mpu9250_i2c_init(8,9); //sda,scl
    mpu9250_init();
    
    char send_data[50];
    while(1){
        mpu9250_data_t data;
        mpu9250_read_all(&data);
        sprintf(send_data,"%d,%d,%d,%d,%d,%d" , data.accel_x,data.accel_y,data.accel_z,data.gyro_x,data.gyro_y,data.gyro_z);
        printf("%s\n",send_data);
        ble_send(send_data);
        printf("sucessfully sent");
        vTaskDelay(pdMS_TO_TICKS(10));



    }

}