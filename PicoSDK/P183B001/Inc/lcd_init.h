#ifndef __LCD_INIT_H
#define __LCD_INIT_H

#include "pico/stdlib.h"

#define USE_HORIZONTAL 0 // ���ú�������������ʾ 0��1Ϊ���� 2��3Ϊ����

#define LCD_SPI_PORT spi0
#define LCD_MISO_PIN -1
#define LCD_SCK_PIN 2
#define LCD_MOSI_PIN 3
#define LCD_RES_PIN 0
#define LCD_DC_PIN 1
#define LCD_CS_PIN 5
#define LCD_BLK_PIN 6

#if USE_HORIZONTAL == 0 || USE_HORIZONTAL == 1
#define LCD_W 240
#define LCD_H 284

#else
#define LCD_W 284
#define LCD_H 240
#endif

//-----------------LCD�˿ڶ���----------------

#define LCD_RES_Clr() gpio_put(LCD_RES_PIN, 0) // RES
#define LCD_RES_Set() gpio_put(LCD_RES_PIN, 1)

#define LCD_DC_Clr() gpio_put(LCD_DC_PIN, 0) // DC
#define LCD_DC_Set() gpio_put(LCD_DC_PIN, 1)

#define LCD_BLK_Clr() gpio_put(LCD_BLK_PIN, 0) // BLK
#define LCD_BLK_Set() gpio_put(LCD_BLK_PIN, 1)

// void LCD_GPIO_Init(void);//��ʼ��GPIO
// void LCD_Writ_Bus(uint8_t dat);//ģ��SPIʱ��
// void LCD_WR_DATA8(uint8_t dat);//д��һ���ֽ�
void LCD_WR_DATA(uint16_t dat); // д�������ֽ�
// void LCD_WR_REG(uint8_t dat);//д��һ��ָ��
void LCD_Address_Set(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2); // �������꺯��
void LCD_Init(void);                                                      // LCD��ʼ��
#endif
