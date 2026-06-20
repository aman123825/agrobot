// Minimal ESP-IDF ADC driver mock (host syntax check only).
#pragma once
#include <cstdint>

typedef enum { ADC_WIDTH_BIT_9, ADC_WIDTH_BIT_10, ADC_WIDTH_BIT_11, ADC_WIDTH_BIT_12 } adc_bits_width_t;
typedef enum { ADC_ATTEN_DB_0, ADC_ATTEN_DB_2_5, ADC_ATTEN_DB_6, ADC_ATTEN_DB_11 } adc_atten_t;
typedef enum { ADC_UNIT_1 = 1, ADC_UNIT_2 = 2 } adc_unit_t;
typedef enum {
    ADC1_CHANNEL_0, ADC1_CHANNEL_1, ADC1_CHANNEL_2, ADC1_CHANNEL_3,
    ADC1_CHANNEL_4, ADC1_CHANNEL_5, ADC1_CHANNEL_6, ADC1_CHANNEL_7
} adc1_channel_t;

int adc1_config_width(adc_bits_width_t width_bit);
int adc1_config_channel_atten(adc1_channel_t channel, adc_atten_t atten);
int adc1_get_raw(adc1_channel_t channel);
