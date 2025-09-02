#include "Inc/lcd_init.h"
#include "hardware/spi.h"

static void LCD_GPIO_Init(void)
{
	// gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
	gpio_set_function(LCD_CS_PIN, GPIO_FUNC_SPI);
	gpio_set_function(LCD_SCK_PIN, GPIO_FUNC_SPI);
	gpio_set_function(LCD_MOSI_PIN, GPIO_FUNC_SPI);

	spi_init(LCD_SPI_PORT, 4 * 1000 * 1000);
	spi_set_format(LCD_SPI_PORT, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);
	spi_set_slave(LCD_SPI_PORT, false);

	gpio_set_function(LCD_RES_PIN, GPIO_FUNC_SIO);
	gpio_set_function(LCD_DC_PIN, GPIO_FUNC_SIO);
	// gpio_set_function(LCD_CS_PIN,   GPIO_FUNC_SIO);
	gpio_set_function(LCD_BLK_PIN, GPIO_FUNC_SIO);

	gpio_set_dir(LCD_RES_PIN, GPIO_OUT);
	gpio_set_dir(LCD_DC_PIN, GPIO_OUT);
	// gpio_set_dir(LCD_CS_PIN,GPIO_OUT);
	gpio_set_dir(LCD_BLK_PIN, GPIO_OUT);

	gpio_put(LCD_RES_PIN, 1);
	gpio_put(LCD_DC_PIN, 1);
	// gpio_put(LCD_CS_PIN,1);
	gpio_put(LCD_BLK_PIN, 0);
}
/******************************************************************************
	  ����˵����LCD��������д�뺯��
	  ������ݣ�dat  Ҫд��Ĵ�������
	  ����ֵ��  ��
******************************************************************************/
static inline void LCD_Writ_Bus(uint8_t dat)
{
	spi_write_blocking(LCD_SPI_PORT, &dat, 1);
}

/******************************************************************************
	  ����˵����LCDд������
	  ������ݣ�dat д�������
	  ����ֵ��  ��
******************************************************************************/
static inline void LCD_WR_DATA8(uint8_t dat)
{
	LCD_Writ_Bus(dat);
}

/******************************************************************************
	  ����˵����LCDд������
	  ������ݣ�dat д�������
	  ����ֵ��  ��
******************************************************************************/
inline void LCD_WR_DATA(uint16_t dat)
{
	LCD_Writ_Bus((dat>>8)&0xF8);//RED
	LCD_Writ_Bus((dat>>3)&0xFC);//GREEN
	LCD_Writ_Bus(dat<<3);//BLUE
}

/******************************************************************************
	  ����˵����LCDд������
	  ������ݣ�dat д�������
	  ����ֵ��  ��
******************************************************************************/
static inline void LCD_WR_REG(uint8_t dat)
{
	LCD_DC_Clr(); // д����
	LCD_Writ_Bus(dat);
	LCD_DC_Set();
}

/******************************************************************************
	  ����˵����������ʼ�ͽ�����ַ
	  ������ݣ�x1,x2 �����е���ʼ�ͽ�����ַ
				y1,y2 �����е���ʼ�ͽ�����ַ
	  ����ֵ��  ��
******************************************************************************/
void LCD_Address_Set(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
	LCD_WR_REG(0x2a); // �е�ַ����
	LCD_WR_DATA8(x1 >> 8);
	LCD_WR_DATA8(x1);
	LCD_WR_DATA8(x2 >> 8);
	LCD_WR_DATA8(x2);
	LCD_WR_REG(0x2b); // �е�ַ����
	LCD_WR_DATA8(y1 >> 8);
	LCD_WR_DATA8(y1);
	LCD_WR_DATA8(y2 >> 8);
	LCD_WR_DATA8(y2);
	LCD_WR_REG(0x2c); // ������д
}

void LCD_Init(void)
{
	LCD_GPIO_Init(); // ��ʼ��GPIO

	LCD_RES_Clr(); // ��λ
	sleep_ms(100);
	LCD_RES_Set();
	sleep_ms(100);

	LCD_WR_REG(0xE0);
	LCD_WR_DATA8(0x00);
	LCD_WR_DATA8(0x07);
	LCD_WR_DATA8(0x0f);
	LCD_WR_DATA8(0x0D);
	LCD_WR_DATA8(0x1B);
	LCD_WR_DATA8(0x0A);
	LCD_WR_DATA8(0x3c);
	LCD_WR_DATA8(0x78);
	LCD_WR_DATA8(0x4A);
	LCD_WR_DATA8(0x07);
	LCD_WR_DATA8(0x0E);
	LCD_WR_DATA8(0x09);
	LCD_WR_DATA8(0x1B);
	LCD_WR_DATA8(0x1e);
	LCD_WR_DATA8(0x0f);

	LCD_WR_REG(0xE1);
	LCD_WR_DATA8(0x00);
	LCD_WR_DATA8(0x22);
	LCD_WR_DATA8(0x24);
	LCD_WR_DATA8(0x06);
	LCD_WR_DATA8(0x12);
	LCD_WR_DATA8(0x07);
	LCD_WR_DATA8(0x36);
	LCD_WR_DATA8(0x47);
	LCD_WR_DATA8(0x47);
	LCD_WR_DATA8(0x06);
	LCD_WR_DATA8(0x0a);
	LCD_WR_DATA8(0x07);
	LCD_WR_DATA8(0x30);
	LCD_WR_DATA8(0x37);
	LCD_WR_DATA8(0x0f);

	LCD_WR_REG(0xC0);
	LCD_WR_DATA8(0x10);
	LCD_WR_DATA8(0x10);

	LCD_WR_REG(0xC1);
	LCD_WR_DATA8(0x41);

	LCD_WR_REG(0xC5);
	LCD_WR_DATA8(0x00);
	LCD_WR_DATA8(0x22);
	LCD_WR_DATA8(0x80);

	LCD_WR_REG(0x36); // Memory Access Control
	if (USE_HORIZONTAL == 0)
		LCD_WR_DATA8(0x48);
	else if (USE_HORIZONTAL == 1)
		LCD_WR_DATA8(0x88);
	else if (USE_HORIZONTAL == 2)
		LCD_WR_DATA8(0x28);
	else
		LCD_WR_DATA8(0xE8);

	LCD_WR_REG(0x3A); // Interface Mode Control���˴�ILI9486Ϊ0X55
	LCD_WR_DATA8(0x66);

	LCD_WR_REG(0XB0); // Interface Mode Control
	LCD_WR_DATA8(0x00);
	LCD_WR_REG(0xB1); // Frame rate 70HZ
	LCD_WR_DATA8(0xB0);
	LCD_WR_DATA8(0x11);
	LCD_WR_REG(0xB4);
	LCD_WR_DATA8(0x02);
	LCD_WR_REG(0xB6); // RGB/MCU Interface Control
	LCD_WR_DATA8(0x02);
	LCD_WR_DATA8(0x02);

	LCD_WR_REG(0xB7);
	LCD_WR_DATA8(0xC6);
	LCD_WR_REG(0xE9);
	LCD_WR_DATA8(0x00);

	LCD_WR_REG(0XF7);
	LCD_WR_DATA8(0xA9);
	LCD_WR_DATA8(0x51);
	LCD_WR_DATA8(0x2C);
	LCD_WR_DATA8(0x82);

	LCD_WR_REG(0x11);
	sleep_ms(120);

	LCD_WR_REG(0x21);
	LCD_WR_REG(0x29);
}
