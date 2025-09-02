#include <SPI.h>

#define LCD_MISO_PIN -1
#define LCD_SCK_PIN  2
#define LCD_MOSI_PIN 3
#define LCD_RES_PIN 0
#define LCD_DC_PIN 1
#define LCD_CS_PIN 5
#define LCD_BLK_PIN 6

#define LCD_RES_Clr()  digitalWrite(LCD_RES_PIN, LOW)  // 拉低RES引脚
#define LCD_RES_Set()  digitalWrite(LCD_RES_PIN, HIGH) // 拉高RES引脚

// 数据/命令引脚操作
#define LCD_DC_Clr()   digitalWrite(LCD_DC_PIN, LOW)   // 拉低DC引脚（通常表示命令模式）
#define LCD_DC_Set()   digitalWrite(LCD_DC_PIN, HIGH)  // 拉高DC引脚（通常表示数据模式）

// 背光引脚操作
#define LCD_BLK_Clr()  digitalWrite(LCD_BLK_PIN, LOW)  // 拉低BLK引脚（关闭背光）
#define LCD_BLK_Set()  digitalWrite(LCD_BLK_PIN, HIGH) // 拉高BLK引脚（打开背光）

// // 片选引脚操作（选中/取消LCD）
#define LCD_CS_Clr()   digitalWrite(LCD_CS_PIN, LOW)   // 拉低CS引脚（选中LCD）
#define LCD_CS_Set()   digitalWrite(LCD_CS_PIN, HIGH)  // 拉高CS引脚（取消选中）


SPISettings lcdSPISettings(4000000, MSBFIRST, SPI_MODE0);

void setup() {
  // put your setup code here, to run once:
  pinMode(LCD_RES_PIN, OUTPUT);
  pinMode(LCD_DC_PIN, OUTPUT);
  pinMode(LCD_CS_PIN, OUTPUT);
  pinMode(LCD_BLK_PIN, OUTPUT);

  // 初始化默认电平（可选，根据硬件要求设置）
  LCD_RES_Set();   // 复位引脚默认高电平（未复位）
  LCD_DC_Set();    // 默认数据模式
  // LCD_CS_Set();    // 未选中LCD
  LCD_BLK_Set();   // 打开背光

	SPI.setSCK(LCD_SCK_PIN);
	SPI.setMOSI(LCD_MOSI_PIN);
	SPI.setCS(LCD_CS_PIN);
	
	SPI.begin(true);

}

void loop() {
  // put your main code here, to run repeatedly:
  SPI.beginTransaction(lcdSPISettings);
  SPI.transfer(0XAA);
  SPI.transfer(0X55);
  SPI.endTransaction();
  delay(1);
}
