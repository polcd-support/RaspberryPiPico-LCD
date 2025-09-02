# -*- coding: utf-8 -*-

from machine import SoftI2C, Pin
import time
from lcd_def import SCREEN_HEIGHT

TOUCH_RST_PIN = 13
TOUCH_INT_PIN = 9
I2C0_SDA_PIN = 11
I2C0_SCL_PIN = 10

# FT6236 设备地址与引脚定义
CST816_ADDR = 0x15

# 寄存器地址定义
GestureID =0x01		# 触摸屏中与手势识别
FingerNum =0x02		# 记录触摸手指数量
XposH =0x03			# X 坐标高位相关的寄存器地址
XposL =0x04			# X 坐标低位部分的寄存器地址
YposH =0x05			# Y 坐标高位相关的寄存器地址
YposL =0x06			# Y 坐标低位部分的寄存器地址
ChipID =0xA7			# 访问触摸屏芯片的唯一标识符寄存器的地址
SleepMode =0xE5		# 控制触摸屏进入或退出睡眠模式的寄存器地址
MotionMask =0xEC		# 对某些运动相关操作的屏蔽或启用设置
IrqPluseWidth =0xED	# 中断低脉冲宽度相关的寄存器地址
NorScanPer =0xEE		# 触摸屏正常扫描周期相关的寄存器地址
MotionSlAngle =0xEF	# 涉及到运动滑动角度相关
LpAutoWakeTime =0xF4 # 长按自动唤醒时间
LpScanTH =0xF5		# 触摸屏的长按扫描阈值
LpScanWin =0xF6		# 触摸屏的长按扫描窗口相关
LpScanFreq =0xF7		# 触摸屏的长按扫描频率
LpScanIdac =0xF8		# 长按扫描电流
AutoSleepTime =0xF9	# 触摸屏自动进入睡眠模式的时间相关
IrqCtl =0xFA			# 触摸屏的中断控制相关
AutoReset =0xFB		# 触摸屏自动复位相关
LongPressTime =0xFC	# 触摸屏的长按时间
IOCtl =0xFD			# 触摸屏的输入输出控制
DisAutoSleep =0xFE	# 禁止触摸屏自动进入睡眠模式

# 手势ID枚举
class Gesture:
    NOGESTURE = 0x00       # 无手势
    DOWNGLIDE = 0x01       # 下滑
    UPGLIDE = 0x02         # 上滑
    LEFTGLIDE = 0x03       # 左滑
    RIGHTGLIDE = 0x04      # 右滑
    CLICK = 0x05           # 单击
    DOUBLECLICK = 0x0B     # 双击
    LONGPRESS = 0x0C       # 长按

# 手势使能枚举
class MotionMask:
    M_DISABLE = 0x00       # 禁用所有手势
    EnConLR = 0x01         # 使能左右滑动
    EnConUD = 0x02         # 使能上下滑动
    EnDClick = 0x03        # 使能双击
    M_ALLENABLE = 0x07     # 使能所有手势

# 中断控制枚举
class IrqCtl:
    OnceWLP = 0x00         # 单次低脉冲
    EnMotion = 0x10        # 运动变化触发中断
    EnChange = 0x20        # 状态变化触发中断
    EnTouch = 0x40         # 触摸事件触发中断
    EnTest = 0x80          # 中断测试模式
    

class CST816:
    def __init__(self, sda=I2C0_SDA_PIN, scl=I2C0_SCL_PIN, rst=TOUCH_RST_PIN):
        self.rst_pin = Pin(rst, Pin.OUT, value=1)
        self.i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl), freq=400000)
        self.TOUCH_OFFSET_Y = 0
        self.REVERSE = 1
        self.X_Pos = 0          # X坐标
        self.Y_Pos = 0          # Y坐标

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
        self.Config_AutoSleepTime(5)
        

    def Get_XY_AXIS(self):
        """获取触摸数据并更新到info结构体"""
        data = self.i2c.readfrom_mem(CST816_ADDR,XposH,4)

        # 解析X坐标
        self.X_Pos = ((data[0] & 0x0F) << 8) | data[1]
        # 解析Y坐标
        self.Y_Pos = ((data[2] & 0x0F) << 8) | data[3] + self.TOUCH_OFFSET_Y

        # 处理X轴反转
        if self.REVERSE:
            self.Y_Pos = SCREEN_HEIGHT - 1 - self.Y_Pos


    def Get_FingerNum(self):
        """获取触摸点数量"""
        status = self.i2c.readfrom_mem(CST816_ADDR,FingerNum,1)
        return status[0]
    
    def get_chip_id(self):
        """获取芯片ID"""
        return self.i2c.readfrom_mem(CST816_ADDR,ChipID,1)

    def Config_MotionMask(self,mode):
        self.i2c.writeto_mem(CST816_ADDR,MotionMask, bytearray([mode]))

    def Config_AutoSleepTime(self,time):
        data_bytearray = bytearray([time])
        self.i2c.writeto_mem(CST816_ADDR,AutoSleepTime, data_bytearray)

    def sleep(self):
        """使芯片进入休眠模式"""
        self.i2c.writeto_mem(CST816_ADDR , SleepMode, bytearray([0x03]))

    def wakeup(self):
        """从休眠模式唤醒芯片"""
        self.reset()

    def Config_MotionSlAngle(self,x_right_y_up_angle):
        self.i2c.writeto_mem(CST816_ADDR,MotionSlAngle, bytearray([x_right_y_up_angle]))
        
    def Config_NorScanPer(self,Period):
        if Period>=30:
            Period=30
        self.i2c.writeto_mem(CST816_ADDR,NorScanPer, bytearray([Period]))

    def Config_IrqPluseWidth(self,Width):
        if Width>=30:
            Width=30
        self.i2c.writeto_mem(CST816_ADDR,IrqPluseWidth, bytearray([Width]))

    def Config_LpScanTH(self,TH):
        self.i2c.writeto_mem(CST816_ADDR,LpScanTH, bytearray([TH]))