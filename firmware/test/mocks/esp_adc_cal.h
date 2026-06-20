// Minimal esp_adc_cal mock (host syntax check only).
#pragma once
#include <cstdint>
#include "driver/adc.h"

typedef enum {
    ESP_ADC_CAL_VAL_EFUSE_VREF = 0,
    ESP_ADC_CAL_VAL_EFUSE_TP   = 1,
    ESP_ADC_CAL_VAL_DEFAULT_VREF = 2
} esp_adc_cal_value_t;

typedef struct {
    uint32_t vref;
    uint32_t coeff_a;
    uint32_t coeff_b;
} esp_adc_cal_characteristics_t;

esp_adc_cal_value_t esp_adc_cal_characterize(adc_unit_t unit, adc_atten_t atten,
                                             adc_bits_width_t bit_width,
                                             uint32_t default_vref,
                                             esp_adc_cal_characteristics_t* chars);
uint32_t esp_adc_cal_raw_to_voltage(uint32_t adc_reading,
                                    const esp_adc_cal_characteristics_t* chars);
