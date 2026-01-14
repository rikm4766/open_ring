#include "mpu9250.h"
#include "driver/i2c.h"
#include "esp_log.h"

#define MPU9250_ADDR         0x68
#define I2C_MASTER_NUM       I2C_NUM_0
// #define I2C_MASTER_SDA_IO    21
// #define I2C_MASTER_SCL_IO    22
#define I2C_MASTER_FREQ_HZ   400000

static const char *TAG = "MPU9250";

void mpu9250_i2c_init(int sda, int scl) {
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = sda,
        .scl_io_num = scl,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };
    i2c_param_config(I2C_MASTER_NUM, &conf);
    i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
}


static esp_err_t mpu9250_write_byte(uint8_t reg, uint8_t data) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, MPU9250_ADDR << 1 | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_write_byte(cmd, data, true);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, pdMS_TO_TICKS(1000));
    i2c_cmd_link_delete(cmd);
    return ret;
}


static int16_t mpu9250_read_word(uint8_t reg) {
    uint8_t data[2];
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, MPU9250_ADDR << 1 | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, MPU9250_ADDR << 1 | I2C_MASTER_READ, true);
    i2c_master_read(cmd, data, 2, I2C_MASTER_LAST_NACK);
    i2c_master_stop(cmd);
    i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, pdMS_TO_TICKS(1000));
    i2c_cmd_link_delete(cmd);
    return (int16_t)((data[0] << 8) | data[1]);
}


void mpu9250_init(void) {
    esp_err_t ret = mpu9250_write_byte(0x6B, 0x00);  // Wake up device
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to wake up MPU9250");
    }
}


void mpu9250_read_all(mpu9250_data_t *data) {
    data->accel_x = mpu9250_read_word(0x3B);
    data->accel_y = mpu9250_read_word(0x3D);
    data->accel_z = mpu9250_read_word(0x3F);
    data->gyro_x  = mpu9250_read_word(0x43);
    data->gyro_y  = mpu9250_read_word(0x45);
    data->gyro_z  = mpu9250_read_word(0x47);
}
