from machine import Pin,SPI,PWM
from src.LCD_ST7789_pico import LCD_ST7789
from src.PicoGFX import PicoGFX
import time
import os
import unittest
import binascii

class TestLCDBasics(unittest.TestCase):

    @unittest.skip("test_hsv_colors")
    def test_hsv_colors(self):
        disp = LCD_ST7789(width=240,height=240)
        lcd = PicoGFX(disp)
        print ("show color wheel on lcd screen starting with 0deg up to 360deg")
        lcd.disp.fill(lcd.colors.white)
        lcd.show()
        for deg in range (0,359,20):
             rgb565 = lcd.disp.hsv_to_rgb565(deg,1,1)
             print (f"{deg:4d} deg - R565 hex({rgb565})")
             lcd.disp.fill(rgb565)
             lcd.disp.show()
             time.sleep_ms(10)
        
        
        print ("<end>-----------------------")
        time.sleep(2)
        pass

    @unittest.skip("test_rgb888_colors")
    def test_rgb888_colors(self):
        disp = LCD_ST7789(width=240,height=240)
        lcd = PicoGFX(disp)

        lcd.show()
        # print ("<end>-----------------------")
        # time.sleep(2)
        pass

    @unittest.skip("test_rect")
    def test_rect(self):
        disp = LCD_ST7789(width=240,height=240)
        lcd = PicoGFX(disp)
        lcd.disp.fill(lcd.colors.black)
        lcd.show()
        cx = int(lcd.disp.width / 2)
        cy = int(lcd.disp.height / 2)
        w = h = 2
        for deg in range(0,359,6):
            rgb565 = lcd.disp.hsv_to_rgb565(deg,1,1)
            x = cx - int(w/2)
            y = cy - int(h/2)
            lcd.disp.fill_rect(x,y,w,h, rgb565)
            #lcd.disp.rect(x,y,w,h,gfx.colors.white)
            lcd.show()
            w = w + 3
            h = h + 3
            time.sleep_ms(25)
            #print(f"Rectangle {x}/{y} color {hex(rgb565)}")
        print ("<end>-----------------------")
        time.sleep(2)
        pass
        
    @unittest.skip("test_rotate")
    def test_rotate(self):
        disp = LCD_ST7789(width=240,height=240)
        lcd = PicoGFX(disp)
        for f in range(8):
            lcd.disp.fill(lcd.colors.black)
            lcd.show()
            offset = 0
            for deg in range(0,359,5):
                c = lcd.disp.hsv_to_rgb565(deg,1,1)
                x1 = 0 + offset
                y1 = int(lcd.disp.height / 2)  
                x2 = lcd.disp.width - offset
                y2 = lcd.disp.height - offset
                x3 = lcd.disp.width - offset
                y3 = 0 + offset
                lcd.triangle(x1,y1,x2,y2,x3,y3,c)   
                lcd.show()
                print (f"X1/Y1 {x1}/{y1} - X2/Y2 {x2}/{y2} - X3/Y3 {x3}/{y3} Offset {offset}")
                time.sleep_ms(10)
                offset = offset + 5     
            time.sleep_ms(100)
            print(f"Flip Dir {hex(f)}")
            lcd.disp.rotate(f)

    #@unittest.skip("test_circle")
    def test_circle(self):
        disp = LCD_ST7789(width=240,height=240)
        lcd = PicoGFX(disp)
        count = 60
        lcd.disp.fill(lcd.colors.black)
        lcd.show()
        c = 0
        x = y = 0
        for deg in range(0,120,2):
            x = int(lcd.disp.width / 2)
            y = int(lcd.disp.height / 2)
            c = lcd.disp.hsv_to_rgb565(deg,1,1)
            lcd.circle (x,y,deg, c)
            lcd.show()
            print(f"Circel ({x},{y} r {deg} c {c}")
            time.sleep_ms(25)



    @unittest.skip("test_text")
    def test_text(self):
        disp = LCD_ST7789(width=240,height=240)
        lcd = PicoGFX(disp)
        lcd.disp.fill(lcd.colors().white)

        lcd.disp.text('LunaX (c) 2022', 0,0, lcd.colors.red)
        lcd.disp.hline(0,9,96, 0xffff)
        lcd.show()
        # print ("<end>-----------------------")
        # time.sleep(3)
        pass
if __name__ == '__main__':
    unittest.main()
