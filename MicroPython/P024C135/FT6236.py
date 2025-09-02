# -*- coding: utf-8 -*-

from machine import SoftI2C, Pin
import time

TOUCH_RST_PIN = 13
TOUCH_INT_PIN = 9
I2C0_SDA_PIN = 11
I2C0_SCL_PIN = 10

# FT6236 设备地址与引脚定义
FT6236_ADDR = 0x38
FT6236_ADDR_FL = 0x39

# 寄存器地址定义
FT6236_REG_MODE = 0x00                  # 设备模式寄存器
FT6236_REG_TD_STATUS = 0x02             # 触摸状态寄存器
FT6236_REG_TOUCH1_XH = 0x03             # 触摸点1 X坐标高8位
FT6236_REG_TOUCH1_XL = 0x04             # 触摸点1 X坐标低8位
FT6236_REG_TOUCH1_YH = 0x05             # 触摸点1 Y坐标高8位
FT6236_REG_TOUCH1_YL = 0x06             # 触摸点1 Y坐标低8位
FT6236_REG_TOUCH1_WEIGHT = 0x07         # 触摸点1压力值
FT6236_REG_TOUCH1_MISC = 0x08           # 触摸点1附加信息
FT6236_REG_TOUCH2_XH = 0x09             # 触摸点2 X坐标高8位
FT6236_REG_TOUCH2_XL = 0x0A             # 触摸点2 X坐标低8位
FT6236_REG_TOUCH2_YH = 0x0B             # 触摸点2 Y坐标高8位
FT6236_REG_TOUCH2_YL = 0x0C             # 触摸点2 Y坐标低8位
FT6236_REG_TOUCH2_WEIGHT = 0x0D         # 触摸点2压力值
FT6236_REG_TOUCH2_MISC = 0x0E           # 触摸点2附加信息
FT6236_REG_THRESHOLD = 0x80             # 触摸阈值寄存器
FT6236_REG_FILTER_COE = 0x85            # 滤波系数寄存器
FT6236_REG_CTRL = 0x86                  # 控制寄存器
FT6236_REG_TIMEENTERMONITOR = 0x87      # 进入监控模式时间
FT6236_REG_PERIODACTIVE = 0x88          # 活跃模式报告率
FT6236_REG_PERIODMONITOR = 0x89         # 监控模式报告率
FT6236_REG_RADIAN_VALUE = 0x91          # 角度值寄存器
FT6236_REG_OFFSET_LEFT_RIGHT = 0x92     # 左右偏移量
FT6236_REG_OFFSET_UP_DOWN = 0x93        # 上下偏移量
FT6236_REG_DISTANCE_LEFT_RIGHT = 0x94   # 左右滑动距离
FT6236_REG_DISTANCE_UP_DOWN = 0x95      # 上下滑动距离
FT6236_REG_DISTANCE_ZOOM = 0x96         # 缩放距离
FT6236_REG_LIB_VERSION_H = 0xA1         # 库版本号高8位
FT6236_REG_LIB_VERSION_L = 0xA2         # 库版本号低8位
FT6236_REG_CHIP_ID = 0xA3               # 芯片ID寄存器
FT6236_REG_G_MODE = 0xA4                # 中断模式寄存器
FT6236_REG_POWER_MODE = 0xA5            # 电源模式寄存器
FT6236_REG_FIRMARE_ID = 0xA6            # 固件ID寄存器
FT6236_REG_FOCALTECH_ID = 0xA8          # 敦泰科技厂商ID
FT6236_REG_RELEASE_CODE_ID = 0xAF       # 发布版本号

FT6236_GESTURE_NO_GESTURE     = 0x00
FT6236_GESTURE_MOVE_UP        = 0x10
FT6236_GESTURE_MOVE_LEFT      = 0x14
FT6236_GESTURE_MOVE_DOWN      = 0x18
FT6236_GESTURE_MOVE_RIGHT     = 0x1C
FT6236_GESTURE_ZOOM_IN        = 0x48
FT6236_GESTURE_ZOOM_OUT       = 0x49

FT6236_TOUCH_EVENT_DOWN       = 0x00
FT6236_TOUCH_EVENT_UP         = 0x01
FT6236_TOUCH_EVENT_CONTACT    = 0x02
FT6236_TOUCH_EVENT_NONE       = 0x03

FT6236_POWER_MODE_ACTIVE      = 0x00
FT6236_POWER_MODE_MONITOR     = 0x01
FT6236_POWER_MODE_HIBERNATE   = 0x03

FT6236_INT_MODE_POLLING       = 0x00
FT6236_INT_MODE_TRIGGER       = 0x01
FT6236_INT_MODE_CONTINUOUS    = 0x02


class FT6236:
    def __init__(self, sda=I2C0_SDA_PIN, scl=I2C0_SCL_PIN, rst=TOUCH_RST_PIN):
        self.rst_pin = Pin(rst, Pin.OUT, value=1)
        self.i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl), freq=400000)
        self.TOUCH_OFFSET_X = 0
        self.TOUCH_OFFSET_Y = 0
        self.REVERSE_X = 0
        self.REVERSE_Y = 0
        self.X_Pos = 0          # X坐标
        self.Y_Pos = 0          # Y坐标
        self.Touch_Count = 0    # 触摸点数量
        self.Touch_Event = FT6236_TOUCH_EVENT_NONE  # 触摸事件
        
        self.init()
        
    def reset(self):
        """复位FT6236芯片"""
        self.rst_pin.value(0)
        time.sleep_ms(10)
        self.rst_pin.value(1)
        time.sleep_ms(100)

    def init(self):
        """初始化FT6236控制器"""
        self.reset()
        # 设置默认触摸阈值
        self.set_threshold(128)
        # 设置中断模式为触发模式
        self.set_interrupt_mode(FT6236_INT_MODE_TRIGGER)
        # 设置活跃模式报告速率为10ms
        self.set_active_rate(10)


    def get_touch_data(self):
        """获取触摸数据并更新到info结构体"""
        status = self.i2c.readfrom_mem(FT6236_ADDR,FT6236_REG_TD_STATUS,1)
        self.Touch_Count = status[0] & 0x0F

        if self.Touch_Count > 0:
            data = self.i2c.readfrom_mem(FT6236_ADDR,FT6236_REG_TOUCH1_XH,4)
            # 解析触摸事件
            self.Touch_Event = (data[0] >> 6) & 0x03
            # 解析X坐标
            self.X_Pos = ((data[0] & 0x0F) << 8) | data[1]
            # 解析Y坐标
            self.Y_Pos = ((data[2] & 0x0F) << 8) | data[3]

            # 处理X轴反转
            if self.REVERSE_X:
                self.info.X_Pos = 239 - self.X_Pos
            # 处理Y轴反转
            if self.REVERSE_Y:
                self.info.Y_Pos = 279 - self.Y_Pos

            # 应用坐标偏移
            self.X_Pos += self.TOUCH_OFFSET_X
            self.Y_Pos += self.TOUCH_OFFSET_Y

    def get_touch_count(self):
        """获取触摸点数量"""
        status = self.i2c.readfrom_mem(FT6236_ADDR,FT6236_REG_TD_STATUS,1)
        self.Touch_Count = status[0] & 0x0F # 低4位表示触摸点数量
        return self.Touch_Count
    
    def get_chip_id(self):
        """获取芯片ID"""
        return self.i2c.readfrom_mem(FT6236_ADDR,FT6236_REG_CHIP_ID,1)

    def get_lib_version(self):
        """获取库版本号"""
        h = self.i2c.readfrom_mem(FT6236_ADDR,FT6236_REG_LIB_VERSION_H,1)
        l = self.i2c.readfrom_mem(FT6236_ADDR,FT6236_REG_LIB_VERSION_L,1)
        return (h << 8) | l

    def set_threshold(self, threshold):
        data_bytearray = bytearray([threshold])
        self.i2c.writeto_mem(FT6236_ADDR,FT6236_REG_THRESHOLD, data_bytearray)

    def set_power_mode(self, mode):
        """设置电源模式"""
        data_bytearray = bytearray([mode])
        self.i2c.writeto_mem(FT6236_ADDR,FT6236_REG_POWER_MODE, data_bytearray)

    def set_interrupt_mode(self, mode):
        data_bytearray = bytearray([mode])
        self.i2c.writeto_mem(FT6236_ADDR,FT6236_REG_G_MODE, data_bytearray)

    def set_active_rate(self, rate):
        
        if rate>14:
            rate = 14
        data_bytearray = bytearray([rate])
        self.i2c.writeto_mem(FT6236_ADDR,FT6236_REG_PERIODACTIVE, data_bytearray)


    def set_monitor_rate(self, rate):
        """设置监控模式下的报告率（Hz）"""
        if rate<10:
            rate=10
        if rate>100:
            rate=100
        data_bytearray = bytearray([rate]) 
        self.i2c.writeto_mem(FT6236_ADDR,FT6236_REG_PERIODMONITOR, data_bytearray)

    def wakeup(self):
        """从休眠模式唤醒芯片"""
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(100)

    def sleep(self):
        """使芯片进入休眠模式"""
        self.set_power_mode(FT6236_POWER_MODE_HIBERNATE)