#ifndef MPU9250_H
#define MPU9250_H

#include <stdint.h>


typedef struct {
    int16_t accel_x;
    int16_t accel_y;
    int16_t accel_z;
    int16_t gyro_x;
    int16_t gyro_y;
    int16_t gyro_z;
} mpu9250_data_t;


void mpu9250_i2c_init(int sda, int scl);
void mpu9250_init(void);
void mpu9250_read_all(mpu9250_data_t *data);

#endif
