from machine import Pin,SPI,PWM
import framebuf as fb
import time
import os

class LCDBase(fb.FrameBuffer):
    """
    BaseClass for LCD displays. This class based on FrameBuffer
    """
    def __init__(self, width, height, cformat):
        self._width = width
        self._height = height
        self.buffer = bytearray(self._height * self._width * 2)
        super().__init__(self.buffer, self._width, self._height, cformat)
        pass

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height 

    
    #-----------------------------------------
    # Color managment
    #-----------------------------------------
    def RGB888toRGB565(self, RGB888):
        """ convert RGB 16Bit to RGB 24Bit """
        RGB565 = (((RGB888 & 0xf80000)>>8) + ((RGB888 & 0xfc00)>>5) + ((RGB888 & 0xf8)>>3))
        return RGB565

    def hsv_to_rgb888(self, h, s, v):
        """ convert hsv color wheel to rgb888 """
        h = h / 360.0
        if s == 0.0: v*=255; return (v, v, v)
        i = int(h*6.) # XXX assume int() truncates!
        f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        if i == 5: return (v, p, q)

    def hsv_to_rgb565(self, h,s,v):
        """ convert color wheel to rgb565 """
        (r,g,b) = self.hsv_to_rgb888(h,s,v)
        rgb = (r << 16) + (g << 8) + (b)
        rgb565 = self.RGB888toRGB565(rgb)
        return rgb565    


    #-----------------------------------------
    # shapes managment
    #-----------------------------------------

    def circle(self, x,y,r,c):
        """ draw a circle on center x/y with radius in color c

        Args:
            x ([type]): [center x]
            y ([type]): [center y]
            r ([type]): [radius]
            c ([type]): [color as RGB565]
        """
        pass

    def roundrect(self, x,y, w,h,r, c):
        """draw a rounded rectangle with width and height in color c
        edge radius in r

        Args:
            x ([type]): [start on lower left corner x]
            y ([type]): [start and lower left corner y]
            w ([type]): [width of rectangle]
            h ([type]): [height of rectangle]
            r ([type]): [edge radius]
            c ([type]): [color as RGB565]
        """
        pass


    #---------------------------------
    # below methods must be implemented from
    # every dedicated LCD Subclass
    #
    # unfortunately ABC is not available on micropython
    # so no saftey implementation, that subclasses implement
    # necessary methods !
    #---------------------------------

    def init_display(self):
        """ must implemented in subclass """
        pass 
    
    def write(self, cmd=None, data=None):
        """ must be implemented in subclass """
        pass 

    def flip(self, dir):
        """ must be implemented in subclass """
        pass 

    def show(self):
        """ must be implemented in subclass """
        pass 

