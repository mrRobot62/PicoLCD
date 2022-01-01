# Raspberry Pico LCD library

under construction. This libray provide a couple of graphic routines to use a color lcd display on a raspberry pico with micropython installed

Fonts are currently not implemented in version 0.1

This libray is tested on a waveshare LCD 1.3" Display with a joystick and 4 buttons.
https://www.waveshare.com/product/raspberry-pi/boards-kits/raspberry-pi-pico-cat/pico-lcd-1.3.htm


## History
| Date | Version | Comments |
|:---: | --- | --- |
| 2022-01-01 | 0.1 | initial, without any font implementations |



# Installation
Assumption latest micropython firmware is installed and a lcd display is mounted on your pico.

* Download git-repo to your local computer
* use Thonny or VS-Code (with installed extension Pico-Go) and download complete repo to your pico device
* start test_ui.py

# Graphic primitives

## Circles (outline & filled)
![IMG_0177](https://user-images.githubusercontent.com/949032/147857273-ef17d61a-2097-46fa-bee3-490bb93bcc3b.png)

## Rectangles (outline & filled)
![IMG_0178](https://user-images.githubusercontent.com/949032/147857289-2207b9ba-b21a-4daa-806b-b0b34d2fa22f.png)

## Triangles (outline)
![IMG_0179](https://user-images.githubusercontent.com/949032/147857277-d1906a97-b6c7-4342-9189-b42f59fd3b2c.png)

## Round-Rectangles (outline & filled)

# HowTo use
This library contain three different files

### PicoGFX.py
This class should be importet in your project and represent the ui component. Via this GFX class you can use all function implemented inside the LCD-classes and which are provided from FrameBuffer.

This class provide all high level graphic functions which you can use in your project

## LCD_ST7789_pico.py
This subclass inherit function from LCDBase and is specilized for a LCD display based on a ST7789 display chip. These subclasses contain all necessary low level routines to use an display. This classes do not contain high level graphic primitives, except those which are provided by Framebuffer

### LCDBase.py
Abstract base class for LCD/OLED subclasses. This base class provide a couple of low level routines, which should be used from subclasses and some methods which muste be implemented inside a subclass. This abstract class is a Framebuffer class

### Framebuffer 
MicroPython built in lib. See : https://docs.micropython.org/en/latest/library/framebuf.html

# Generel links
In regrads to below sites, I got a couple of ideas, solutions and good vibes ;-)

**Adafruit**
From AdafruitGFX a couple of low level routines were adapted in python for this LCD lib
https://learn.adafruit.com/adafruit-gfx-graphics-library/using-fonts?view=all#graphics-primitives

**Peter Hinch**
A very good implementation of fonts for MicroPython
https://github.com/peterhinch/micropython-font-to-py



