#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "Inc/lcd_demo.h"
#include "hardware/clocks.h"
// SPI Defines
// We are going to use SPI 0, and allocate it to the following GPIO pins
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments


int main()
{
    //stdio_init_all();
    set_sys_clock_khz(133000, true); 
    LCD_DEMO();
    while (true)
    {
        sleep_ms(1000);
    }

    return 0;
}
