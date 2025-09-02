#include "Inc/iic_hal.h"
#include "pico/stdlib.h"

#define IIC_DELAY 5

void IICInit(iic_bus_t *bus)
{
    gpio_init(bus->sda_pin);
    gpio_set_function(bus->sda_pin, GPIO_FUNC_SIO);
    gpio_set_dir(bus->sda_pin, GPIO_OUT);

    gpio_init(bus->scl_pin);
    gpio_set_function(bus->scl_pin, GPIO_FUNC_SIO);
    gpio_set_dir(bus->scl_pin, GPIO_OUT);

    gpio_put(bus->sda_pin, 1);
    gpio_put(bus->scl_pin, 1);
}

void IICStart(iic_bus_t *bus)
{
    gpio_put(bus->sda_pin, 1);
    gpio_put(bus->scl_pin, 1);
    sleep_us(IIC_DELAY);
    gpio_put(bus->sda_pin, 0);
    sleep_us(IIC_DELAY);
    gpio_put(bus->scl_pin, 0);
}

void IICStop(iic_bus_t *bus)
{
    gpio_put(bus->scl_pin, 0);
    gpio_put(bus->sda_pin, 0);
    sleep_us(IIC_DELAY);
    gpio_put(bus->scl_pin, 1);
    sleep_us(IIC_DELAY);
    gpio_put(bus->sda_pin, 1);
    sleep_us(IIC_DELAY);
}

uint8_t IICWaitAck(iic_bus_t *bus)
{
    uint16_t ucErrTime = 0XFFF;
    gpio_put(bus->scl_pin, 0);
    gpio_set_dir(bus->sda_pin, GPIO_IN);
    sleep_us(IIC_DELAY);
    gpio_put(bus->scl_pin, 1);

    while (gpio_get(bus->sda_pin))
    {
        if ((ucErrTime--) == 0)
        {
            gpio_put(bus->sda_pin, 1);
            gpio_set_dir(bus->sda_pin, GPIO_OUT);
            IICStop(bus);
            return 1;
        }
    }
    sleep_us(IIC_DELAY);
    gpio_put(bus->scl_pin, 0);
    gpio_put(bus->sda_pin, 1);
    gpio_set_dir(bus->sda_pin, GPIO_OUT);
    return 0;
}

void IICAck(iic_bus_t *bus)
{
    gpio_put(bus->scl_pin, 0);
    gpio_set_dir(bus->sda_pin, GPIO_OUT);
    gpio_put(bus->sda_pin, 0);
    sleep_us(IIC_DELAY);
    gpio_put(bus->scl_pin, 1);
    sleep_us(IIC_DELAY);
    gpio_put(bus->scl_pin, 0);
}

void IICNAck(iic_bus_t *bus)
{
    gpio_put(bus->scl_pin, 0);
    gpio_set_dir(bus->sda_pin, GPIO_OUT);
    gpio_put(bus->sda_pin, 0);
    sleep_us(IIC_DELAY);
    gpio_put(bus->sda_pin, 1);
    sleep_us(IIC_DELAY);
    gpio_put(bus->scl_pin, 1);
    sleep_us(IIC_DELAY);
    gpio_put(bus->scl_pin, 0);
}

void IICSendByte(iic_bus_t *bus, uint8_t txd)
{
    uint8_t t;

    for (t = 0; t < 8; t++)
    {
        gpio_put(bus->scl_pin, 0);
        sleep_us(IIC_DELAY);
        if (txd & 0x80)
            gpio_put(bus->sda_pin, 1);
        else
            gpio_put(bus->sda_pin, 0);
        gpio_put(bus->scl_pin, 1);
        sleep_us(IIC_DELAY);
        txd <<= 1;
    }
}

uint8_t IICRecvByte(iic_bus_t *bus)
{
    uint8_t i, receive = 0;
    gpio_set_dir(bus->sda_pin,GPIO_IN);

    for (i = 0; i < 8; i++)
    {
        receive <<= 1;
        gpio_put(bus->scl_pin, 0);
        sleep_us(IIC_DELAY);
        gpio_put(bus->scl_pin, 1);

        if (gpio_get(bus->sda_pin))
            receive|=0x01;

        sleep_us(IIC_DELAY);
    }

    return receive;
}

uint8_t IIC_Read_One_Byte(iic_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr)
{
    uint8_t res;

    IICStart(bus);
    IICSendByte(bus, dev_addr << 1);
    IICWaitAck(bus);
    IICSendByte(bus, reg_addr);
    IICWaitAck(bus);

    IICStart(bus);
    IICSendByte(bus, (dev_addr << 1) | 1);
    IICWaitAck(bus);
    res = IICRecvByte(bus);
    IICNAck(bus);
    IICStop(bus);

    return res;
}

void IIC_Write_One_Byte(iic_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, uint8_t dat)
{
    IICStart(bus);
    IICSendByte(bus, dev_addr << 1);
    IICWaitAck(bus);
    IICSendByte(bus, reg_addr);
    IICWaitAck(bus);
    IICSendByte(bus, dat);
    IICWaitAck(bus);
    IICStop(bus);
}

void IIC_Read_Multi_Byte(iic_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, uint8_t len, uint8_t *buf)
{
    IICStart(bus);
    IICSendByte(bus, dev_addr << 1);
    IICWaitAck(bus);
    IICSendByte(bus, reg_addr);
    IICWaitAck(bus);

    IICStart(bus);
    IICSendByte(bus, (dev_addr << 1) | 1);
    IICWaitAck(bus);

    while (len)
    {
        if (len == 1)
        {
            *buf = IICRecvByte(bus);
            IICNAck(bus);
        }
        else
        {
            *buf = IICRecvByte(bus);
            IICAck(bus);
        }
        buf++;
        len--;
    }

    IICStop(bus);
}
