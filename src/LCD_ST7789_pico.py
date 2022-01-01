from machine import Pin,SPI,PWM
import framebuf as fb
from .LCDBase import LCDBase
import time
import os

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

class LCD_ST7789(LCDBase):
    """LCD display based on ST7890 controller

        Details: https://www.waveshare.com/w/upload/a/ae/ST7789_Datasheet.pdf

        PicoLCD Display 240x240 or 320x240
    """
    def __init__(self, width=240, height=240, cformat=fb.RGB565):
        super().__init__(width, height, cformat)
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,100000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)

        self.MADCTR_normal      = 0b000
        self.MADCTR_ymir        = 0b001
        self.MADCTR_xmir        = 0b010
        self.MADCTR_xymir       = 0b011
        self.MADCTR_ex          = 0b100
        self.MADCTR_ex_ymir     = 0b101
        self.MADCTR_ex_ymir     = 0b110
        self.MADCTR_ex_xymir    = 0b111 #default 

        self.init_display()
 
    #-----------------------------------------
    # low level methods
    #-----------------------------------------
    def write(self, cmd=None, data=None):
        """
        low level write to lcd display.
        
        If data = None, send a command to LCD
        If data != None, send data to LCD
        
        """
        self.cs(1)
        if data == None:
            self.dc(0)
            self.cs(0)
            self.spi.write(bytearray([cmd]))
        else:
            self.dc(1)
            self.cs(0)
            self.spi.write(bytearray([data]))        
        self.cs(0)
        
    def init_display(self):
        """ initialize LCD display """
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        # MADCTL Control
        #self.write(cmd=0x36)
        # display orientation
        #self.write(data=0x70)
        self.flip(self.MADCTR_ex_xymir)

        # Color coding to RGB565
        self.write(cmd=0x3A) 
        self.write(data=0x05)

        #System settings
        # Porch Settings, default setting
        self.write(cmd=0xB2)    
        self.write(data=0x0C)    
        self.write(data=0x0C)
        self.write(data=0x00)
        self.write(data=0x33)
        self.write(data=0x33)

        # Gate Controld, default
        self.write(cmd=0xB7)
        self.write(data=0x35) 

        # VCom Setting, 
        self.write(cmd=0xBB)
        self.write(data=0x19) # 0.725

        # LCM Control
        self.write(cmd=0xC0)
        self.write(data=0x2C) # default

        # VDV/VRH Command Enabling 
        self.write(cmd=0xC2)
        self.write(data=0x01) # default

        # VRH set
        self.write(cmd=0xC3)
        self.write(data=0x12) # 4.45 +(vcom+vocom offset + vdv)

        # VDV set
        self.write(cmd=0xC4)
        self.write(data=0x20) # 0

        # Frame rate
        self.write(cmd=0xC6)
        self.write(data=0x0F) # 60 (default)

        # Power control 1, default
        self.write(cmd=0xD0)
        self.write(data=0xA4) #
        self.write(data=0xA1)

        # Positive Voltage Gamma Control
        # 14 Parameters
        self.write(cmd=0xE0)
        self.write(data=0xD0)   # 
        self.write(data=0x04)
        self.write(data=0x0D)
        self.write(data=0x11)
        self.write(data=0x13)
        self.write(data=0x2B)
        self.write(data=0x3F)
        self.write(data=0x54)
        self.write(data=0x4C)
        self.write(data=0x18)
        self.write(data=0x0D)
        self.write(data=0x0B)
        self.write(data=0x1F)
        self.write(data=0x23)

        # negative voltage gamma control
        self.write(cmd=0xE1)
        self.write(data=0xD0)
        self.write(data=0x04)
        self.write(data=0x0C)
        self.write(data=0x11)
        self.write(data=0x13)
        self.write(data=0x2C)
        self.write(data=0x3F)
        self.write(data=0x44)
        self.write(data=0x51)
        self.write(data=0x2F)
        self.write(data=0x1F)
        self.write(data=0x1F)
        self.write(data=0x20)
        self.write(data=0x23)
        
        # Display inversion ON
        self.write(cmd=0x21)
        # Display inversion OFF
        #self.write(cmd=0x20)

        # Sleep OUT
        self.write(cmd=0x11)
        # Sleep IN
        #self.write(cmd=0x10)

        #
        self.write(cmd=0x29)

    def dispOn(self):
        self.write(cmd=0x29)

    def dispOff (self):
        self.write(cmd=0x28)
  
    def invertOn(self):
        self.write(cmd=0x21)

    def invertOff(self):
        self.write(cmd=0x20)

    def memoryDataAccessControl(self):
        """Move data from frame buffer to display

        """
        self.write(cmd=0x36)
        self.write(data=0x00)

    def rotate(self, dir):
        if dir <= 0:
            dir = 0
        if dir >= 7:
            dir = 7
        # MADCTL Control
        self.write(cmd=0x36)
        # display orientation
        v =dir << 4
        self.write(data=v)

    def show(self):
        """ """
        # Column Address Set
        self.write(cmd=0x2A)
        self.write(data=0x00)
        self.write(data=0x00)
        self.write(data=0x00)
        self.write(data=0xef)
        # Row Address Set
        self.write(cmd=0x2B)
        self.write(data=0x00)
        self.write(data=0x00)
        self.write(data=0x00)
        self.write(data=0xEF)
        # Memory Write
        self.write(cmd=0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        # write buffer to frame memory
        self.spi.write(self.buffer)
        self.cs(1)                           
                        
                           