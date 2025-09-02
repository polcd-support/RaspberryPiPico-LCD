# -*- coding: utf-8 -*-
from lcd import LCD
from CST816 import CST816
import time
from lcd_def import *
from machine import Pin, SPI


#显示状态机
STATE_LOGO = 0
STATE_TEXT = 1
STATE_IMAGE = 2
STATE_COLOR_FULL = 3
STATE_COLOR_BAR = 4
STATE_GRAYSCALE = 5
STATE_COUNTDOWN = 6
STATE_HANDWRITING = 7


global g_state
global g_state_timer
#global  g_img_index = 0
global color_full_index
#global  g_countdown = 3

def IsTouchInButton(x, y):
    if x>=SCREEN_WIDTH-BTN_WIDTH and y >= SCREEN_HEIGHT-BTN_HEIGHT:
        return True
    else:
        return False

def lcd_demo():
    spi = SPI(id=0, baudrate=15_000_000, polarity=0, phase=0, sck=Pin(2,Pin.OUT), mosi=Pin(3,Pin.OUT), bits=8, firstbit=SPI.MSB)
    lcd = LCD(spi, rotation = USE_HORIZONTAL)
    cst816 = CST816()
    lcd.lcd_Fill(0,0,SCREEN_WIDTH,SCREEN_HEIGHT,BLACK)
    time.sleep_ms(100)
    
    g_state = STATE_LOGO
    g_state_timer = 0
    color_full_index = 0

    lastX=lastY=0
    g_state_timer = time.ticks_ms()
    while True:
        cst816.Get_XY_AXIS()
        
        if g_state == STATE_LOGO:
            lcd.LCD_ShowPicture(bmp_path,0,0)
            
            if (time.ticks_ms() - g_state_timer)>LOGO_DURATION:
                lcd.lcd_Fill(0, 0, 199,199, BLACK)
                g_state = STATE_TEXT
                g_state_timer = time.ticks_ms()
            
        elif g_state==STATE_TEXT:
            lcd.show_text(0,0,"6",GREEN,BLACK,32)
            lcd.show_text(20,50,"PICO Display",WHITE,BLACK,24)
            lcd.show_text(30,100,"Multi-Size Text",BLUE,BLACK,16)
            lcd.show_text(80,150,"浦洋液晶",RED,BLACK,32)
            
            if (time.ticks_ms() - g_state_timer)>TEXT_DURATION:
                lcd.lcd_Fill(0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, BLACK)
                g_state = STATE_COLOR_FULL
                g_state_timer = time.ticks_ms()
                
        #elif g_state==STATE_IMAGE:
            
        elif g_state==STATE_COLOR_FULL:
            if color_full_index==0:
                lcd.lcd_Fill(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, RED)
            elif color_full_index==1:
                lcd.lcd_Fill(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, GREEN)   
            elif color_full_index==2:
                lcd.lcd_Fill(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, BLUE)
            elif color_full_index==3:
                lcd.lcd_Fill(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE)
            elif color_full_index==4:
                lcd.lcd_Fill(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK)
                
            if (time.ticks_ms() - g_state_timer)>COLOR_FULL_INTERVAL:
                color_full_index=color_full_index+1
                if color_full_index > 4:
                    color_full_index=0
                    g_state = STATE_COLOR_BAR
                g_state_timer = time.ticks_ms()
        elif g_state==STATE_COLOR_BAR:
            lcd.DrawColorBars()
            
            if (time.ticks_ms() - g_state_timer)>EFFECT_DURATION:
                lcd.lcd_Fill(0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, BLACK)
                g_state = STATE_GRAYSCALE
                g_state_timer = time.ticks_ms()
                
                
        elif g_state==STATE_GRAYSCALE:
            lcd.DrawGrayscale()
            
            if (time.ticks_ms() - g_state_timer)>EFFECT_DURATION:
                lcd.lcd_Fill(0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, BLACK)
                g_state = STATE_HANDWRITING
                g_state_timer = time.ticks_ms()       
                lcd.DrawClearButton()
            
        #elif g_state==STATE_COUNTDOWN:
            
        elif g_state==STATE_HANDWRITING:
            if cst816.Get_FingerNum()>0:
                if lastX != 0xFFFF and lastY != 0xFFFF:
                    lcd.LCD_DrawThickLine(lastX, lastY, cst816.X_Pos, cst816.Y_Pos, WHITE,2)
                lastX = cst816.X_Pos
                lastY = cst816.Y_Pos
                
                if IsTouchInButton(lastX, lastY):
                    lcd.lcd_Fill(0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, BLACK)
                    lcd.DrawClearButton()
            else:
                lastX = lastY = 0xFFFF
            
            
