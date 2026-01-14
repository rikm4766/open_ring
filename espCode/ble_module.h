#ifndef BLE_MODULE_H
#define BLE_MODULE_H

#include "stdint.h"


void ble_init(char *name);

void ble_send(const char *msg);

#endif
