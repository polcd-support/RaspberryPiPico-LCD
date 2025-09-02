# -*- coding: utf-8 -*-
import time
from machine import Pin, SPI
from lcd_def import *
import struct

class LCD:
    def __init__(self, spi, csp=5, dcp=1, rstp=0, backlightp=6, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, rotation=0):
        """
        初始化显示屏驱动类实例，配置硬件引脚和初始参数。
        """
        self.spi = spi  # 保存SPI总线对象，用于后续数据传输
        # 初始化片选引脚（CS）：输出模式，初始高电平（未选中）
        self.cs = Pin(csp, Pin.OUT, value=1)
        # 初始化数据/命令引脚（DC）：输出模式，初始低电平（默认传输命令）
        self.dc = Pin(dcp, Pin.OUT, value=0)
        # 初始化复位引脚（RST）：输出模式，初始高电平（未复位状态）
        self.rst = Pin(rstp, Pin.OUT, value=1)
        # 初始化背光引脚：输出模式，初始高电平（背光开启）
        self.backlight = Pin(backlightp, Pin.OUT, value=1)
        self.width = width        # 保存显示屏宽度
        self.height = height      # 保存显示屏高度
        self.rotation = rotation  # 保存初始旋转方向
        self.init()  # 调用初始化方法，执行硬件启动序列

    def hard_reset(self):
        """
        对显示屏执行执行硬件复位操作。
        """
        self.rst(0)  # 拉低复位引脚，触发硬件复位
        time.sleep_ms(100)  # 保持复位状态100毫秒
        self.rst(1)  # 拉高复位引脚，结束复位
        time.sleep_ms(100)  # 延迟100毫秒，等待显示屏稳定

    def LCD_WR_REG(self,dat):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([dat]))
        self.cs(1)
        self.dc(1)
    
    def LCD_WR_DATA8(self,dat):
        self.cs(0)
        self.spi.write(bytearray([dat]))
        self.cs(1)
    
    def LCD_Address_Set(self,x1, y1, x2, y2):
        if self.rotation == 0:
            self.LCD_WR_REG(0x2a) #列地址设置
            self.LCD_WR_DATA8(x1>>8 )
            self.LCD_WR_DATA8(x1& 0xFF )
            self.LCD_WR_DATA8(x2>>8 )
            self.LCD_WR_DATA8(x2& 0xFF )
            self.LCD_WR_REG(0x2b) #行地址设置
            self.LCD_WR_DATA8((y1+20)>>8)
            self.LCD_WR_DATA8((y1+20)& 0xFF)
            self.LCD_WR_DATA8((y2+20)>>8)
            self.LCD_WR_DATA8((y2+20)& 0xFF)
            self.LCD_WR_REG(0x2c) #储存器写
        elif self.rotation == 1:
            self.LCD_WR_REG(0x2a) #列地址设置
            self.LCD_WR_DATA8(x1>>8 )
            self.LCD_WR_DATA8(x1& 0xFF )
            self.LCD_WR_DATA8(x2>>8 )
            self.LCD_WR_DATA8(x2& 0xFF )
            self.LCD_WR_REG(0x2b) #行地址设置
            self.LCD_WR_DATA8((y1+80)>>8)
            self.LCD_WR_DATA8((y1+80)& 0xFF)
            self.LCD_WR_DATA8((y2+80)>>8)
            self.LCD_WR_DATA8((y2+80)& 0xFF)
            self.LCD_WR_REG(0x2c) #储存器写
        elif self.rotation == 2:
            self.LCD_WR_REG(0x2a) #列地址设置
            self.LCD_WR_DATA8(x1>>8 )
            self.LCD_WR_DATA8(x1& 0xFF )
            self.LCD_WR_DATA8(x2>>8 )
            self.LCD_WR_DATA8(x2& 0xFF )
            self.LCD_WR_REG(0x2b) #行地址设置
            self.LCD_WR_DATA8(y1>>8)
            self.LCD_WR_DATA8(y1& 0xFF)
            self.LCD_WR_DATA8(y2>>8)
            self.LCD_WR_DATA8(y2& 0xFF)
            self.LCD_WR_REG(0x2c) #储存器写            
        else:
            self.LCD_WR_REG(0x2a) #列地址设置
            self.LCD_WR_DATA8((x1+80)>>8 )
            self.LCD_WR_DATA8((x1+80)& 0xFF )
            self.LCD_WR_DATA8((x2+80)>>8 )
            self.LCD_WR_DATA8((x2+80)& 0xFF )
            self.LCD_WR_REG(0x2b) #行地址设置
            self.LCD_WR_DATA8(y1>>8)
            self.LCD_WR_DATA8(y1& 0xFF)
            self.LCD_WR_DATA8(y2>>8)
            self.LCD_WR_DATA8(y2& 0xFF)
            self.LCD_WR_REG(0x2c) #储存器写            
            
            
    def init(self):
        self.hard_reset()
        self.LCD_WR_REG(0x11)  # Sleep out 指令：唤醒屏幕
        time.sleep_ms(120)      # 等待 120ms，确保屏幕稳定唤醒

        # 2. 设置内存访问方向（默认竖屏，可根据需求调整 0x36 指令参数）
        self.LCD_WR_REG(0x36)   # Memory Access Control 指令
        if self.rotation == 0:
            self.LCD_WR_DATA8(0x00) # 方向配置
        elif self.rotation == 1:
            self.LCD_WR_DATA8(0xC0) # 方向配置
        elif self.rotation == 2:
            self.LCD_WR_DATA8(0x70) # 方向配置
        else:
            self.LCD_WR_DATA8(0xA0) # 方向配置

        # 3. 设置像素格式（RGB565）
        self.LCD_WR_REG(0x3A)   # Pixel Format Set 指令
        self.LCD_WR_DATA8(0x05) # 0x05 表示 16 位像素格式（RGB565）

        # 4. 设置 porch 控制（垂直前/后肩、水平前/后肩）
        self.LCD_WR_REG(0xB2)   # Porch Control 指令
        self.LCD_WR_DATA8(0x0C) # 垂直前肩配置
        self.LCD_WR_DATA8(0x0C) # 垂直后肩配置
        self.LCD_WR_DATA8(0x00) # 水平前肩配置
        self.LCD_WR_DATA8(0x33) # 水平后肩配置（高字节）
        self.LCD_WR_DATA8(0x33) # 水平后肩配置（低字节）

        # 5. 设置 GPIO 配置
        self.LCD_WR_REG(0xB7)   # GPIO Control 指令
        self.LCD_WR_DATA8(0x35) # GPIO 输出电平配置（具体值需参考屏幕手册）

        # 6. 设置 VCOM 电压（1.35V）
        self.LCD_WR_REG(0xBB)   # VCOM Setting 指令
        self.LCD_WR_DATA8(0x32) # VCOM 电压值：0x32 对应 1.35V

        # 7. 设置电源控制 2（增强驱动能力）
        self.LCD_WR_REG(0xC2)   # Power Control 2 指令
        self.LCD_WR_DATA8(0x01) # 电源增强模式配置

        # 8. 设置 GVDD 电压（4.8V，影响颜色深度）
        self.LCD_WR_REG(0xC3)   # Power Control 3 指令
        self.LCD_WR_DATA8(0x15) # GVDD 电压值：0x15 对应 4.8V

        # 9. 设置 VDV 电压（0V，动态电压调整）
        self.LCD_WR_REG(0xC4)   # Power Control 4 指令
        self.LCD_WR_DATA8(0x20) # VDV 电压值：0x20 对应 0V

        # 10. 设置显示帧率（60Hz）
        self.LCD_WR_REG(0xC6)   # VCOM Offset Control 指令
        self.LCD_WR_DATA8(0x0F) # 帧率配置：0x0F 对应 60Hz

        # 11. 设置电源模式配置
        self.LCD_WR_REG(0xD0)   # Power Control 1 指令
        self.LCD_WR_DATA8(0xA4) # 主电源模式
        self.LCD_WR_DATA8(0xA1) # 辅助电源模式

        # 12. 设置正 gamma 校正（影响亮度/色彩曲线）
        self.LCD_WR_REG(0xE0)   # Positive Gamma Correction 指令
        self.LCD_WR_DATA8(0xD0) # Gamma 参数 1
        self.LCD_WR_DATA8(0x08) # Gamma 参数 2
        self.LCD_WR_DATA8(0x0E) # Gamma 参数 3
        self.LCD_WR_DATA8(0x09) # Gamma 参数 4
        self.LCD_WR_DATA8(0x09) # Gamma 参数 5
        self.LCD_WR_DATA8(0x05) # Gamma 参数 6
        self.LCD_WR_DATA8(0x31) # Gamma 参数 7
        self.LCD_WR_DATA8(0x33) # Gamma 参数 8
        self.LCD_WR_DATA8(0x48) # Gamma 参数 9
        self.LCD_WR_DATA8(0x17) # Gamma 参数 10
        self.LCD_WR_DATA8(0x14) # Gamma 参数 11
        self.LCD_WR_DATA8(0x15) # Gamma 参数 12
        self.LCD_WR_DATA8(0x31) # Gamma 参数 13
        self.LCD_WR_DATA8(0x34) # Gamma 参数 14

        # 13. 设置负 gamma 校正（与正 gamma 配合优化色彩）
        self.LCD_WR_REG(0xE1)   # Negative Gamma Correction 指令
        self.LCD_WR_DATA8(0xD0) # Gamma 参数 1
        self.LCD_WR_DATA8(0x08) # Gamma 参数 2
        self.LCD_WR_DATA8(0x0E) # Gamma 参数 3
        self.LCD_WR_DATA8(0x09) # Gamma 参数 4
        self.LCD_WR_DATA8(0x09) # Gamma 参数 5
        self.LCD_WR_DATA8(0x15) # Gamma 参数 6
        self.LCD_WR_DATA8(0x31) # Gamma 参数 7
        self.LCD_WR_DATA8(0x33) # Gamma 参数 8
        self.LCD_WR_DATA8(0x48) # Gamma 参数 9
        self.LCD_WR_DATA8(0x17) # Gamma 参数 10
        self.LCD_WR_DATA8(0x14) # Gamma 参数 11
        self.LCD_WR_DATA8(0x15) # Gamma 参数 12
        self.LCD_WR_DATA8(0x31) # Gamma 参数 13
        self.LCD_WR_DATA8(0x34) # Gamma 参数 14

        # 14. 设置显示反转（可选，根据屏幕极性调整）
        self.LCD_WR_REG(0x21)   # Display Inversion Control 指令（0x21 开启反转，0x20 关闭）

        # 15. 开启显示（核心指令，最后执行）
        self.LCD_WR_REG(0x29)   # Display On 指令：激活屏幕显示
     
    def fill_color_buffer(self, color: int, length: int):
        """
        向显示屏缓冲区缓冲区填充指定颜色的像素数据。）
        """
        #buffer_pixel_size = 512  # 每个缓冲区包含256个像素
        # 计算完整块（512字节）数量和剩余字节数
        chunks, rest = divmod(length, MAX_BUFFER_SIZE * 2)
        
        # 将16位颜色值转换为大端序2字节数据
        pixel = struct.pack('>H', color)
        # 生成256像素的缓冲区（256 * 2 = 512字节）
        buffer = pixel * MAX_BUFFER_SIZE  # 结果为字节数组
        
        # 传输所有完整块
        if chunks:
            for count in range(chunks):
                self.spi.write(buffer)
        
        # 传输剩余字节（不足512字节的部分）
        if rest:
            # 按剩余字节数生成数据（每个像素2字节，故需重复rest#2次）
            self.spi.write(pixel * (rest // 2))
     
    def lcd_Fill(self,xsta, ysta, xend, yend, color):
        self.LCD_Address_Set(xsta, ysta, xend, yend) # 设置显示范围
        # 准备颜色数据 (高位在前)
        width = xend-xsta+1
        height = yend-ysta+1
        
        self.cs(0)
        self.dc(1)
        self.fill_color_buffer(color,width*height*2)
        
        self.cs(1)
        
    def LCD_DrawPoint(self,x,y,color):
    
        self.LCD_Address_Set(x,y,x,y) #设置光标位置 
        pixel = struct.pack('>H', color)
        self.cs(0)  # 拉低片选信号，选中显示屏
        self.dc(1)  # 拉高DC信号，标识传输数据
        self.spi.write(pixel)  # 发送像素颜色数据
        self.cs(1)  # 拉高片选信号，结束传输
            
    def LCD_DrawLine(self,x1, y1, x2, y2, color):
        """
        使用Bresenham算法绘制直线
        """
        # 初始化算法参数，与原C代码逻辑完全对齐
        xerr = 0
        yerr = 0
        delta_x = x2 - x1  # 计算X轴坐标增量
        delta_y = y2 - y1  # 计算Y轴坐标增量
        uRow = x1          # 当前绘制点X坐标（初始为起点X）
        uCol = y1          # 当前绘制点Y坐标（初始为起点Y）
        
        # 设置X轴单步方向（1：递增，0：水平不变，-1：递减）
        if delta_x > 0:
            incx = 1
        elif delta_x == 0:
            incx = 0  # 垂直线（X轴无变化）
        else:
            incx = -1
            delta_x = -delta_x  # 取绝对值，简化后续计算
        
        # 设置Y轴单步方向（1：递增，0：垂直不变，-1：递减）
        if delta_y > 0:
            incy = 1
        elif delta_y == 0:
            incy = 0  # 水平线（Y轴无变化）
        else:
            incy = -1
            delta_y = -delta_y  # 取绝对值，简化后续计算
        
        # 选取主增量轴（增量绝对值更大的轴作为基准，确保线条无断点）
        if delta_x > delta_y:
            distance = delta_x
        else:
            distance = delta_y
        
        # 核心循环：沿主增量轴步进，计算并绘制每个点
        for _ in range(distance + 1):
            # 绘制当前点（需确保 LCD_DrawPoint 函数已实现且参数匹配）
            self.LCD_DrawPoint(uRow, uCol, color)
            
            # 累积X、Y轴误差
            xerr += delta_x
            yerr += delta_y
            
            # X轴误差超限：调整X坐标，重置误差
            if xerr > distance:
                xerr -= distance
                uRow += incx
            
            # Y轴误差超限：调整Y坐标，重置误差
            if yerr > distance:
                yerr -= distance
                uCol += incy       

    def gui_draw_hline(self, x0, y0, length, color):
        if length==0:
            return
        self.LCD_DrawLine(x0,y0,x0+length-1,y0,color)
        
    def gui_draw_hline_batch(self, x0, y0, length, color):
        """批量绘制水平线（核心优化：合并SPI传输）"""
        if length <= 0:
            return
        # 1. 边界校验：确保绘制区域在屏幕内
        x_start = max(x0, 0)
        x_end = min(x0 + length - 1, self.width - 1)
        if x_start > x_end:
            return  # 无效区域直接返回
        
        # 2. 设置显示窗口：仅需一次窗口配置（避免逐点重复设置）
        self.LCD_Address_Set(x_start, y0, x_end, y0)
        
        # 3. 生成批量颜色数据（RGB565格式，每个像素2字节）
        pixel_count = x_end - x_start + 1
        # 预计算颜色的高低字节（避免循环内重复移位）
        color_hi = (color >> 8) & 0xFF
        color_lo = color & 0xFF
        
        # 4. 批量生成数据：用bytearray预分配内存（比循环append快3倍）
        batch_data = bytearray(pixel_count * 2)
        for i in range(pixel_count):
            batch_data[i*2] = color_hi
            batch_data[i*2 + 1] = color_lo
        
        # 5. 单次SPI传输：减少cs切换和函数调用开销
        self.cs(0)
        self.dc(1)
        self.spi.write(batch_data)
        self.cs(1)
        
    def gui_fill_circle(self, x0, y0, r, color):
        
        if r <= 0:
            return
        # 1. 预计算圆半径的平方（避免循环内重复计算平方）
        r_sq = r * r
        
        # 2. 垂直方向扫描范围：y从y0-r到y0+r（减少冗余循环）
        y_min = max(y0 - r, 0)
        y_max = min(y0 + r, self.height - 1)
        
        
        for y in range(y_min, y_max + 1):
            dy = y-y0
            dy_sq = dy * dy
            if dy_sq > r_sq:
                continue  # 超出圆范围，跳过当前y
            # 整数平方根优化
            x_half = int((r_sq - dy_sq) ** 0.5)  # 简化为整数
            # 计算当前y的水平绘制范围
            x_start = x0 - x_half
            length = 2 * x_half + 1  # 水平像素个数
            self.gui_draw_hline_batch(x_start, y, length, color)

    # 画宽线
    def LCD_DrawThickLine(self, x1, y1, x2, y2, color, size):
        if size == 1:
            self.LCD_DrawLine(x1, y1, x2, y2, color)
            return
    
        # 快速边界检查
        if x1 < size or x2 < size or y1 < size or y2 < size:
            return
    
        dx = x2 - x1
        dy = y2 - y1
    
        # 快速距离检查（近似）
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        if abs_dx > MAX_ALLOWED_DISTANCE or abs_dy > MAX_ALLOWED_DISTANCE:
            return
        
        xerr = 0
        yerr = 0
        delta_x = dx  # 坐标增量（X轴）
        delta_y = dy  # 坐标增量（Y轴）
        uRow = x1     # 当前绘制点X坐标（初始为起点X）
        uCol = y1     # 当前绘制点Y坐标（初始为起点Y）
        
        incx = 1 if delta_x > 0 else (-1 if delta_x < 0 else 0)
        incy = 1 if delta_y > 0 else (-1 if delta_y < 0 else 0)
        delta_x = abs(delta_x)
        delta_y = abs(delta_y)
        
        distance = delta_x if delta_x > delta_y else delta_y
        
        # 核心绘制循环：沿主增量轴步进，每个点绘制填充圆形成粗线
        for _ in range(distance + 2):  # 循环次数+2，确保终点完全覆盖（与原C代码t<=distance+1一致）
            # 在当前坐标绘制填充圆，形成粗线的"点"
            self.gui_fill_circle(uRow, uCol, size, color)
            
            # 累积X、Y轴误差
            xerr += delta_x
            yerr += delta_y
            
            # X轴误差超限：调整X坐标，重置误差
            if xerr > distance:
                xerr -= distance
                uRow += incx
            
            # Y轴误差超限：调整Y坐标，重置误差
            if yerr > distance:
                yerr -= distance
                uCol += incy
            
    def DrawThickLine(self,x0,y0,x1,y1,thickness,color):
        if x0<0:
            x0=0
        if y0<0:
            y0=0
        if x1<0:
            x1=0
        if y1<0:
            y1=0        
        
        if x0>=self.width:
            x0=self.width-1
        if y0>=self.height:
            y0=self.height-1
        if x1>=self.width:
            x1=self.width-1
        if y1>=self.height:
            y1=self.height-1
            
        # 初始化Bresenham算法参数（简化版，适配粗线绘制）
        dx = abs(x1 - x0)                # X轴距离（绝对值）
        sx = 1 if x0 < x1 else -1        # X轴步进方向（1：递增，-1：递减）
        dy = -abs(y1 - y0)              # Y轴距离（绝对值取负，用于误差计算）
        sy = 1 if y0 < y1 else -1        # Y轴步进方向（1：递增，-1：递减）
        err = dx + dy                   # 初始误差值
        e2 = 0                          # 误差两倍缓存（避免重复计算）            
        
        # 无限循环：直到绘制到终点才退出
        while True:
            # 绘制当前点的"粗点"：以(x0,y0)为中心，绘制thickness厚度的方块
            for i in range(-thickness, thickness + 1):
                for j in range(-thickness, thickness + 1):
                    # 计算当前方块点的坐标
                    current_x = x0 + i
                    current_y = y0 + j
                    # 确保方块点在屏幕范围内，避免越界绘制
                    if 0 <= current_x < SCREEN_WIDTH and 0 <= current_y < SCREEN_HEIGHT:
                        self.LCD_DrawPoint(current_x, current_y, color)
            
            # 检查是否到达终点：到达则退出循环
            if x0 == x1 and y0 == y1:
                break
            
            # 误差更新：Bresenham算法核心，调整下一个绘制点坐标
            e2 = 2 * err
            # X轴方向需要步进：更新误差和X坐标
            if e2 >= dy:
                err += dy
                x0 += sx
            # Y轴方向需要步进：更新误差和Y坐标
            if e2 <= dx:
                err += dx
                y0 += sy        
        
    def LCD_DrawRectangle(self,x1, y1, x2, y2, color):
        self.LCD_DrawLine(x1,y1,x2,y1,color)
        self.LCD_DrawLine(x1,y1,x1,y2,color)
        self.LCD_DrawLine(x1,y2,x2,y2,color)
        self.LCD_DrawLine(x2,y1,x2,y2,color)
    
    
    def Draw_Circle(self, x0, y0, r, color):
        a=0
        b=r
        while a<=b:
            self.LCD_DrawPoint(x0-b,y0-a,color);             #3           
            self.LCD_DrawPoint(x0+b,y0-a,color);             #0           
            self.LCD_DrawPoint(x0-a,y0+b,color);             #1                
            self.LCD_DrawPoint(x0-a,y0-b,color);             #2             
            self.LCD_DrawPoint(x0+b,y0+a,color);             #4               
            self.LCD_DrawPoint(x0+a,y0-b,color);             #5
            self.LCD_DrawPoint(x0+a,y0+b,color);             #6 
            self.LCD_DrawPoint(x0-b,y0+a,color);             #7
            a=a+1
            if a*a+b*b>r*r:
                b=b-1
    
    def blit_buffer(self, buffer: bytearray, x: int, y: int, width: int, height: int):
        """
        将缓冲区数据块复制到显示屏的指定区域。
        
        参数:
            buffer (bytearray): 待绘制的像素数据缓冲区（需为RGB565格式的字节序列）
            x (int): 目标区域左上角的X坐标
            y (int): 目标区域左上角的Y坐标
            width (int): 目标区域的宽度（像素）
            height (int): 目标区域的高度（像素）
        """
        # 校验目标区域是否在显示屏有效范围内
        if (not 0 <= x < self.width or
            not 0 <= y < self.height or
            not 0 < x + width <= self.width or
            not 0 < y + height <= self.height):
                raise ValueError("目标区域超出显示屏范围")
        
        # 设置与目标区域对应的操作窗口（转换为[Xstart, Ystart, Xend, Yend]）
        self.LCD_Address_Set(x, y, x + width - 1, y + height - 1)
        
        self.cs(0)  # 拉低片选信号，选中显示屏
        self.dc(1)  # 拉高DC信号，标识传输数据
        
        buffer_size = 512  # 每次SPI传输的最大字节数（分块大小）
        # 计算有效数据长度（不超过缓冲区大小，且不超过区域所需的总像素字节数）
        limit = min(len(buffer), width * height * 2)
        # 计算完整块数量和剩余字节数
        chunks, rest = divmod(limit, buffer_size)
        
        # 传输所有完整的数据块
        if chunks:
            for i in range(chunks):
                self.spi.write(buffer[i*buffer_size: (i+1)*buffer_size])
        
        # 传输剩余不足一块的数据
        if rest:
            self.spi.write(buffer[chunks*buffer_size: chunks*buffer_size + rest])
        
        self.cs(1)  # 拉高片选信号，结束传输
    
    
    def map_bitarray_to_rgb565(self, bitarray, buffer, width, color, bg_color):
        """
        将位数组（bitarray）转换为RGB565格式的颜色缓冲区，适用于后续的blit绘制操作。

        参数:
            bitarray: 输入的位数据数组，每个字节包含8个像素的位信息（1字节=8像素）
            buffer: 输出的RGB565格式缓冲区（字节数组），用于存储转换后的像素数据
            width: 每行的像素宽度，超过该宽度时自动换行
            color (int): 位值为1时的像素颜色（RGB565格式）
            bg_color (int): 位值为0时的像素颜色（RGB565格式）
        """
        row_pos = 0  # 跟踪当前行的像素位置，用于控制换行
        length = len(bitarray)  # 位数组的总字节数
        id = 0  # 输出缓冲区的索引，用于定位当前写入位置

        # 遍历位数组中的每个字节
        for i in range(length):
            byte = bitarray[i]  # 获取当前字节（包含8个像素的位信息）
            
            # 按从高位到低位（bit7到bit0）的顺序处理每个位
            for bi in range(0, 8, 1):
                # 提取当前位的值（1或0）
                b = byte & (1 << bi)
                
                # 根据位值选择对应的颜色
                cur_color = color if b else bg_color
                
                # 将RGB565颜色拆分为高8位和低8位，存入缓冲区
                buffer[id] = (cur_color & 0xFF00) >> 8  # 高8位
                id += 1
                buffer[id] = cur_color & 0xFF          # 低8位
                id += 1
                
                # 更新当前行的像素位置
                row_pos += 1
                
                # 若当前行像素数达到指定宽度，换行（重置行位置并跳出当前字节的循环）
                if row_pos >= width:
                    row_pos = 0
                    break
    
    
    def show_text(self, x: int, y: int, num: str, fc:int,bc:int,sizey:int):
        """
        在LCD上显示单个ASCII字符
        
        参数:
            x (int): 显示起始X坐标
            y (int): 显示起始Y坐标
            num (str): 要显示的字符串
            fc (int): 字符颜色（RGB565格式）
            bc (int): 背景颜色（RGB565格式）
            sizey (int): 字符高度（支持12、16、24、32）
        """


        blitable = []

        for sprite_bitmap in num:
            if ord(sprite_bitmap)<128:
                # 计算字符宽度（宽=高/2）
                sizex = sizey // 2
            else:
                sizex = sizey

            # 计算单个字符所占字节数：(宽度/8向上取整) * 高度
            typeface_num = (sizex // 8 + (1 if sizex % 8 else 0)) * sizey
            # 根据字号选择对应的字库
            if sizey == 12:
                temp = ascii_1206[sprite_bitmap]  # 6x12字体库
            elif sizey == 16:
                temp = ascii_1608[sprite_bitmap]  # 8x16字体库
            elif sizey == 24:
                temp = ascii_2412[sprite_bitmap]  # 12x24字体库
            elif sizey == 32:
                temp = ascii_3216[sprite_bitmap]  # 16x32字体库
            else:
                return  # 不支持的字号

            sprite = bytearray(typeface_num*8*2) #存储字符颜色

            self.map_bitarray_to_rgb565(temp,sprite,sizex,fc,bc)
            blitable.append(sprite)
            
        for i in range(0, len(blitable)):
            self.blit_buffer(blitable[i], x+sizex*i, y, sizex, sizey)
            
    
    def LCD_ShowPicture(self, filename, x: int, y: int, chunk_size=MAX_BUFFER_SIZE):    
        chunk_size = chunk_size  * 3
        
        with open(filename, 'rb') as f:
            header = f.read(54)
            
            if len(header) != 54 or header[0:2] != b'BM':
                raise ValueError("不是有效的BMP文件")
    
            data_offset = struct.unpack('<I', header[10:14])[0]  # 像素数据起始偏移量（跳过文件头）
            width = struct.unpack('<I', header[18:22])[0]        # 图片宽度（像素）
            height = struct.unpack('<I', header[22:26])[0]       # 图片高度（像素，负值表示"上下颠倒存储"）
            bpp = struct.unpack('<H', header[28:30])[0]          # 色深（每像素位数）
    
            #判断图像位深是否为24位
            if bpp != 24:
                raise ValueError("仅支持24位色深的BMP文件")
            
    
            # 计算每行像素占用的字节数(24位BMP)
            row_size = (width * 3 + 3) & ~3  # 4字节对齐
            # 校验目标区域是否在显示屏有效范围内
            if (not 0 <= x < self.width or
                not 0 <= y < self.height or
                not 0 < x + width <= self.width or
                not 0 < y + height <= self.height):
                    raise ValueError("目标区域超出显示屏范围")
    
    
            self.LCD_Address_Set(x, y, x + width - 1, y + height - 1)
            # 移动到像素数据起始位置
            f.seek(data_offset)
    
                # 计算总像素数据大小
            total_data_size = abs(height) * row_size
            self.cs(0)  # 拉低片选信号，选中显示屏
            self.dc(1)  # 拉高DC信号，标识传输数据
            # 分块读取并转换
            bytes_read = 0
            
            while bytes_read < total_data_size:
                # 计算当前块的实际大小
                current_read  = min(chunk_size, total_data_size - bytes_read)
                # 读取一块数据
                chunk = f.read(current_read )     
                # 处理当前块中的像素
                rgb565_chunk = bytearray(len(chunk)//3*2)
                id=0
                for i in range(0,len(chunk),3):

                    blue = chunk[i]
                    green = chunk[i+1]
                    red = chunk[i+2]
                    # 转换为RGB565
                    # R: 8位 -> 5位 (取高5位)
                    r5 = (red >> 3) & 0x1F
                    # G: 8位 -> 6位 (取高6位)
                    g6 = (green >> 2) & 0x3F
                    # B: 8位 -> 5位 (取高5位)
                    b5 = (blue >> 3) & 0x1F
                    rgb565 = (r5 << 11) | (g6 << 5) | b5
                    rgb565_chunk[id]=(rgb565 & 0xFF00) >> 8
                    id += 1
                    rgb565_chunk[id]=(rgb565 & 0xFF)
                    id += 1

                self.spi.write(rgb565_chunk)
                bytes_read += current_read

            self.cs(1)  # 拉高片选信号，结束传输   
    
    
    
    def DrawColorBars(self):
        colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA]
        for i in range(len(colors)):
            self.lcd_Fill(i*40, 0, ((i+1)*40)-1, self.height-1, colors[i])
    
    
    def DrawGrayscale(self):
        GRAY_LEVELS = 24  # 灰度级数
        
        level_width = self.width // GRAY_LEVELS  # GRAY_LEVELS
        remainder = self.width % GRAY_LEVELS  # 余数分配给最后一级灰度
    
        for n in range(GRAY_LEVELS):
            # 计算当前灰度级的X坐标范围
            start_x = n * level_width
            end_x = start_x + level_width - 1

            # 最后一级灰度包含余数，确保覆盖整个屏幕宽度
            if n == GRAY_LEVELS - 1:
                end_x += remainder

            # 计算当前灰度值（0~255）：将0~23映射到0~255
            gray = (n * 255) // (GRAY_LEVELS - 1)

            # 生成RGB565格式的灰度颜色（R=G=B，确保无偏色）
            # R5: 8位gray取高5位，G6: 取高6位，B5: 取高5位
            color = ((gray & 0xF8) << 8)|((gray & 0xFC) << 3)|(gray>>3)

            # 填充当前灰度级的矩形区域（全屏高度）
            self.lcd_Fill(
                start_x,       # 起始X
                0,             # 起始Y（屏幕顶部）
                end_x,         # 结束X
                self.height - 1,  # 结束Y（屏幕底部）
                color          # 灰度颜色
            )   
    
    def DrawClearButton(self):
        self.lcd_Fill(self.width-BTN_WIDTH, self.height-BTN_HEIGHT, 
            self.width, self.height, GRAY)
        self.show_text(self.width-BTN_WIDTH+5, self.height-BTN_HEIGHT+8, 
                  "Clear", BLACK, GRAY, 16)
    
    def LCD_FillCircle(self, x0: int, y0: int, r: int, color: int):
        """
        使用Bresenham算法绘制填充圆
        """
        if r == 0:
            return  # 半径为0时无需绘制

        x = r
        y = 0
        err = 0

        while x >= y:
            # 填充4个对称的水平线段（覆盖圆的8个对称方向）
            # 1. 上半圆右侧
            self.lcd_Fill(x0 - x, y0 + y, x0 + x, y0 + y, color)
            # 2. 上半圆左侧
            self.lcd_Fill(x0 - y, y0 + x, x0 + y, y0 + x, color)
            # 3. 下半圆右侧
            self.lcd_Fill(x0 - x, y0 - y, x0 + x, y0 - y, color)
            # 4. 下半圆左侧
            self.lcd_Fill(x0 - y, y0 - x, x0 + y, y0 - x, color)
            
            # 更新Bresenham算法误差值和坐标
            if err <= 0:
                y += 1
                err += 2 * y + 1  # 误差累加（Y方向步进）
            if err > 0:
                x -= 1
                err -= 2 * x + 1  # 误差调整（X方向步进）   
    
    
    
    
    
    
    
    
    
    
    
    
    