from machine import Pin,SPI,PWM
import framebuf as fb
from .LCDBase import LCDBase
import math
import time
import os

class PicoGFX():

    def __init__(self, display):
        self.disp = display
        self._cursorX       = 0
        self._cursorY       = 0
        self._bgcolor       = 0x0000
        self._textbgcolor   = 0x0000
        self._fgcolor       = 0xFFFF
        self._textfgcolor   = 0xFFFF
        self._textSize      = 8

    def circle(self, x0,y0,r,c):
        """draw a outline circel with center x0/y0, radius r and color c

        Args:
            x0 ([type]): [center point x]
            y0 ([type]): [center point y]
            r ([type]): [radius]
            c ([type]): [rgb565]
        """
        f = 1 - r 
        ddF_x = 1 
        ddF_y = -2 * r 
        x = 0
        y = r 
        self.disp.pixel(x0, y0 + r, c)
        self.disp.pixel(x0, y0 - r, c)
        self.disp.pixel(x0 + r, y0, c)
        self.disp.pixel(x0 - r, y0, c)
        while (x < y) :
            if (f >= 0):
                y -= 1
                ddF_y += 2
                f += ddF_y 
            x = x + 1
            ddF_x += 2
            f += ddF_x 
            self.disp.pixel(x0 + x, y0 + y, c)
            self.disp.pixel(x0 - x, y0 + y, c)
            self.disp.pixel(x0 + x, y0 - y, c)
            self.disp.pixel(x0 - x, y0 - y, c)
            self.disp.pixel(x0 + y, y0 + x, c)
            self.disp.pixel(x0 - y, y0 + x, c)
            self.disp.pixel(x0 + y, y0 - x, c)
            self.disp.pixel(x0 - y, y0 - x, c)
            
        pass 

    def qcircleHelper(self, x0, y0, r, corner, c):
        """helper for quarter circles, used for circels and
           round rectangles

        Args:
            x0 ([type]): [cp x]
            y0 ([type]): [cp y]
            r ([type]): [radius]
            corner ([type]): [mask bit #1 or bit #2 to indicate quarter of the circel]
            c ([type]): [rgb565]
        """
        f = 1-r
        ddF_x = 1 
        ddF_y = -2*r 
        x = 0
        y = r 
        while(x < y):
            if (f >= 0):
                y -= 1
                ddF_y += 2
                f += ddF_y 

            x += 1
            ddF_x += 2 
            f += ddF_x 
            if (corner & 0x04):
                self.disp.pixel(x0 + x, y0 + y, c)
                self.disp.pixel(x0 + y, y0 + x, c)
            if (corner & 0x02):
                self.disp.pixel(x0 + x, y0 - y, c)
                self.disp.pixel(x0 + y, y0 - x, c)
            if (corner & 0x08):
                self.disp.pixel(x0 - y, y0 + x, c)
                self.disp.pixel(x0 - x, y0 + y, c)
            if (corner & 0x01):
                self.disp.pixel(x0 - y, y0 - x, c)
                self.disp.pixel(x0 - x, y0 - y, c)
        pass

    def qfillcircleHelper(self, x0, y0, r, corner, delta, c):
        """quarter filled circel, used by circels and rectangles

        Args:
            x0 ([type]): [cp x]
            y0 ([type]): [cp y]
            r ([type]): [radius]
            corner ([type]): [mask bit for corners]
            delta ([type]): [offset from cp, used by round-rects]
            c ([type]): [rgb565]
        """
        f = 1-r
        ddF_x = 1 
        ddF_y = -2*r 
        x = 0
        y = r 
        px = x
        py = y 
        delta += 1
        while (x < y):
            if (f >= 0):
                y -= 1
                ddF_y += 2
                f += ddF_y 

            x += 1
            ddF_x += 2 
            f += ddF_x 
            if (x < (y+1)):
                if (corner & 0x01):
                    self.disp.vline(x0 + x, y0 - y, 2*y+delta,c)
                if (corner & 0x02):
                    self.disp.vline(x0 - x, y0 - y, 2*y+delta,c)

            if (y != py):
                if (corner & 0x01):
                    self.disp.vline(x0 + py, y0 - px, 2*px+delta,c)
                if (corner & 0x02):
                    self.disp.vline(x0 - py, y0 - px, 2*px+delta,c)
                py = y
            px = x
        pass
    
    def fill_circle(self, x0, y0, r, c):
        """draw a filled circle, use qcircleHelper to do this

        Args:
            x0 ([type]): [description]
            y0 ([type]): [description]
            r ([type]): [description]
            c ([type]): [description]
        """
        self.disp.vline(x0, y0-r, 2*r+1, c)
        self.qfillcircleHelper(x0, y0, r, 3, 0, c)
        pass

    def rect(self, x, y, w, h, c):
        self.disp.rect(x,y,w,h,c)
        
    def fill_rect(self, x,y,w,h,c):
        self.disp.fill_rect(x,y,w,h,c)
        
    def round_rect(self, x,y,w,h,r,c):
        if (w < h):
            max_r = int (w / 2)
        else:
            max_r = int (h / 2)
            
        if (r > max_r):
            r = max_r
        self.disp.hline(x+r, y, w-2 * r, c)
        self.disp.hline(x+r, y+h-1, w-2*r, c)
        self.disp.vline(x,y+r,h-2*r,c)
        self.disp.vline(x+w-1,y+r,h-2*r,c)
        # corners
        self.qcircleHelper(x+r,y+r,r,1,c)
        self.qcircleHelper(x+w-r-1,y+r,r,2,c)
        self.qcircleHelper(x+w-r-1,y+h-r-1,r,4,c)
        self.qcircleHelper(x+r,y+h-r-1,r,8,c)
        
    def clear(self, c=0x00):
        self.disp.fill(c)
        self.show()
        
    def show(self):
        self.disp.show()

    def update(self):
        self.disp.show()

    def triangle(self, x1,y1,x2,y2,x3,y3,c):
        self.disp.line(x1,y1,x2,y2,c)
        self.disp.line(x2,y2,x3,y3,c)
        self.disp.line(x1,y1,x3,y3,c)
        
        

    @property
    def cursorX(self):
        return self._cursorX

    @cursorX.setter
    def cursorX(self, cX):
        self._cursorX = cX

    @property
    def cursorY(self):
        return self._cursorY

    @cursorY.setter
    def cursorY(self, cY):
        self._cursorY = cY

    @property
    def bgcolor(self):
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, c):
        self._bgcolor = c

    @property
    def fgcolor(self):
        return self._fgcolor

    @fgcolor.setter
    def fgcolor(self, c):
        self._fgcolor = c
    
    @property
    def textSize(self):
        return self._textSize

    @textSize.setter
    def textSize(self, size):
        self._textSize = size

    @property 
    def textFGColor(self):
        return self._textfgcolor

    @textFGColor.setter
    def textFGColor(self, c):
        self._textfgcolor = c

    @property 
    def textBGColor(self):
        return self._textbgcolor

    @textBGColor.setter
    def textBGColor(self, c):
        self._textbgcolor = c

    class colors():
        """ define default colors as RGB565 """ 
        white      = 0xffff
        black      = 0x00
        red        = 0x07E0
        green      = 0x001f
        blue       = 0xf800

        indianred   = 0xCAEB
        deeppink    = 0xF8B2
        lightsalomon= 0xFD0F
        tomato      = 0xFB08
        yellow      = 0xFFE0
        gold        = 0xFEA0
        kaki        = 0xF731
        darkkaki    = 0xBDAD
        magenta     = 0xF81F
        blueviolet  = 0x895C
        greenyellow = 0xAFE5
        lime        = 0x07E0
        limegreen   = 0x3666
        teal        = 0x0410
        olive       = 0x8400
        aqua        = 0x07FF
        cyan        = 0x07FF
        turquoise   = 0x47BA
        skyblue     = 0x867D
        steelblue   = 0x4416
        darkblue    = 0x0011
        wheat       = 0xF6F6
        tan         = 0xD5B1
        goldenrod   = 0xDD23
        choclate    = 0xD343
        saddlebrown = 0x8A22
        beige       = 0xF7BB
        lightgray   = 0xD69A
        silver      = 0xC618
        gray        = 0x8410
        darkgray    = 0x2A69
        black       = 0x0000

