#!/usr/bin/env python

#----------------------------------------------------------------------
#  Arcade Retro Clock(tm)
#  
#  Copyright 2019 William McEvoy
#  Metropolis Dreamware Inc.
#  william.mcevoy@gmail.com
#
#  NOT FOR COMMERCIAL USE
#  If you want to use my code for commercial purposes, contact me
#  and we can make a deal. Contact William McEvoy.
#
#  Note:
#    This program evolved out of an experiment and is not necessarily
#    coded following best practices.  I was learning python and 
#    decided to use the Unicorn Hat to faciliate this learning.
#    Before releasing this code officially, it will be tidied up and
#    not be such a mess.
#   
#    PacDot was the first mini-game I made, and it is pretty messy.
#    VirusWorld is the latest mini-game and features a scrolling map that
#    is 6 screens in size, with virus objects going about their business
#    even when they are not on the screen.
#
#----------------------------------------------------------------------


#running PacDot automatically as background task (non interactive)
# cd /etc
# sudo nano rc.local
# nohup sudo python /home/pi/Pimoroni/unicornhat/examples/ArcadeRetroyClock.py 0.07 0.07 0.07 20 40 200 >/dev/null 2>&1 &

#running PacDot after auto-loggin in
#modify profile script to include call to bash file
#cd /etc
#sudo nano profile
#cd pi
#./go.sh



#------------------------------------------------------------------------------
# Initialization Section                                                     --
#------------------------------------------------------------------------------
from __future__ import print_function


import sys
import os
import time
import random
import string
from datetime import datetime, timedelta
from random import randint
import unicornhat as unicorn
import argparse
import gc
import copy
import numpy
import math

from ConfigParser import SafeConfigParser


#For capturing keypresses
import curses

#Check for keyboard input
#c = stdscr.getch()
#  if c > 1:
#  time.sleep(5)



    

unicorn.set_layout(unicorn.AUTO)
unicorn.rotation(90)
#unicorn.brightness(random.uniform(0.0,1.0))     
unicorn.brightness(1)

width,height=unicorn.get_shape()
random.seed()

#python debugger
import pdb


#------------------------------------------------------------------------------
# Variable Declaration Section                                               --
#------------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("MainSleep",  type=float, nargs='?',default=0.15)
parser.add_argument("FlashSleep", type=float, nargs='?',default=0.01)
parser.add_argument("ScrollSleep",type=float, nargs='?',default=0.07)

parser.add_argument("MinDots",          type=int, nargs='?',default=1)
parser.add_argument("MaxDots",          type=int, nargs='?',default=64)
parser.add_argument("MaxMoves",         type=int, nargs='?',default=2000)
parser.add_argument("TinyClockStartHH", type=int, nargs='?',default=0)
parser.add_argument("TinyClockHours",   type=int, nargs='?',default=0)
parser.add_argument("CPUModifier",      type=float, nargs='?',default=1.0)  #used to compensate for CPU speeds (A+ vs Pi 3)

args = parser.parse_args()

MainSleep        = args.MainSleep
FlashSleep       = args.FlashSleep
ScrollSleep      = args.ScrollSleep
MinDots          = args.MinDots
MaxDots          = args.MaxDots
MaxMoves         = args.MaxMoves
TinyClockStartHH = args.TinyClockStartHH
TinyClockHours   = args.TinyClockHours
CPUModifier      = args.CPUModifier

KeyboardSpeed  = 100
ConfigFileName = "ClockConfig.ini"
CheckTime = 30


#----------------------------
# Virus World              --
#----------------------------
mutationrate      = 20
replicationrate   = 3500
mutationdeathrate = 15
InstabilityFactor = 10
walllives         = 20
VirusStartSpeed   = 1
ScrollSpeedLong   = 500
ScrollSpeedShort  = 5
ClumpingSpeed     = -5
ReplicationSpeed  = -5
VirusTopSpeed     = 1
VirusBottomSpeed  = 20

#apply CPU modifier
ScrollSpeedLong   = ScrollSpeedLong  * CPUModifier
ScrollSpeedShort  = ScrollSpeedShort * CPUModifier
VirusStartSpeed   = VirusStartSpeed  * CPUModifier
VirusTopSpeed     = VirusTopSpeed    * CPUModifier
VirusBottomSpeed  = VirusBottomSpeed * CPUModifier


#----------------------------
#-- PacDot                 --
#----------------------------

#thise things are left over from before I made the PacDot function
#cleanup later I hope (likely too lazy, likkit!)

PowerPills  = 1
moves       = 0
MaxPacmoves = 12
DotsEaten   = 0
Pacmoves    = 0
PowerPillActive = 0
PowerPillmoves  = 0
BlueGhostmoves = 50
StartGhostSpeed1    = 1
StartGhostSpeed2    = 2
StartGhostSpeed3    = 3
GhostSpeed1    = StartGhostSpeed1
GhostSpeed2    = StartGhostSpeed2
GhostSpeed3    = StartGhostSpeed3
PacSpeed       = 1
BlueGhostSpeed = 4
LevelCount     = 1
PacPoints      = 0
PacStuckMaxCount = 20
PacStuckCount    = 1
PacOldH          = 0
PacOldV          = 0

NumDots  = 40
MaxMoves = 2000


#Pac Scoring
DotPoints         = 1
BlueGhostPoints   = 5
PillPoints        = 10
PacDotScore       = 0
PacDotGamesPlayed = 0
PacDotHighScore   = 0


#Timers
start_time = time.time()

DotMatrix = [[0 for x in range(8)] for y in range(8)] 




#----------------------------
#-- Colors                 --
#----------------------------
#Yellow
YellowR = 100
YellowG = 100
YellowB = 0

#Red
RedR = 100
RedG = 0
RedB = 0

#HighRed
HighRedR = 225
HighRedG = 0
HighRedB = 0

#MedRed
MedRedR = 100
MedRedG = 0
MedRedB = 0

#Orange
OrangeR = 100
OrangeG = 50
OrangeB = 0


#Purple
PurpleR = 75
PurpleG = 0
PurpleB = 75

#Green
GreenR = 0
GreenG = 100
GreenB = 0

#HighGreen
HighGreenR = 0
HighGreenG = 225
HighGreenB = 0

#MedGreen
MedGreenR = 0
MedGreenG = 155
MedGreenB = 0

#LowGreen
LowGreenR = 0
LowGreenG = 100
LowGreenB = 0

#DarkGreen
DarkGreenR = 0
DarkGreenG = 45
DarkGreenB = 0


#Blue
BlueR = 0
BlueG = 0
BlueB = 100

#WhiteLow
WhiteLowR = 45
WhiteLowG = 45
WhiteLowB = 45

#WhiteMed
WhiteMedR = 100
WhiteMedG = 100
WhiteMedB = 100

#WhiteHigh
WhiteHighR = 225
WhiteHighG = 225
WhiteHighB = 225

#Character Colors
PacR = YellowR
PacG = YellowG
PacB = YellowB


#Red
Ghost1R = 100
Ghost1G = 0
Ghost1B = 0

#Orange
Ghost2R = 100
Ghost2G = 45
Ghost2B = 0

#Purple
Ghost3R = 75
Ghost3G = 0
Ghost3B = 75

#Dots
DotR = 65
DotG = 65
DotB = 65

#Wall
WallR = 45
WallG = 100
WallB = 100


#PowerPills
PillR = 0
PillG = 100
PillB = 0

BlueGhostR = 0
BlueGhostG = 0
BlueGhostB = 100

Ghost1Alive = 1
Ghost2Alive = 1
Ghost3Alive = 1 



#----------------------------
#-- Worms                  --
#----------------------------

GreenObstacleFadeValue = 10
GreenObstacleMinVisible = 45



#----------------------------
#-- Ping                   --
#----------------------------



#------------------------------------------------------------------------------
# SPRITES / Classes                                                          --
#------------------------------------------------------------------------------


class Sprite(object):
  def __init__(self,width,height,r,g,b,grid):
    self.width  = width
    self.height = height
    self.r      = r
    self.g      = g
    self.b      = b
    self.grid   = grid

  def Display(self,h1,v1):
    x = 0,
    y = 0
    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          unicorn.set_pixel(x+h1,y+v1,self.r,self.g,self.b)
    unicorn.show()

  def Erase(self,h1,v1):
    #This function draws a black sprite, erasing the sprite.  This may be useful for
    #a future "floating over the screen" type of sprite motion
    #It is pretty fast now, seems just as fast as blanking whole screen using off() or clear()
    x = 0
    y = 0
    #print ("Erase:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          unicorn.set_pixel(x+h1,y+v1,0,0,0)
    unicorn.show()

  def HorizontalFlip(self):
    x = 0
    y = 0
    flipgrid = []
    
    #print ("flip:",self.width, self.height)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      #print("Calculations: ",(y*self.height)+ self.height-x-1)  
      flipgrid.append(self.grid[(y*self.height)+ self.height-x-1])  
    #print("Original:", str(self.grid))
    #print("Flipped :", str(flipgrid))
    self.grid = flipgrid      

    
  def Scroll(self,h,v,direction,moves,delay):
    #print("Entering Scroll")
    x = 0
    oldh = 0
    Buffer = unicorn.get_pixels()
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      for count in range (0,moves):
        h = h + (modifier)
        #erase old sprite
        if count >= 1:
          oldh = h - modifier
          #print ("Scroll:",self.width, self.height, self.r, self.g, self.b,h,v)
          #self.Erase(oldh,v)
          unicorn.set_pixels(Buffer)
        #draw new sprite
        self.Display(h,v)
        unicorn.show()
        time.sleep(delay)
        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()


    if direction == "up" or direction == "down":
      for count in range (0,moves):
        v = v + (modifier)
        #erase old sprite
        if count >= 1:
          oldv = v - modifier
          #self.Erase(h,oldv)
          unicorn.set_pixels(Buffer)
        #draw new sprite
        self.Display(h,v)
        unicorn.show()
        time.sleep(delay)
        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()
        

        
  
  def ScrollAcrossScreen(self,h,v,direction,ScrollSleep):
    #print ("--ScrollAcrossScreen--")
    #print ("width height",self.width,self.height)
    if (direction == "right"):
      self.Scroll((0- self.width),v,"right",(8 + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Scroll(7,v,"left",(8 + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Scroll(h,7,"left",(8 + self.height),ScrollSleep)



# ----------------------
# -- Animated Sprites --
# ----------------------

class AnimatedSprite(object):
  def __init__(self,width,height,r,g,b,frames,grid):
    self.width  = width
    self.height = height
    self.r      = r
    self.g      = g
    self.b      = b
    self.frames = frames
    self.grid   = []

  def Display(self,h1,v1,frame):
    x = 0,
    y = 0

    #print ("Display:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y, " frame: ", frame)
      if self.grid[frame][count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          unicorn.set_pixel(x+h1,y+v1,self.r,self.g,self.b)
    unicorn.show() 

  def Erase(self,h1,v1,frame):
    #This function draws a black sprite, erasing the sprite.  This may be useful for
    #a future "floating over the screen" type of sprite motion
    #It is pretty fast now, seems just as fast as blanking whole screen using off() or clear()
    x = 0
    y = 0
    #print ("Erase:",self.width, self.height, self.r, self.g, self.b,v1,h1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      if self.grid[frame][count] == 1:
        if (CheckBoundary(x+h1,y+v1) == 0):
          #unicorn.set_pixel(x+h1,y+v1,255,255,255)
          #unicorn.show()
          #time.sleep(0.05)
          unicorn.set_pixel(x+h1,y+v1,0,0,0)

          
  def HorizontalFlip(self):
    #Attempting to speed things up by disabling garbage collection
    gc.disable()
    for f in range(0,self.frames + 1):
      x = 0
      y = 0
      flipgrid = []
      #print ("flip:",self.width, self.height)
      for count in range (0,(self.width * self.height )):
        y,x = divmod(count,self.width)
        #print("Count:",count,"xy",x,y)
        #print("Calculations: ",(y*self.height)+ self.height-x-1)  
        flipgrid.append(self.grid[f][(y*self.height)+ self.height-x-1])  
      #print("Original:", str(self.grid[f]))
      #print("Flipped :", str(flipgrid))
      self.grid[f] = flipgrid      
    gc.enable()
          
  def Scroll(self,h,v,direction,moves,delay):
    #print("AnimatedSprite.scroll")
    x = 0
    oldh = 0
    #Capture Background
    Buffer = unicorn.get_pixels()
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("Direction: ",direction)  
      
      for count in range (0,moves):
        oldf = f
        f = f+1
        if (f > self.frames):
          f = 0
        h = h + (modifier)
        #erase old sprite
        #print ("Erasing Frame HV:",oldf," ",h,v)
        if count >= 1:
          oldh = h - modifier
          #print ("Scroll:",self.width, self.height, self.r, self.g, self.b,h,v)
          #self.Erase(oldh,v,oldf)
        #draw new sprite
        unicorn.set_pixels(Buffer)
        self.Display(h,v,f)
        time.sleep(delay)

        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()



  def ScrollWithFrames(self,h,v,direction,moves,delay):
    #print("Entering Scroll")
    x    = 0
    oldh = 0
    Buffer = unicorn.get_pixels()
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    oldf = self.frames
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      for count in range (0,moves):
        #print ("Count:",count)
        if (count >= 1):
          oldh = h
          #print ("Erasing Frame: ", oldf, " hv: ",oldh,v)
          #self.Erase(oldh,v,oldf+1)
        h = h + (modifier)
        #print ("incrementing H:",h)

        #Check for keyboard input
        r = random.randint(0,5)
        if (r == 0):
          Key = PollKeyboard()


        for f in range (0, self.frames+1):
          #erase old sprite
          oldf = f-1
          if oldf < 0:
            oldf = self.frames
          #print ("Erasing Frame: ", oldf, " hv: ",h,v)
          #self.Erase(h,v,oldf)
          unicorn.set_pixels(Buffer)
            
          #draw new sprite
          #print ("Display Frame: ", f, " hv: ",h,v)
          self.Display(h,v,f)
          time.sleep(delay)
          self.Erase(h,v,f)

       
  
  def ScrollAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Scroll((0- self.width),v,"right",(8 + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Scroll(7,v,"left",(8 + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Scroll(h,7,"left",(8 + self.height),ScrollSleep)


  def Animate(self,h,v,delay,direction):
    x = 0,
    y = 0,
    Buffer = unicorn.get_pixels()
    
    if (direction == 'forward'):
      for f in range (0,self.frames+1):
        self.Display(h,v,f)
        unicorn.show()
        time.sleep(delay)
        unicorn.set_pixels(Buffer)
    else:  
      for f in range (0,self.frames+1):
        self.Display(h,v,(self.frames-f))
        unicorn.show()
        time.sleep(delay)
        unicorn.set_pixels(Buffer)
      
      
      


# ----------------------------
# -- Color Animated Sprites --
# ----------------------------

class ColorAnimatedSprite(object):
  def __init__(self,h,v,name,width,height,frames,currentframe,framerate,grid):
    self.h      = h
    self.v      = v
    self.name   = name
    self.width  = width
    self.height = height
    self.frames = frames
    self.currentframe = currentframe
    self.framerate    = framerate     
    
    self.grid         = []  #holds numbers that indicate color of the pixel

  def Display(self,h1,v1):
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    
    #print ("CAS - Display -", self.name, "Display width height HV",self.width, self.height,h1,v1)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("CAS - Display - Count:",count,"xy",x,y, " frame: ", frame)
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary(x+h1,y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          #print ("CAS - Display - rgb",r,g,b)
          if (r > -1 and g > -1 and b > -1):
            unicorn.set_pixel(x+h1,y+v1,r,g,b)
    unicorn.show() 

  def Erase(self):
    #This function draws a black sprite, erasing the sprite.  This may be useful for
    #a future "floating over the screen" type of sprite motion
    #It is pretty fast now, seems just as fast as blanking whole screen using off() or clear()
    x = 0
    y = 0
    h1 = self.h
    v1 = self.v
    frame = self.currentframe
    #print ("CAS - Erase - width hieigh HV currentframe",self.width, self.height, h1,v1,frame)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
     # print("Count:",count,"xy",x,y)
     # print ("CAS - Erase Frame Count",frame,count)
      if self.grid[frame][count] > 0:
        if (CheckBoundary(x+h1,y+v1) == 0):
         # print ("CAS - Erase HV:",x+h1,y+v1)
          unicorn.set_pixel(x+h1,y+v1,0,0,0)

          
  def EraseLocation(self,h,v):
    x = 0
    y = 0
    frame = self.currentframe
    #print ("CAS - EraseLocation - width height HV currentframe",self.width, self.height, h,v,frame)
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      #print("Count:",count,"xy",x,y)
      #print ("CAS - EraseLocation Frame Count",frame,count)
      if self.grid[frame][count] > 0:
        if (CheckBoundary(x+h,y+v) == 0):
          #print ("CAS - EraseLocation HV:",x+h,y+v)
          unicorn.set_pixel(x+h,y+v,0,0,0)
          
          
  def Scroll(self,h,v,direction,moves,delay):
    #print("CAS - Scroll -   HV Direction moves Delay", h,v,direction,moves,delay)
    x = 0
    oldh = 0
    r = 0
    g = 0
    b = 0
    
    #Capture Background
    Buffer = unicorn.get_pixels()
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      #print ("CAS - Scroll - Direction: ",direction)  
      
      for count in range (0,moves):
        #print ("CAS - Scroll - currentframe: ",self.currentframe)
        if (self.currentframe < (self.frames-1)):
          self.currentframe = self.currentframe + 1
        else:
          self.currentframe = 0
        h = h + (modifier)
        if count >= 1:
          oldh = h - modifier
        #draw new sprite
        unicorn.set_pixels(Buffer)
        self.Display(h,v)
        time.sleep(delay)


  def ScrollWithFrames(self,h,v,direction,moves,delay):
    #print("CAS - ScrollWithFrames - HV direction moves delay", h,v,direction,moves,delay)
    x    = 0
    oldh = 0
    Buffer = unicorn.get_pixels()
    self.currentframe = 0
    
    #modifier is used to increment or decrement the location
    if direction == "right" or direction == "down":
      modifier = 1
    else: 
      modifier = -1
    
    #print("Modifier:",modifier)
    oldf = self.frames
    #we use f to iterate the animation frames
    f = self.frames
    if direction == "left" or direction == "right":
      for count in range (0,moves):
        #print ("Count:",count)
        if (count >= 1):
          oldh = h
          h = h + (modifier)
          #print ("CAS - SWF - H oldh modifier",h,oldh,modifier)
        

        for f in range (0, self.frames+1):
          #erase old sprite
          unicorn.set_pixels(Buffer)

          #draw new sprite
         #print ("CAS - SWF - currentframe: ",self.currentframe)
          self.Display(h,v)

          #Increment current frame counter
          if (self.currentframe < (self.frames-1)):
            self.currentframe = self.currentframe + 1
          else:
            self.currentframe = 0
            
          time.sleep(delay)
          
  def HorizontalFlip(self):
    #print ("CAS - Horizontalflip width heigh frames",self.width, self.height,self.frames)
    for f in range(0,self.frames):
      x = 0
      y = 0
      cells = (self.width * self.height)

      flipgrid = []
      #print ("Frame: ",f)
      #print ("cells: ",cells)
      for count in range (0,cells):
        y,x = divmod(count,self.width)
       #print("y,x = divmod(",count,self.width,"): ",y,x)
        #print ("cell to flip: ",((y*self.width)+ self.width-x-1), "value: ",self.grid[f][((y*self.width)+ self.width-x-1)])
        
        flipgrid.append(self.grid[f][((y*self.width)+ self.width-x-1)])  

      #print("Original:", str(self.grid[f]))
      #print("Flipped :", str(flipgrid))
      self.grid[f] = flipgrid      
    #print ("Done Flipping")
    
       
  
  def ScrollAcrossScreen(self,h,v,direction,ScrollSleep):
    if (direction == "right"):
      self.Scroll((0- self.width),v,"right",(8 + self.width),ScrollSleep)
    elif (direction == "left"):
      self.Scroll(7,v,"left",(8 + self.width),ScrollSleep)
    elif (direction == "up"):
      self.Scroll(h,7,"left",(8 + self.height),ScrollSleep)


  def Animate(self,h,v,direction,delay):
   #print("CAS - Animate - HV delay ",h,v,delay,)
    x = 0,
    y = 0,
    Buffer = unicorn.get_pixels()
    
    if (direction == 'forward'):
      for f in range (0,self.frames):
        #erase old sprite
        unicorn.set_pixels(Buffer)
        #draw new sprite
       #print ("CAS - Animate - currentframe: ",self.currentframe)
        self.Display(h,v)

        #Increment current frame counter
        if (self.currentframe < (self.frames-1)):
          self.currentframe = self.currentframe + 1
        else:
          self.currentframe = 0
          
        time.sleep(delay)
        

    else:  
      for f in range (0,self.frames+1):
        #erase old sprite
        unicorn.set_pixels(Buffer)
        #draw new sprite
        #print ("CAS - Animate - currentframe: ",self.currentframe)
        self.Display(h,v)

        #Increment current frame counter
        if (self.currentframe <= (self.frames-1)):
          self.currentframe = self.currentframe -1
        else:
          self.currentframe = self.frames
          
        time.sleep(delay)
      

  #Draw the sprite using an affect like in the movie Tron 
  def LaserScan(self,h1,v1,speed):
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    #print ("CAS - LaserScan -")
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary(x+h1,y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          if (r > 0 or g > 0 or b > 0):
            unicorn.set_pixel(x+h1,y+v1,r,g,b)
            FlashDot4(x+h1,y+v1,speed)
      unicorn.show() 
          
  def LaserErase(self,h1,v1,speed):
    x = 0
    y = 0
    r = 0
    g = 0
    b = 0
    frame = self.currentframe
    #print ("CAS - LaserErase -")
    for count in range (0,(self.width * self.height)):
      y,x = divmod(count,self.width)
      if(self.grid[frame][count] >= 0):
        if (CheckBoundary(x+h1,y+v1) == 0):
          r,g,b =  ColorList[self.grid[frame][count]]
          if (r > 0 or g > 0 or b > 0):
            FlashDot4(x+h1,y+v1,speed)
            unicorn.set_pixel(x+h1,y+v1,0,0,0)
      unicorn.show() 



# --------------------------
# -- Dot and Ship Sprites --
# --------------------------
      
      
class Dot(object):
  def __init__(self,h,v,r,g,b,direction,speed,alive,name,trail,score,maxtrail,erasespeed):
    self.h          = h 
    self.v          = v
    self.r          = r
    self.g          = g
    self.b          = b
    self.direction  = direction
    self.speed      = speed
    self.alive      = 1
    self.name       = name
    self.trail      = [] # a list of tuples, holding hv coordinates of the dot trail
    self.score      = 0
    self.maxtrail   = 0
    self.erasespeed = erasespeed #sleep time for the erase trail function

  def Display(self):
    unicorn.set_pixel(self.h,self.v,self.r,self.g,self.b)
    unicorn.show()
      
  def EraseTrail(self,direction,flash):
    r = self.r
    g = self.g
    b = self.b
    
    
    #Turn trail bright, then gradually fade
    if (flash == 'flash'):
      for x in range(10):
        newr = r + (100) - (25*x-1)
        newg = g + (100) - (25*x-1)
        newb = b + (100) - (25*x-1)
        if (newr > 255):
          newr = 255
        if (newg > 255):
          newg = 255
        if (newb > 255):
          newb = 255
        if (newr < r):
          newr = r
        if (newg < g):
          newg = g
        if (newb < b):
          newb = b
          
        for i,dot in enumerate(self.trail):
          h = dot[0]
          v = dot[1]
          unicorn.set_pixel(h,v,newr,newg,newb)
        time.sleep(self.erasespeed * 0.75)
        unicorn.show()
      
    #Erase 
    if (direction == 'forward'):
     #print ("Erasing Trail: forward")
      for i,dot in enumerate(self.trail):
        h = dot[0]
        v = dot[1]
        unicorn.set_pixel(h,v,100,100,100)
        unicorn.show()
        time.sleep(self.erasespeed)
        unicorn.set_pixel(h,v,0,0,0)
        unicorn.show()
      
    else:
     #print ("Erasing Trail: backward")
      for i,dot in reversed(list(enumerate(self.trail))):
        h = dot[0]
        v = dot[1]
        unicorn.set_pixel(h,v,100,100,100)
        unicorn.show()
        time.sleep(self.erasespeed)
        unicorn.set_pixel(h,v,0,0,0)
        unicorn.show()

      
  def ColorizeTrail(self,r,g,b):
    
    for i,dot in enumerate(self.trail):
      h = dot[0]
      v = dot[1]
      unicorn.set_pixel(h,v,r,g,b)
    time.sleep(self.erasespeed * 1.5)
    unicorn.show()
    
      


      
class Ship(object):
  def __init__(self,h,v,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding):
    self.h          = h 
    self.v          = v
    self.r          = r
    self.g          = g
    self.b          = b
    self.direction  = direction
    self.scandirection = scandirection
    self.speed      = speed
    self.alive      = 1
    self.lives      = 3
    self.name       = name
    self.score      = 0
    self.exploding  = 0
    

  def Display(self):
    if (self.alive == 1):
      unicorn.set_pixel(self.h,self.v,self.r,self.g,self.b)
     #print("display HV:", self.h,self.v)
      unicorn.show()

      
      
  def Erase(self):
    unicorn.set_pixel(self.h,self.v,0,0,0)
    unicorn.show()
      
  def Flash(self):
    sleep = FlashSleep * 0.75
    LowR  = int(self.r * 0.75)
    LowG  = int(self.g * 0.75)
    LowB  = int(self.b * 0.75)
    HighR = int(self.r * 1.5)
    HighG = int(self.g * 1.5)
    HighB = int(self.b * 1.5)
    
    if (LowR < 0 ):
      LowR = 0
    if (LowG < 0 ):
      LowG = 0
    if (LowB < 0 ):
      LowBB = 0
    
    if (HighR > 255):
      HighR = 255
    if (HighG > 255):
      HighG = 255
    if (HighB > 255):
      HighB = 255
      
    unicorn.set_pixel(self.h,self.v,HighR,HighG,HighB)
    unicorn.show()
    time.sleep(sleep)
    unicorn.set_pixel(self.h,self.v,self.r,self.g,self.b)
    unicorn.show()
    unicorn.set_pixel(self.h,self.v,LowR,LowG,LowB)
    unicorn.show()
    time.sleep(sleep)
    unicorn.show()
    unicorn.set_pixel(self.h,self.v,HighR,HighG,HighB)
    unicorn.show()
    time.sleep(sleep)
    unicorn.set_pixel(self.h,self.v,self.r,self.g,self.b)
    unicorn.show()
    unicorn.set_pixel(self.h,self.v,LowR,LowG,LowB)
    unicorn.show()
    time.sleep(sleep)
    unicorn.show()
  


# I tried including a color animated sprite in this class, but could
# not figure out the syntax.
# The workaround is to simply define a ship sprite that goes along with this object
class AnimatedShip(object):
  def __init__(self,h,v,direction,scandirection,speed,animationspeed,alive,lives,name,score,exploding):
    self.h              = h 
    self.v              = v
    self.direction      = direction
    self.scandirection  = scandirection
    self.speed          = speed
    self.animationspeed = animationspeed
    self.alive          = 1
    self.lives          = 3
    self.name           = name
    self.score          = 0
    self.exploding      = 0
    

     
class Wall(object):
  def __init__(self,h,v,r,g,b,alive,lives,name):
    self.h          = h 
    self.v          = v
    self.r          = r
    self.g          = g
    self.b          = b
    self.alive      = 1
    self.lives      = lives
    self.name       = name
    

  def Display(self):
    if (self.alive == 1):
      unicorn.set_pixel(self.h,self.v,self.r,self.g,self.b)
      unicorn.show()

      
  def Erase(self):
    unicorn.set_pixel(self.h,self.v,0,0,0)
    unicorn.show()
      

class Door(object):
  def __init__(self,h,v,alive,locked,name):
    self.h          = h 
    self.v          = v
    self.alive      = 1
    self.locked     = 0
    self.name       = name

  def Display(self):
    #print("Door.Display - alive locked",self.alive,self.locked)
    if (self.alive == 1):
    
      if (self.locked == 1):

        unicorn.set_pixel(self.h,self.v,SDLowPurpleR,SDLowPurpleG,SDLowPurpleB)
      else:
        unicorn.set_pixel(self.h,self.v,SDDarkYellowR,SDDarkYellowG,SDDarkYellowB)
      unicorn.show()
    

      
  def Erase(self):
    unicorn.set_pixel(self.h,self.v,0,0,0)
    unicorn.show()

      
      
# ----------------------------
# -- World Object           --
# ----------------------------

#DotZerk uses this one

class World(object):
  def __init__(self,name,width,height,Map,Playfield,CurrentRoomH,CurrentRoomV,DisplayH, DisplayV):
    self.name      = name
    self.width     = width
    self.height    = height
    self.Map       = ([[]])
    self.Playfield = ([[]])
    self.CurrentRoomH = 0
    self.CurrentRoomV = 0
    self.DisplayH     = 0
    self.DisplayV     = 0
    
    
    self.Map = [[0 for i in xrange(width)] for i in xrange(height)]

    #Playfield is the physical size of the Unicorn Hat
    self.Playfield = [[0 for i in xrange(8)] for i in xrange(8)]

  def Display(self):
    if (self.alive == 1):
      unicorn.set_pixel(self.h,self.v,self.r,self.g,self.b)
      unicorn.show()
    

  def DisplayWindow(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64)    
    for V in range(0,8):
      for H in range (0,8):
        #The map was created visually for me the programmer
        #turns out the H and V are swapped.  Sorry!
        #print("WO - Display Window - HV hv",H,V,h,v)
          
        #print ("DisplayWindow - HV hv:",H,V,h,v)
        try:
          SDColor = self.Map[V+v][H+h]
        except:
          print ("########################")
          print ("ERROR: Diplay Window function encountered an out of index error.  HV hv",H,V,h,v)
        
        r,g,b =  ColorList[SDColor] 
        #print("WO - Display Window - SDColor rgb",SDColor,r,g,b)
        unicorn.set_pixel(H,V,r,g,b)
        
  #WALL(h,v,r,g,b,alive,lives,name):
           
  def CopyMapToPlayfield(self):
    
    global Door1
    global Door2
    global Door3
    global Door4
    
    h = self.CurrentRoomH * 8
    v = self.CurrentRoomV * 8
    V = 0
    H = 0
    Door1.alive = 0
    Door2.alive = 0
    Door3.alive = 0
    Door4.alive = 0

    
    
    #print ("WO - self.CurrentRoomHV:",h,v,"==============================================")
    for V in range(0,8):
      for H in range (0,8):
        #print ("WO - CopyMapToPlayfield - Map[",V+v,"][",H+h,"]",self.Map[V+v][H+h])
        if (self.Map[V+v][H+h] <> 0):
          SDColor = self.Map[V+v][H+h]
          r,g,b =  ColorList[SDColor]
          #print ("WO - CopyMapToPlayfield - V+v H+h (rgb)",V+v,H+h,"(",r,g,b,")")
          
          #Doors are represented by SDLowYellow (21)
          #I decided to force their positions in order to cut down the complexity
          #They are alive if a door exists, otherwise the space is treated as a wall
          if (SDColor == 21):
            #print ("WO - CopyMapToPlayfield - placing door")
            if (H == 3 and V == 0):
              #print ("###Door1#########################################################################")
              Door1.alive = 1
              Door1.locked == 0
              self.Playfield[H][V] = Door1
            if (H == 7 and V == 3):
              #print ("###Door2#########################################################################")
              Door2.alive = 1
              Door2.locked == 0
              self.Playfield[H][V] = Door2
            if (H == 3 and V == 7):
              #print ("###Door3#########################################################################")
              Door3.alive = 1
              Door3.locked == 0
              self.Playfield[H][V] = Door3
            if (H == 0 and V == 3):
              #print ("###Door4#########################################################################")
              Door4.alive = 1
              Door4.locked == 0
              self.Playfield[H][V] = Door4
          
            #print ("Door1.alive:",Door1.alive)
            #print ("Door2.alive:",Door2.alive)
            #print ("Door3.alive:",Door3.alive)
            #print ("Door4.alive:",Door4.alive)
          
          else:
            self.Playfield[H][V] = Wall(H,V,r,g,b,1,1,'Wall')
            #print ("WO - CopyMapToPlayfield - placing wall")

          
      
      
  def DisplayPlayfield(self,ShowFlash):
    #print ("WO - Display Playfield")
    for y in range (0,8):
      for x in range (0,8):
        #print("WO - DisplayPlayfield XY: ",x,y,self.Playfield[x][y].name)
        if (self.Playfield[x][y].name == 'Door' ):
          print ("WO - DisplayPlayfield - Door found locked:",self.Playfield[x][y].locked)
        if (self.Playfield[x][y].name <> 'empty' ):
          self.Playfield[x][y].Display()
          #print ("WO - DisplayPlayfield - self.Playfield[x][y].hv",self.Playfield[x][y].h,self.Playfield[x][y].v)
          if (ShowFlash == 1):
            FlashDot4(x,y,0.005)
          
          

  
    
  

  
  def ScrollMapRoom(self,direction,speed):

    ScrollH = 0
    SCrollV = 0

    #Scroll Up
    if (direction == 1):
      self.CurrentRoomV = self.CurrentRoomV - 1

      ScrollH = self.CurrentRoomH *8
      ScrollV = self.CurrentRoomV *8
          
      #We display the window 8 times, moving it one column every time
      #this gives a neat scrolling effect
      for x in range (ScrollV+8,ScrollV-1,-1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow ScrollH x:",ScrollH,x)
        self.DisplayWindow(ScrollH,x)
        unicorn.show()
        time.sleep(speed)
       

    
    #Scroll Down
    if (direction == 3):
      self.CurrentRoomV = self.CurrentRoomV + 1

      ScrollH = self.CurrentRoomH *8
      ScrollV = self.CurrentRoomV *8
          
      #We display the window 8 times, moving it one column every time
      #this gives a neat scrolling effect
      for x in range (ScrollV-8,ScrollV+1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow ScrollH x:",ScrollH,x)
        self.DisplayWindow(ScrollH,x)
        unicorn.show()
        time.sleep(speed)
      
    #Scroll right
    if (direction == 2):
      self.CurrentRoomH = self.CurrentRoomH + 1

      ScrollH = self.CurrentRoomH *8
      ScrollV = self.CurrentRoomV *8
          
      #We display the window 8 times, moving it one column every time
      #this gives a neat scrolling effect
      for x in range (ScrollH-8,ScrollH+1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
        self.DisplayWindow(x,ScrollV)
        unicorn.show()
        time.sleep(speed)
      
    
    #Scroll left
    elif (direction == 4):
      self.CurrentRoomH = self.CurrentRoomH -1
      ScrollH = self.CurrentRoomH *8
      ScrollV = self.CurrentRoomV *8
      #print("DZER - ScrollHV",ScrollH,ScrollV)
      for x in range (ScrollH+8,ScrollH-1,-1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
        self.DisplayWindow(x,ScrollV)
        unicorn.show()
        time.sleep(speed)

        
        
        
        
        
        
        
        
        
            
# ----------------------------
# -- GameWorld Object       --
# ----------------------------

#Rallydot

#The GameWorld object contains the entire game layout, the map, the playfield, etc.
#The map is how we draw the roads and structures.  The playfield holds all the objects currently in play.
#The playfield is populated with map objects (loaded from the map, they may have extra properties such as getting destroyed) and player objects
#A window into the playfield is then displayed on the unicorn hat grid.


class EmptyObject(object):
  def __init__(self,name):
    self.name = name
    
    
    
class GameWorld(object):
  def __init__(self,name,width,height,Map,Playfield,CurrentRoomH,CurrentRoomV,DisplayH, DisplayV):
    self.name      = name
    self.width     = width
    self.height    = height
    self.Map       = ([[]])
    self.Playfield = ([[]])
    self.CurrentRoomH = 0
    self.CurrentRoomV = 0
    self.DisplayH     = 0
    self.DisplayV     = 0
    
    
    print ("RD - Initialize map and playfield  width height: ",self.width, self.height)
    self.Map       = [[0 for i in xrange(self.width)] for i in xrange(self.height)]
    self.Playfield = [[EmptyObject('EmptyObject') for i in xrange(self.width)] for i in xrange(self.height)]

    print ("--Initializing map--")
    print (*self.Map[0])
    print (*self.Map[2])
    print ("Map Length: ",len(self.Map[0]))
    print ("Playfield Length",len(self.Playfield[0]))
    print ("-------------------")
    


  def DisplayExplodingObjects(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64)    
    #Displays what is on the playfield currently, including walls, cars, etc.
    r = 0
    g = 0
    b = 0
    count = 0

    for V in range(0,8):
      for H in range (0,8):
         
        name = self.Playfield[v+V][h+H].name
        
        if (name in ("Enemy") and self.Playfield[v+V][h+H].exploding == 1):
          print("Exploding Object - h,v,name ",h,v,name)
          r = 0
          g = 0
          b = 0          
          
          #EXPLODE ENEMY CAR BOMBS
          #Source Car blows up
          self.Playfield[v+V][h+H].exploding = 0
          self.Playfield[v+V][h+H].lives = 0
          self.Playfield[v+V][h+H].alive = 0
          for count in range (1,10):
            print ("Blowing Up: ",count)
            r = r + 25
            g = g + 25
            b = b + 25
            if (r > 255):
              r = 255
            if (g > 255):
              g = 255
            if (b > 255):
              b = 255
            unicorn.set_pixel(H,V,r,g,b)
            unicorn.show()

          unicorn.set_pixel(H,V,0,0,0)
          unicorn.show()
    return;    
    
    

  def DisplayWindow(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64)    
    #Displays what is on the playfield currently, including walls, cars, etc.
    r = 0
    g = 0
    b = 0
    count = 0
        

    for V in range(0,8):
      for H in range (0,8):
        #print("WO - Display Window - HV hv",H,V,h,v)
         
        name = self.Playfield[v+V][h+H].name
        
        if (name == "EmptyObject"):
          r = 0
          g = 0
          b = 0          

        else:
          r = self.Playfield[v+V][h+H].r
          g = self.Playfield[v+V][h+H].g
          b = self.Playfield[v+V][h+H].b
          
        #Our map is an array of arrays [v][h] but we draw h,v
        unicorn.set_pixel(H,V,r,g,b)
    
    unicorn.show()
        

  def UpdateObjectDisplayCoordinates(self,h,v):
    #This function looks at a window (an 8x8 display grid for the unicorn hat)
    #and updates the dh,dv location information for objects in that grid
    #This is useful if we want to blow something up on screen
    
    #scroll off
    for V in range(0,8):
      for H in range (0,8):
        name = self.Playfield[v+V][h+H].name
        if (name == "Player" or name == "Enemy" or name == "Fuel"):
          self.Playfield[v+V][h+H].dh = H
          self.Playfield[v+V][h+H].dv = V
          

  
  def CopyMapToPlayfield(self):
    #This function is run once to populate the playfield with wall objects, based on the map drawing
    #XY is actually implemented as YX.  Counter intuitive, but it works.

    width  = self.width 
    height = self.height 
   
    #print ("RD - CopyMapToPlayfield - Width Height: ", width,height)
    x = 0
    y = 0
    
    
    print ("width height: ",width,height)
    
    for y in range (0,height):
      #print ("-------------------")
      #print (*self.Map[y])
  
      for x in range(0,width):
        #print ("RD xy color: ",x,y, self.Map[y][x])
        SDColor = self.Map[y][x]
        
        
  
        if (SDColor <> 0):
          #print ("Wall")
          r,g,b =  ColorList[SDColor]
          #print ("RD xy: ",x,y," rgb(",r,g,b,")")
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,1,'Wall')
        else:
          #print ("EmptyObject")
          self.Playfield[y][x] = EmptyObject('EmptyObject')
          
          
          
         
      
      
          
          
  def ScrollMapDots(self,direction,dots,speed):

    #we only want to scroll the number of dots, not the whole room
    #DisplayWindow has HV starting in upper left hand corner
    
    x = 0
    ScrollH = self.DisplayH
    ScrollV = self.DisplayV

    #print("ScrollMapDots - ScrollH ScrollV direction width",ScrollH,ScrollV, direction, self.width)
     
    #Scroll Up
    if (direction == 1):
      
      if (ScrollV - dots >= 0):
      
        for x in range (ScrollV-1,ScrollV-dots-1,-1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
         

    
    #Scroll Down
    if (direction == 3):
          
      if (ScrollV + 8 + dots <= self.height):
        for x in range (ScrollV+1,ScrollV+dots+1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
      
    #Scroll right
    if (direction == 2):
      if (ScrollH + 8 + dots  <= self.width):
        for x in range (ScrollH+1,ScrollH+dots+1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x
      
    
    #Scroll left
    elif (direction == 4):
      if (ScrollH - dots >= 0):
        for x in range (ScrollH-1,ScrollH-dots-1,-1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x


    #Set current room number
    self.CurrentRoomH,r = divmod(ScrollH,8)
    self.CurrentRoomV,r = divmod(ScrollV,8)
    self.DisplayH = ScrollH
    self.DisplayV = ScrollV
  
    time.sleep(speed)


    
  def ScrollMapDots8Way(self,direction,dots,speed):

    #we only want to scroll the number of dots, not the whole room
    #DisplayWindow has HV starting in upper left hand corner
    
    x = 0
    ScrollH = self.DisplayH
    ScrollV = self.DisplayV

    print("ScrollMapDots8Way - ScrollH ScrollV direction width",ScrollH,ScrollV, direction, self.width)
     
    #Scroll N
    if (direction == 1):
      
      if (ScrollV - dots >= 0):
      
        for x in range (ScrollV-1,ScrollV-dots-1,-1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
         
    #Scroll NE
    if (direction == 2):
      
      #Scroll up and right
      if (ScrollV - dots >= 0):
        for x in range (ScrollV-1,ScrollV-dots-1,-1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x

      if (ScrollH + 8 + dots  <= self.width):
        for x in range (ScrollH+1,ScrollH+dots+1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x
         
         
    #Scroll E
    if (direction == 3):
      if (ScrollH + 8 + dots  <= self.width):
        for x in range (ScrollH+1,ScrollH+dots+1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x

    #Scroll SE
    
    #Scroll right then down
    if (direction == 4):
      if (ScrollH + 8 + dots  <= self.width):
        for x in range (ScrollH+1,ScrollH+dots+1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x

      if (ScrollV + 8 + dots <= self.height):
        for x in range (ScrollV+1,ScrollV+dots+1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x

        
        
         
    #Scroll S
    if (direction == 5):
          
      if (ScrollV + 8 + dots <= self.height):
        for x in range (ScrollV+1,ScrollV+dots+1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
      
    
    #Scroll SW
    
    #Scroll down then left
    elif (direction == 6):
      if (ScrollH - dots >= 0):
        for x in range (ScrollH-1,ScrollH-dots-1,-1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x

      if (ScrollV + 8 + dots <= self.height):
        for x in range (ScrollV+1,ScrollV+dots+1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
        
        
    #Scroll W
    elif (direction == 7):
      if (ScrollH - dots >= 0):
        for x in range (ScrollH-1,ScrollH-dots-1,-1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x
      
      
    #Scroll NW
    #Scroll upd then left
    elif (direction == 8):
      if (ScrollV - dots >= 0):
        for x in range (ScrollV-1,ScrollV-dots-1,-1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x

      if (ScrollH - dots >= 0):
        for x in range (ScrollH-1,ScrollH-dots-1,-1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x

    
    time.sleep(0.5)
 


    #Set current room number
    self.CurrentRoomH,r = divmod(ScrollH,8)
    self.CurrentRoomV,r = divmod(ScrollV,8)
    self.DisplayH = ScrollH
    self.DisplayV = ScrollV
  





  

            
# ----------------------------
# -- BigWorld Object        --
# ----------------------------

#Not sure when I was going to use this

class BigWorld(object):
  def __init__(self,name,width,height,Map,Playfield,CurrentRoomH,CurrentRoomV,DisplayH, DisplayV):
    self.name      = name
    self.width     = width
    self.height    = height
    self.Map       = ([[]])
    self.Playfield = ([[]])
    self.CurrentRoomH = 0
    self.CurrentRoomV = 0
    self.DisplayH     = 0
    self.DisplayV     = 0
    
    
    self.Map = [[0 for i in xrange(width)] for i in xrange(height)]

    #Playfield is the physical size of the Unicorn Hat
    self.Playfield = [[0 for i in xrange(8)] for i in xrange(8)]

  def Display(self):
    if (self.alive == 1):
      unicorn.set_pixel(self.h,self.v,self.r,self.g,self.b)
      unicorn.show()
    

  def DisplayWindow(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64)    
    for V in range(0,8):
      for H in range (0,8):
        #Array is addressed[v][h] based on how the map is built
        #print("WO - Display Window - HV hv",H,V,h,v)
          
        SDColor = self.Map[V+v][H+h]
        r,g,b =  ColorList[SDColor] 
        #print("WO - Display Window - SDColor rgb",SDColor,r,g,b)
        unicorn.set_pixel(H,V,r,g,b)
        
  #WALL(h,v,r,g,b,alive,lives,name):


  
  def CopyMapToPlayfield(self):
    width  = self.width
    height = self.height
   
    x = 0
    y = 0

    
    
    #print ("WO - self.CurrentRoomHV:",h,v,"==============================================")
    for x in range(0,width):
      for y in range (0,height):
        #print ("WO - CopyMapToPlayfield - Map[",V+v,"][",H+h,"]",self.Map[V+v][H+h])
        if (self.Map[y][x] <> 0):
          SDColor = self.Map[y][x]
          r,g,b =  ColorList[SDColor]
          #print ("WO - CopyMapToPlayfield - V+v H+h (rgb)",V+v,H+h,"(",r,g,b,")")
          self.Playfield[H][V] = Wall(H,V,r,g,b,1,1,'Wall')

          
      
      
  def DisplayPlayfield(self,ShowFlash):
    #print ("WO - Display Playfield")
    for y in range (0,8):
      for x in range (0,8):
        #print("WO - DisplayPlayfield XY: ",x,y,self.Playfield[x][y].name)
        if (self.Playfield[x][y].name == 'Door' ):
           print ("WO - DisplayPlayfield - Door found locked:",self.Playfield[x][y].locked)
           DoNothing = "Nothing"
        if (self.Playfield[x][y].name <> 'empty' ):
          self.Playfield[x][y].Display()
          #print ("WO - DisplayPlayfield - self.Playfield[x][y].hv",self.Playfield[x][y].h,self.Playfield[x][y].v)
          if (ShowFlash == 1):
            FlashDot4(x,y,0.005)
          
          

  
    
  

  
  def ScrollMapRoom(self,direction,speed):

    ScrollH = 0
    SCrollV = 0

    #Scroll Up
    if (direction == 1):
      self.CurrentRoomV = self.CurrentRoomV - 1

      ScrollH = self.CurrentRoomH *8
      ScrollV = self.CurrentRoomV *8
          
      #We display the window 8 times, moving it one column every time
      #this gives a neat scrolling effect
      for x in range (ScrollV+8,ScrollV-1,-1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow ScrollH x:",ScrollH,x)
        self.DisplayWindow(ScrollH,x)
        unicorn.show()
        time.sleep(speed)
       

    
    #Scroll Down
    if (direction == 3):
      self.CurrentRoomV = self.CurrentRoomV + 1

      ScrollH = self.CurrentRoomH *8
      ScrollV = self.CurrentRoomV *8
          
      #We display the window 8 times, moving it one column every time
      #this gives a neat scrolling effect
      for x in range (ScrollV-8,ScrollV+1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow ScrollH x:",ScrollH,x)
        self.DisplayWindow(ScrollH,x)
        unicorn.show()
        time.sleep(speed)
      
    #Scroll right
    if (direction == 2):
      self.CurrentRoomH = self.CurrentRoomH + 1

      ScrollH = self.CurrentRoomH *8
      ScrollV = self.CurrentRoomV *8
          
      #We display the window 8 times, moving it one column every time
      #this gives a neat scrolling effect
      for x in range (ScrollH-8,ScrollH+1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
        self.DisplayWindow(x,ScrollV)
        unicorn.show()
        time.sleep(speed)
      
    
    #Scroll left
    elif (direction == 4):
      self.CurrentRoomH = self.CurrentRoomH -1
      ScrollH = self.CurrentRoomH *8
      ScrollV = self.CurrentRoomV *8
      #print("DZER - ScrollHV",ScrollH,ScrollV)
      for x in range (ScrollH+8,ScrollH-1,-1):
        #print ("DZER X:",x)
        #print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
        self.DisplayWindow(x,ScrollV)
        unicorn.show()
        time.sleep(speed)




  def ScrollMapDots(self,direction,dots,speed):

    #we only want to scroll the number of dots, not the whole room
    #DisplayWindow has HV starting in upper left hand corner
    
    x = 0
    ScrollH = self.DisplayH
    ScrollV = self.DisplayV

    #print("ScrollMapDots - ScrollH ScrollV direction width",ScrollH,ScrollV, direction, self.width)
     
    #Scroll Up
    if (direction == 1):
      
      if (ScrollV - dots >= 0):
      
        for x in range (ScrollV-1,ScrollV-dots-1,-1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
         

    
    #Scroll Down
    if (direction == 3):
          
      if (ScrollV + 8 + dots <= self.height):
        for x in range (ScrollV+1,ScrollV+dots+1):
          self.DisplayWindow(ScrollH,x)
        ScrollV = x
      
    #Scroll right
    if (direction == 2):
      if (ScrollH + 8 + dots  <= self.width):
        for x in range (ScrollH+1,ScrollH+dots+1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x
      
    
    #Scroll left
    elif (direction == 4):
      if (ScrollH - dots >= 0):
        for x in range (ScrollH-1,ScrollH-dots-1,-1):
          self.DisplayWindow(x,ScrollV)
        ScrollH = x


    #Set current room number
    self.CurrentRoomH,r = divmod(ScrollH,8)
    self.CurrentRoomV,r = divmod(ScrollV,8)
    self.DisplayH = ScrollH
    self.DisplayV = ScrollV
    


# -------------------------
# --      Cars           --
# -------------------------



class CarDot(object):
  
  def __init__(self,h,v,dh,dv,r,g,b,direction,scandirection,gear,currentgear,speed,alive,lives,name,score,exploding,radarrange,destination):
    self.h             = h         # location on playfield (e.g. 10,35)
    self.v             = v         # location on playfield (e.g. 10,35)
    self.dh            = dh        # location on display   (e.g. 3,4) 
    self.dv            = dv        # location on display   (e.g. 3,4) 
    self.r             = r
    self.g             = g
    self.b             = b
    self.direction     = direction      #direction of travel
    self.scandirection = scandirection  #direction of scanners, if equipped
    self.currentgear   = currentgear    
    self.speed         = speed
    self.alive         = 1
    self.lives         = 3
    self.name          = name
    self.score         = 0
    self.exploding     = 0
    self.radarrange    = 20
    self.destination   = ""
    
    #Hold speeds in a list, acting like gears
    self.gear = []
    self.gear.append(100)
    self.gear.append(50)
    self.gear.append(40)
    self.gear.append(30)
    self.gear.append(25)
    self.gear.append(15)


  def Display(self):
    if (self.alive == 1):
      unicorn.set_pixel(self.h,self.v,self.r,self.g,self.b)
     # print("display HV:", self.h,self.v)
      unicorn.show()

      
  def ShiftGear(self,direction):
    if (direction == 'down'):
      self.currentgear = self.currentgear -1
    else:
      self.currentgear = self.currentgear +1
    
    if (self.currentgear >= 5):
      self.currentgear = 5
    elif (self.currentgear <= 0):
      self.currentgear = 0 
    
  
      
  def Erase(self):
    unicorn.set_pixel(self.h,self.v,0,0,0)
    unicorn.show()



  def AdjustSpeed(self, increment):
    speed = self.speed
    speed = self.speed + increment
    if (speed > 1000):
      speed = 1000
    elif (speed < 1):
      speed = 1

    self.speed = speed
    return;

  
    
                   
      
      
ColonSprite = Sprite(
  3,
  5,
  RedR,
  RedG,
  RedB,
  [0,0,0,
   0,1,0,
   0,0,0,
   0,1,0,
   0,0,0]
)


WheelAnimatedSprite = AnimatedSprite(8,8,BlueR,BlueG,BlueB,5,[])
WheelAnimatedSprite.grid.append(
  [0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0]
)

WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0]
)


WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0]
)


WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0,
   0,0,1,1,1,0,0,0]
)

WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,1,1,1,0,0,0,
   0,1,1,1,1,1,0,0]
)

WheelAnimatedSprite.grid.append(
  [0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   0,0,0,0,0,0,0,0,
   1,1,1,1,1,1,1,0]
)


TestAnimatedSprite = AnimatedSprite(5,5,GreenR,GreenG,GreenB,3,[])
TestAnimatedSprite.grid.append(
  [0,0,1,0,0,
   0,0,1,0,0,
   0,0,1,0,0,
   0,0,1,0,0,
   0,0,1,0,0]
)
TestAnimatedSprite.grid.append(
  [0,0,0,0,1,
   0,0,0,1,0,
   0,0,1,0,0,
   0,1,0,0,0,
   1,0,0,0,0]
)
TestAnimatedSprite.grid.append(
  [0,0,0,0,0,
   0,0,0,0,0,
   1,1,1,1,1,
   0,0,0,0,0,
   0,0,0,0,0]
)
TestAnimatedSprite.grid.append(
  [1,0,0,0,0,
   0,1,0,0,0,
   0,0,1,0,0,
   0,0,0,1,0,
   0,0,0,0,1]
)


PacDotAnimatedSprite = AnimatedSprite(5,5,YellowR,YellowG,YellowB,7,[])
PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,0,0,
   1,1,0,0,0,
   1,1,1,0,0,
   0,1,1,1,0]
)
PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,0,0,
   1,1,0,0,0,
   1,1,1,0,0,
   0,1,1,1,0]
)
PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,0,0,
   1,1,0,0,0,
   1,1,1,0,0,
   0,1,1,1,0]
)

PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,1,1,
   1,1,0,0,0,
   1,1,1,1,1,
   0,1,1,1,0]
)


PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,1,1,
   1,1,1,1,1,
   1,1,1,1,1,
   0,1,1,1,0]
)
PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,1,1,0,
   1,1,1,0,0,
   1,1,1,1,0,
   0,1,1,1,0]
)

PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,0,0,0,
   1,0,0,0,0,
   1,1,0,0,0,
   0,1,1,1,0]
)

PacDotAnimatedSprite.grid.append(
  [0,1,1,1,0,
   1,1,0,0,0,
   1,0,0,0,0,
   1,1,0,0,0,
   0,1,1,1,0]
)

# Make left and right facing pacmen
PacRightAnimatedSprite = copy.deepcopy(PacDotAnimatedSprite)
PacLeftAnimatedSprite  = copy.deepcopy(PacDotAnimatedSprite)
PacLeftAnimatedSprite.HorizontalFlip()






PacSprite = Sprite(
  5,
  5,
  YellowR,
  YellowG,
  YellowB,
  [0,1,1,1,0,
   1,1,1,0,0,
   1,1,0,0,0,
   1,1,1,0,0,
   0,1,1,1,0]
)


RedGhostSprite = Sprite(
  5,
  5,
  RedR,
  RedG,
  RedB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)
    

OrangeGhostSprite = Sprite(
  5,
  5,
  OrangeR,
  OrangeG,
  OrangeB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)
    
BlueGhostSprite = Sprite(
  5,
  5,
  BlueR,
  BlueG,
  BlueB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)

PurpleGhostSprite = Sprite(
  5,
  5,
  PurpleR,
  PurpleG,
  PurpleB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)


IsaacSprite =([0,0,1,0,0,
               1,0,1,0,0,
               0,1,1,1,1,
               0,0,1,0,0,
               0,1,0,1,0,
               0,1,0,1,0])
 
DigitList = []
#0
DigitList.append([1,1,1, 
                  1,0,1,
                  1,0,1,
                  1,0,1,
                  1,1,1])
#1
DigitList.append([0,0,1, 
                  0,0,1,
                  0,0,1,
                  0,0,1,
                  0,0,1])
#2
DigitList.append([1,1,1, 
                  0,0,1,
                  1,1,1,
                  1,0,0,
                  1,1,1])
#3
DigitList.append([1,1,1, 
                  0,0,1,
                  0,1,1,
                  0,0,1,
                  1,1,1])
#4
DigitList.append([1,0,1, 
                  1,0,1,
                  1,1,1,
                  0,0,1,
                  0,0,1])
               
#5  
DigitList.append([1,1,1, 
                  1,0,0,
                  1,1,1,
                  0,0,1,
                  1,1,1])
#6
DigitList.append([1,1,1, 
                  1,0,0,
                  1,1,1,
                  1,0,1,
                  1,1,1])
#7
DigitList.append([1,1,1, 
                  0,0,1,
                  0,1,0,
                  1,0,0,
                  1,0,0])
#8  
DigitList.append([1,1,1, 
                  1,0,1,
                  1,1,1,
                  1,0,1,
                  1,1,1])
#9  
DigitList.append([1,1,1, 
                  1,0,1,
                  1,1,1,
                  0,0,1,
                  0,0,1])
                    

# List of Digit sprites
DigitSpriteList = [Sprite(3,5,RedR,RedG,RedB,DigitList[i]) for i in range(0,10)]


AlphaList = []
#A
AlphaList.append([0,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0])

#B
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0])
#c
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,0,
                  1,0,0,0,0,
                  1,0,0,0,0,
                  0,1,1,1,0])

#D
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,1,1,0,0])

#E
AlphaList.append([1,1,1,1,0,
                  1,0,0,0,0,
                  1,1,1,0,0,
                  1,0,0,0,0,
                  1,1,1,1,0])
                  
#F
AlphaList.append([1,1,1,1,0,
                  1,0,0,0,0,
                  1,1,1,0,0,
                  1,0,0,0,0,
                  1,0,0,0,0])

#G
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,0,
                  1,0,1,1,0,
                  1,0,0,1,0,
                  0,1,1,1,0])

#H
AlphaList.append([1,0,0,1,0,
                  1,0,0,1,0,
                  1,1,1,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0])
#I
AlphaList.append([0,1,1,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,1,1,1,0])
#J
AlphaList.append([0,1,1,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  1,0,1,0,0,
                  0,1,0,0,0])
                  
#K
AlphaList.append([1,0,0,1,0,
                  1,0,1,0,0,
                  1,1,0,0,0,
                  1,0,1,0,0,
                  1,0,0,1,0])
#L
AlphaList.append([0,1,0,0,0,
                  0,1,0,0,0,
                  0,1,0,0,0,
                  0,1,0,0,0,
                  0,1,1,1,0])

#M
AlphaList.append([1,0,0,0,1,
                  1,1,0,1,1,
                  1,0,1,0,1,
                  1,0,0,0,1,
                  1,0,0,0,1])

#N
AlphaList.append([1,0,0,0,1,
                  1,1,0,0,1,
                  1,0,1,0,1,
                  1,0,0,1,1,
                  1,0,0,0,1])
#O
AlphaList.append([0,1,1,0,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  0,1,1,0,0])
#P
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0,
                  1,0,0,0,0,
                  1,0,0,0,0])
#Q
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,1,
                  1,0,0,0,1,
                  1,0,0,1,0,
                  0,1,1,0,1])
#R 
AlphaList.append([1,1,1,0,0,
                  1,0,0,1,0,
                  1,1,1,0,0,
                  1,0,1,0,0,
                  1,0,0,1,0])
#S
AlphaList.append([0,1,1,1,0,
                  1,0,0,0,0,
                  0,1,1,0,0,
                  0,0,0,1,0,
                  1,1,1,0,0])
#T
AlphaList.append([0,1,1,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0])
#U
AlphaList.append([1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  1,0,0,1,0,
                  0,1,1,0,0])
#V
AlphaList.append([1,0,0,0,1,
                  1,0,0,0,1,
                  0,1,0,1,0,
                  0,1,0,1,0,
                  0,0,1,0,0])
#W
AlphaList.append([1,0,0,0,1,
                  1,0,0,0,1,
                  1,0,1,0,1,
                  0,1,0,1,0,
                  0,1,0,1,0])
#X
AlphaList.append([1,0,0,0,1,
                  0,1,0,1,0,
                  0,0,1,0,0,
                  0,1,0,1,0,
                  1,0,0,0,1])
#Y
AlphaList.append([0,1,0,1,0,
                  0,1,0,1,0,
                  0,0,1,0,0,
                  0,0,1,0,0,
                  0,0,1,0,0])
#Z
AlphaList.append([1,1,1,1,0,
                  0,0,0,1,0,
                  0,0,1,0,0,
                  0,1,0,0,0,
                  1,1,1,1,0])


                  
                  
# List of Alpha sprites
AlphaSpriteList = [Sprite(5,5,RedR,RedG,RedB,AlphaList[i]) for i in range(0,26)]



                  
                  
#space                  
SpaceSprite = Sprite(
  3,
  5,
  0,
  0,
  0,
  [0,0,0,
   0,0,0,
   0,0,0,
   0,0,0,
   0,0,0]
)

#Exclamation
ExclamationSprite = Sprite(
  3,
  5,
  0,
  0,
  0,
  [0,1,0,
   0,1,0,
   0,1,0,
   0,0,0,
   0,1,0]
)


#QuestionMark
QuestionMarkSprite = Sprite(
  5,
  5,
  0,
  0,
  0,
  [0,0,1,1,0,
   0,0,0,1,0,
   0,0,1,1,0,
   0,0,0,0,0,
   0,0,1,0,0]
)


#PoundSignSprite
PoundSignSprite = Sprite(
  5,
  5,
  0,
  0,
  0,
  [0,1,0,1,0,
   1,1,1,1,1,
   0,1,0,1,0,
   1,1,1,1,1,
   0,1,0,1,0]
)



#(h,v,name,width,height,frames,currentframe,framerate,grid):


FrogSprite = ColorAnimatedSprite(h=0, v=0, name="Frog", width=8, height=8, frames=1, currentframe=0,framerate=1,grid=[])
FrogSprite.grid.append(
  [
   0, 9, 9, 0, 0, 9, 9, 0,
   0, 9, 9, 9, 9, 9, 9, 0,
   9, 9, 0, 2, 9, 0, 2, 0,
   9, 9, 9, 9, 9, 9, 9, 0,
   9,17,17,17,17,17,17,17,
  13, 9,17,17,17,17,17, 0,
  13, 9, 9, 9, 9, 9, 0, 0,
  13,13,13,13,13,13, 0, 0,
   ]
)



RedGhostSprite = Sprite(
  5,
  5,
  RedR,
  RedG,
  RedB,
  [0,1,1,1,0,
   1,1,1,1,1,
   1,0,1,0,1,
   1,1,1,1,1,
   1,0,1,0,1]
)




  


ThreeGhostPacSprite = ColorAnimatedSprite(h=0, v=0, name="ThreeGhost", width=24, height=5, frames=6, currentframe=0,framerate=1,grid=[])

ThreeGhostPacSprite.grid.append(
  [
    0,30,30,30, 0, 0, 0,17,17,17, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0,22,22,22,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,22,0,0,
   30, 1,30, 1,30, 0,17, 1,17, 1,17, 0, 6, 1, 6, 1, 6, 0, 0, 22,22,0,0,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,22,0,0,
   30, 0,30, 0,30, 0,17, 0,17, 0,17, 0, 6, 0, 6, 0, 6, 0, 0, 0,22,22,22,0
  
   ]
)


ThreeGhostPacSprite.grid.append(
  [
    0,30,30,30, 0, 0, 0,17,17,17, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0,22,22,22,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,22,22,22,
   30, 1,30, 1,30, 0,17, 1,17, 1,17, 0, 6, 1, 6, 1, 6, 0, 0, 22,22,0,0,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,22,22,22,
   30, 0,30, 0,30, 0,17, 0,17, 0,17, 0, 6, 0, 6, 0, 6, 0, 0, 0,22,22,22,0
  
   ]
)



ThreeGhostPacSprite.grid.append(
  [
    0,30,30,30, 0, 0, 0,17,17,17, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0,22,22,22,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,22,22,22,
   30, 1,30, 1,30, 0,17, 1,17, 1,17, 0, 6, 1, 6, 1, 6, 0, 0, 22,22,22,22,22,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,22,22,22,
   30, 0,30, 0,30, 0,17, 0,17, 0,17, 0, 6, 0, 6, 0, 6, 0, 0, 0,22,22,22,0
  
   ]
)

ThreeGhostPacSprite.grid.append(
  [
    0,30,30,30, 0, 0, 0,17,17,17, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0,22,22,22,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,22,22,0,
   30, 1,30, 1,30, 0,17, 1,17, 1,17, 0, 6, 1, 6, 1, 6, 0, 0, 22,22,22,0,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,22,22,0,
   30, 0,30, 0,30, 0,17, 0,17, 0,17, 0, 6, 0, 6, 0, 6, 0, 0, 0,22,22,22,0
  
   ]
)

 
ThreeGhostPacSprite.grid.append(
  [
    0,30,30,30, 0, 0, 0,17,17,17, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0,22,22,22,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,0,0,0,
   30, 1,30, 1,30, 0,17, 1,17, 1,17, 0, 6, 1, 6, 1, 6, 0, 0, 22,0,0,0,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,0,0,0,
   30, 0,30, 0,30, 0,17, 0,17, 0,17, 0, 6, 0, 6, 0, 6, 0, 0, 0,22,22,22,0
  
   ]
)

ThreeGhostPacSprite.grid.append(
  [
    0,30,30,30, 0, 0, 0,17,17,17, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0,22,22,22,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,0,0,0,
   30, 1,30, 1,30, 0,17, 1,17, 1,17, 0, 6, 1, 6, 1, 6, 0, 0, 22,0,0,0,0,
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 0, 22,22,0,0,0,
   30, 0,30, 0,30, 0,17, 0,17, 0,17, 0, 6, 0, 6, 0, 6, 0, 0, 0,22,22,22,0
  
   ]
)




ThreeBlueGhostPacSprite = ColorAnimatedSprite(h=0, v=0, name="ThreeGhost", width=24, height=5, frames=6, currentframe=0,framerate=1,grid=[])

ThreeBlueGhostPacSprite.grid.append(
  [
    0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,22,22,22,0,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,22,22,22,
   14, 2,14, 1,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,22,22,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,22,22,22,
   14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,22,22,22,0
  
   ]
)


ThreeBlueGhostPacSprite.grid.append(
  [
    0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,22,22,22,0,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 22,22,22,22,22,
   14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,22,22,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 22,22,22,22,22,
   14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,22,22,22,0
  
   ]
)



ThreeBlueGhostPacSprite.grid.append(
  [
    0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,22,22,22,0,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 22,22,22,22,22,
   14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 22,22,22,22,22,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 22,22,22,22,22,
   14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,22,22,22,0
  
   ]
)

ThreeBlueGhostPacSprite.grid.append(
  [
    0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,22,22,22,0,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,22,22,22,22,
   14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,22,22,22,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,22,22,22,22,
   14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,22,22,22,0
  
   ]
)

 
ThreeBlueGhostPacSprite.grid.append(
  [
    0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,22,22,22,0,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,22,22,
   14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,0,22,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,22,22,
   14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,22,22,22,0
  
   ]
)

ThreeBlueGhostPacSprite.grid.append(
  [
    0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0, 0,22,22,22,0,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,22,22,
   14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 0, 0,0,0,0,22,
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 0, 0,0,0,22,22,
   14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0, 0, 0,22,22,22,0
  
   ]
)






ThreeGhostSprite = ColorAnimatedSprite(h=0, v=0, name="ThreeGhost", width=18, height=5, frames=1, currentframe=0,framerate=1,grid=[])
ThreeGhostSprite.grid.append(
  [
    0,30,30,30, 0, 0, 0,17,17,17, 0, 0, 0, 6, 6, 6, 0, 0, 
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 
   30, 1,30, 1,30, 0,17, 1,17, 1,17, 0, 6, 1, 6, 1, 6, 0, 
   30,30,30,30,30, 0,17,17,17,17,17, 0, 6, 6, 6, 6, 6, 0, 
   30, 0,30, 0,30, 0,17, 0,17, 0,17, 0, 6, 0, 6, 0, 6, 0 
  
   ]
)


ThreeBlueGhostSprite = ColorAnimatedSprite(h=0, v=0, name="ThreeBlueGhost", width=18, height=5, frames=1, currentframe=0,framerate=1,grid=[])
ThreeBlueGhostSprite.grid.append(
  [
    0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 0,14,14,14, 0, 0, 
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 
   14, 2,14, 2,14, 0,14, 2,14, 2,14, 0,14, 2,14, 2,14, 0, 
   14,14,14,14,14, 0,14,14,14,14,14, 0,14,14,14,14,14, 0, 
   14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0,14, 0 
  
   ]
)




PlayerShipExplosion = ColorAnimatedSprite(h=0, v=0, name="PlayerShipExplosion", width=5, height=5, frames=14, currentframe=0,framerate=1,grid=[])
PlayerShipExplosion.grid.append(
  [0,0,0,0,0,
   0,0,0,0,0,
   0,0,17,0,0,
   0,0,0,0,0,
   0,0,0,0,0
   ]
)

PlayerShipExplosion.grid.append(
   [0,0,0,0,0,
    0, 0,17, 0,0,
    0,17,18,17,0,
    0, 0,17, 0,0,
    0,0,0,0,0
   ]
)
  
PlayerShipExplosion.grid.append(
   [ 0, 0,17, 0, 0,
     0,18,18,18, 0,
    17,18,19,18,17,
     0,18,18,18, 0,
     0, 0,17, 0,0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0,18,18,18, 0,
    18,19,19,19,18,
    18,18,20,19,18,
    18,19,19,19,18,
     0,18,18,18, 0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0,19,19,19, 0,
    19,20,20,20,19,
    19,20,20,20,19,
    19,20,20,20,19,
     0,19,19,19, 0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0,20,20,20, 0,
    20,20,20,20,20,
    20,20,20,20,20,
    20,20,20,20,20,
     0,20,20,20, 0
   ]


)
PlayerShipExplosion.grid.append(
   [00,20,20,20,00,
    20,20,20,20,20,
    20,20, 8,20,20,
    20,20,20,20,20,
    00,20,20,20,00
   ]
)
PlayerShipExplosion.grid.append(
   [00,20,20,20,00,
    20,20, 8,20,20,
    20, 8, 7, 8,20,
    20,20, 8,20,20,
    00,20,20,20,00
   ]
)  

PlayerShipExplosion.grid.append(
   [00,20, 8,20,00,
    20, 8, 7, 8,20,
     8, 7, 6, 7, 8,
    20, 8, 7, 8,20,
    00,20, 8,20,00
   ]
)
PlayerShipExplosion.grid.append(
   [00, 8,07, 8,00,
     8,07,06,07, 8,
    07,06, 5,06, 7,
     8,07,06,07, 8,
    00, 8,07, 8,00
   ]
)
PlayerShipExplosion.grid.append(
   [00,07,06,07,00,
    07,06, 0,06,07,
    06, 5, 0, 5,06,
    07,06, 0,06,07,
    00,07,06,07,00
   ]
)
PlayerShipExplosion.grid.append(
   [ 0, 6, 5, 6, 0,
     6, 5, 0, 5, 6,
     5, 0, 0, 0, 5,
     6, 5, 0, 5, 6,
     0, 6, 5, 6, 0
   ]
)
PlayerShipExplosion.grid.append(
   [ 0, 5, 0, 5, 0,
     5, 0, 0, 0, 5,
     0, 0, 0, 0, 0,
     5, 0, 0, 0, 5,
     0, 5, 0, 5, 0
   ]
)  
PlayerShipExplosion.grid.append(
   [00,00,00,00,00,
    00,00,00,00,00,
    00,00,00,00,00,
    00,00,00,00,00,
    00,00,00,00,00
   ]
   
   
   
   
)


DropShip = ColorAnimatedSprite(h=0, v=0, name="DropShip", width=5, height=6, frames=2, currentframe=0,framerate=1,grid=[])
DropShip.grid.append(
  [
    0, 0,15, 0, 0,
    0, 0,15, 0, 0,
    0,14,15,14, 0,
    0,14, 7,14, 0,
    0, 0, 6, 0, 0,
    0, 0, 5, 0, 0
  ]
)

DropShip.grid.append(
  [
    0, 0,15, 0, 0,
    0, 0,15, 0, 0,
    0,14,15,14, 0,
    0,14, 6,14, 0,
    0, 0, 5, 0, 0,
    0, 0, 5, 0, 0
  ]
)


SpaceInvader = ColorAnimatedSprite(h=0, v=0, name="SpaceInvader", width=11, height=8, frames=2, currentframe=0,framerate=1,grid=[])
SpaceInvader.grid.append(
  [
    0, 0, 0, 9, 0, 0, 0, 9, 0, 0, 0,
    0, 0, 9, 9, 9, 9, 9, 9, 9, 9, 0,
    0, 9, 9,11, 9, 9, 9,11, 9, 9, 0,
    9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
    9, 0, 9, 9, 9, 9, 9, 9, 9, 0, 9,
    9, 0, 9, 0, 0, 0, 0, 0, 9, 0, 9,
    0, 0, 0, 9, 0, 0, 0, 9, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  ]
)
SpaceInvader.grid.append(
  [
    0, 0, 0, 0, 9, 0, 9, 0, 0, 0, 0,
    0, 0, 9, 9, 9, 9, 9, 9, 9, 9, 0,
    0, 9, 9,11, 9, 9, 9,11, 9, 9, 0,
    9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
    9, 0, 9, 9, 9, 9, 9, 9, 9, 0, 9,
    9, 0, 9, 0, 0, 0, 0, 0, 9, 0, 9,
    0, 0, 9, 0, 0, 0, 0, 0, 9, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
  ]
)



TinyInvader = ColorAnimatedSprite(h=0, v=0, name="TinyInvader", width=5, height=6, frames=4, currentframe=0,framerate=1,grid=[])
TinyInvader.grid.append(
  [
   0, 0, 8, 0, 0,
   0, 9, 9, 9, 0,
   9,11, 9,11, 9,
   9, 9, 9, 9, 9,
   0, 9, 0, 9, 0,
   9, 0, 0, 0, 9
  ]
)
TinyInvader.grid.append(
  [
   0, 0, 8, 0, 0,
   0, 9, 9, 9, 0,
   9,11, 9,11, 9,
   9, 9, 9, 9, 9,
   0, 9, 0, 9, 0,
   9, 0, 0, 0, 9
  ]
)
TinyInvader.grid.append(
  [
   0, 0,16, 0, 0,
   0, 9, 9, 9, 0,
   9,11, 9,11, 9,
   9, 9, 9, 9, 9,
   0, 9, 0, 9, 0,
   9, 0, 0, 0, 9
  ]
)

TinyInvader.grid.append(
  [
   0, 0,16, 0, 0,
   0, 9, 9, 9, 0,
   9,11, 9,11, 9,
   9, 9, 9, 9, 9,
   0, 9, 0, 9, 0,
   0, 9, 0, 9, 0
  ]
)




SmallInvader = ColorAnimatedSprite(h=0, v=0, name="SmallInvader", width=7, height=6, frames=2, currentframe=0,framerate=1,grid=[])
SmallInvader.grid.append(
  [
    0, 0, 9, 9, 9, 0, 0,
    0, 9, 9, 9, 9, 9, 0,
    9,10,11, 9,11,10, 9,
    9, 9, 9, 9, 9, 9, 9,
    9, 0, 9, 0, 9, 0, 9,
    0, 9, 0, 9, 0, 9, 0
  ]
)
SmallInvader.grid.append(
  [
    0, 0, 9, 9, 9, 0, 0,
    0, 9, 9, 9, 9, 9, 0,
    9,10,11, 9,11,10, 9,
    9, 9, 9, 9, 9, 9, 9,
    9, 0, 9, 0, 9, 0, 9,
    9, 0, 9, 0, 9, 0, 9
  ]
)



LittleShipFlying = ColorAnimatedSprite(h=0, v=0, name="LittleShips", width=16, height=8, frames=2, currentframe=0,framerate=1,grid=[])

LittleShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 5, 6, 7, 8, 5,14,14,14, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 5,14,14,14,
    0, 0, 0, 0, 0,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 6, 7, 8, 5,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    
   ]
)

LittleShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 5, 6, 7, 8, 5,14,14,14, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 5,14,14,14,
    0, 0, 0, 0, 0,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 6, 7, 8, 5,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    
   ]
)


                  
BigShipFlying = ColorAnimatedSprite(h=0, v=0, name="PlayerShipExplosion", width=34, height=8, frames=6, currentframe=0,framerate=1,grid=[])

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 6, 5, 5, 5,14,14,14,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 7,21, 6, 1, 2,17,14,14, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0, 7,21, 6, 1, 2,17,14,14,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,14,14,14,
    0, 0, 0, 0, 0, 6, 6, 5, 5, 1,14,13,13,13,13,13, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 7, 7, 6, 6,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,21, 6, 7, 2,18,17,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0,21, 6, 7, 2,18,17,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5,14,14,14,
    0, 0, 0, 0, 0, 7, 7, 6, 6, 1,14,15,13,13,13,13, 0, 5, 5, 5, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 6, 5, 5, 5,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 7,21, 6, 1,17,18,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0, 7,21, 6, 1,17,18,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,14,14,14,
    0, 0, 0, 0, 0, 6, 6, 5, 5, 1,14,15,13,13,13,13, 0, 0, 0, 0, 0, 5, 5, 5, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 7, 7, 6, 6,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,21, 6, 7, 2,18,17,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0,21, 6, 7, 2,18,17,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5,14,14,14,
    0, 0, 0, 0, 0, 7, 7, 6, 6, 1,14,15,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 7, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 6, 5, 5, 5,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 7,21, 6, 1,18,17,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0, 7,21, 6, 1,18,17,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,14,14,14,
    0, 0, 0, 0, 0, 6, 6, 5, 5, 1,14,15,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5, 7, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)

BigShipFlying.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0,15,15,15,15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 7, 7, 6, 6,14,14,15,14,14,16,14,16,14,14,14,14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,21, 6, 7, 2, 1,17,14,15, 9,14, 9,14,14,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,15, 0, 0,
    0, 0, 0, 0,21, 6, 7, 2, 1,17,14,15,14, 9,14, 9,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5,14,14,14,
    0, 0, 0, 0, 0, 7, 7, 6, 6, 1,14,15,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 5,
    0, 0, 0, 0, 0, 0, 0, 5,13,13,13,13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   ]
)
 

#This will hold HH:MM
BigSprite = Sprite(16,5,GreenR,GreenG,GreenB,
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
)


#DotZerk Human Death
HumanExplosion = ColorAnimatedSprite(h=0, v=0, name="HumanExplosion", width=3, height=3, frames=6, currentframe=0,framerate=1,grid=[])
HumanExplosion.grid.append(
  [
    0, 0, 0,
    0, 5, 0,
    0, 0, 0
  ]
)
HumanExplosion.grid.append(
  [
    0, 5, 0,
    5, 6, 5,
    0, 5, 0
  ]
)
HumanExplosion.grid.append(
  [
    0, 6, 0,
    6, 7, 6,
    0, 6, 0
  ]
)
HumanExplosion.grid.append(
  [
    0, 7, 0,
    7, 8, 7,
    0, 7, 0
  ]
)
HumanExplosion.grid.append(
  [
    0, 8, 0,
    8, 0, 8,
    0, 8, 0
  ]
)

HumanExplosion.grid.append(
  [
    0, 0, 0,
    0, 0, 0,
    0, 0, 0
  ]
)


DotZerkRobot = ColorAnimatedSprite(h=0, v=0, name="Robot", width=8, height=8, frames=9, currentframe=0,framerate=1,grid=[])
DotZerkRobot.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6, 8, 1, 6, 6, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 0, 6, 6, 0

  ]
)
DotZerkRobot.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6, 1, 8, 6, 6, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 0, 6, 6, 0

  ]
)
DotZerkRobot.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6, 6, 1, 8, 6, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 0, 6, 6, 0

  ]
)
DotZerkRobot.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 1, 8, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 0, 6, 6, 0

  ]
)


DotZerkRobot.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 1, 8, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 0, 6, 6, 0

  ]
)

DotZerkRobot.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6, 6, 6, 8, 1, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 0, 6, 6, 0

  ]
)


DotZerkRobot.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6, 6, 8, 1, 6, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 0, 6, 6, 0

  ]
)


DotZerkRobot.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6, 8, 1, 6, 6, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 0, 6, 6, 0

  ]
)

DotZerkRobot.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6, 8, 1, 6, 6, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 0, 6, 6, 0

  ]
)




DotZerkRobotWalking = ColorAnimatedSprite(h=0, v=0, name="Robot", width=8, height=8, frames=2, currentframe=0,framerate=1,grid=[])
DotZerkRobotWalking.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6,14,14, 6, 6, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 0, 6, 0, 0, 6, 0, 0,
    0, 6, 6, 0, 6, 6, 0, 0

  ]
)
DotZerkRobotWalking.grid.append(
  [
    0, 0, 6, 6, 6, 6, 0, 0,
    0, 6,14,14, 6, 6, 6, 0,
    6, 6, 6, 6, 6, 6, 6, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    6, 0, 6, 6, 6, 6, 0, 6,
    0, 0, 0, 6, 6, 0, 0, 0,
    0, 0, 0, 6, 6, 0, 0, 0,
    0, 0, 6, 6, 6, 0, 0, 0

  ]
)


DotZerkRobotWalkingSmall = ColorAnimatedSprite(h=0, v=0, name="Robot", width=7, height=5, frames=4, currentframe=0,framerate=1,grid=[])
DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0,10,10,10,10, 0,
   0,10, 7, 7,10,10,10,
   0,10,10,10,10,10,10,
   0,10, 0, 0, 0, 0,10,
  10,10, 0, 0, 0,10,10,

  ]
)
DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0,10,10,10,10, 0,
   0,10, 7, 7,10,10,10,
   0,10,10,10,10,10,10,
   0, 0,10, 0, 0,10, 0,
   0,10,10, 0,10,10, 0,

  ]
)

DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0,10,10,10,10, 0,
   0,10, 7, 7,10,10,10,
   0,10,10,10,10,10,10,
   0, 0, 0,10,10, 0, 0,
   0, 0,10,10,10, 0, 0,

  ]
)
DotZerkRobotWalkingSmall.grid.append(
  [
   0, 0,10,10,10,10, 0,
   0,10, 7, 7,10,10,10,
   0,10,10,10,10,10,10,
   0, 0,10, 0, 0,10, 0,
   0,10,10, 0,10,10, 0,

  ]
)






ChickenRunning = ColorAnimatedSprite(h=0, v=0, name="Chicken", width=8, height=8, frames=4, currentframe=0,framerate=1,grid=[])
ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0,22, 0,21, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)

ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)

ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0,21, 0,22, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)


ChickenRunning.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0

  ]
)







WormChasingChicken = ColorAnimatedSprite(h=0, v=0, name="Chicken", width=24, height=8, frames=4, currentframe=0,framerate=1,grid=[])
WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17,17, 0, 0, 0, 0,
    0, 0, 0,22, 0,21, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17,17, 0, 0, 0, 0,

  ]
)

WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17, 0, 0,17,17, 0, 0, 0, 0,

  ]
)

WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0,17,17, 0, 0, 0, 0,
    0, 0, 0,21, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0,17,17, 0, 0, 0, 0

  ]
)


WormChasingChicken.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,17, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 5, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,17,17, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17,17,17,17,17, 0, 0, 0, 0,
    0, 0, 0, 0,22, 0, 0, 0, 0, 0, 0, 0, 0,17,17,17, 0, 0,17,17, 0, 0, 0, 0

  ]
)












ChickenChasingWorm = ColorAnimatedSprite(h=0, v=0, name="Chicken", width=16, height=8, frames=4, currentframe=0,framerate=1,grid=[])
ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
   05,17,05,17,17, 0, 0, 0, 0, 0, 0,22, 0,21, 0, 0

  ]
)

ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0,05, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    0,05,17, 0,17, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0

  ]
)

ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
   05,17,05,17,17, 0, 0, 0, 0, 0, 0,21, 0,22, 0, 0

  ]
)


ChickenChasingWorm.grid.append(
  [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,17, 2, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 0, 2, 2, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0,
    0, 0, 0,05, 0, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0,
    0,05,17, 0,17, 0, 0, 0, 0, 0, 0, 0,22, 0, 0, 0

  ]
)




#----------------------------
#-- SpaceDot               --
#----------------------------

#Custom Colors because we will be running at full brightness

#HighRed
SDHighRedR = 255
SDHighRedG = 0
SDHighRedB = 0

#MedRed
SDMedRedR = 175
SDMedRedG = 0
SDMedRedB = 0

#LowRed
SDLowRedR = 100
SDLowRedG = 0
SDLowRedB = 0

#DarkRed
SDDarkRedR = 45
SDDarkRedG = 0
SDDarkRedB = 0


#HighOrange
SDHighOrangeR = 255
SDHighOrangeG = 128
SDHighOrangeB = 0

#MedOrange
SDMedOrangeR = 200
SDMedOrangeG = 100
SDMedOrangeB = 0

#LowOrange
SDLowOrangeR = 155
SDLowOrangeG = 75
SDLowOrangeB = 0

#DarkOrange
SDDarkOrangeR = 100
SDDarkOrangeG = 45
SDDarkOrangeB = 0



#SDHighPurple
SDHighPurpleR = 230
SDHighPurpleG = 0
SDHighPurpleB = 255

#MedPurple
SDMedPurpleR = 105
SDMedPurpleG = 0
SDMedPurpleB = 155

#SDLowPurple
SDLowPurpleR = 75
SDLowPurpleG = 0
SDLowPurpleB = 120


#SDDarkPurple
SDDarkPurpleR = 45
SDDarkPurpleG = 0
SDDarkPurpleB = 45



#HighGreen
SDHighGreenR = 0
SDHighGreenG = 255
SDHighGreenB = 0

#MedGreen
SDMedGreenR = 0
SDMedGreenG = 200
SDMedGreenB = 0

#LowGreen
SDLowGreenR = 0
SDLowGreenG = 100
SDLowGreenB = 0

#DarkGreen
SDDarkGreenR = 0
SDDarkGreenG = 45
SDDarkGreenB = 0


#HighBlue
SDHighBlueR = 0
SDHighBlueG = 0
SDHighBlueB = 255


#MedBlue
SDMedBlueR = 0
SDMedBlueG = 0
SDMedBlueB = 175

#LowBlue
SDLowBlueR = 0
SDLowBlueG = 0
SDLowBlueB = 100

#DarkBlue
SDDarkBlueR = 0
SDDarkBlueG = 0
SDDarkBlueB = 45


#WhiteMax
SDMaxWhiteR = 255
SDMaxWhiteG = 255
SDMaxWhiteB = 255

#WhiteHigh
SDHighWhiteR = 200
SDHighWhiteG = 200
SDHighWhiteB = 200

#WhiteMed
SDMedWhiteR = 150
SDMedWhiteG = 150
SDMedWhiteB = 150

#WhiteLow
SDLowWhiteR = 100
SDLowWhiteG = 100
SDLowWhiteB = 100

#WhiteDark
SDDarkWhiteR = 45
SDDarkWhiteG = 45
SDDarkWhiteB = 45



#YellowMax
SDMaxYellowR = 255
SDMaxYellowG = 255
SDMaxYellowB = 0


#YellowHigh
SDHighYellowR = 200
SDHighYellowG = 200
SDHighYellowB = 0

#YellowMed
SDMedYellowR = 150
SDMedYellowG = 150
SDMedYellowB = 0

#YellowLow
SDLowYellowR = 100
SDLowYellowG = 100
SDLowYellowB = 0


#YellowDark
SDDarkYellowR = 55
SDDarkYellowG = 55
SDDarkYellowB = 0


#Pink
SDMaxPinkR = 155
SDMaxPinkG = 0
SDMaxPinkB = 130

SDHighPinkR = 130
SDHighPinkG = 0
SDHighPinkB = 105

SDMedPinkR = 100
SDMedPinkG = 0
SDMedPinkB = 75

SDLowPinkR = 75
SDLowPinkG = 0
SDLowPinkB = 50

SDDarkPinkR = 45
SDDarkPinkG = 0
SDDarkPinkB = 50




ColorList = []
ColorList.append((0,0,0))
# 1 2 3 4
ColorList.append((SDDarkWhiteR,SDDarkWhiteG,SDDarkWhiteB))
ColorList.append((SDLowWhiteR,SDLowWhiteG,SDLowWhiteB))
ColorList.append((SDMedWhiteR,SDMedWhiteG,SDMedWhiteB))
ColorList.append((SDHighWhiteR,SDHighWhiteG,SDHighWhiteB))

# 5 6 7 8
ColorList.append((SDDarkRedR,SDDarkRedG,SDDarkRedB))
ColorList.append((SDLowRedR,SDLowRedG,SDLowRedB))
ColorList.append((SDMedRedR,SDMedRedG,SDMedRedB))
ColorList.append((SDHighRedR,SDHighRedG,SDHighRedB))

# 9 10 11 12
ColorList.append((SDDarkGreenR,SDDarkGreenG,SDDarkGreenB))
ColorList.append((SDLowGreenR,SDLowGreenG,SDLowGreenB))
ColorList.append((SDMedGreenR,SDMedGreenG,SDMedGreenB))
ColorList.append((SDHighGreenR,SDHighGreenG,SDHighGreenB))

# 13 14 15 16
ColorList.append((SDDarkBlueR,SDDarkBlueG,SDDarkBlueB))
ColorList.append((SDLowBlueR,SDLowBlueG,SDLowBlueB))
ColorList.append((SDMedBlueR,SDMedBlueG,SDMedBlueB))
ColorList.append((SDHighBlueR,SDHighBlueG,SDHighBlueB))

# 17 18 19 20
ColorList.append((SDDarkOrangeR,SDDarkOrangeG,SDDarkOrangeB))
ColorList.append((SDLowOrangeR,SDLowOrangeG,SDLowOrangeB))
ColorList.append((SDMedOrangeR,SDMedOrangeG,SDMedOrangeB))
ColorList.append((SDHighOrangeR,SDHighOrangeG,SDHighOrangeB))

# 21 22 23 24
ColorList.append((SDDarkYellowR,SDDarkYellowG,SDDarkYellowB))
ColorList.append((SDLowYellowR,SDLowYellowG,SDLowYellowB))
ColorList.append((SDMedYellowR,SDMedYellowG,SDMedYellowB))
ColorList.append((SDHighYellowR,SDHighYellowG,SDHighYellowB))

# 25 26 27 28
ColorList.append((SDDarkPurpleR,SDDarkPurpleG,SDDarkPurpleB))
ColorList.append((SDLowPurpleR,SDLowPurpleG,SDLowPurpleB))
ColorList.append((SDMedPurpleR,SDMedPurpleG,SDMedPurpleB))
ColorList.append((SDHighPurpleR,SDHighPurpleG,SDHighPurpleB))

# 29 30 31 32 33
ColorList.append((SDDarkPinkR,SDDarkPinkG,SDDarkPinkB))
ColorList.append((SDLowPinkR,SDLowPinkG,SDLowPinkB))
ColorList.append((SDMedPinkR,SDMedPinkG,SDMedPinkB))
ColorList.append((SDHighPinkR,SDHighPinkG,SDHighPinkB))
ColorList.append((SDMaxPinkR,SDMaxPinkG,SDMaxPinkB))


#ColorList.append((SDDarkR,SDDarkG,SDDarkB))
#ColorList.append((SDLowR,SDLowG,SDLowB))
#ColorList.append((SDMedR,SDMedG,SDMedB))
#ColorList.append((SDHighR,SDHighG,SDHighB))



PlayerShipR = SDLowBlueR
PlayerShipG = SDLowBlueG
PlayerShipB = SDLowBlueB
PlayerMissileR = SDDarkWhiteR
PlayerMissileG = SDDarkWhiteG
PlayerMissileB = SDDarkWhiteB


#def __init__(h,v,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding):
Empty         = Ship(-1,-1,0,0,0,0,1,0,0,0,'empty',0,0)
UFOMissile1   = Ship(-1,-1,PlayerMissileR,PlayerMissileG,PlayerMissileB,3,3,15,0,0,'UFOMissile',0,0)
UFOMissile2   = Ship(-1,-1,PlayerMissileR,PlayerMissileG,PlayerMissileB,3,3,20,0,0,'UFOMissile',0,0)
UFOMissile3   = Ship(-1,-1,PlayerMissileR,PlayerMissileG,PlayerMissileB,3,3,25,0,0,'UFOMissile',0,0)
PlayerMissile1 = Ship(-0,-0,PlayerMissileR,PlayerMissileG,PlayerMissileB,1,1,8,0,0,'PlayerMissile', 0,0)
PlayerMissile2 = Ship(-0,-0,PlayerMissileR,PlayerMissileG,PlayerMissileB,1,1,5,0,0,'PlayerMissile', 0,0)



# BomberShip records the location and status
# BomberSprite is the color animated sprite of the ship

#(self,h,v,name,width,height,frames,currentframe,framerate,grid):
BomberSprite = ColorAnimatedSprite(h=0, v=0, name="BomberShip", width=3, height=1, frames=4, currentframe=0,framerate=1,grid=[])
BomberSprite.grid.append(
  [ 9, 9, 9 ]
)
BomberSprite.grid.append(
  [ 9,10, 9 ]
)
BomberSprite.grid.append(
  [ 9,11, 9 ]
)
BomberSprite.grid.append(
  [ 9,10, 9 ]
)

BomberShip = AnimatedShip(h=0,v=0,direction=2,scandirection=3,speed=25,animationspeed=5,alive=0,lives=3,name="BomberShip",score=0,exploding=0) 




#----------------------------
#-- Dot Invaders           --
#----------------------------

ArmadaHeight = 3
ArmadaWidth  = 6



#----------------------------
#-- DotZerk                --
#----------------------------




    
#------------------------------------------------------------------------------
# Functions                                                                  --
#------------------------------------------------------------------------------


def random_message(MessageFile):
  lines = open(MessageFile).read().splitlines()
  return random.choice(lines)

    


def SaveConfigData():
  
   
  print ("--Save Config Data--")
  #we save the time to file as 5 minutes in future, which allows us to unplug the device temporarily
  #the time might be off, but it might be good enough
  
  AdjustedTime = (datetime.now() + timedelta(minutes=5)).strftime('%I:%M:%S %p')

  
  if (os.path.exists(ConfigFileName)):
    print ("Config file (",ConfigFileName,"): already exists")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)
  else:
    print ("Config file not found.  Creating new one.")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)
    ConfigFile.add_section('main')

    
  ConfigFile.set('main', 'CurrentTime', AdjustedTime)
  print ("Time to save: ",AdjustedTime)

  print ("Writing configuration file")
  with open(ConfigFileName, 'w') as f:
    ConfigFile.write(f)
  
  

def SaveConfigDataCurrentTime():
  
  print ("--Save Config Data Current Time--")
  #we save the time to file as 5 minutes in future, which allows us to unplug the device temporarily
  #the time might be off, but it might be good enough
  
  AdjustedTime = (datetime.now() + timedelta(minutes=5)).strftime('%I:%M:%S %p')
  
  if (os.path.exists(ConfigFileName)):
    print ("Config file (",ConfigFileName,"): already exists")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)
  else:
    print ("Config file not found.  Creating new one.")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)
    ConfigFile.add_section('main')


  #Set Current Time (actually 5 mins in future)
  ConfigFile.set('main', 'CurrentTime', AdjustedTime)
  print ("Time to save: ",AdjustedTime)

  print ("Writing configuration file")
  with open(ConfigFileName, 'w') as f:
    ConfigFile.write(f)

    
def LoadConfigData():

  print ("--Load Config Data--")
  
  if (os.path.exists(ConfigFileName)):
    print ("Config file (",ConfigFileName,"): already exists")
    ConfigFile = SafeConfigParser()
    ConfigFile.read(ConfigFileName)

    #Get and set time    
    TheTime = ConfigFile.get("main","CurrentTime")
    print ("Setting time: ",TheTime)
    CMD = "sudo date --set " + TheTime
    os.system(CMD)
    
  else:
    print ("Config file not found! Running with default values.")

    


 
  
    

  
def ProcessKeypress(Key):

  global MainSleep
  global ScrollSleep
  global NumDots

  # a = animation demo
  # h = set time - hours minutes
  # q = quit - go on to next game
  # r = reboot
  # p or space = pause 5 seconds
  # c = analog clock for 1 hour
  # t = show time
  # 1 - 6 Games
  # 7 = ShowDotZerkRobotTime
  # 8 = ShowFrogTime
  # 9 = Bright Snakes
  
    
  if (Key == "p" or Key == " "):
    time.sleep(5)
  elif (Key == "q"):
    unicorn.off()
    ShowScrollingBanner("Quit!",100,0,0,ScrollSleep * 0.55)
  elif (Key == "r"):
    unicorn.off()
    ShowScrollingBanner("Reboot!",100,0,0,ScrollSleep * 0.45)
    os.execl(sys.executable, sys.executable, *sys.argv)
  elif (Key == "t"):
    ScrollScreenShowTime('down',ScrollSleep)         
  elif (Key == "c"):
    DrawTinyClock(60)
  elif (Key == "h"):
    SetTimeHHMM()
  elif (Key == "a"):
    ShowAllAnimations(ScrollSleep)
  elif (Key == "1"):
    PlayPacDot(NumDots)
  elif (Key == "2"):
    PlayLightDot()
  elif (Key == "3"):
    PlayWormDot()
  elif (Key == "4"):
    PlaySpaceDot()
  elif (Key == "5"):
    PlayDotZerk()
  elif (Key == "6"):
    PlayDotInvaders()
  elif (Key == "7"):
    unicorn.off()
    PlayRallyDot()
  elif (Key == "8"):
    unicorn.off()
    PlayVirusWorld()
    
  elif (Key == "9"):
    unicorn.off()
    ShowDotZerkRobotTime(0.03)
    ShowFrogTime(0.04)
  elif (Key == "0"):
    unicorn.off()
    DrawSnake(random.randint(0,7),random.randint(0,7),255,0,0,random.randint(1,4),.5)
    DrawSnake(random.randint(0,7),random.randint(0,7),0,255,0,random.randint(1,4),.5)
    DrawSnake(random.randint(0,7),random.randint(0,7),0,0,255,random.randint(1,4),.5)
    DrawSnake(random.randint(0,7),random.randint(0,7),125,125,0,random.randint(1,4),.5)
    DrawSnake(random.randint(0,7),random.randint(0,7),0,125,125,random.randint(1,4),.5)
    DrawSnake(random.randint(0,7),random.randint(0,7),125,0,125,random.randint(1,4),.5)
  elif (Key == "+"):
    MainSleep = MainSleep -0.01
    ScrollSleep = ScrollSleep * 0.75
    if (MainSleep <= 0.01):
      MainSleep = 0.01

    #print("Game speeding up")
    #print("MainSleep: ",MainSleep, " ScrollSleep: ",ScrollSleep)
  elif (Key == "-"):
    MainSleep = MainSleep +0.01
    ScrollSleep = ScrollSleep / 0.75
    #print("Game slowing down ")
    #print("MainSleep: ",MainSleep, " ScrollSleep: ",ScrollSleep)



    
    
    


def GetKey(stdscr):
  ReturnChar = ""
  stdscr.nodelay(1) # doesn't keep waiting for a key press
  c = stdscr.getch()  
  
  #Look for specific characters
  if  (c == ord(" ") 
    or c == ord("+")
    or c == ord("-")
    or c == ord("a")
    or c == ord("c")
    or c == ord("h")
    or c == ord("p")
    or c == ord("q")
    or c == ord("r")
    or c == ord("t") ):
    ReturnChar = chr(c)       

  #Look for digits (ascii 48-57 == digits 0-9)
  elif (c >= 48 and c <= 57):
    print ("Digit detected")
    ReturnChar = chr(c)    

  return ReturnChar
 

  
  

def PollKeyboard():
  Key = ""
  curses.filter()
  stdscr = curses.initscr()
  curses.noecho()
  Key = curses.wrapper(GetKey)
  if (Key <> ""):
    print ("----------------")
    print ("Key Pressed: ",Key)
    print ("----------------")
    ProcessKeypress(Key)
    SaveConfigData()

  
  return Key


  
def GetKeyInt(stdscr):
  ReturnInt = -1
  stdscr.nodelay(1) # doesn't keep waiting for a key press
  
  #gets ascii value
  c = stdscr.getch()  

  
  #Look for digits (ascii 48-57 == digits 0-9)
  if (c >= 48 and c <= 57):
    print ("Digit detected")
    ReturnInt = c - 48   

  return ReturnInt

  
  
def PollKeyboardInt():
  Key = -1
  stdscr = curses.initscr()
  curses.noecho()
  Key = curses.wrapper(GetKeyInt)
  if (Key <> -1):
    print ("----------------")
    print ("Key Pressed: ",Key)
    print ("----------------")
    ProcessKeypress(Key)
  
  return Key


  

  
  
  
# This section deals with getting specific input from a question and does not
# trigger events  
  
def GetKeyRegular(stdscr):
  ReturnChar = ""
  stdscr.nodelay(1) # doesn't keep waiting for a key press
  c = stdscr.getch()  

  if (c >= 48 and c <= 150):
    ReturnChar = chr(c)    

  return ReturnChar
  
def PollKeyboardRegular():
  Key = ""
  stdscr = curses.initscr()
  curses.noecho()
  Key = curses.wrapper(GetKeyRegular)
  if (Key <> ""):
    print ("----------------")
    print ("Key Pressed: ",Key)
    print ("----------------")
  
  return Key
  
  
  
  
  
def SetTimeHHMM():
  DigitsEntered = 0
  H1  = 0
  H2  = 0
  M1  = 0
  M2  = 0
  Key = -1

  CustomH = ([1,0,1,
              1,0,1,
              1,1,1,
              1,0,1,
              1,0,1])

  CustomM = ([1,0,1,
              1,1,1,
              1,1,1,
              1,0,1,
              1,0,1])

  QuestionMarkSprite = Sprite(
  3,
  5,
  0,
  0,
  0,
  [0,1,1,
   0,0,1,
   0,1,1,
   0,0,0,
   0,1,0]
)

              
              
  CustomHSprite = Sprite(3,5,SDLowRedR,SDLowRedG,SDLowRedB,CustomH)
  CustomMSprite = Sprite(3,5,SDLowRedR,SDLowRedG,SDLowRedB,CustomM)
  AMSprite      = Sprite(5,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,AlphaSpriteList[0].grid)
  PMSprite      = Sprite(5,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,AlphaSpriteList[15].grid)
  AMPMSprite    = JoinSprite(QuestionMarkSprite,CustomMSprite,1)
  

  
  ScrollScreen('up',ScrollSleep*0.5)
  ShowScrollingBanner("set time: hours minutes",100,100,0,ScrollSleep * 0.65)

  
  HHSprite = TrimSprite(CustomHSprite)
  HHSprite = JoinSprite (HHSprite,TrimSprite(CustomHSprite),1)
  
  HHSprite.Display(1,1)
  
  #Get first hour digit
  while (Key <> 0 and Key <> 1):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  H1 = Key
  
  #Convert user input H1 to a sprite
  #x = ord(H1) -48
  
  UserH1Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[H1].grid)
  CustomHSprite.Erase(1,1)
  UserH1Sprite.Display(1,1)
  
  #Get second hour digit (special conditions to make sure we keep 12 hour time)
  Key = -1
  while ((H1 == 1 and (Key <> 0 and Key <> 1 and Key <> 2))
     or (H1 == 0 and (Key == -1)) ):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  H2 = Key
 
  #Convert user input H2 to a sprite
  UserH2Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[H2].grid)
  CustomHSprite.Erase(5,1)
  UserH2Sprite.Display(5,1)
    
  #print ("HH: ",H1,H2)
  

  
  
  
  #Get minutes
  time.sleep(1)
  unicorn.off()

  
  MMSprite = TrimSprite(CustomMSprite)
  MMSprite = JoinSprite (MMSprite,TrimSprite(CustomMSprite),1)
  
  MMSprite.Display(1,1)
  
  #Get first minute digit
  Key = -1
  while (Key < 0 or Key >= 6):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  M1 = Key
  
  #Convert user input M1 to a sprite
  UserM1Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[M1].grid)
  CustomMSprite.Erase(1,1)
  UserM1Sprite.Display(1,1)
  
  #Get second hour digit
  Key = -1
  while (Key == -1):
    Key = PollKeyboardInt()
    time.sleep(0.15)
  M2 = Key
 
  #Convert user input M2 to a sprite
  UserM2Sprite = Sprite(3,5,SDLowGreenR,SDLowGreenG,SDLowGreenB,DigitSpriteList[M2].grid)
  CustomMSprite.Erase(5,1)
  UserM2Sprite.Display(5,1)
    
  #print ("MM: ",M1,M2)
  
  time.sleep(1)
  unicorn.off()

  # a.m / p.m.
  ShowScrollingBanner("AM or PM",100,100,0,ScrollSleep * 0.65)
  AMPMSprite.Display(1,1)
  #Get A or P
  KeyChar = ''
  while (KeyChar == '' or (KeyChar <> 'A' and KeyChar <> 'a' and KeyChar <> 'P' and KeyChar <> 'p' )):
    KeyChar = PollKeyboardRegular()
    time.sleep(0.15)

  AMPMSprite.r = SDLowGreenR
  AMPMSprite.g = SDLowGreenG
  AMPMSprite.b = SDLowGreenB
  AMPMSprite.Display(1,1)
  
  QuestionMarkSprite.Erase(1,1)

  AMPM = ''
  if (KeyChar == 'a' or KeyChar == 'A'):
    AMSprite.Display(0,1)
    AMPM  = 'am'
    
  elif (KeyChar == 'p' or KeyChar == 'P'):
    PMSprite.Display(0,1)
    AMPM = 'pm'
    
  
  #print ("KeyChar ampm:",KeyChar, AMPM)    
  time.sleep(1)
 
  
  
  
  #set system time
  NewTime = str(H1) + str(H2) + ":" + str(M1) + str(M2) + AMPM
  CMD = "sudo date --set " + NewTime
  os.system(CMD)
  
  unicorn.off()
  ScrollScreenShowTime('down',ScrollSleep)         
  









#Draws the dots on the screen  
def DrawDotMatrix(DotMatrix):
  #print ("--Draw DotMatrix--")
  NumDots = 0
  for h in range (0,8):
    for v in range (0,8):
      #print ("hv dot: ",h,v,DotMatrix[h][v])
      if (DotMatrix[h][v] == 1):
        NumDots = NumDots + 1
        unicorn.set_pixel(h,v,DotR,DotG,DotB)
  #print ("Dots Found: ",NumDots)
  unicorn.show()        
  return NumDots;
  

def CountDotsRemaining(DotMatrix):
  NumDots = 0
  lasth   = 0
  lastv   = 0
  for h in range (0,8):
    for v in range (0,8):
      #print ("hv dot: ",h,v,DotMatrix[h][v])
      if (DotMatrix[h][v] == 1):
        NumDots = NumDots + 1
        lasth = h
        lastv = v
  if (NumDots == 1 ):
    unicorn.set_pixel(lasth,lastv,DotR,DotG,DotB)
    #FlashDot4(lasth,lastv,.01)
  return NumDots;


  
def ScrollSprite2(Sprite,h,v,direction,moves,r,g,b,delay):
  x = 0
  #modifier is used to increment or decrement the location
  if direction == "right" or direction == "down":
    modifier = 1
  else: 
    modifier = -1
  
  if direction == "left" or direction == "right":
    for count in range (0,moves):
      h = h + (modifier)
      #erase old sprite
      if count >= 1:
        DisplaySprite(Sprite,Sprite.width,Sprite.height,h-(modifier),v,0,0,0)
      #draw new sprite
      DisplaySprite(Sprite,Sprite.width,Sprite.height,h,v,r,g,b)
      unicorn.show()
      time.sleep(delay)
  
  return;

 
  

def ScrollSprite(Sprite,width,height,Direction,startH,startV,stopH,stopV,r,g,b,delay):
  x = 0
  h = startH
  v = startV
  movesH = abs(startH - stopH)
  movesV = abs(startV - stopV)

  #modifier is used to increment or decrement the location
  if Direction == "right" or Direction == "down":
    modifier = 1
  else: 
    modifier = -1
  
  if Direction == "left" or Direction == "right":
    for count in range (0,movesH):
      #print ("StartH StartV StopH StopV X",startH,startV,stopH,stopV,x)
      h = h + (modifier)
      #erase old sprite
      if count >= 1:
        DisplaySprite(Sprite,width,height,h-(modifier),v,0,0,0)
      #draw new sprite
      DisplaySprite(Sprite,width,height,h,v,r,g,b)
      unicorn.show()
      time.sleep(delay)
  
  return;
    
def DisplaySprite(Sprite,width,height,h,v,r,g,b):
  x = 0,
  y = 0
  
  for count in range (0,(width * height)):
    y,x = divmod(count,width)
    #print("Count:",count,"xy",x,y)
    if Sprite[count] == 1:
      if (CheckBoundary(x+h,y+v) == 0):
        unicorn.set_pixel(x+h,y+v,r,g,b)
  return;    

  
def DrawDigit(Digit,h,v,r,g,b):
  #print ("Digit:",Digit)
  x = h
  y = v,
  width = 3
  height = 5  

  if Digit == 0:
    Sprite = ([1,1,1, 
               1,0,1,
               1,0,1,
               1,0,1,
               1,1,1])

  elif Digit == 1:
    Sprite = ([0,0,1, 
               0,0,1,
               0,0,1,
               0,0,1,
               0,0,1])

  elif Digit == 2:
    Sprite = ([1,1,1, 
               0,0,1,
               0,1,0,
               1,0,0,
               1,1,1])

  elif Digit == 3:
    Sprite = ([1,1,1, 
               0,0,1,
               0,1,1,
               0,0,1,
               1,1,1])

  elif Digit == 4:
    Sprite = ([1,0,1, 
               1,0,1,
               1,1,1,
               0,0,1,
               0,0,1])
               
  
  elif Digit == 5:
    Sprite = ([1,1,1, 
               1,0,0,
               1,1,1,
               0,0,1,
               1,1,1])

  elif Digit == 6:
    Sprite = ([1,1,1, 
               1,0,0,
               1,1,1,
               1,0,1,
               1,1,1])

  elif Digit == 7:
    Sprite = ([1,1,1, 
               0,0,1,
               0,1,0,
               1,0,0,
               1,0,0])
  
  elif Digit == 8:
    Sprite = ([1,1,1, 
               1,0,1,
               1,1,1,
               1,0,1,
               1,1,1])
  
  elif Digit == 9:
    Sprite = ([1,1,1, 
               1,0,1,
               1,1,1,
               0,0,1,
               0,0,1])
  

  DisplaySprite(Sprite,width,height,h,v,r,g,b)

  unicorn.show()
  return;  
  
  
def DrawPowerPills( PowerPills ):
  global DotMatrix
  global NumDots
  r = 0
  g = 0
  b = 0
  h = randint(0,7)
  v = randint(0,7)
  DotCount = 1
  while DotCount <= PowerPills:
   # print ("Green Pill: ",h," ",v)
    r,g,b = unicorn.get_pixel(h,v)
    unicorn.set_pixel(h,v,PillR,PillG,PillB)
    DotCount = DotCount + 1        
    
    #if we overwrite a dot, take one away from count
    if (r == DotR and g == DotG and b == DotB ):
      DotMatrix[h][v] = 0
      NumDots = NumDots -1  
  

    h = randint(0,7)
    v = randint(0,7)
  return;

def DrawDots( NumDots ):
  #Keep track of the dots in a 2D array
  #DotMatrix = [[0 for x in range(8)] for y in range(8)] 
  #print("--DrawDots--")
  if (NumDots < 5 or NumDots > 64):
    print ("ERROR - NumDots not valid: ",NumDots)
    NumDots = 20
    
  global DotMatrix
  h = randint(0,7)
  v = randint(0,7)
  DotCount = 1
  Tries    = 0
  while (DotCount <= NumDots and Tries <= 500):
    Tries = Tries + 1
    if DotMatrix[h][v] <> 1:
      DotMatrix[h][v] = 1
      unicorn.set_pixel(h,v,DotR,DotG,DotB)  
      DotCount = DotCount + 1
    h = randint(0,7)
    v = randint(0,7)
  return DotMatrix; 

 

def DrawMaze():
  unicorn.set_pixel(1,1,WallR,WallG,WallB)
  unicorn.set_pixel(2,2,WallR,WallG,WallB)
  unicorn.set_pixel(3,3,WallR,WallG,WallB)
  unicorn.set_pixel(4,4,WallR,WallG,WallB)
  unicorn.set_pixel(5,5,WallR,WallG,WallB)
  unicorn.set_pixel(6,6,WallR,WallG,WallB)
  unicorn.set_pixel(7,7,WallR,WallG,WallB)

  return; 

  
  
def DrawGhost(h,v,r,g,b):
   global PowerPillActive
   if PowerPillActive == 1:
     unicorn.set_pixel(h,v,BlueGhostR,BlueGhostG,BlueGhostB)
   else:
     unicorn.set_pixel(h,v,r,g,b)
   return h,v;


def DrawPacDot(h,v,r,g,b):
   unicorn.set_pixel(h,v,r,g,b)
   #unicorn.show()
   return h,v;
 
   

def CheckBoundaries(h,v,Direction):
  if v < 0:
    v = 0
    Direction = TurnRight(Direction)
  elif v > 7:
    v = 7
    Direction = TurnRight(Direction)
  elif h < 0:
    h = 0
    Direction = TurnRight(Direction)
  elif h > 7:
    h = 7
    Direction = TurnRight(Direction)
  return h,v,Direction

  
  
def CheckBoundary(h,v):
  BoundaryHit = 0
  if v < 0 or v > 7 or h < 0 or h > 7:
    BoundaryHit = 1
  return BoundaryHit;


  

  
def CalculateMovement(h,v,Direction):
  # I am not sure why this function returns the direction 
  #1N 2E 3S 4W
  if (Direction == 1):
    v = v -1
  if (Direction == 2):
    h = h + 1
  if (Direction == 3):
    v = v + 1
  if (Direction == 4):
    h = h -1
  return h,v,Direction;


def CalculateDotMovement(h,v,Direction):
  #1N 2E 3S 4W
  if (Direction == 1):
    v = v -1
  if (Direction == 2):
    h = h + 1
  if (Direction == 3):
    v = v + 1
  if (Direction == 4):
    h = h -1
  return h,v;

  
def FlashDot(h,v,FlashSleep):
  r,g,b = unicorn.get_pixel(h,v)
  unicorn.set_pixel(h,v,0,0,255)
  time.sleep(FlashSleep)
  unicorn.show()
  unicorn.set_pixel(h,v,r,g,b)
  time.sleep(FlashSleep)
  unicorn.show()
  unicorn.set_pixel(h,v,0,255,0)
  time.sleep(FlashSleep)
  unicorn.show()
  unicorn.set_pixel(h,v,r,g,b)
  time.sleep(FlashSleep)
  unicorn.show()
  return;

def FlashDot2(h,v,FlashSleep):
  r,g,b = unicorn.get_pixel(h,v)
  unicorn.set_pixel(h,v,75,75,000)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,100,100,0)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,125,125,0)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,150,150,0)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,125,150,0)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,100,150,0)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,75,150,0)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,50,150,0)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,r,g,b)
  unicorn.show()
  time.sleep(FlashSleep)
  return;


  
def FlashDot3(h,v,r,g,b,FlashSleep):
 
    
  LowR = int(r * 0.75)
  LowG = int(g * 0.75)
  LowB = int(b * 0.75)
  HighR = int(r * 1.5)
  HighG = int(g * 1.5)
  HighB = int(b * 1.5)
  
  if (LowR < 0 ):
    LowR = 0
  if (LowG < 0 ):
    LowG = 0
  if (LowB < 0 ):
    LowBB = 0
  
  
  if (HighR > 255):
    HighR = 255
  if (HighG > 255):
    HighG = 255
  if (HighB > 255):
    HighB = 255
    
  unicorn.set_pixel(h,v,HighR,HighG,HighB)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,r,g,b)
  unicorn.show()
  unicorn.set_pixel(h,v,LowR,LowG,LowB)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.show()
  unicorn.set_pixel(h,v,HighR,HighG,HighB)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,r,g,b)
  unicorn.show()
  unicorn.set_pixel(h,v,LowR,LowG,LowB)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.show()
  
  
def FlashDot4(h,v,FlashSleep):
  r,g,b = unicorn.get_pixel(h,v)
  unicorn.set_pixel(h,v,0,0,100)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,0,0,175)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,0,0,255)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,0,255,255)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,255,255,255)
  unicorn.show()
  time.sleep(FlashSleep)
  unicorn.set_pixel(h,v,r,g,b)
  unicorn.show()
  time.sleep(FlashSleep)
  return;
  
  
  
  
def ScanDot(h,v):
  BoundaryHit = CheckBoundary(h,v)
  if BoundaryHit == 1:
    item = "boundary"
  else:
    r,g,b = unicorn.get_pixel(h,v)
    
    #FlashDot(h,v,FlashSleep)
  
  
    if r == DotR and g == DotG and b == DotB:
      item = "dot"
    elif r == PillR and g == PillG and b == PillB:
      item = "pill"
    elif r == Ghost1R and g == Ghost1G and b == Ghost1B:
      item = "ghost"
    elif r == Ghost2R and g == Ghost2G and b == Ghost2B:
      item = "ghost"
    elif r == Ghost3R and g == Ghost3G and b == Ghost3B:
      item = "ghost"
    elif r == PacR and g == PacG and b == PacB:
      item = "pacdot"
    elif r == BlueGhostR and g == BlueGhostG and b == BlueGhostB:
      item = "blueghost"
    elif r == WallR and g == WallG and b == WallB:
      item = "wall"
    else: 
      item = "empty"
  return item;

def ScanBox(h,v,Direction):
  #pass in current h,v,direction
  #will examine multiple dots in front and to sides
  
  
  item = "NULL"
  ScanHit = "NULL"
  ScanH = 0
  ScanV = 0
  ScanDirection = 0
  


 #Front + 1 location (see long distance!)
  ScanDirection = Direction
  ScanH, ScanV, ScanDirection = CalculateMovement(h,v,ScanDirection)
  ScanH, ScanV, ScanDirection = CalculateMovement(ScanH,ScanV,ScanDirection)
  item = ScanDot(ScanH,ScanV)
  if item == "dot":
    ScanHit = "frontdot"
  elif item == "ghost":  
    ScanHit = "frontghost"
  elif item == "blueghost":  
    ScanHit = "frontblueghost"
  elif item == "pill":
    ScanHit = "frontpill"
  elif item == "wall":
    ScanHit = "frontwall"

  
 #Front
  ScanDirection = Direction
  ScanH, ScanV, ScanDirection = CalculateMovement(h,v,ScanDirection)
  item = ScanDot(ScanH,ScanV)
  if item == "dot":
    ScanHit = "frontdot"
  elif item == "ghost":  
    ScanHit = "frontghost"
  elif item == "blueghost":  
    ScanHit = "frontblueghost"
  elif item == "pill":
    ScanHit = "frontpill"
  elif item == "wall":
    ScanHit = "frontwall"

  #Left
  if ScanHit == "NULL":
    ScanDirection = TurnLeft(Direction)
    ScanH, ScanV, ScanDirection = CalculateMovement(h,v,ScanDirection)
    item = ScanDot(ScanH,ScanV)
    if item == "dot":
      ScanHit = "leftdot"
    elif item == "ghost":  
      ScanHit = "leftghost"
    elif item == "blueghost":  
      ScanHit = "leftblueghost"
    elif item == "pill":
      ScanHit = "leftpill"
    elif item == "wall":
      ScanHit = "leftwall"

  #Left + 1 long distance
  if ScanHit == "NULL":
    ScanDirection = TurnLeft(Direction)
    ScanH, ScanV, ScanDirection = CalculateMovement(h,v,ScanDirection)
    ScanH, ScanV, ScanDirection = CalculateMovement(ScanH,ScanV,ScanDirection)
    item = ScanDot(ScanH,ScanV)
    if item == "dot":
      ScanHit = "leftdot"
    elif item == "ghost":  
      ScanHit = "leftghost"
    elif item == "blueghost":  
      ScanHit = "leftblueghost"
    elif item == "pill":
      ScanHit = "leftpill"
    elif item == "wall":
      ScanHit = "leftwall"
      
      
 #Right
  if ScanHit == "NULL":
    ScanDirection = TurnRight(Direction)
    ScanH, ScanV, ScanDirection = CalculateMovement(h,v,ScanDirection)
    item = ScanDot(ScanH,ScanV)
    if item == "dot":
      ScanHit = "rightdot"
    elif item == "ghost":  
      ScanHit = "rightghost"
    elif item == "blueghost":  
      ScanHit = "rightblueghost"
    elif item == "pill":
      ScanHit = "rightpill"
    elif item == "wall":
      ScanHit = "rightwall"

 #Right + 1 long distance!
  if ScanHit == "NULL":
    ScanDirection = TurnRight(Direction)
    ScanH, ScanV, ScanDirection = CalculateMovement(h,v,ScanDirection)
    ScanH, ScanV, ScanDirection = CalculateMovement(ScanH,ScanV,ScanDirection)
    item = ScanDot(ScanH,ScanV)
    if item == "dot":
      ScanHit = "rightdot"
    elif item == "ghost":  
      ScanHit = "rightghost"
    elif item == "blueghost":  
      ScanHit = "rightblueghost"
    elif item == "pill":
      ScanHit = "rightpill"
    elif item == "wall":
      ScanHit = "rightwall"

      
  return ScanHit


  
def FollowScanner(h,v,Direction):
  ScanHit = ScanBox(h,v,Direction)

  #Pills get priority action
  if ScanHit   == "leftpill":
    Direction  =  TurnLeft(Direction)
  elif ScanHit == "frontpill":
    Direction  =  Direction
  elif ScanHit == "rightpill":
    Direction  =  TurnRight(Direction)



  #Dots and BlueGhosts get followed
  elif ScanHit == "leftdot" or ScanHit == "leftblueghost":
    Direction = TurnLeft(Direction)
  
  #ignore ghost on the left
  elif ScanHit == "leftghost":
    Direction = Direction

  elif ScanHit == "frontdot" or ScanHit == "frontblueghost":
    Direction = Direction

  elif ScanHit == "frontghost":
    Direction = ReverseDirection(Direction)

  elif ScanHit == "rightdot" or ScanHit == "rightblueghost":
    Direction = TurnRight(Direction)
  elif ScanHit == "rightghost":
    Direction = Direction
    
  elif ScanHit ==  "leftwall"  or ScanHit == "frontwall"  or ScanHit == "rightwall":
    Direction = TurnRight(Direction)

  
  return Direction;
  
  
  
def ReverseDirection(direction):
  if direction == 1:
    direction = 3
  elif direction == 2:
    direction = 4
  elif direction == 3:
    direction = 1
  elif direction == 4:
    direction = 2
  return direction;
    

def TurnRight(direction):
  if direction == 1:
    direction = 2
  elif direction == 2:
    direction = 3
  elif direction == 3:
    direction = 4
  elif direction == 4:
    direction = 1
  #print "  new: ",direction
  return direction;
    

def TurnLeft(direction):
  #print "ChangeDirection!"
  #print "  old: ",direction
  if direction == 1:
    direction = 4
  elif direction == 2:
    direction = 1
  elif direction == 3:
    direction = 2
  elif direction == 4:
    direction = 3
  #print "  new: ",direction
  return direction;
    
def ChanceOfTurning(Direction,Chance):
  #print ("Chance of turning: ",Chance)
  if Chance > randint(1,100):
    if randint(0,1) == 0:
      Direction = TurnLeft(Direction)
    else:
      Direction = TurnRight(Direction)
  return Direction;




# We need to move the ghost and leave behind the proper colored pixel
  
def MoveGhost(h,v,CurrentDirection,r,g,b):
  global DotMatrix
  item = "NULL"
  #print ("MoveGhost old:",h,v,CurrentDirection)
  
  newh, newv, CurrentDirection = CalculateMovement(h,v,CurrentDirection)
  item = ScanDot(newh,newv)

  #print ("MoveGhost New:",newh,newv,CurrentDirection, item)
  
  if item == "wall" or item == "pill" or item == "ghost":
    CurrentDirection = randint(1,4)
    newh = h
    newv = v     

  elif item == "empty":
    unicorn.set_pixel(newh,newv,r,g,b)
    if (DotMatrix[h][v]==1):
      unicorn.set_pixel(h,v,DotR,DotG,DotB)
    else:
      unicorn.set_pixel(h,v,0,0,0)

  #if item is pacot, don't do anything just sit there
  elif item == "pacdot":
    newh = h
    newv = v     

  # if item is a normal dot, jump over it
  elif item == "dot":
    unicorn.set_pixel(newh,newv,r,g,b)
    if DotMatrix[h][v]==1:
      unicorn.set_pixel(h,v,DotR,DotG,DotB)
    else:
      unicorn.set_pixel(h,v,0,0,0)

  elif item == "boundary":    
    CurrentDirection = randint(1,4)
    newh = h
    newv = v     
 
  #unicorn.show()

  #print "After  HVD:",h,v,CurrentDirection
  return newh,newv,CurrentDirection;


def KillGhost(h,v):  
    global Ghost1Alive
    global Ghost1H
    global Ghost1V
    global Ghost2Alive
    global Ghost2H
    global Ghost2V
    global Ghost3Alive
    global Ghost3H
    global Ghost3V
    if h == Ghost1H and v == Ghost1V:
      Ghost1Alive = 0
      #print ("Killing Ghost:",Ghost1Alive)
    if h == Ghost2H and v == Ghost2V:
      Ghost2Alive = 0
      #print ("Killing Ghost:",Ghost2Alive)
    if h == Ghost3H and v == Ghost3V:
      Ghost3Alive = 0
      #print ("Killing Ghost:",Ghost3Alive)


def MovePacDot(h,v,CurrentDirection,r,g,b,DotsEaten):
  global Pacmoves
  global PowerPillActive
  global Ghost1Alive
  global Ghost2Alive
  global Ghost3Alive
  global DotMatrix
  global PacDotScore
  global DotPoints
  global PillPoints
  global BlueGhosePoints
  Pacmoves = Pacmoves + 1
  item = "NULL"

  newh, newv, CurrentDirection = CalculateMovement(h,v,CurrentDirection)
  item = ScanDot(newh,newv)

  #print ("MovePacDot item:",item)
  if item == "dot":
    DotsEaten = DotsEaten + 1
    Pacmoves = 0
    PacDotScore = PacDotScore + DotPoints
    unicorn.set_pixel(newh,newv,r,g,b)
    unicorn.set_pixel(h,v,0,0,0)
    DotMatrix[newh][newv] = 0
    
  elif item == "pill":
    Pacmoves = 0
    PacDotScore = PacDotScore + PillPoints
    unicorn.set_pixel(newh,newv,r,g,b)
    unicorn.set_pixel(h,v,0,0,0)
    PowerPillActive = 1

  #Pacman needs to leave walls alone
  elif item == "wall":
    Pacmoves = 0
    CurrentDirection = TurnRight(CurrentDirection)
    #unicorn.set_pixel(newh,newv,r,g,b)
    #unicorn.set_pixel(h,v,0,0,0)

    
    
  elif item == "blueghost":
    Pacmoves = 0
    PacDotScore = PacDotScore + BlueGhostPoints
    unicorn.set_pixel(newh,newv,r,g,b)
    unicorn.set_pixel(h,v,0,0,0)
    KillGhost(newh,newv)

    
  elif item == "ghost":
    if PowerPillActive == 1:
      KillGhost(newh, newv)
    else:  
      CurrentDirection = TurnLeft(CurrentDirection)

    CurrentDirection = CurrentDirection
    newh = h
    newv = v

      
      
  elif item == "empty":
    unicorn.set_pixel(newh,newv,r,g,b)
    unicorn.set_pixel(h,v,0,0,0)

  elif item == "boundary":    
    CurrentDirection = randint(1,4)
    newh = h
    newv = v     


  #print "After  HVD:",h,v,CurrentDirection
  return newh,newv,CurrentDirection,DotsEaten;

  
  
def MoveBigSprite(sprite,FlashSleep):
  for i in range (0,80):
    
    y,x = divmod(i,16)
    #print ("x,y,i",x,y,i)
    if (x >= 0 and x<= 2):
      BigSprite.grid[i] = DigitSpriteList[2].grid[x-(0*4)+(y*3)]
    if (x >= 4 and x<= 6):
      BigSprite.grid[i] = DigitSpriteList[3].grid[x-(1*4)+(y*3)]
    if (x >=8  and x<= 10):
      BigSprite.grid[i] = DigitSpriteList[0].grid[x-(2*4)+(y*3)]
    if (x >=12  and x<= 14):
      BigSprite.grid[i] = DigitSpriteList[7].grid[x-(3*4)+(y*3)]
    #"looping"
  BigSprite.Scroll(-16,0,"right",24,FlashSleep)
  BigSprite.Scroll(9,0,"left",24,FlashSleep)
    

  
def JoinSprite(Sprite1, Sprite2, buffer):
  #This function takes two sprites, and joins them together horizontally
  #The color of the second sprite is used for the new sprite
  height = Sprite1.height
  width  = Sprite1.width + buffer + Sprite2.width
  elements = height * width
  x = 0
  y = 0
  
 
  TempSprite = Sprite(
  width,
  height,
  Sprite2.r,
  Sprite2.g,
  Sprite2.b,
  [0]*elements
  )
  for i in range (0,elements):
    y,x = divmod(i,width)
    
    #copy elements of first sprite
    if (x >= 0 and x< Sprite1.width):
      TempSprite.grid[i] = Sprite1.grid[x + (y * Sprite1.width)]
    
    if (x >= (Sprite1.width + buffer) and x< (Sprite1.width + buffer + Sprite2.width)):
      TempSprite.grid[i] = Sprite2.grid[(x - (Sprite1.width + buffer)) + (y * Sprite2.width)]

  #TempSprite.Scroll(1,1,"right",24,FlashSleep)
  return TempSprite    


def TrimSprite(Sprite1):
  height       = Sprite1.height
  width        = Sprite1.width
  newwidth     = 0
  elements     = height * width
  Empty        = 1
  Skipped      = 0
  EmptyColumns = []
  EmptyCount   = 0
  BufferX      = 0
  BufferColumn = [(0) for i in range(height)]
  
  i = 0
  x = 0
  y = 0

  
  for x in range (0,width):
    
    #Find empty columns, add them to a list
    Empty = 1  
    for y in range (0,height):
      i = x + (y * width)
      
      BufferColumn[y] = Sprite1.grid[i]
      if (Sprite1.grid[i] <> 0):
        Empty = 0
    
    if (Empty == 0):
      newwidth =  newwidth + 1
    
    elif (Empty == 1):
      #print ("Found empty column: ",x)
      EmptyColumns.append(x)
      EmptyCount = EmptyCount +1

      
  BufferSprite = Sprite(
    newwidth,
    height,
    Sprite1.r,
    Sprite1.g,
    Sprite1.b,
    [0]*(newwidth*height)
    )
      
  #Now that we identified the empty columns, copy data and skip those columns
  for x in range (0,width):
    Skipped = 0
    
    for y in range (0,height):
      i = x + (y * width)
      b = BufferX + (y * newwidth)
      if (x in EmptyColumns):
        Skipped = 1
      else:
        BufferSprite.grid[b] = Sprite1.grid[i]
    
    
    #advance our buffer column counter only if we skipped a column
    if (Skipped == 0):
      BufferX = BufferX + 1
    
    
  
  BufferSprite.width = newwidth
  
  
  
  #print (BufferSprite.grid)
  return BufferSprite
    
 
  
def CreateClockSprite(format):   
  #print ("CreateClockSprite")
  #Create the time as HHMMSS
  
  if (format == 12 or format == 2):  
    hhmmss = datetime.now().strftime('%I:%M:%S')
    hh,mm,ss = hhmmss.split(':')
  
  if format == 24:  
    hhmmss = datetime.now().strftime('%H:%M:%S')
    hh,mm,ss = hhmmss.split(':')
  
   

  
  #get hour digits
  h1 = int(hh[0])
  h2 = int(hh[1])
  #get minute digits
  m1 = int(mm[0])
  m2 = int(mm[1])


  #For 12 hour format, we don't want to display leading zero 
  #for tiny clock (2) format we only get hours
  if ((format == 12 or format == 2) and h1 == 0):
    ClockSprite = DigitSpriteList[h2]
  else:
    ClockSprite = JoinSprite(DigitSpriteList[h1], DigitSpriteList[h2], 1)
  
  if (format == 12 or format == 24):
    ClockSprite = JoinSprite(ClockSprite, ColonSprite, 0)
    ClockSprite = JoinSprite(ClockSprite, DigitSpriteList[m1], 0)
    ClockSprite = JoinSprite(ClockSprite, DigitSpriteList[m2], 1)
    

  ClockSprite.r = SDLowRedR
  ClockSprite.g = SDLowRedG
  ClockSprite.b = SDLowRedB
  
  return ClockSprite 




  
def ShowScrollingClock():
  TheTime = CreateClockSprite(12)
  
  
  #PacRightAnimatedSprite.Scroll(-5,1,'right',13,ScrollSleep)
  #OrangeGhostSprite.ScrollAcrossScreen(0,1,"right",ScrollSleep)

  ThreeGhostPacSprite.ScrollAcrossScreen(0,1,"right",ScrollSleep)
  TheTime.ScrollAcrossScreen(0,1,"right",ScrollSleep)

  #PacSprite.HorizontalFlip()
  #BlueGhostSprite.ScrollAcrossScreen(0,1,"left",ScrollSleep)
  ThreeBlueGhostPacSprite.ScrollAcrossScreen(0,1,"left",ScrollSleep)
  
  #PacLeftAnimatedSprite.Scroll(8,1,'left',13,ScrollSleep)

  TheTime.ScrollAcrossScreen(0,1,"left",ScrollSleep)
  #PacSprite.HorizontalFlip()
  

  
 
  
def CreateBannerSprite(TheMessage):
  #We need to dissect the message and build our banner sprite one letter at a time
  #We need to initialize the banner sprite object first, so we pick the first letter
  x = -1
  
  BannerSprite = Sprite(1,5,0,0,0,[0,0,0,0,0])
  
  #Iterate through the message, decoding each characater
  for i,c, in enumerate(TheMessage):
    x = ord(c) -65
    if (c == '?'):
      BannerSprite = JoinSprite(BannerSprite, QuestionMarkSprite,0)
    elif (c == '#'):
      BannerSprite = JoinSprite(BannerSprite, PoundSignSprite,0)
    elif (c == ':'):
      BannerSprite = JoinSprite(BannerSprite, ColonSprite,0)
    elif (c == '!'):
      BannerSprite = JoinSprite(BannerSprite, ExclamationSprite,0)
    elif (c == ' '):
      BannerSprite = JoinSprite(BannerSprite, SpaceSprite,0)
    elif (ord(c) >= 48 and ord(c)<= 57):
      BannerSprite = JoinSprite(BannerSprite, DigitSpriteList[int(c)],1)
    else:
      BannerSprite = JoinSprite(BannerSprite, TrimSprite(AlphaSpriteList[x]),1)
  return BannerSprite

  
    

  
  

def ShowLevelCount(LevelCount):
  global MainSleep
  unicorn.off()
      
  SDColor = (random.randint (0,6) *4 + 1) 
  print ("LevelCountColor:",SDColor)
  
  r,g,b =  ColorList[SDColor]  
  max   = 75
  sleep = 0.06 * MainSleep
  print ("sleep: ",sleep," MainSleep: ",MainSleep)
  
  LevelSprite = Sprite(1,5,r,g,b,[0,0,0,0,0])
  
  if (LevelCount > 9):
    LevelString = str(LevelCount)
    LevelSprite1 = DigitSpriteList[int(LevelString[0])]
    LevelSprite2 = DigitSpriteList[int(LevelString[1])]
   
    
    for x in range(0,max,1):
      LevelSprite1.r = r + x
      LevelSprite1.g = g + x
      LevelSprite1.b = b + x
      LevelSprite2.r = r + x
      LevelSprite2.g = g + x
      LevelSprite2.b = b + x

      if(LevelSprite1.r > 255):
        LevelSprite1.r = 255
      if(LevelSprite1.g > 255):
        LevelSprite1.g = 255
      if(LevelSprite1.b > 255):
        LevelSprite1.b = 255
      if(LevelSprite2.r > 255):
        LevelSprite2.r = 255
      if(LevelSprite2.g > 255):
        LevelSprite2.g = 255
      if(LevelSprite2.b > 255):
        LevelSprite2.b = 255
        
      LevelSprite1.Display(0,1)
      LevelSprite2.Display(4,1)
      unicorn.show()
      time.sleep(sleep)

    
    for x in range(0,max,1):
      LevelSprite1.r = r + max -x
      LevelSprite1.g = g + max -x
      LevelSprite1.b = b + max -x
      LevelSprite2.r = r + max -x
      LevelSprite2.g = g + max -x
      LevelSprite2.b = b + max -x

      if(LevelSprite1.r < r):
        LevelSprite1.r = r
      if(LevelSprite1.g < g):
        LevelSprite1.g = g
      if(LevelSprite1.b < b):
        LevelSprite1.b = b
      if(LevelSprite2.r < r):
        LevelSprite2.r = r
      if(LevelSprite2.g < g):
        LevelSprite2.g = g
      if(LevelSprite2.b < b):
        LevelSprite2.b = b

      LevelSprite1.Display(0,1)
      LevelSprite2.Display(4,1)
      unicorn.show()
      time.sleep(sleep) 
     
      
  else:    
    LevelSprite = DigitSpriteList[LevelCount]

    for x in range(0,max,1):
      LevelSprite.r = r + x
      LevelSprite.g = g + x
      LevelSprite.b = b + x

      if(LevelSprite.r > 255):
        LevelSprite.r = 255
      if(LevelSprite.g > 255):
        LevelSprite.g = 255
      if(LevelSprite.b > 255):
        LevelSprite.b = 255

      LevelSprite.Display(3,1)
      unicorn.show()
      time.sleep(sleep) 
      
    for x in range(0,max,1):
      LevelSprite.r = r + max -x
      LevelSprite.g = g + max -x
      LevelSprite.b = b + max -x

      if(LevelSprite.r < r):
        LevelSprite.r = r
      if(LevelSprite.g < g):
        LevelSprite.g = g
      if(LevelSprite.b < b):
        LevelSprite.b = b
      LevelSprite.Display(3,1)
      unicorn.show()
      time.sleep(sleep)
      

  
  unicorn.off()
  return
  

  
  
  
  
def ShowScrollingBanner(TheMessage,r,g,b,ScrollSpeed):
  TheMessage = TheMessage.upper()
  TheBanner = CreateBannerSprite(TheMessage)
  TheBanner.r = r 
  TheBanner.g = g 
  TheBanner.b = b 
  TheBanner.ScrollAcrossScreen(7,1,"left",ScrollSpeed)

  
  
def ScreenWipe(Wipe, Speed):
  if Wipe == "RedCurtain":
    for x in range (8):
      for y in range (8):
        unicorn.set_pixel(x,y,255,0,0)
        unicorn.show()
        time.sleep(Speed)
    
#Primitive, single color
def ScrollThreeGhostSprite(direction):
  ThreeGhostSprite = JoinSprite(RedGhostSprite, OrangeGhostSprite, 2)
  ThreeGhostSprite = JoinSprite(ThreeGhostSprite, PurpleGhostSprite, 2)
  ThreeGhostSprite.ScrollAcrossScreen(0,1,direction,ScrollSleep)

    
#--------------------------------------
#--            PING                  --
#--------------------------------------
    
  
def PlayPing():

  #Variables
  Player1H = 0
  Player1V = 2
  Player2H = 7
  Player2V = 2
  PingDotH = 3
  PingDotV = 4
  Player1Speed = 4
  Player2Speed = 4
  DotSpeed = 4
  

    
  #Define Characters
  Player1Sprite = Sprite(1,2,WhiteLowR, WhiteLowG, WhiteLowB, [1,1])
  Player2Sprite = Sprite(1,2,WhiteLowR, WhiteLowG, WhiteLowB, [1,1])
  DotSprite     = Sprite(1,1,WhiteHighR, WhiteHighG, WhiteHighB, [1])

  #Title
  ShowScrollingBanner("Ping",205,205,205,ScrollSleep)
  

  Player1Sprite.Display(Player1H,Player1V)
  Player1Sprite.Display(Player2H, Player2V)
  DotSprite.Display(PingDotH,PingDotV)
  
  #Draw Playfield
  unicorn.show()


  
#--------------------------------------
#--          Light Dot               --
#--------------------------------------




def TurnLeftOrRight(direction):
  WhichWay = random.randint(1,2)
  #print ("WhichWay:",WhichWay)
  if (WhichWay == 1):
    #print ("turning left")
    direction = TurnLeft(direction)
  else:
    #print ("turning right")
    direction = TurnRight(direction)
    
  return direction;

  
  
def ScanLightDot(h,v):
# I am keeping this simple for now, will remove color checking later
# border
# empty
# wall

  
  global GreenObstacleFadeValue
  global GreenObstacleMinVisible

  Item = ''
  OutOfBounds = CheckBoundary(h,v)
  
  if (OutOfBounds == 1):
    Item = 'border'
  else:
    #FlashDot(h,v,0)
    r,g,b = unicorn.get_pixel(h,v)  
    #print ("rgb scanned:",r,g,b)
    if (r == 0 and g == 0 and b == 0):
      Item = 'empty'
    
    #wormdot obstacles are green
    #Every time they are scanned, they grow dim and eventually disappear
    elif (r == 0 and g >= GreenObstacleMinVisible and b == 0):
      print ("Green obstacle found g:,g")  
      g = g - GreenObstacleFadeValue
      if (g < GreenObstacleMinVisible):
        unicorn.set_pixel(h,v,0,0,0)
        Item = 'empty'
      else:
        unicorn.set_pixel(h,v,0,g,0)
        Item = 'obstacle'
    elif (r == SDLowRedR and g == SDLowRedG and b == SDLowRedB):      
        #unicorn.set_pixel(h,v,0,0,0)
        Item = 'speeduppill'      
    else:
      Item = 'wall'
  return Item
    
    
def ScanLightDots(h,v,direction):
  ScanDirection = 0
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
  
  # We will scan 5 spots around the dot
  #  LF FF FR
  #  LL    RR 
  #
  #  2  3  4
  #  1     5
  #
  
  #Scanning Probe
  #Turn left move one + SCAN
  #Turn Right move one + SCAN
  #Turn Right Move one + SCAN 
  #Move one + SCAN 
  #Turn Right Move one + SCAN 
  
  
  #LL 1
  ScanDirection = TurnLeft(direction)
  ScanH, ScanV = CalculateDotMovement(h,v,ScanDirection)
  Item = ScanLightDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #LF 2
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanLightDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #FF 3
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanLightDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #FR 4
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanLightDot(ScanH,ScanV)
  ItemList.append(Item)
  
  #RR 5
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanLightDot(ScanH,ScanV)
  ItemList.append(Item)
    
  return ItemList;


def FadePixel(r,g,b,fadeval):
  newr = r - fadeval
  newg = g - fadeval
  newb = b - fadeval
  
  if (newr < 0):
    newr = 0
  if (newg < 0):
    newg = 0
  if (newb < 0):
    newb = 0

  return r,g,b;
  
  
def MoveDot(Dot):
  h = 0
  v = 0
  Dot.trail.append((Dot.h, Dot.v))
  ItemList = []
  #Scan all around, make decision, move
  ItemList = ScanLightDots(Dot.h,Dot.v,Dot.direction)
  
  #print('DotName: ', Dot.name, 'hv',Dot.h,Dot.v, ' ', *ItemList, sep='|')
  
  #get possible items, then prioritize

  #The red dot must be hit head on
  #once this happens we erase it and increase the speed
  if (ItemList[3] == 'speeduppill'):
    h,v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    Dot.speed = Dot.speed -1
    Dot.maxtrail = Dot.maxtrail + 1
    if (Dot.speed <= 3):
      Dot.speed = 3
    ItemList[3] = 'empty'
    #print ("Speed: ",Dot.speed)
    unicorn.set_pixel(h,v,0,0,0)
  
 
  #Red on left
  if (ItemList[1] == 'speeduppill'):
    Dot.direction = TurnLeft(Dot.direction)
    h,v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)    
    Dot.speed = Dot.speed -1
    Dot.maxtrail = Dot.maxtrail + 1
    if (Dot.speed <= 3):
      Dot.speed = 3
    ItemList[1] = 'empty'
    #print ("Speed: ",Dot.speed)
    unicorn.set_pixel(h,v,0,0,0)

  elif (ItemList[5] == 'speeduppill'):
    Dot.direction = TurnRight(Dot.direction)
    h,v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)    
    Dot.maxtrail = Dot.maxtrail + 1
    Dot.speed = Dot.speed -1
    if (Dot.speed <= 3):
      Dot.speed = 3
    ItemList[5] = 'empty'
    #print ("Speed: ",Dot.speed)
    unicorn.set_pixel(h,v,0,0,0)

  #empty = move forward
  elif (ItemList[3] == 'empty'):
    Dot.h, Dot.v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)

  #This was an accident, but I like it
  #If the worm has a head on collision with the obstacle, it gets stuck and the obstacle
  #fades, almost as if the worm is eating it.  The worm ends up shorter though!  Weird.
  #print ('ItemList[3]:', ItemList[3])
  if ItemList[3]  == 'obstacle':
    print ("Obstacle hit!  Draining our power!")
    r,g,b = unicorn.get_pixel(h,v)
    if (g > 45):
      r,g,b = FadePixel(r,g,b,1)
      unicorn.set_pixel(h,v,r,g,b)
      
      #I have decided to try moving away from green dot
      Dot.direction = TurnLeftOrRight(Dot.direction)
      Dot.h, Dot.v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)    
      Dot.speed = Dot.speed +1


    
    
  #if heading to boundary or wall
  elif (ItemList[3] == 'wall' or ItemList[3] == 'border' or ItemList[3] == 'obstacle'):
    if (ItemList[1] == 'empty' and ItemList[5] == 'empty'):
      #print ("both empty picking random direction")
      Dot.direction = TurnLeftOrRight(Dot.direction)
      Dot.h, Dot.v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[1] == 'empty' and ItemList[5] <> 'empty'):
      #print ("left empty turning left")
      Dot.direction = TurnLeft(Dot.direction)
      Dot.h, Dot.v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[5] == 'empty' and ItemList[1] <> 'empty'):
      #print ("left empty turning right")
      Dot.direction = TurnRight(Dot.direction)
      Dot.h, Dot.v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    
    
    else:
      #print ("you died")
      Dot.alive = 0
      Dot.trail.append((Dot.h, Dot.v))
      Dot.EraseTrail('forward','flash')
  
  return Dot

  



  
  
  
def PlayLightDot():
  
  #Local variables
  moves      = 0
  Finished   = 'N'
  LevelCount = 5
  Worm1h      = 0
  Worm1v      = 0
  Worm2h      = 0
  Worm2v      = 0
  Worm3h      = 0
  Worm3v      = 0
  SleepTime  = MainSleep * 3
  
  #def __init__(self,h,v,r,g,b,direction,speed,alive,name,trail,score):
  Worm1Dot = Dot(Worm1h,Worm1v,BlueR,BlueG,BlueB,(random.randint(1,5)),1,1,'BLUE',(Worm1h, Worm1v), 0, 25,0.03)
  Worm2Dot = Dot(Worm2h,Worm2v,PurpleR,PurpleG,PurpleB,(random.randint(1,5)),1,1,'PURPLE',(Worm2h,Worm2v),0, 25,0.03)
  Worm3Dot = Dot(Worm3h,Worm3v,OrangeR,OrangeG,OrangeB,(random.randint(1,5)),1,1,'ORANGE',(Worm3h,Worm3v),0, 25,0.03)
      
  #Title
  unicorn.off()
  ShowScrollingBanner("LightDot",OrangeR,OrangeG,OrangeB,ScrollSleep)
  ShowClock(ScrollSleep)

  
  while (LevelCount > 0):
    print ("Show level")
    DrawSnake(7,0,OrangeR,OrangeG,OrangeB,3,1)

    
    ShowLevelCount(LevelCount)


    LevelCount = LevelCount - 1
    unicorn.off()
    #print ("=======================psp========")



    
    #Reset Variables between rounds
    Worm1Dots = 0
    Worm2Dots = 0
    Worm3Dots = 0
    LevelFinished = 'N'
  

    #Set random starting points
    Worm1h = random.randint(1,6)
    Worm1v = random.randint(1,6)
    Worm2h = random.randint(1,6)
    Worm2v = random.randint(1,6)
    Worm3h = random.randint(1,6)
    Worm3v = random.randint(1,6)
    while (Worm2h == Worm1h and Worm2v == Worm1v):
      Worm2h = random.randint(1,6)
      Worm2v = random.randint(1,6)
    while ((Worm3h == Worm2h and Worm3v == Worm2v) or (Worm3h == Worm1h and Worm3v == Worm1v)):
      Worm3h = random.randint(1,6)
      Worm3v = random.randint(1,6)
      
    Worm1Dot.h         = Worm1h
    Worm1Dot.v         = Worm1v
    Worm1Dot.direction = (random.randint(1,4))
    Worm1Dot.alive     = 1
    Worm1Dot.trail     = [(Worm1h, Worm1v)]
    
    Worm2Dot.h         = Worm2h
    Worm2Dot.v         = Worm2v
    Worm2Dot.direction = (random.randint(1,4))
    Worm2Dot.alive     = 1
    Worm2Dot.trail     = [(Worm2h, Worm2v)]
    

    Worm3Dot.h         = Worm3h
    Worm3Dot.v         = Worm3v
    Worm3Dot.direction = (random.randint(1,4))
    Worm3Dot.alive     = 1
    Worm3Dot.trail     = [(Worm3h, Worm3v)]

    while (LevelFinished == 'N'):
      
      #reset variables
      SleepTime = MainSleep * 3
      
      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = PollKeyboard()
        if (Key == 'q'):
          LevelCount    = 0
          LevelFinished = 'Y'
          return
      
      #print ("direction:",Worm1Dot.direction,Worm2Dot.direction,Worm3Dot.direction)
      #Display dots if they are alive
      if (Worm1Dot.alive == 1):
        Worm1Dot.Display()
      if (Worm2Dot.alive == 1):
        Worm2Dot.Display()
      if (Worm3Dot.alive == 1):
        Worm3Dot.Display()
      unicorn.show()
    

     #Calculate Movement
      moves = moves +1

      
      if (Worm1Dot.alive == 1):
        m,r = divmod(moves,Worm1Dot.speed)
        if (r == 0):
          MoveDot(Worm1Dot)
          #check for head on collisions
          if ((Worm1Dot.h == Worm2Dot.h and Worm1Dot.v == Worm2Dot.v and Worm2Dot.alive == 1) or (Worm1Dot.h == Worm3Dot.h and Worm1Dot.v == Worm3Dot.v and Worm3Dot.alive == 1)):
            Worm1Dot.alive = 0
            Worm1Dot.EraseTrail('forward','flash')

      if (Worm2Dot.alive == 1):
        m,r = divmod(moves,Worm2Dot.speed)
        if (r == 0):
          #Worm2Dot.trail.append((Worm2Dot.h, Worm2Dot.v))
          MoveDot(Worm2Dot)
          #check for head on collisions
          if ((Worm2Dot.h == Worm3Dot.h and Worm2Dot.v == Worm3Dot.v and Worm3Dot.alive == 1) or (Worm2Dot.h == Worm1Dot.h and Worm2Dot.v == Worm1Dot.v and Worm1Dot.alive == 1)):
            Worm2Dot.alive = 0
            Worm2Dot.EraseTrail('forward','flash')
          
      if (Worm3Dot.alive == 1):
        m,r = divmod(moves,Worm3Dot.speed)
        if (r == 0):
          #Worm3Dot.trail.append((Worm3Dot.h, Worm3Dot.v))
          MoveDot(Worm3Dot)
          #check for head on collisions
          if ((Worm3Dot.h == Worm2Dot.h and Worm3Dot.v == Worm2Dot.v and Worm2Dot.alive == 1) or (Worm3Dot.h == Worm1Dot.h and Worm3Dot.v == Worm1Dot.v and Worm1Dot.alive == 1)):
            Worm3Dot.alive = 0
            Worm3Dot.EraseTrail('forward','flash')
      
      if(Worm1Dot.alive == 0 and Worm2Dot.alive == 0 and Worm3Dot.alive == 0):
        LevelFinished = 'Y'
      
      #print ("Alive:",Worm1Dot.alive,Worm2Dot.alive,Worm3Dot.alive)
    
      PlayersAlive = Worm1Dot.alive + Worm2Dot.alive + Worm3Dot.alive
      if (PlayersAlive == 2):
        SleepTime = MainSleep * 2
      elif (PlayersAlive == 1):
        SleepTime = MainSleep 
      time.sleep(SleepTime)

    #Determine round winner
    Worm1Dots = len(Worm1Dot.trail)
    Worm2Dots = len(Worm2Dot.trail)
    Worm3Dots = len(Worm3Dot.trail)
      
    if (Worm1Dots >= Worm2Dots and Worm1Dots >= Worm3Dots):
      Worm1Dot.score = Worm1Dot.score + Worm1Dots    
    elif (Worm2Dots >= Worm1Dots and Worm2Dots >= Worm3Dots):
      Worm2Dot.score = Worm2Dot.score + Worm2Dots
    else:
      Worm3Dot.score = Worm3Dot.score + Worm3Dots
    
    #Display animation and clock every X seconds
    if (CheckElapsedTime(CheckTime) == 1):
      ScrollScreenShowTime('up',ScrollSleep)         
    
  #Calculate Game score
  FinalWinner = ''
  FinalScore  = 0
  Finalr      = 0
  Finalg      = 0
  Finalb      = 0
  if (Worm1Dot.score > Worm2Dot.score and Worm1Dot.score >= Worm3Dot.score):
    FinalScore  = Worm1Dot.score
    FinalWinner = Worm1Dot.name
    Finalr      = Worm1Dot.r
    Finalg      = Worm1Dot.g
    Finalb      = Worm1Dot.b
  elif (Worm2Dot.score >= Worm1Dot.score and Worm2Dot.score >= Worm3Dot.score):
    FinalScore  = Worm2Dot.score
    FinalWinner = Worm2Dot.name
    Finalr      = Worm2Dot.r
    Finalg      = Worm2Dot.g
    Finalb      = Worm2Dot.b
  else:
    FinalScore = Worm3Dot.score
    FinalWinner = Worm3Dot.name
    Finalr      = Worm3Dot.r
    Finalg      = Worm3Dot.g
    Finalb      = Worm3Dot.b
  
  ScrollString = FinalWinner + ' ' + str(FinalScore)
  
  ShowScrollingBanner(ScrollString,Finalr,Finalg,Finalb,ScrollSleep*1.25)
  ShowScrollingBanner("GAME OVER",255,0,50,ScrollSleep)


#--------------------------------------
#  WormDOt                           --
#--------------------------------------

def TrimTrail(Dot):
  if (len(Dot.trail) > Dot.maxtrail):
    h,v = Dot.trail[0]
    unicorn.set_pixel(h,v,0,0,0)
    del Dot.trail[0]

def PlaceGreenObstacle():
  finished = 'N'
  h = 1
  v = 0

  h = random.randint(0,7)
  v = random.randint(0,7)

  while (finished == 'N'):
    h = random.randint(0,7)
    v = random.randint(0,7)
    while ((h == 1 and v == 0)
        or (h == 0 and v == 1)
        or (h == 7 and v == 1)
        or (h == 0 and v == 6)
        or (h == 7 and v == 6)
        or (h == 1 and v == 7)
        or (h == 6 and v == 7)
        or (h == 6 and v == 0)):
        
        # actually, I will allow it for now
        #or (v == 1) # I decided to not let any obstacles on these rows, to increase play time
        #or (v == 6)
        #or (h == 1)
        #or (h == 6)):
      h = random.randint(0,7)
      v = random.randint(0,7)
    r,g,b = unicorn.get_pixel(h,v)
    #print ("got pixel rgb hv",r,g,b,h,v)
    
    #The color of green is very important as it denotes an obstacle
    #The scanner will fade the obstacle until it disappears
    if (r == 0 and g == 0 and b == 0):
      
      #Once in a while, we will make the obstacle permanent (white dot)
      if (random.randint(1,7) == 1):
        unicorn.set_pixel(h,v,0,125,125)
      else:
        unicorn.set_pixel(h,v,0,75,0)
  
      finished = 'Y'
    
    #Sometimes it takes too long to find a empty spot and the program
    #seems to hang. We now have a 1 in 20 chance of exiting
    if (random.randint(1,20) == 1):
      finished = 'Y'

        
      
      

def PlaceSpeedupPill():
  finished = 'N'
  while (finished == 'N'):
    h = random.randint(0,7)
    v = random.randint(0,7)
    r,g,b = unicorn.get_pixel(h,v)
    if (r == 0 and g == 0 and b == 0):
      unicorn.set_pixel(h,v,SDLowRedR,SDLowRedG,SDLowRedB)
      finished = 'Y'

    
    
def PlayWormDot():
  
  #Local variables
  moves       = 0
  Finished    = 'N'
  LevelCount  = 3
  Worm1h      = 0
  Worm1v      = 0
  Worm2h      = 0
  Worm2v      = 0
  Worm3h      = 0
  Worm3v      = 0
  SleepTime   = MainSleep / 8
  
  #How often to obstacles appear?
  ObstacleTrigger = 150
  SpeedupTrigger  = 100
  SpeedupMultiplier = 0.99
  
  
  
  #def __init__(self,h,v,r,g,b,direction,speed,alive,name,trail,score,maxtrail,erasespeed):
  Worm1Dot = Dot(Worm1h,Worm1v,SDLowBlueR,SDLowBlueG,SDLowBlueB,(random.randint(1,5)),10,1,'Blue',(Worm1h, Worm1v), 0, 1,0.03)
  Worm2Dot = Dot(Worm2h,Worm2v,SDLowPurpleR,SDLowPurpleG,SDLowPurpleB,(random.randint(1,5)),10,1,'Purple',(Worm2h,Worm2v),0, 1,0.03)
  Worm3Dot = Dot(Worm3h,Worm3v,SDDarkOrangeR,SDDarkOrangeG,SDDarkOrangeB,(random.randint(1,5)),10,1,'Orange',(Worm3h,Worm3v),0, 1,0.03)
 
  
  #Title
  unicorn.off()
  ShowScrollingBanner("Worms",SDDarkOrangeR,SDDarkOrangeG,SDDarkOrangeB,ScrollSleep)
    

  
  while (LevelCount > 0):
    print ("show worms")
    unicorn.off()
    #Display animation and clock every 30 seconds

    print ("Show level")
    ShowLevelCount(LevelCount)
    LevelCount = LevelCount - 1
    unicorn.off()
    #print ("===============================")
  
    #Reset Variables between rounds
    Worm1Dot.speed = 10
    Worm2Dot.speed = 10
    Worm3Dot.speed = 10
    Worm1Dot.maxtrail = 0
    Worm2Dot.maxtrail = 0
    Worm3Dot.maxtrail = 0
    Worm1Dots = 0
    Worm2Dots = 0
    Worm3Dots = 0
    LevelFinished = 'N'
    moves     = 0

    #Place obstacles
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    PlaceGreenObstacle()
    
    
    #Increase length of trail
    Worm1Dot.maxtrail = Worm1Dot.maxtrail + 1
    Worm2Dot.maxtrail = Worm2Dot.maxtrail + 1
    Worm3Dot.maxtrail = Worm3Dot.maxtrail + 1
    
    #Set random starting points
    Worm1h = random.randint(1,6)
    Worm1v = random.randint(1,6)
    Worm2h = random.randint(1,6)
    Worm2v = random.randint(1,6)
    Worm3h = random.randint(1,6)
    Worm3v = random.randint(1,6)
    while (Worm2h == Worm1h and Worm2v == Worm1v):
      Worm2h = random.randint(1,6)
      Worm2v = random.randint(1,6)
    while ((Worm3h == Worm2h and Worm3v == Worm2v) or (Worm3h == Worm1h and Worm3v == Worm1v)):
      Worm3h = random.randint(1,6)
      Worm3v = random.randint(1,6)
      
         
      
    Worm1Dot.h         = Worm1h
    Worm1Dot.v         = Worm1v
    Worm1Dot.direction = (random.randint(1,4))
    Worm1Dot.alive     = 1
    Worm1Dot.trail     = [(Worm1h, Worm1v)]
    
    Worm2Dot.h         = Worm2h
    Worm2Dot.v         = Worm2v
    Worm2Dot.direction = (random.randint(1,4))
    Worm2Dot.alive     = 1
    Worm2Dot.trail     = [(Worm2h, Worm2v)]
    

    Worm3Dot.h         = Worm3h
    Worm3Dot.v         = Worm3v
    Worm3Dot.direction = (random.randint(1,4))
    Worm3Dot.alive     = 1
    Worm3Dot.trail     = [(Worm3h, Worm3v)]

    while (LevelFinished == 'N'):
      
      #reset variables
      #Display animation and clock every X seconds
      if (CheckElapsedTime(CheckTime) == 1):
        ScrollScreenShowChickenWormTime('up',ScrollSleep)


      
      
      #print ("direction:",Worm1Dot.direction,Worm2Dot.direction,Worm3Dot.direction)
      #Display dots if they are alive
      if (Worm1Dot.alive == 1):
        Worm1Dot.Display()
      if (Worm2Dot.alive == 1):
        Worm2Dot.Display()
      if (Worm3Dot.alive == 1):
        Worm3Dot.Display()
      unicorn.show()
    

      #Calculate Movement
      moves = moves +1

      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = PollKeyboard()
        if (Key == 'q'):
          LevelFinished = 'Y'
          LevelCount = 0
          return
      
      #PlaceObstacle and Increase Speed of the game
      m,r = divmod(moves,ObstacleTrigger)
      if (r==0):
        PlaceGreenObstacle()
        SleepTime = SleepTime * SpeedupMultiplier

      #PlaceSpeedupPill
      m,r = divmod(moves,SpeedupTrigger)
      if (r==0):
        PlaceSpeedupPill()
        
        
      if (Worm1Dot.alive == 1):
        m,r = divmod(moves,Worm1Dot.speed)
        if (r == 0):
          MoveDot(Worm1Dot)
          Worm1Dot.score = Worm1Dot.score + 1
          #check for head on collisions
          if ((Worm1Dot.h == Worm2Dot.h and Worm1Dot.v == Worm2Dot.v and Worm2Dot.alive == 1) or (Worm1Dot.h == Worm3Dot.h and Worm1Dot.v == Worm3Dot.v and Worm3Dot.alive == 1)):
            #Worm1Dot.alive = 0
            #Worm1Dot.EraseTrail()
            Worm1Dot.maxtrail - 1
            if (Worm1Dot.maxtrail <= 0):
              Worm1Dot.maxtrail = 1
            Worm1Dot.speed = Worm1Dot.speed + 2

      if (Worm2Dot.alive == 1):
        m,r = divmod(moves,Worm2Dot.speed)
        if (r == 0):
          #Worm2Dot.trail.append((Worm2Dot.h, Worm2Dot.v))
          MoveDot(Worm2Dot)
          Worm2Dot.score = Worm2Dot.score + 1
          #check for head on collisions
          if ((Worm2Dot.h == Worm3Dot.h and Worm2Dot.v == Worm3Dot.v and Worm3Dot.alive == 1) or (Worm2Dot.h == Worm1Dot.h and Worm2Dot.v == Worm1Dot.v and Worm1Dot.alive == 1)):
            #Worm2Dot.alive = 0
            #Worm2Dot.EraseTrail()
            Worm2Dot.maxtrail - 1
            if (Worm2Dot.maxtrail <= 0):
              Worm1Dot.maxtrail = 1
            Worm2Dot.speed = Worm2Dot.speed + 2

      if (Worm3Dot.alive == 1):
        m,r = divmod(moves,Worm3Dot.speed)
        if (r == 0):
          #Worm3Dot.trail.append((Worm3Dot.h, Worm3Dot.v))
          MoveDot(Worm3Dot)
          Worm3Dot.score = Worm3Dot.score + 1
          #check for head on collisions
          if ((Worm3Dot.h == Worm2Dot.h and Worm3Dot.v == Worm2Dot.v and Worm2Dot.alive == 1) or (Worm3Dot.h == Worm1Dot.h and Worm3Dot.v == Worm1Dot.v and Worm1Dot.alive == 1)):
            #Worm3Dot.alive = 0
            #Worm3Dot.EraseTrail()
            Worm3Dot.maxtrail - 1
            if (Worm3Dot.maxtrail <= 0):
              Worm1Dot.maxtrail = 1
            Worm3Dot.speed = Worm3Dot.speed + 2
      
      #Trim length of Tails
      TrimTrail(Worm1Dot)
      TrimTrail(Worm2Dot)
      TrimTrail(Worm3Dot)
      
      
      if(Worm1Dot.alive == 0 and Worm2Dot.alive == 0 and Worm3Dot.alive == 0):
        LevelFinished = 'Y'
      
      #print ("Alive:",Worm1Dot.alive,Worm2Dot.alive,Worm3Dot.alive)
    
      PlayersAlive = Worm1Dot.alive + Worm2Dot.alive + Worm3Dot.alive
      if (PlayersAlive == 2):
        SleepTime = (SleepTime )
      elif (PlayersAlive == 1):
        SleepTime = (SleepTime )
      time.sleep(SleepTime)
    
    
  
  #Calculate Game score
  FinalWinner = ''
  FinalScore  = 0
  Finalr      = 0
  Finalg      = 0
  Finalb      = 0
  if (Worm1Dot.score > Worm2Dot.score and Worm1Dot.score >= Worm3Dot.score):
    FinalScore  = Worm1Dot.score
    FinalWinner = Worm1Dot.name
    Finalr      = Worm1Dot.r
    Finalg      = Worm1Dot.g
    Finalb      = Worm1Dot.b
  elif (Worm2Dot.score >= Worm1Dot.score and Worm2Dot.score >= Worm3Dot.score):
    FinalScore  = Worm2Dot.score
    FinalWinner = Worm2Dot.name
    Finalr      = Worm2Dot.r
    Finalg      = Worm2Dot.g
    Finalb      = Worm2Dot.b
  else:
    FinalScore = Worm3Dot.score
    FinalWinner = Worm3Dot.name
    Finalr      = Worm3Dot.r
    Finalg      = Worm3Dot.g
    Finalb      = Worm3Dot.b

  unicorn.off()
  ScrollString = FinalWinner + ' ' + str(FinalScore)
  
  ShowScrollingBanner(ScrollString,Finalr,Finalg,Finalb,ScrollSleep)
  ShowScrollingBanner("GAME OVER",SDLowPinkR,SDLowPinkG,SDLowPinkB,ScrollSleep)


#--------------------------------------
#  SpaceDot                          --
#--------------------------------------


#We need an 8 x 8 grid to represent the playfield
#each ship, each missile, each bunker will be an object that
#is located on the playfield.  That way we can scan the individual 
#objects and not have to rely on the pixel colors to determine what is what




def CheckBoundarySpaceDot(h,v):
  BoundaryHit = 0
  if (v < 0 or v > 6 or h < 0 or h > 7):
    BoundaryHit = 1
  return BoundaryHit;




  
def ScanSpaceDot(h,v,Playfield):
# I am keeping this simple for now, will remove color checking later
# border
# empty
# wall

#  print ("SSD - HV:",h,v)
#  Item = ''
  OutOfBounds = CheckBoundarySpaceDot(h,v)
  
  if (OutOfBounds == 1):
    Item = 'border'
#    print ("Border found HV: ",h,v)
  else:
    #FlashDot(h,v,0.005)
    Item = Playfield[h][v].name
    
  return Item
  
  
def ScanShip(h,v,direction,Playfield):
  ScanDirection = 0
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']

  
  # We will scan 5 spots around the dot
  # and 6 more in front
  
  # Note: we now have grass, so the scan distance is 1 level shorter
  #       It will be complicated to remove slot 7 
  #       (because of the use of slots 11,12,13, so I will instead populate it
  #       with a copy of slot 6.
  #       
  #  F6 F7 F8
  #     F5
  #     F4
  #     F3
  #     F2
  #     F1
  #  LF FF FR
  #  LL    RR 
  #
  #  11 12 13
  #    10
  #     9
  #     8
  #     7
  #     6
  #  2  3  4
  #  1     5
  #
  
  #Scanning Probe
  #Turn left move one + SCAN
  #Turn Right move one + SCAN
  #Turn Right Move one + SCAN 
  #Move one + SCAN 
  #Turn Right Move one + SCAN 
  
  
  #LL 1
  ScanDirection = TurnLeft(direction)
  ScanH, ScanV = CalculateDotMovement(h,v,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #LF 2
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #FF 3
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #FR 4
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #RR 5
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)

  #F1 6
  ScanDirection = ReverseDirection(ScanDirection)
  ScanH, ScanV  = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = TurnLeft(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)

  #F2 7
  # This slot has become redundant due to a shorter playfield.
  #ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #F3 8
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #F4 9
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)

  #F5 10
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)

  #F6 11
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = TurnLeft(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)

  #F7 12
  ScanDirection = ReverseDirection(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)

  #F8 13
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)

  return ItemList;


def ScanBomberShip(BomberShip, Playfield):
  ScanDirection = BomberShip.direction
  ScanH         = BomberShip.h
  ScanV         = BomberShip.v
  Item          = ''
  ItemList      = ['NULL']

  
  # We will scan 5 spots around the dot
  # and 6 more in front
  
  # Note: we now have grass, so the scan distance is 1 level shorter
  #       It will be complicated to remove slot 7 
  #       (because of the use of slots 11,12,13, so I will instead populate it
  #       with a copy of slot 6.
  #       
  
  #
  #          
  #      
  #  1  .  .  .  3
  #  x  x  2  x  x
  #        4
  #        5

  
  
  
  #1
  ScanH = ScanH-1
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #2
  ScanH, ScanV = ScanH +2, ScanV + 1
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #3
  ScanH, ScanV = ScanH + 2, ScanV -1
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #4
  ScanH, ScanV = ScanH -2, ScanV + 2
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  
  #5
  ScanH = ScanH + 1
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)

  return ItemList;


  
  
def HitBomber(BomberShip,Playfield):
  h = BomberShip.h
  v = BomberShip.v
  if (BomberShip.lives > 0):
    BomberShip.lives = BomberShip.lives - 1
  else:
    BomberShip.alive = 0

    PlayerShipExplosion.Animate(h-2,v-2,'forward',0.025)
    #Erase playfield (ship is 3 dots across)
    if (h > 0 and h <= 7):
      Playfield[h][v] = Empty
    if (h+1 > 0 and h+1 <= 7):
      Playfield[h+1][v] = Empty
    if (h+2 > 0 and h+2 <= 7):
      Playfield[h+2][v] = Empty

  
def AdjustSpeed(Ship,setting,amount):
  #print ("AS - BEFORE Ship.name Ship.speed setting amount",Ship.name, Ship.speed, setting,amount)
  if (setting == 'slow'):
    Ship.speed = Ship.speed + amount
  else:
    Ship.speed = Ship.speed - amount
  
  if (Ship.speed <= 10):
    Ship.speed = 10
  elif (Ship.speed >= 50):
    Ship.speed = 50   
  #print ("AS - AFTER Ship.name Ship.speed setting amount",Ship.name, Ship.speed, setting,amount)
  

def ExplodeMissile(Ship,Playfield,increment):
  #print("EM - ExplodeMissile Ship.exploding: ",Ship.exploding)
  #print("EM - Before: ",Ship.name, "HV",Ship.h,Ship.v," rgb",Ship.r,Ship.g,Ship.b)
  Ship.r = Ship.r + increment
  Ship.g = 0 #Ship.g + increment
  Ship.b = 0 #Ship.b + increment

  #After explosion, reset colors
  if (Ship.r >= 255 or Ship.g >= 255 or Ship.b >= 255):
    if (Ship.name == 'PlayerMissile'):
      Ship.r = PlayerMissileR
      Ship.g = PlayerMissileG
      Ship.b = PlayerMissileB
    elif (Ship.name == 'Asteroid'):
      Ship.r = SDDarkOrangeR
      Ship.g = SDDarkOrangeG
      Ship.b = SDDarkOrangeB
    elif (Ship.name == 'UFOMissile'):
      Ship.r = PlayerMissileR
      Ship.g = PlayerMissileG
      Ship.b = PlayerMissileB
    elif (Ship.name == 'UFO'):
      Ship.r = SDDarkPurpleR
      Ship.g = SDDarkPurpleG
      Ship.b = SDDarkPurpleB


    Ship.exploding = 0
    Ship.alive     = 0
    #print ("Ship Exploded")
    Ship.Erase()
    Playfield[Ship.h][Ship.v] = Empty

  if (Ship.exploding == 1):
    unicorn.set_pixel(Ship.h,Ship.v,255,255,255)
    unicorn.set_pixel(Ship.h,Ship.v,Ship.r,Ship.g,Ship.b)
  #print("EM - Ship.exploding: ",Ship.exploding)
  #print("EM - After: ",Ship.name, "HV",Ship.h,Ship.v," rgb",Ship.r,Ship.g,Ship.b)
  
  
def MovePlayerShip(Ship,Playfield):
  #print ("moveship Direction HV:",Ship.name,Ship.direction,Ship.h,Ship.v)
  
  #Player ships always points up, enemy ships point down
  h = Ship.h
  v = Ship.v
  ItemList = []
  #Scan all around, make decision, move
  ItemList = ScanShip(Ship.h,Ship.v,Ship.scandirection,Playfield)
  
  #print("MPS - ItemList",ItemList)
  #print("MPS - Ship.name HV",Ship.name,Ship.h,Ship.v)
  #get possible items, then prioritize

  #Priority
  # 1 Evade close objects
  # 2 Blast far objects

  #If UFO is detected, fire missile!
  if ("UFO" in ItemList or "Asteroid" in ItemList or "UFOMissile" in ItemList or "BomberShip" in ItemList):
    if (PlayerMissile1.alive == 0 and PlayerMissile1.exploding == 0):
      #print ("MPS - UFO/Bomber/asteroid Detected PlayerMissile1.alive:",PlayerMissile1.alive)
      PlayerMissile1.h = h
      PlayerMissile1.v = v
      PlayerMissile1.alive = 1
      PlayerMissile1.exploding = 0
        
    elif (PlayerMissile2.alive == 0 and PlayerMissile2.exploding == 0):
      #print ("MPS - UFO or asteroid Detected PlayerMissile1.alive:",PlayerMissile1.alive)
      PlayerMissile2.h = h
      PlayerMissile2.v = v
      PlayerMissile2.alive = 1
      PlayerMissile2.exploding = 0

  #Follow UFO
  #slow down if ahead of UFO, speed up if behind
  if (ItemList[11] == 'UFO' or ItemList[11] == 'BomberShip'):
    #print ("****************************")
    #print ("****************************")
    #print ("****************************")
    Ship.direction = Playfield[h-1][0].direction
    #print ("MPS - ENEMY TO LEFT Enemy.name HV direction",Playfield[h-1][0].name,Playfield[h-1][0].h,Playfield[h-1][0].v, Playfield[h-1][0].direction)
    if (Playfield[h-1][0].direction == 4):
      AdjustSpeed(Ship,'fast',5)
    elif (Playfield[h-1][0].direction == 2):
      AdjustSpeed(Ship,'slow',1)
    
  elif (ItemList[13] == 'UFO' or ItemList[13] == 'BomberShip'):

    #for x in range (0,8):
      #for y in range (0,8):
        #print("Playfield[x][y].name HV speed direction: ",x,y,Playfield[x][y].name,Playfield[x][y].h,Playfield[x][y].v,Playfield[x][y].speed,Playfield[x][y].direction)


    Ship.direction = Playfield[h+1][0].direction
    print ("MPS - ENEMY TO RIGHT Enemy.name HV direction",Playfield[h+1][0].name,Playfield[h+1][0].h,Playfield[h+1][0].v, Playfield[h+1][0].direction)
    if (Playfield[h+1][0].direction == 2):
      #print ("MPS - adjusting speed fast 3")
      AdjustSpeed(Ship,'fast',4)
    elif (Playfield[h+1][0].direction == 4):
      #print ("MPS - adjusting speed slow 1")
      AdjustSpeed(Ship,'slow',1)
  
    
  #print("MPS - 1Ship.direction: ",Ship.direction)
    
  
  #if heading to boundary or wall Reverse direction
  #print("checking border")
  if ((Ship.direction == 4 and ItemList[1] == 'border') or
      (Ship.direction == 2 and ItemList[5] == 'border')):
    Ship.direction = ReverseDirection(Ship.direction)
    #print ("MPS - border detected, reversing direction")
    AdjustSpeed(Ship,'slow',1)
    #print("MPS - 2Ship.direction: ",Ship.direction)
  
  #Evade close objects
  # - if object in path of travel, reverse direction
  elif ((Ship.direction == 4 and (ItemList[1] <> 'empty' or ItemList[2] <> 'empty')) or
        (Ship.direction == 2 and (ItemList[5] <> 'empty' or ItemList[4] <> 'empty'))):      
    Ship.direction = ReverseDirection(Ship.direction)
    #print("MPS - object in path, reversed direction")
    #print("MPS - 3Ship.direction: ",Ship.direction)
    

  # - speed up and move if object is directly above
  elif ((Ship.direction == 4 and (ItemList[3] <> 'empty' and ItemList[1] == 'empty')) or
        (Ship.direction == 2 and (ItemList[3] <> 'empty' and ItemList[5] == 'empty'))):
    AdjustSpeed(Ship,'fast',8)
    Ship.h, Ship.v =  CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    #print("MPS - speeding up to avoid collision")
    #print("MPS - 4Ship.direction: ",Ship.direction)

  # - travelling left, move if empty
  # - travelling right, move if empty
  # - randomly switch directions
  elif ((ItemList[1] == 'empty' and Ship.direction == 4) or 
        (ItemList[5] == 'empty' and Ship.direction == 2 )):
    if ((random.randint(0,7) == 1) and Ship.h <> 0 and Ship.h <> 7):
      Ship.direction = ReverseDirection(Ship.direction)
    Ship.h, Ship.v =  CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    #print("MPS - Travelling, move if empty")
    #print("MPS - 5Ship.direction: ",Ship.direction)


  #if nothing nearby, and near the middle, stop moving
  if (ItemList[1]  == 'empty' and
      ItemList[2]  == 'empty' and
      ItemList[3]  == 'empty' and
      ItemList[4]  == 'empty' and
      ItemList[5]  == 'empty' and
      ItemList[6]  == 'empty' and
      ItemList[7]  == 'empty' and
      ItemList[8]  == 'empty' and
      ItemList[9]  == 'empty' and
      ItemList[10] == 'empty' and
      ItemList[12] == 'empty' and Ship.h >= 3 and Ship.h <= 4):
    if (random.randint (0,5) <> 1):
      #print ("MPS - Staying in the middle")
      Ship.h = h
      Ship.v = v
    
  #print("MPS - 6Ship.direction: ",Ship.direction)

  #print("MPS - OldHV: ",h,v, " NewHV: ",Ship.h,Ship.v, "direction: ",Ship.direction)
  Playfield[Ship.h][Ship.v]= Ship
  Ship.Display()
  
  if ((h <> Ship.h or v <> Ship.v) or
     (Ship.alive == 0)):
    Playfield[h][v] = Empty
    unicorn.set_pixel(h,v,0,0,0)
    #print ("MPS - Erasing Player")
  unicorn.show()

  #print("MPS - 7Ship.direction: ",Ship.direction)

  return 

  
def MoveEnemyShip(Ship,Playfield):
  #print ("MES - moveship Direction HV:",Ship.name,Ship.direction,Ship.h,Ship.v)
  
  #Player ships always points up, enemy ships point down
  h = Ship.h
  v = Ship.v
  ItemList = []
  #Scan all around, make decision, move
  ItemList = ScanShip(Ship.h,Ship.v,Ship.scandirection,Playfield)
  #print("MES - ItemList: ",ItemList)    
  #get possible items, then prioritize

  #Priority
  # 1 Shoot Player
  

  #If player is detected, fire missile!
  if ("Player1" in ItemList):
    if (UFOMissile1.alive == 0 and UFOMissile1.exploding == 0):
      UFOMissile1.h = h
      UFOMissile1.v = v
      UFOMissile1.alive = 1
    elif (UFOMissile2.alive == 0 and UFOMissile2.exploding == 0):
      UFOMissile2.h = h
      UFOMissile2.v = v
      UFOMissile2.alive = 1
    elif (UFOMissile3.alive == 0 and UFOMissile3.exploding == 0):
      UFOMissile3.h = h
      UFOMissile3.v = v
      UFOMissile3.alive = 1
    

  
  #UFO goes from one side to the other
  #print("checking border")
  if ((Ship.direction == 2 and ItemList[1] == 'border') or
      (Ship.direction == 4 and ItemList[5] == 'border')):
    #Ship.alive = 0
    Ship.v = Ship.v + 1
    if (Ship.v > 5):
      Ship.v = 5
    Ship.direction = ReverseDirection(Ship.direction)
    Ship.h, Ship.v =  CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    if (Ship.h == 6):
      Ship.h = 7
    elif (Ship.h == 1):
      Ship.h == 0
    
    #print ("MES - hit border, died")
  

  # - travelling left, move if empty
  # - travelling right, move if empty
  elif ((ItemList[5] == 'empty' and Ship.direction == 4) or 
        (ItemList[1] == 'empty' and Ship.direction == 2 )):
    Ship.h, Ship.v =  CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    #print("MES - Travelling, move if empty")
      
      
  #print("OldHV: ",h,v, " NewHV: ",Ship.h,Ship.v)
  Playfield[Ship.h][Ship.v]= Ship
  Ship.Display()
  
  if ((h <> Ship.h or v <> Ship.v) or
     (Ship.alive == 0)):
    Playfield[h][v] = Empty
    unicorn.set_pixel(h,v,0,0,0)
    #print ("MES - Erasing UFO")
  unicorn.show()

  return 
  

def MoveBomberShip(BomberShip,BomberSprite,Playfield):
  #print ("MBS - Name Direction HV:",BomberShip.name,Ship.direction,Ship.h,Ship.v)
  
  #Player ships always points up, enemy ships point down
  h = BomberShip.h
  v = BomberShip.v
  ItemList = []
  #Scan all around, make decision, move
  ItemList = ScanBomberShip(BomberShip,Playfield)
  
  #Priority
  # 1 Shoot Player
  


  #Bomber needs to be allowed to go off the screen
  
  
  #Bomber goes from one side to the other
  #print("checking border")
  if ((BomberShip.direction == 2 and ItemList[1] == 'border' and BomberShip.h > 1)):
    BomberShip.v = BomberShip.v + 1
    BomberShip.direction = ReverseDirection(BomberShip.direction)
  elif ((BomberShip.direction == 4 and ItemList[3] == 'border' and BomberShip.h < 5)):
    BomberShip.v = BomberShip.v + 1
    BomberShip.direction = ReverseDirection(BomberShip.direction)

  BomberShip.h, BomberShip.v =  CalculateDotMovement(BomberShip.h,BomberShip.v,BomberShip.direction)
  
  # - travelling left, move if empty
  # - travelling right, move if empty
  if ((ItemList[3] == 'empty' and BomberShip.direction == 4) or 
     (ItemList[1] == 'empty' and BomberShip.direction == 2 )):
    BomberShip.h, BomberShip.v =  CalculateDotMovement(BomberShip.h,BomberShip.v,BomberShip.direction)
    #print("MES - Travelling, move if empty")
      
      
#  print("MBS - OldHV: ",h,v, " NewHV: ",BomberShip.h,BomberShip.v)
#  if (BomberShip.direction == 2):
#    print ("MBS - check boundary - h+2,V",BomberShip.h+2,BomberShip.v)
#    if ((CheckBoundary(BomberShip.h+2,BomberShip.v) == 0)):
#      Playfield[BomberShip.h+2][BomberShip.v] = Empty
#    if ((CheckBoundary(BomberShip.h-1,BomberShip.v) == 0)):
#      Playfield[BomberShip.h-1][BomberShip.v] = Empty
      
#  if (BomberShip.direction == 4):
#    if ((CheckBoundary(BomberShip.h-1,BomberShip.v) == 0)):
#      Playfield[BomberShip.h-1][BomberShip.v] = Empty
#    if ((CheckBoundary(BomberShip.h+1,BomberShip.v) == 0)):
#      Playfield[BomberShip.h+1][BomberShip.v] = Empty
  
  

  return 
  
  

def MoveMissile(Missile,Playfield):
  global Empty
  #print ("MM - MoveMissile:",Missile.name)
  
  #Record the current coordinates
  h = Missile.h
  v = Missile.v

  
  #Missiles simply drop to bottom and kablamo!
  #FF (one square in front of missile direction of travel)
  ScanH, ScanV = CalculateDotMovement(Missile.h,Missile.v,Missile.scandirection)
  Item = ScanSpaceDot(ScanH,ScanV,Playfield)
  
  #print("Item: ",Item)
  
  #Priority
  # 1 Hit target
  # 2 See if we are hit by enemy missle
  # 3 Move forward
  
  #BomberShip is special
  if (Item == 'BomberShip'):
    #print ("MM - Playfield - BEFORE Bomberhit",Playfield[ScanH][ScanV].name)
    HitBomber(Playfield[ScanH][ScanV],Playfield)  
    #print ("MM - Playfield - AFTER Bomberhit",Playfield[ScanH][ScanV].name)
    Missile.h = ScanH
    Missile.v = ScanV
    #Playfield[Missile.h][Missile.v] = Missile
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0
    #print ("MM - Bomber Hit!: ",Item)

  #See if other target ship is hit
  elif (Item  == 'Player1' or Item == 'UFO' or Item == 'UFOMissile' or Item == 'Asteroid'):
    #target hit, kill target
    Playfield[ScanH][ScanV].alive = 0
    Playfield[ScanH][ScanV]= Empty
    unicorn.set_pixel(ScanH,ScanV,0,0,0)
    unicorn.set_pixel(h,v,0,0,0)

    Missile.h = ScanH
    Missile.v = ScanV
    #Playfield[Missile.h][Missile.v] = Missile
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0
  
#  elif (Item  == 'PlayerMissile'):
#    #We are hit
#    Missile.Alive = 0
#    Missile.exploding = 1
#    Playfield[ScanH][ScanV].alive = 0
#    Playfield[ScanH][ScanV]= Empty
#    Missile.Erase()
#    print ("MM - We have been  hit!")
  
  #Player missiles fire off into space
  #Enemy missiles explode on ground
  elif (Item == 'border' and Missile.name == 'PlayerMissile'):
    #print ("MM - Missile hit border")
    Missile.alive  = 0
    Missile.exploding = 0
    Missile.Erase()
  elif (Item == 'border' and (Missile.name == 'UFOMissile' or Missile.name == 'Asteroid')):
    #print ("MM - Missile hit border")
    Missile.alive  = 0
    Missile.exploding = 1
    Missile.Erase()
    #print ("MM - UFO hit border HV:",Missile.h,Missile.v)
    
  #empty = move forward
  elif (Item == 'empty' and Missile.alive == 1):
    Missile.h = ScanH
    Missile.v = ScanV
    Playfield[Missile.h][Missile.v] = Missile
    Missile.Display()
    #print ("MM - empty, moving forward")
    

  if ((h <> Missile.h or v <> Missile.v) or
     (Missile.alive == 0)):
    Playfield[h][v] = Empty
    unicorn.set_pixel(h,v,0,0,0)
    #print ("MM - Erasing Missile")
  unicorn.show()
  
  return 


  
def PlaySpaceDot():
  
  
  unicorn.off()
  
  #Local variables
  moves       = 0
  Finished    = 'N'
  LevelCount  = 3
  Playerh     = 0
  Playerv     = 0
  SleepTime   = MainSleep / 4
  ChanceOfUFO = 200
  ChanceOfAsteroid1 = 500
  ChanceOfAsteroid2 = 2000
  ChanceOfAsteroid3 = 3000
  ChanceOfAsteroid4 = 40000
  ChanceOfBomberShip = 1000
  
  PlanetSurfaceSleep = 100
  
  #define sprite objects
  #def __init__(self,h,v,r,g,b,direction,scandirection,speed,alive,lifes,name,score,exploding):
  PlayerShip = Ship(3,6,PlayerShipR,PlayerShipG,PlayerShipB,4,1,10,1,3,'Player1', 0,0)
  EnemyShip  = Ship(7,0,SDLowPurpleR,SDLowPurpleG,SDLowPurpleB,4,3,50,0,3,'UFO', 0,0)
  Asteroid1  = Ship(0,0,SDLowOrangeR,SDLowOrangeG,SDLowOrangeB,3,3,25,0,1,'Asteroid', 0,0)
  Asteroid2  = Ship(0,0,SDLowOrangeR,SDLowOrangeG,SDLowOrangeB,3,3,25,0,1,'Asteroid', 0,0)
  Asteroid3  = Ship(0,0,SDMedOrangeR,SDMedOrangeG,SDMedOrangeB,3,3,25,0,1,'Asteroid', 0,0)
  Asteroid4  = Ship(0,0,SDMedRedR,SDMedRedG,SDMedRedB,3,3,25,0,1,'Asteroid', 0,0)
  Empty      = Ship(-1,-1,0,0,0,0,1,0,0,0,'empty',0,0)
   
  BomberShip.h = -2
  BomberShip.v = 0
  BomberShip.alive = 0
  
  
  #Create playfield
  Playfield = ([[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]])

 
  
  #Reset Playfield
  for x in range (0,8):
    for y in range (0,8):
      #print ("XY",x,y)
      Playfield[x][y] = Empty
               
  Playfield[PlayerShip.h][PlayerShip.v] = PlayerShip

  #Title
  unicorn.off()
  ShowScrollingBanner("SpaceDot",SDLowOrangeR,SDLowOrangeG,SDLowOrangeB,ScrollSleep)

  #Animation Sequence
  ShowBigShipTime(ScrollSleep)  

  
  while (LevelCount > 0):
    print ("show playership")
    unicorn.off()
    print ("Show level")

    ShowLevelCount(LevelCount)
    LevelCount = LevelCount - 1
    unicorn.off()
    
    #Reset Variables between rounds
    LevelFinished     = 'N'
    moves             = 1
    PlayerShip.alive  = 1
    PlayerShip.speed  = 10
    PlayerShip.h      = random.randint (0,7)
    if (random.randint(0,2) == 1):
      PlayerShip.direction = 2
    else:
      PlayerShip.direction = 4
    EnemyShip.alive   = 0
    UFOMissile1.alive = 0
    UFOMissile2.alive = 0
    EnemyShip.speed   = random.randint (5,25)
    Asteroid1.alive = 0
    Asteroid2.alive = 0
    Asteroid3.alive = 0
    Asteroid4.alive = 0
    Asteroid1.speed = random.randint(1,25)
    Asteroid2.speed = random.randint(5,30)
    Asteroid3.speed = random.randint(5,50)
    Asteroid4.speed = random.randint(2,50)
    
    #Reset colors
    UFOMissile1.r = PlayerMissileR
    UFOMissile1.g = PlayerMissileG
    UFOMissile1.b = PlayerMissileB
    UFOMissile2.r = PlayerMissileR
    UFOMissile2.g = PlayerMissileG
    UFOMissile2.b = PlayerMissileB
    UFOMissile3.r = PlayerMissileR
    UFOMissile3.g = PlayerMissileG
    UFOMissile3.b = PlayerMissileB
    PlayerMissile1.r = PlayerMissileR
    PlayerMissile1.g = PlayerMissileG
    PlayerMissile1.b = PlayerMissileB
    BomberShip.alive = 0
    BomberShip.lives = 3
    
    
    #Reset Playfield
    for x in range (0,8):
      for y in range (0,8):
        #print ("XY",x,y)
        Playfield[x][y] = Empty
                 
    Playfield[PlayerShip.h][PlayerShip.v] = PlayerShip

    #Draw bottom background
    for i in range (0,8):
      unicorn.set_pixel(i,7,SDDarkYellowR,SDDarkYellowG,SDDarkYellowB)

    
    # Main timing loop
    while (LevelFinished == 'N' and PlayerShip.alive == 1):
      moves = moves + 1
      
      #Draw bottom background
      m,r = divmod(moves,PlanetSurfaceSleep)  
      for i in range (0,8):
        unicorn.set_pixel(i,7,SDDarkYellowR,SDDarkYellowG,SDDarkYellowB)

      
      ChanceOfAsteroid1 = ChanceOfAsteroid1 -1
      if (ChanceOfAsteroid1 <= 20):
        ChanceOfAsteroid1 = 1000
      ChanceOfAsteroid2 = ChanceOfAsteroid2 -1
      if (ChanceOfAsteroid2 <= 20):
        ChanceOfAsteroid2 = 2000
      ChanceOfAsteroid3 = ChanceOfAsteroid3 -1
      if (ChanceOfAsteroid3 <= 20):
        ChanceOfAsteroid3 = 3000
      ChanceOfAsteroid4 = ChanceOfAsteroid4 -1
      if (ChanceOfAsteroid4 <= 20):
        ChanceOfAsteroid4 = 4000

      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = PollKeyboard()
        if (Key == 'Q' or Key == 'q'):
          LevelCount = 0
          return
      
#      print ("=================================================")
#      for H in range(0,7):
#        for V in range (0,7):
#          if (Playfield[H][V].name <> 'empty'):
#            print ("Playfield: HV Name",H,V,Playfield[H][V].name)
#      print ("=================================================")
      


      
      if (PlayerShip.alive == 1):
        #print ("M - Playership HV speed alive exploding direction: ",PlayerShip.h, PlayerShip.v,PlayerShip.speed, PlayerShip.alive, PlayerShip.exploding, PlayerShip.direction)
        #print ("M - moves: ", moves)        
        m,r = divmod(moves,PlayerShip.speed)
        if (r == 0):
          MovePlayerShip(PlayerShip,Playfield)
          i = random.randint(0,2)
          if (i >= 0):
            AdjustSpeed(PlayerShip,'fast',1)
            
      
      if (EnemyShip.alive == 1):
        m,r = divmod(moves,EnemyShip.speed)
        if (r == 0):
          MoveEnemyShip(EnemyShip,Playfield)
          


      #print ("M - Bombership Alive Lives HV:",BomberShip.alive, BomberShip.lives,BomberShip.h,BomberShip.v)
      if (BomberShip.alive == 1):
        m,r = divmod(moves,BomberShip.speed)
        if (r == 0):
          if (BomberShip.v == 6):
            BomberShip.v = 0
          BomberOldH = BomberShip.h
          BomberOldV = BomberShip.v
          MoveBomberShip(BomberShip,BomberSprite,Playfield)

          BomberSprite.EraseLocation(BomberOldH, BomberOldV)
          if (BomberOldH >= 0 and BomberOldH <= 7):
            Playfield[BomberOldH][BomberOldV] = Empty
          if (BomberOldH+1 >= 0 and BomberOldH+1 <= 7):
            Playfield[BomberOldH+1][BomberOldV] = Empty
          if (BomberOldH+2 >= 0 and BomberOldH+2 <= 7):
            Playfield[BomberOldH+2][BomberOldV] = Empty


          if (BomberShip.h >= 0 and BomberShip.h <= 7):
            Playfield[BomberShip.h][BomberShip.v] = BomberShip
          if (BomberShip.h+1 >= 0 and BomberShip.h+1 <= 7):
            Playfield[BomberShip.h+1][BomberShip.v] = BomberShip
          if (BomberShip.h+2 >= 0 and BomberShip.h+2 <= 7):
            Playfield[BomberShip.h+2][BomberShip.v] = BomberShip
          
         
          BomberSprite.Display(BomberShip.h,BomberShip.v)
          
          
      if (UFOMissile1.alive == 1 and UFOMissile1.exploding == 0):
        m,r = divmod(moves,UFOMissile1.speed)
        if (r == 0):
          MoveMissile(UFOMissile1,Playfield)

      if (UFOMissile2.alive == 1 and UFOMissile2.exploding == 0):
        m,r = divmod(moves,UFOMissile2.speed)
        if (r == 0):
          MoveMissile(UFOMissile2,Playfield)

      if (UFOMissile3.alive == 1 and UFOMissile3.exploding == 0):
        m,r = divmod(moves,UFOMissile3.speed)
        if (r == 0):
          MoveMissile(UFOMissile3,Playfield)

          
      if (PlayerMissile1.alive == 1 and PlayerMissile1.exploding == 0):
        m,r = divmod(moves,PlayerMissile1.speed)
        if (r == 0):
          MoveMissile(PlayerMissile1,Playfield)

      if (PlayerMissile2.alive == 1 and PlayerMissile2.exploding == 0):
        m,r = divmod(moves,PlayerMissile2.speed)
        if (r == 0):
          MoveMissile(PlayerMissile2,Playfield)

      if (Asteroid1.alive == 1):
        m,r = divmod(moves,Asteroid1.speed)
        if (r == 0):
          MoveMissile(Asteroid1,Playfield)
          
      if (Asteroid2.alive == 1):
        m,r = divmod(moves,Asteroid2.speed)
        if (r == 0):
          MoveMissile(Asteroid2,Playfield)
          
      if (Asteroid3.alive == 1):
        m,r = divmod(moves,Asteroid3.speed)
        if (r == 0):
          MoveMissile(Asteroid3,Playfield)

      if (Asteroid4.alive == 1):
        m,r = divmod(moves,Asteroid4.speed)
        if (r == 0):
          MoveMissile(Asteroid4,Playfield)
          

      #Spawn UFO
      m,r = divmod(moves,ChanceOfUFO)
      if (r == 0 and EnemyShip.alive == 0):
        print ("Spawning UFO")
        EnemyShip.alive = 1
        EnemyShip.direction = ReverseDirection(EnemyShip.direction)
        if (EnemyShip.direction == 2):
          EnemyShip.h = 0
          EnemyShip.v = 0
          #EnemyShip.v = random.randint(0,4)
        else:
          EnemyShip.h = 7
          EnemyShip.v = 0
        EnemyShip.Display()


        

      #Spawn BomberShip
      #BomberShip is the dot on the far left.  BomberSprite is drawn using that HV
      m,r = divmod(moves,ChanceOfBomberShip)
      if (r == 0 and BomberShip.alive == 0):
        print ("Spawning BomberShip")
        BomberShip.alive = 1
        BomberShip.lives = 3 #(takes 3 hits to die)
        BomberShip.direction = ReverseDirection(BomberShip.direction)
        if (BomberShip.direction == 2):
          BomberShip.h = -2
          BomberShip.v = 0
          Playfield[0][0] = BomberShip
        else:
          BomberShip.h = 7
          BomberShip.v = 0
          Playfield[7][0] = BomberShip
      if (BomberShip.h >= 3 and BomberShip.h <= 5 and Asteroid4.alive == 0 and BomberShip.lives <=2 and BomberShip.alive == 1):
        Asteroid4.alive = 1
        Asteroid4.speed = 3
        Asteroid4.h = BomberShip.h+1
        Asteroid4.v = BomberShip.v
      
        
          
      #Animate BomberSprite
      m,r = divmod(moves,BomberShip.animationspeed)
      if (r == 0 and BomberShip.alive == 1):
        #print ("M - Animating BomberShip - hv frames currentframe animationspeed",BomberShip.h,BomberShip.v,BomberSprite.frames,BomberSprite.currentframe, BomberShip.animationspeed)
        
        BomberSprite.Display(BomberShip.h,BomberShip.v)
        
        if (BomberSprite.currentframe < (BomberSprite.frames -1)):
          BomberSprite.currentframe = BomberSprite.currentframe +1
        else:
          BomberSprite.currentframe = 0
        
      
          
          
      #Spawn Asteroid1
      m,r = divmod(moves,ChanceOfAsteroid1)
      if (r == 0 and Asteroid1.alive == 0):
        print ("Spawning Asteroid")
        Asteroid1.alive = 1
        Asteroid1.h = random.randint(0,7)
        while (Playfield[Asteroid1.h][0].name <> 'empty'):
          Asteroid1.h = random.randint(0,7)
        Asteroid1.v = 0
        Asteroid1.Display()

      #Spawn Asteroid2
      m,r = divmod(moves,ChanceOfAsteroid2)
      if (r == 0 and Asteroid2.alive == 0):
        print ("Spawning Asteroid2")
        Asteroid2.alive = 1
        Asteroid2.h = random.randint(0,7)
        while (Playfield[Asteroid2.h][0].name <> 'empty'):
          Asteroid2.h = random.randint(0,7)
        Asteroid2.v = 0
        Asteroid2.Display()

      #Spawn Asteroid3
      m,r = divmod(moves,ChanceOfAsteroid3)
      if (r == 0 and Asteroid3.alive == 0):
        print ("Spawning Asteroid3")
        Asteroid3.alive = 1
        Asteroid3.h = random.randint(0,7)
        while (Playfield[Asteroid3.h][0].name <> 'empty'):
          Asteroid3.h = random.randint(0,7)
        Asteroid3.v = 0
        Asteroid3.Display()

      #Spawn Asteroid4
      m,r = divmod(moves,ChanceOfAsteroid4)
      if (r == 0 and Asteroid4.alive == 0):
        print ("Spawning Asteroid4")
        Asteroid4.alive = 1
        Asteroid4.h = random.randint(0,7)
        while (Playfield[Asteroid4.h][0].name <> 'empty'):
          Asteroid4.h = random.randint(0,7)
        Asteroid4.v = 0
        Asteroid4.Display()

        

      #Check for exploding objects
      if (PlayerMissile1.exploding == 1):
        #print("------> PlayerMissile1.exploding: ",PlayerMissile1.exploding)
        ExplodeMissile(PlayerMissile1,Playfield,20)

      if (PlayerMissile2.exploding == 1 ):
        #print("------> PlayerMissile2.exploding: ",PlayerMissile2.exploding)
        ExplodeMissile(PlayerMissile2,Playfield,20)


      if (Asteroid1.exploding == 1 ):
        #print("------> Asteroid1.exploding: ",Asteroid1.exploding)
        ExplodeMissile(Asteroid1,Playfield,20)
              
      if (Asteroid2.exploding == 1 ):
        #print("------> Asteroid2.exploding: ",Asteroid2.exploding)
        ExplodeMissile(Asteroid2,Playfield,20)


      if (Asteroid3.exploding == 1 ):
        #print("------> Asteroid3.exploding: ",Asteroid3.exploding)
        ExplodeMissile(Asteroid3,Playfield,20)

      if (UFOMissile1.exploding == 1 ):
        #print("------> UFOMissile1.exploding: ",UFOMissile1.exploding)
        ExplodeMissile(UFOMissile1,Playfield,20)

      if (UFOMissile2.exploding == 1 ):
        #print("------> UFOMissile2.exploding: ",UFOMissile2.exploding)
        ExplodeMissile(UFOMissile2,Playfield,20)

      if (UFOMissile3.exploding == 1 ):
        #print("------> UFOMissile3.exploding: ",UFOMissile3.exploding)
        ExplodeMissile(UFOMissile3,Playfield,20)

      if (PlayerShip.alive == 0):
        PlayerShipExplosion.Animate(PlayerShip.h-2,PlayerShip.v-2,'forward',0.025)
        
      #Display animation and clock every X seconds
      if (CheckElapsedTime(CheckTime) == 1):
        ScrollScreenShowLittleShipTime('up',ScrollSleep)         
     
      time.sleep(MainSleep / 5)
      
      

#--------------------------------------
#--         Dot Invaders             --
#--------------------------------------


def PutArmadaOnPlayfield(Armada,Playfield):
  #we need to examine the armada, and see which ones are visible and should be put on the playfield

  for x in range (ArmadaWidth):
    for y in range (ArmadaHeight):
      if(Armada[x][y].alive == 1):
        #print ("PAPF - Armada[x][y] HV:",x,y,Armada[x][y].h,Armada[x][y].v)
        #print ("placing on field:",Armada[x][y].name)
        Playfield[Armada[x][y].h][Armada[x][y].v] = Armada[x][y]

def DisplayPlayfield(Playfield):
  for x in range (8):
    for y in range (8):
      if (Playfield[x][y].name <> 'empty'):
        #print("Playfield: ",Playfield[x][y].name)
        Playfield[x][y].Display()
        if (Playfield[x][y].name == 'UFO'):
          FlashDot2(x,y,0.005)
        


def DotInvadersCheckBoundarySpaceDot(h,v):
  BoundaryHit = 0
  if (v < 0 or v > 7 or h < 0 or h > 7):
    BoundaryHit = 1
  return BoundaryHit;

def DotInvadersExplodeMissile(Ship,Playfield,increment):
  Ship.r = Ship.r + increment
  Ship.g = 0 #Ship.g + increment
  Ship.b = 0 #Ship.b + increment

  #After explosion, reset colors
  if (Ship.r >= 255 or Ship.g >= 255 or Ship.b >= 255):
    if (Ship.name == 'PlayerMissile'):
      Ship.r = PlayerMissileR
      Ship.g = PlayerMissileG
      Ship.b = PlayerMissileB
    elif (Ship.name == 'Asteroid'):
      Ship.r = SDDarkOrangeR
      Ship.g = SDDarkOrangeG
      Ship.b = SDDarkOrangeB
    elif (Ship.name == 'UFOMissile'):
      Ship.r = PlayerMissileR
      Ship.g = PlayerMissileG
      Ship.b = PlayerMissileB
    elif (Ship.name == 'UFO'):
      Ship.r = SDDarkPurpleR
      Ship.g = SDDarkPurpleG
      Ship.b = SDDarkPurpleB

    Ship.exploding = 0
    Ship.alive     = 0
    #print ("Ship Exploded")
    Ship.Erase()
    Playfield[Ship.h][Ship.v].alive = 0
    Playfield[Ship.h][Ship.v] = Empty

  if (Ship.exploding == 1):
    unicorn.set_pixel(Ship.h,Ship.v,255,255,255)
    unicorn.set_pixel(Ship.h,Ship.v,Ship.r,Ship.g,Ship.b)
    #print("EM - Ship.exploding: ",Ship.exploding)
    #print("EM - After: ",Ship.name, "HV",Ship.h,Ship.v," rgb",Ship.r,Ship.g,Ship.b)
  
  



def MoveArmada(Armada,Playfield):
  #every ship in the armada will look in the directon they are travelling
  #if a wall is found, drop down a level and reverse direction
  #if you hit the ground, game over

  ScanH = 0
  ScanV = 0
  direction = 0
  x = 0
  y = 0
  #print ("MA - moving armada")
  BorderDetected = 0
  LowestV = 0


#  print ("=====***************************************************================")
#  for x in range(ArmadaWidth-1,-1,-1):
#    for y in range (ArmadaHeight-1,-1,-1):
#      h = Armada[x][y].h
#      v = Armada[x][y].v
#      FlashDot(h,v,0.005)
#      print ("XY hv Alive Armada.Name Playfield.Name",x,y,h,v,Armada[x][y].alive,Armada[x][y].name,Playfield[h][v].name)
#  print ("=====***************************************************================")



  
  #Check for border
  for x in range(ArmadaWidth-1,-1,-1):
    for y in range (ArmadaHeight-1,-1,-1):
      if (Armada[x][y].alive == 1):
        #print ("MA - Calculating Armada[x][y].hv: ",x,y,Armada[x][y].h,Armada[x][y].v)
        h = Armada[x][y].h
        v = Armada[x][y].v
        direction = Armada[x][y].direction
        ScanH,ScanV = CalculateDotMovement(h,v,direction)
        
        #we just want to know the lowest armada ship, for firing missiles
        if (LowestV < v):
          LowestV = v
        #if (DotInvadersCheckBoundarySpaceDot(ScanH, ScanV) == 0):
        #FlashDot(h,v,0.005)
          
        #print ("MA - checking xy ScanH ScanV: ",x,y,ScanH,ScanV)
        if (DotInvadersCheckBoundarySpaceDot(ScanH, ScanV) == 1):
          BorderDetected = 1
          print ("MA - border detected - inner break")
          break
      if (DotInvadersCheckBoundarySpaceDot(ScanH, ScanV) == 1):
        BorderDetected = 1
        print ("MA - border detected - outer break")
        break
  
  #Move
  if (BorderDetected == 1):
    direction = ReverseDirection(direction)
  
  if (direction == 2):
    for x in range(ArmadaWidth-1,-1,-1):
      for y in range (ArmadaHeight-1,-1,-1):
        if (Armada[x][y].alive == 1):

          OldH = Armada[x][y].h
          OldV = Armada[x][y].v
          #print ("MA  - OldH OldV direction",OldH,OldV,direction)
          
          NewH, NewV = CalculateDotMovement(OldH,OldV,direction)
          if(BorderDetected == 1):
            NewH = OldH
            NewV = NewV + 1
          Armada[x][y].h = NewH
          Armada[x][y].v = NewV

          unicorn.set_pixel(OldH,OldV,0,0,0)
          Armada[x][y].Display()
          Armada[x][y].direction = direction
          Playfield[OldH][OldV] = Empty
          Playfield[NewH][NewV] = Armada[x][y]
          
  else:
    for x in range(ArmadaWidth):
      for y in range (ArmadaHeight-1,-1,-1):
        if (Armada[x][y].alive == 1):
  
          OldH = Armada[x][y].h
          OldV = Armada[x][y].v
          #print ("MA  - OldH OldV direction",OldH,OldV,direction)
          
          NewH, NewV = CalculateDotMovement(OldH,OldV,direction)
          if(BorderDetected == 1):
            NewH = OldH
#            NewV = NewV + 1
            NewV = NewV 
          Armada[x][y].h = NewH
          Armada[x][y].v = NewV

          unicorn.set_pixel(OldH,OldV,0,0,0)
          Armada[x][y].Display()
          Armada[x][y].direction = direction
          Playfield[OldH][OldV] = Empty
          Playfield[NewH][NewV] = Armada[x][y]
          

  #Drop missiles
  h,v = NewH, NewV
  if (UFOMissile1.alive == 0 and UFOMissile1.exploding == 0):
    UFOMissile1.h = h
    UFOMissile1.v = LowestV
    UFOMissile1.alive = 1
  elif (UFOMissile2.alive == 0 and UFOMissile2.exploding == 0):
    UFOMissile2.h = h
    UFOMissile2.v = LowestV
    UFOMissile2.alive = 1

      
def DotInvadersMoveMissile(Missile,Ship,Playfield):
  global Empty
  #print ("MM - MoveMissile:",Missile.name)
  
  #Record the current coordinates
  h = Missile.h
  v = Missile.v

  
  #Missiles simply drop to bottom and kablamo!
  #FF (one square in front of missile direction of travel)
  ScanH, ScanV = CalculateDotMovement(Missile.h,Missile.v,Missile.scandirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  
  #print("Item: ",Item)
  
  #Priority
  # 1 Hit target
  # 2 See if we are hit by enemy missle
  # 3 Move forward
  

  #See if other target ship is hit
  if (Item  == 'Player1' or Item == 'UFO' or Item == 'UFOMissile' or Item == 'Bunker'):
    #target hit, kill target
    print ("DIMM - Item Name", Item, Playfield[ScanH][ScanV].name)
    Playfield[ScanH][ScanV].alive = 0
    Playfield[ScanH][ScanV]= Empty
    unicorn.set_pixel(ScanH,ScanV,0,0,0)
    unicorn.set_pixel(h,v,0,0,255)
    if (Item == 'EnemyShip'):
      Ship.score = Ship.score + random.randint(1,11)
    else:
      Ship.score = Ship.score + 1


    Missile.h = ScanH
    Missile.v = ScanV
    #Playfield[Missile.h][Missile.v] = Missile
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0
  
  
  #Player missiles fire off into space
  #Enemy missiles explode on ground
  elif (Item == 'border' and Missile.name == 'PlayerMissile'):
    #print ("MM - Missile hit border")
    Missile.alive  = 0
    Missile.exploding = 0
    Missile.Erase()
  elif (Item == 'border' and (Missile.name == 'UFOMissile' or Missile.name == 'Asteroid')):
    #print ("MM - Missile hit border")
    Missile.alive  = 0
    Missile.exploding = 1
    Missile.Erase()
    #print ("MM - UFO hit border HV:",Missile.h,Missile.v)
    
  #empty = move forward
  elif (Item == 'empty' and Missile.alive == 1):
    Missile.h = ScanH
    Missile.v = ScanV
    Playfield[Missile.h][Missile.v] = Missile
    Missile.Display()
    #print ("MM - empty, moving forward")
    

  if ((h <> Missile.h or v <> Missile.v) or
     (Missile.alive == 0)):
    Playfield[h][v] = Empty
    unicorn.set_pixel(h,v,0,0,0)
    #print ("MM - Erasing Missile")
  unicorn.show()
  
  return 
    
def DotInvadersScanSpaceDot(h,v,Playfield):
# border
# empty
# wall

  #print ("SSD - HV:",h,v)
  Item = ''
  OutOfBounds = DotInvadersCheckBoundarySpaceDot(h,v)
  
  if (OutOfBounds == 1):
    Item = 'border'
#    print ("Border found HV: ",h,v)
  else:
    #FlashDot(h,v,0.01)
    Item = Playfield[h][v].name
  return Item


        
def DotInvaderScanShip(h,v,direction,Playfield):
  ScanDirection = 0
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']

  
  # We will scan 5 spots around the dot
  # and 8 more in front
  
  
  #       
  #  F6 F7 F8
  #     F5
  #     F4
  #     F3
  #     F2
  #     F1
  #  LF FF FR
  #  LL    RR 
  #
  #  11 12 13
  #    10
  #     9
  #     8
  #     7
  #     6
  #  2  3  4
  #  1     5
  #
  
  
  #LL 1
  ScanDirection = TurnLeft(direction)
  ScanH, ScanV = CalculateDotMovement(h,v,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS1 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #LF 2
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS2 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #FF 3
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS3 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #FR 4
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS4 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #RR 5
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS5 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F1 6
  ScanDirection = ReverseDirection(ScanDirection)
  ScanH, ScanV  = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = TurnLeft(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS6 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F2 7
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS7 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #F3 8
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS8 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #F4 9
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS9 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F5 10
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS10 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F6 11
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = TurnLeft(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS11 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F7 12
  ScanDirection = ReverseDirection(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS12 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #F8 13
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotInvadersScanSpaceDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DISS13 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  return ItemList;


def DotInvaderMovePlayerShip(Ship,Playfield):
  #print ("DIMPS - moveship HV Direction:",Ship.h,Ship.v,Ship.direction)
  
  #Player ships always points up, enemy ships point down
  h = Ship.h
  v = Ship.v
  ItemList = []
  #Scan all around, make decision, move
  ItemList = DotInvaderScanShip(Ship.h,Ship.v,Ship.scandirection,Playfield)
  
  #print("MPS - ItemList",ItemList)
  #print("MPS - Ship.name HV",Ship.name,Ship.h,Ship.v)
  #get possible items, then prioritize

  #Priority
  # 1 Evade close objects
  # 2 Blast far objects

  #If UFO is detected, fire missile!
  if ("UFO" in ItemList or "UFOMissile" in ItemList):
    if (PlayerMissile1.alive == 0 and PlayerMissile1.exploding == 0):
      #print ("MPS - UFO/Bomber/asteroid Detected PlayerMissile1.alive:",PlayerMissile1.alive)
      PlayerMissile1.h = h
      PlayerMissile1.v = v
      PlayerMissile1.alive = 1
      PlayerMissile1.exploding = 0
      Ship.score = Ship.score + 1
        
#    elif (PlayerMissile2.alive == 0 and PlayerMissile2.exploding == 0):
#      #print ("MPS - UFO or asteroid Detected PlayerMissile1.alive:",PlayerMissile1.alive)
#      PlayerMissile2.h = h
#      PlayerMissile2.v = v
#      PlayerMissile2.alive = 1
#      PlayerMissile2.exploding = 0

  #Follow UFO
  #slow down if ahead of UFO, speed up if behind
  if (ItemList[11] == 'UFO' or ItemList[11] == 'BomberShip'):
    #print ("****************************")
    #print ("****************************")
    #print ("****************************")
    Ship.direction = Playfield[h-1][0].direction
    #print ("MPS - ENEMY TO LEFT Enemy.name HV direction speed",Playfield[h-1][0].name,Playfield[h-1][0].h,Playfield[h-1][0].v, Playfield[h-1][0].direction,Playfield[h-1][0].speed)
    if (Playfield[h-1][0].direction == 4):
      AdjustSpeed(Ship,'fast',5)
    elif (Playfield[h-1][0].direction == 2):
      AdjustSpeed(Ship,'slow',1)
    
  elif (ItemList[13] == 'UFO' or ItemList[13] == 'BomberShip'):

    #for x in range (0,8):
      #for y in range (0,8):
        #print("Playfield[x][y].name HV speed direction: ",x,y,Playfield[x][y].name,Playfield[x][y].h,Playfield[x][y].v,Playfield[x][y].speed,Playfield[x][y].direction)


    Ship.direction = Playfield[h+1][0].direction
    #print ("MPS - ENEMY TO RIGHT Enemy.name HV direction",Playfield[h+1][0].name,Playfield[h+1][0].h,Playfield[h+1][0].v, Playfield[h+1][0].direction)
    if (Playfield[h+1][0].direction == 2):
      #print ("MPS - adjusting speed fast 3")
      AdjustSpeed(Ship,'fast',4)
    elif (Playfield[h+1][0].direction == 4):
      #print ("MPS - adjusting speed slow 1")
      AdjustSpeed(Ship,'slow',1)
  
    
     
  
  #if heading to boundary or wall Reverse direction
  #print("checking border")
  if ((Ship.direction == 4 and ItemList[1] == 'border') or
      (Ship.direction == 2 and ItemList[5] == 'border')):
    Ship.direction = ReverseDirection(Ship.direction)
    print ("MPS - border detected, reversing direction")
    AdjustSpeed(Ship,'slow',1)
    print("MPS - 2Ship.direction: ",Ship.direction)
  
  #Evade close objects
  # - if object in path of travel, reverse direction
  elif ((Ship.direction == 4 and ((ItemList[1] <> 'empty' and ItemList[1] <> 'Bunker') or (ItemList[2] <> 'empty'and ItemList[2] <> 'Bunker'))) or
        (Ship.direction == 2 and ((ItemList[5] <> 'empty' and ItemList[5] <> 'Bunker') or (ItemList[4] <> 'empty' and ItemList[4] <> 'Bunker')))):      
    Ship.direction = ReverseDirection(Ship.direction)
    print("MPS - object in path, reversed direction")
    print("MPS - 3Ship.direction: ",Ship.direction)
    

  # - speed up and move if object is directly above
  elif ((Ship.direction == 4 and (ItemList[3] <> 'empty' and ItemList[1] == 'empty')) or
        (Ship.direction == 2 and (ItemList[3] <> 'empty' and ItemList[5] == 'empty'))):
    AdjustSpeed(Ship,'fast',8)
    Ship.h, Ship.v =  CalculateDotMovement(Ship.h,Ship.v,Ship.direction)

  # - travelling left, move if empty
  # - travelling right, move if empty
  # - randomly switch directions
  elif ((ItemList[1] == 'empty' and Ship.direction == 4) or 
        (ItemList[5] == 'empty' and Ship.direction == 2 )):
    if ((random.randint(0,7) == 1) and Ship.h <> 0 and Ship.h <> 7):
      Ship.direction = ReverseDirection(Ship.direction)
    Ship.h, Ship.v =  CalculateDotMovement(Ship.h,Ship.v,Ship.direction)
    print("MPS - Travelling, move if empty")


  #if nothing nearby, and near the middle, stop moving
  if (ItemList[1]  == 'empty' and
      ItemList[2]  == 'empty' and
      ItemList[3]  == 'empty' and
      ItemList[4]  == 'empty' and
      ItemList[5]  == 'empty' and
      ItemList[6]  == 'empty' and
      ItemList[7]  == 'empty' and
      ItemList[8]  == 'empty' and
      ItemList[9]  == 'empty' and
      ItemList[10] == 'empty' and
      ItemList[12] == 'empty' and Ship.h >= 3 and Ship.h <= 4):
    if (random.randint (0,5) <> 1):
      print ("MPS - Staying in the middle")
      Ship.h = h
      Ship.v = v
    
  #print("MPS - 6Ship.direction: ",Ship.direction)

  print("MPS - OldHV: ",h,v, " NewHV: ",Ship.h,Ship.v, "direction: ",Ship.direction)
  Playfield[Ship.h][Ship.v]= Ship
  Ship.Display()
  
  if ((h <> Ship.h or v <> Ship.v) or
     (Ship.alive == 0)):
    Playfield[h][v] = Empty
    unicorn.set_pixel(h,v,0,0,0)
    print ("MPS - Erasing Player")
  unicorn.show()

  print("MPS - 7Ship.direction: ",Ship.direction)

  return 
        
          
          
def PlayDotInvaders():
  
  #Local variables
  moves       = 0
  Finished    = 'N'
  LevelCount  = 1
  Playerh     = 0
  Playerv     = 0
  SleepTime   = MainSleep / 4
  ChanceOfEnemyShip = 500

  #define sprite objects
  #def __init__(self,h,v,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding):
  BunkerDot1 = Ship(1,6,SDDarkGreenR,SDDarkGreenG,SDDarkGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot2 = Ship(2,6,SDDarkGreenR,SDDarkGreenG,SDDarkGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot3 = Ship(5,6,SDDarkGreenR,SDDarkGreenG,SDDarkGreenB,1,1,999,1,5,'Bunker', 0,0)
  BunkerDot4 = Ship(6,6,SDDarkGreenR,SDDarkGreenG,SDDarkGreenB,1,1,999,1,5,'Bunker', 0,0)
  PlayerShip = Ship(3,7,PlayerShipR,PlayerShipG,PlayerShipB,4,1,10,1,3,'Player1', 0,0)
  EnemyShip  = Ship(7,0,SDLowPurpleR,SDLowPurpleG,SDLowPurpleB,4,3,50,0,3,'UFO', 0,0)
  Ship(7,0,SDLowPurpleR,SDLowPurpleG,SDLowPurpleB,4,3,50,0,3,'UFO', 0,0)
  Empty      = Ship(-1,-1,0,0,0,0,1,0,0,0,'empty',0,0)


  # Create armada of 4x4 ships
  Armada = [[Ship(1,1,SDDarkGreenR,SDDarkGreenG,SDDarkGreenB,2,3,50,1,1,'UFO', 0,0) for y in range(ArmadaHeight)] for x in range(ArmadaWidth)]
  ArmadaSpeed = 100
  ArmadaAlive = 1
  
      
  
  #Create playfield
  Playfield = ([[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]])

  
  
  #Title
  unicorn.off()
  ShowScrollingBanner("DotInvader",45,100,0,ScrollSleep)

  ShowSpaceInvaderTime(ScrollSleep)
  

  #Main Game Loop
  while (Finished == 'N'):

    # Set initial starting positions
    for x in range (ArmadaWidth):
      for y in range(ArmadaHeight):
        Armada[x][y].h = x+1
        Armada[x][y].v = y
        Armada[x][y].alive = 1
    ArmadaSpeed = 50
    ArmadaAlive = 1

    unicorn.off()
    LevelCount = LevelCount + 1
    ShowLevelCount(LevelCount)



    
    #Reset Variables between rounds
    LevelFinished     = 'N'
    moves             = 1
    PlayerShip.alive  = 1
    PlayerShip.speed  = 5
    PlayerShip.h      = 3
    PlayerMissile1.speed = 2
    if (random.randint(0,2) == 1):
      PlayerShip.direction = 2
    else:
      PlayerShip.direction = 4
    EnemyShip.alive   = 0
    UFOMissile1.alive = 0
    UFOMissile2.alive = 0
    EnemyShip.speed   = random.randint (5,25)

    
    #Reset colors
    UFOMissile1.r = PlayerMissileR
    UFOMissile1.g = PlayerMissileG
    UFOMissile1.b = PlayerMissileB
    UFOMissile2.r = PlayerMissileR
    UFOMissile2.g = PlayerMissileG
    UFOMissile2.b = PlayerMissileB
    PlayerMissile1.r = PlayerMissileR
    PlayerMissile1.g = PlayerMissileG
    PlayerMissile1.b = PlayerMissileB
    

    ShowDropShip(PlayerShip.h,PlayerShip.v,'dropoff',ScrollSleep * 0.25)

    #Reset Playfield
    for x in range (0,8):
      for y in range (0,8):
        #print ("XY",x,y)
        Playfield[x][y] = Empty
                 
    #Put items on Playfield
    Playfield[PlayerShip.h][PlayerShip.v] = PlayerShip
    PutArmadaOnPlayfield(Armada,Playfield)
        
    
    #Draw Bunkers
    Playfield[1][6] = BunkerDot1
    Playfield[2][6] = BunkerDot2
    Playfield[5][6] = BunkerDot3
    Playfield[6][6] = BunkerDot4
    
    BunkerDot1.alive = 1
    BunkerDot2.alive = 1
    BunkerDot3.alive = 1
    BunkerDot4.alive = 1
    BunkerDot1.Flash()
    BunkerDot1.Display()
    BunkerDot4.Flash()
    BunkerDot4.Display()
    BunkerDot2.Flash()
    BunkerDot2.Display()
    BunkerDot3.Flash()
    BunkerDot3.Display()
    DisplayPlayfield(Playfield)
   

    
    # Main timing loop
    while (LevelFinished == 'N' and PlayerShip.alive == 1):
      moves = moves + 1

      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = PollKeyboard()
        if (Key == 'q'):
          LevelFinished = 'Y'
          Finished      = 'Y'
          PlayerShip.alive   = 0
          return

        
      
#      print ("=================================================")
#      for H in range(0,7):
#        for V in range (0,7):
#          if (Playfield[H][V].name <> 'empty'):
#            print ("Playfield: HV Name Alive",H,V,Playfield[H][V].name,Playfield[H][V].alive)
#      print ("=================================================")
      

      
      #Spawn EnemyShip
      m,r = divmod(moves,ChanceOfEnemyShip)
      if (r == 0 and EnemyShip.alive == 0):
        print ("Spawning UFO")
        EnemyShip.alive = 1
        EnemyShip.direction = ReverseDirection(EnemyShip.direction)
        if (EnemyShip.direction == 2):
          EnemyShip.h = 0
          EnemyShip.v = 0
          #EnemyShip.v = random.randint(0,4)
        else:
          EnemyShip.h = 7
          EnemyShip.v = 0
        EnemyShip.Display()
      
      
      
      if (PlayerShip.alive == 1):
        #print ("M - Playership HV speed alive exploding direction: ",PlayerShip.h, PlayerShip.v,PlayerShip.speed, PlayerShip.alive, PlayerShip.exploding, PlayerShip.direction)
        m,r = divmod(moves,PlayerShip.speed)
        if (r == 0):
          DotInvaderMovePlayerShip(PlayerShip,Playfield)
          i = random.randint(0,2)
          if (i >= 0):
            AdjustSpeed(PlayerShip,'fast',1)
          print ("M - Player moved?")
          
            
      
      if (EnemyShip.alive == 1):
        m,r = divmod(moves,EnemyShip.speed)
        if (r == 0):
          if ((EnemyShip.h == 0 and EnemyShip.direction == 4)
            or EnemyShip.h == 7 and EnemyShip.direction == 2):
            EnemyShip.alive = 0
            Playfield[EnemyShip.h][EnemyShip.v] = Empty
            unicorn.set_pixel(EnemyShip.h,EnemyShip.v,0,0,0)
          else:
            MoveEnemyShip(EnemyShip,Playfield)
        
          

      if (ArmadaAlive == 1):
        m,r = divmod(moves,ArmadaSpeed)
        if (r == 0):
          MoveArmada(Armada,Playfield)
        
          
          
      if (UFOMissile1.alive == 1 and UFOMissile1.exploding == 0):
        m,r = divmod(moves,UFOMissile1.speed)
        if (r == 0):
          DotInvadersMoveMissile(UFOMissile1,PlayerShip,Playfield)

      if (UFOMissile2.alive == 1 and UFOMissile2.exploding == 0):
        m,r = divmod(moves,UFOMissile2.speed)
        if (r == 0):
          DotInvadersMoveMissile(UFOMissile2,PlayerShip,Playfield)

      if (UFOMissile3.alive == 1 and UFOMissile3.exploding == 0):
        m,r = divmod(moves,UFOMissile3.speed)
        if (r == 0):
          DotInvadersMoveMissile(UFOMissile3,PlayerShip,Playfield)

          
      if (PlayerMissile1.alive == 1 and PlayerMissile1.exploding == 0):
        m,r = divmod(moves,PlayerMissile1.speed)
        if (r == 0):
          DotInvadersMoveMissile(PlayerMissile1,PlayerShip,Playfield)

#      if (PlayerMissile2.alive == 1 and PlayerMissile2.exploding == 0):
#        m,r = divmod(moves,PlayerMissile2.speed)
#        if (r == 0):
#          DotInvadersMoveMissile(PlayerMissile2,PlayerShip,Playfield)

          



        
      
          
          

        

      #Check for exploding objects
      if (PlayerMissile1.exploding == 1):
        #print("------> PlayerMissile1.exploding: ",PlayerMissile1.exploding)
        DotInvadersExplodeMissile(PlayerMissile1,Playfield,20)

#      if (PlayerMissile2.exploding == 1 ):
#        #print("------> PlayerMissile2.exploding: ",PlayerMissile2.exploding)
#        DotInvadersExplodeMissile(PlayerMissile2,Playfield,20)


      if (UFOMissile1.exploding == 1 ):
        #print("------> UFOMissile1.exploding: ",UFOMissile1.exploding)
        DotInvadersExplodeMissile(UFOMissile1,Playfield,20)

      if (UFOMissile2.exploding == 1 ):
        #print("------> UFOMissile2.exploding: ",UFOMissile2.exploding)
        DotInvadersExplodeMissile(UFOMissile2,Playfield,20)

        
      #Display animation and clock every X seconds
      if (CheckElapsedTime(CheckTime) == 1):
        ScrollScreenShowLittleShipTime('up',ScrollSleep)         
     
      #=================================
      #= End of level conditions       =
      #=================================
     
      #Count armada UFOs alive
      #See how low down Armada is
      ArmadaCount = 0
      ArmadaLevel = 0
      for x in range (ArmadaWidth):
        for y in range (ArmadaHeight):
          if (Armada[x][y].alive == 1):
            ArmadaCount = ArmadaCount + 1
            if (Armada[x][y].v > ArmadaLevel):
              ArmadaLevel = Armada[x][y].v
      #print ("M - Armada AliveCount ArmadaLevel: ",ArmadaCount,ArmadaLevel)
      ArmadaSpeed = ArmadaCount *5
        

      if (ArmadaCount == 0):
        LevelFinished = 'Y'
        print ("M - Level:", LevelCount)
        unicorn.set_pixel(PlayerMissile1.h,PlayerMissile1.v,0,0,0)
        ShowDropShip(PlayerShip.h,PlayerShip.v,'pickup',ScrollSleep * 0.25)

      
      if (ArmadaLevel == 7):
        PlayerShip.alive = 0
        LevelFinished = 'Y'
        
      if (PlayerShip.alive == 0):
        PlayerShip.lives = PlayerShip.lives - 1
        if (PlayerShip.lives <=0):
          Finished = 'Y'
        PlayerShipExplosion.Animate(PlayerShip.h-2,PlayerShip.v-2,'forward',0.025)

      #Display animation and clock every X seconds
      if (CheckElapsedTime(CheckTime) == 1):
        ScrollScreenShowTime('up',ScrollSleep)         



        
      time.sleep(MainSleep / 5)
  print ("M - The end?")    
  unicorn.off()
  
  ScoreString = str(PlayerShip.score) 
  ShowScrollingBanner("Score",SDLowGreenR,SDLowGreenG,SDLowGreenB,ScrollSleep)
  ShowScrollingBanner(ScoreString,SDLowYellowR,SDLowYellowG,SDLowYellowB,(ScrollSleep * 2))
  ShowScrollingBanner("GAME OVER",SDLowRedR,SDLowRedG,SDLowRedR,ScrollSleep)




      







      
      
      
      
      
      
      
      
      
      
      


#------------------------------------------------------------------------------
# D o t Z e r k                                                              --
#------------------------------------------------------------------------------

# Notes
#
# Due to the unforseen complexity of navigating the maps, we are going to force
# doors to be in fixed positions
# We should make the doors be meta objects, and not items on the playfield
# It is very difficult to treat them as special wall objects

#Variables
ExitingRoom   = 0
RobotsAlive   = 0
HumanMissileR = SDLowWhiteR
HumanMissileG = SDLowWhiteG
HumanMissileB = SDLowWhiteB
RobotMissileR = SDHighWhiteR
RobotMissileG = SDHighWhiteG
RobotMissileB = SDHighWhiteB
DotZerkScore  = 0

#Hold speeds in a list, acting like gears
Gear = []
Gear.append(100)
Gear.append(50)
Gear.append(40)
Gear.append(30)
Gear.append(25)
Gear.append(15)
global CurrentGear
CurrentGear = 4

#Track previous human direction so we can close the door in a new room
DirectionOfTravel = 2



#define sprite objects
#def __init__(self,h,v,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding):
Human         = Ship(1,3,SDLowGreenR,SDLowGreenG,SDLowGreenB,2,2,10,1,10,'Human', 0,0)
HumanMissile1 = Ship(-1,-1,HumanMissileR,HumanMissileG,HumanMissileB,1,1,4,0,0,'HumanMissile', 0,0)
HumanMissile2 = Ship(-1,-1,HumanMissileR,HumanMissileG,HumanMissileB,1,1,4,0,0,'HumanMissile', 0,0)

Robot1 = Ship(3,7,SDLowRedR,SDLowRedG,SDLowRedB,4,1,10,0,3,'Robot', 0,0)
Robot2 = Ship(3,7,SDLowRedR,SDLowRedG,SDLowRedB,4,1,10,0,3,'Robot', 0,0)
Robot3 = Ship(3,7,SDMedYellowR,SDMedYellowG,SDMedYellowB,4,1,10,0,3,'Robot', 0,0)
Robot4 = Ship(3,7,SDLowRedR,SDLowRedG,SDLowRedB,4,1,10,0,3,'Robot', 0,0)
Empty  = Ship(-1,-1,0,0,0,0,1,0,0,0,'empty',0,0)



Robot1Missile   = Ship(-5,-1,RobotMissileR,RobotMissileG,RobotMissileB,0,0,15,0,0,'RobotMissile',0,0)
Robot2Missile   = Ship(-5,-1,RobotMissileR,RobotMissileG,RobotMissileB,0,0,15,0,0,'RobotMissile',0,0)
Robot3Missile   = Ship(-5,-1,RobotMissileR,RobotMissileG,RobotMissileB,0,0,15,0,0,'RobotMissile',0,0)
Robot4Missile   = Ship(-5,-1,RobotMissileR,RobotMissileG,RobotMissileB,0,0,15,0,0,'RobotMissile',0,0)

#(h,v,alive,locked,name):
Door1 = Door(3,0,0,0,'Door')
Door2 = Door(7,3,0,0,'Door')
Door3 = Door(3,7,0,0,'Door')
Door4 = Door(0,3,0,0,'Door')


#(self,name,width,height,Map,Playfield):
MazeWorld = World(name='Maze',width=40,height=64,Map=[[]],Playfield=[[]],CurrentRoomH = 0,CurrentRoomV=0,DisplayH=0,DisplayV=0)
MazeWorld.CurrentRoomH = random.randint(0,4)
MazeWorld.CurrentRoomV = random.randint(0,7)

#MazeWorld.CurrentRoomH = 0
#MazeWorld.CurrentRoomV = 0

  
MazeWorld.Map[0]  = ([14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,14,])    
MazeWorld.Map[1]  = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0,14, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14, 1, 0, 0,26,10,15,14,])    
MazeWorld.Map[2]  = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0,14, 0,14,  14, 0, 0, 0,14, 0, 0,14,  14,14,14,14, 0, 0, 0,14, 14, 0, 0, 0, 0, 7,22,14,])    
MazeWorld.Map[3]  = ([14, 0,14,14,14,14, 0,21,  21, 0, 0, 0, 0,14, 0,21,  21, 0, 0, 0,14, 0, 0,21,  21, 0, 0,14, 0,14, 0,21, 21, 0, 0, 0, 0, 0,17,14,])    
MazeWorld.Map[4]  = ([14, 0, 0, 0, 0,14, 0,14,  14, 0,14,14,14,14, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0,14,14,14, 0,14, 14,26, 0, 0, 0, 0, 0,14,])    
MazeWorld.Map[5]  = ([14, 0,14, 0, 0, 0, 0,14,  14, 0, 0, 0, 0,14, 0,14,  14, 0,14, 0, 0,14,14,14,  14, 0, 0, 0, 0, 0, 0,14, 14,10, 7, 0, 0, 0, 0,14,])    
MazeWorld.Map[6]  = ([14, 0,00, 0, 0, 0, 0,14,  14, 0, 0, 0, 0,14, 0,14,  14, 0,14, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14,15,22, 0,17, 0, 1,14,])    
MazeWorld.Map[7]  = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    
  
MazeWorld.Map[8]  = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    
MazeWorld.Map[9]  = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0,14,])    
MazeWorld.Map[10] = ([14,14,14, 0,14, 0, 0,14,  14, 0, 9, 9, 9, 9, 0,14,  14, 0, 0, 9, 0, 0, 0,14,  14, 0, 0, 0,22, 0, 0,14, 14, 0,10,18, 0,10, 0,14,])    
MazeWorld.Map[11] = ([14, 0, 0, 0,14, 0, 0,21,  21, 0, 9, 0, 0, 0, 0,21,  21, 0, 9, 9, 9, 9, 0,21,  21, 0, 0,22,22,22, 0,14, 14, 0, 0, 0, 0,18, 6,14,])    
MazeWorld.Map[12] = ([14, 0, 0, 0,14, 0, 0,14,  14, 0, 9, 0, 0, 9, 0,14,  14, 0, 0, 9, 0, 0, 0,14,  14, 0, 0, 0,22, 0, 0,14, 14, 6,18, 0, 0, 0, 0,14,])    
MazeWorld.Map[13] = ([14, 0, 0,00,14, 0, 0,14,  14, 0, 9, 0, 9, 9, 0,14,  14, 0, 0, 9, 0, 0, 0,14,  14, 0, 0, 0,22, 0, 0,14, 14, 0,10, 0,18,10, 0,14,])    
MazeWorld.Map[14] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 6, 0, 0,14,])    
MazeWorld.Map[15] = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    

MazeWorld.Map[16] = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    
MazeWorld.Map[17] = ([14, 0, 0, 0, 0, 0, 0,14,  14,14, 0, 0, 0, 0,14,14,  14, 0, 9, 0, 0, 9, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14,15, 7, 0, 7, 0, 0,14,])    
MazeWorld.Map[18] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 9, 9, 9, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0,17,17, 0,17, 0,14, 14, 7, 7, 0, 7,17, 0,14,])    
MazeWorld.Map[19] = ([14, 0,14, 0, 0, 0, 0,21,  21, 0, 0, 0, 0, 0, 0,21,  21, 0, 0, 0, 0, 0, 0,21,  21, 0, 0, 0, 0,17, 0,21, 21, 0, 0, 0, 7, 7, 0,14,])    
MazeWorld.Map[20] = ([14, 0,14,14,14,14, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0,17, 0,14, 14, 7, 7, 0, 7, 0, 0,14,])    
MazeWorld.Map[21] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 9, 9, 9, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0,17,17, 0,17, 0,14, 14, 0, 0, 0, 0, 0, 0,14,])    
MazeWorld.Map[22] = ([14, 0, 0, 0, 0, 0, 0,14,  14,14, 0, 0, 0, 0,14,14,  14, 0, 9, 0, 0, 9, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14,24, 7, 0, 7,17, 0,14,])    
MazeWorld.Map[23] = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    

MazeWorld.Map[24] = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    
MazeWorld.Map[25] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14,13, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14,24,17, 0,10,24,24,14,])    
MazeWorld.Map[26] = ([14, 0,14,14, 0, 0, 0,14,  14,14, 0,14,14, 0,14,14,  14, 0,13, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14,17,17, 0,10, 0,24,14,])    
MazeWorld.Map[27] = ([14, 0,14, 0, 0, 0, 0,21,  21, 0, 0,14,14, 0, 0,21,  21, 0, 0,13, 0, 0, 0,21,  21, 0, 5, 5, 5, 5, 0,21, 21, 0, 0, 0,10, 0, 0,14,])    
MazeWorld.Map[28] = ([14, 0,14, 0, 0, 0, 0,14,  14,14, 0,14,14, 0,14,14,  14, 0, 0, 0,13, 0, 0,14,  14, 0, 5, 0, 0, 5, 0,14, 14,10,10, 0,10, 0, 0,14,])    
MazeWorld.Map[29] = ([14, 0,14, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0,13, 0,14,  14, 0, 5, 0, 0, 5, 0,14, 14, 6,10, 0,10, 0, 0,14,])    
MazeWorld.Map[30] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 5, 0,14, 14, 0, 0, 0, 0, 0,18,14,])    
MazeWorld.Map[31] = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    

MazeWorld.Map[32] = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    
MazeWorld.Map[33] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14,25,25, 0,25, 0, 0,14, 14, 0, 0, 0, 0, 0,14,14,])    
MazeWorld.Map[34] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0,25,25, 0, 0,14,  14,25,25, 0,25, 0, 0,14, 14, 0,14, 0,14, 0, 0,14,])    
MazeWorld.Map[35] = ([14, 0, 0, 0, 0, 0, 0,21,  21, 0, 0, 0, 0, 0, 0,21,  21, 0,25,26,26,25, 0,21,  21, 0, 0, 0,25, 0, 0,14, 14, 0,14, 0,14,14, 0,14,])    
MazeWorld.Map[36] = ([14, 0, 0, 5, 5, 0, 0,14,  14, 0,17,17,17,17, 0,14,  14, 0, 0,25,25, 0, 0,14,  14, 0,25,25,25, 0, 0,14, 14, 0,14, 0,14, 0, 0,14,])    
MazeWorld.Map[37] = ([14, 0, 6, 6, 6, 6, 0,14,  14, 0,17,18,18,17, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14, 0,14, 0,14, 0,14,14,])    
MazeWorld.Map[38] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0,17,18,18,17, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0,14,])    
MazeWorld.Map[39] = ([14,14,14,21,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    


MazeWorld.Map[40] = ([14,14,14,21,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    
MazeWorld.Map[41] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0,22,22, 0,14, 14, 0, 0, 0, 0, 0, 0,14,])    
MazeWorld.Map[42] = ([14, 0, 0, 0, 0, 0, 0,14,  14,25,25,25,25,25, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0,22,22, 0,14, 14, 0,22, 0,22, 0, 0,14,])    
MazeWorld.Map[43] = ([14, 0,15,15,15,15, 0,21,  21, 0, 0, 0, 0,25, 0,21,  21, 0, 0, 1, 1, 0, 0,21,  21, 0, 0, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0,14,])    
MazeWorld.Map[44] = ([14, 0,15, 0, 0,15, 0,14,  14, 0,25,25, 0,25, 0,14,  14, 0, 0, 1, 1, 0, 0,14,  14, 0,22,22,22,22, 0,14, 14,22, 0, 0, 0,22, 0,14,])    
MazeWorld.Map[45] = ([14, 0,15, 0, 0,15, 0,14,  14, 0, 0,25, 0,25, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0,22, 0, 0,22, 0,14, 14, 0,22,22,22, 0, 0,14,])    
MazeWorld.Map[46] = ([14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0,22, 0, 0, 0, 0,14, 14, 0, 0, 0, 0, 0, 0,14,])    
MazeWorld.Map[47] = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    

MazeWorld.Map[48] = ([14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14,  14,14,14,21,14,14,14,14, 14,14,14,21,14,14,14,14,])    
MazeWorld.Map[49] = ([14, 0, 0, 0, 0, 0, 0,14,  14,13,13, 0,13,13,13,14,  14,25,25, 0, 0,25,25,14,  14, 0, 0, 0,18,18,18,14, 14,22,17, 0, 0,17,17,14,])    
MazeWorld.Map[50] = ([14, 0,10, 0, 0,10, 0,14,  14,13,13, 0,13,13,13,14,  14,25,25, 0, 0,25,25,14,  14, 0, 0, 0,18,18,18,14, 14, 0,17, 0, 0,17,17,14,])    
MazeWorld.Map[51] = ([14, 0, 0, 0, 0, 0, 0,21,  21, 0, 0, 0,13,13, 0,21,  21, 0,25, 0, 0,25, 0,21,  21, 0, 0, 0, 0, 0, 0,21, 21, 0,17,17, 0, 0,17,14,])    
MazeWorld.Map[52] = ([14, 0, 0, 0, 0, 0, 0,14,  14,13,13, 0,13,13, 0,14,  14, 0,25, 0, 0,25, 0,14,  14, 0,18,18,18,18,18,14, 14, 0,17, 0, 0,17,17,14,])    
MazeWorld.Map[53] = ([14, 0,10, 0, 0,10, 0,14,  14,13,13, 0,13,13, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0,18, 5, 6, 7, 8,14, 14, 0, 0, 0, 0, 5, 1,14,])    
MazeWorld.Map[54] = ([14, 0, 0, 0, 0, 0, 0,14,  14,13,13, 0, 0, 0, 0,14,  14, 0, 0,25,25, 0, 0,14,  14, 0,18, 5, 6, 7, 8,14, 14, 0, 0, 0, 0, 0, 5,14,])    
MazeWorld.Map[55] = ([14,14,14,21,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14, 14,14,14,21,14,14,14,14,])    

MazeWorld.Map[56] = ([14,14,14,21,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14, 14,14,14,21,14,14,14,14,])    
MazeWorld.Map[57] = ([14,22,14, 0,14,22,22,14,  14, 0, 0,13, 0, 0, 0,14,  14,25,25, 0, 0,25,25,14,  14, 0, 0, 0,18,18,18,14, 14, 0,17, 0, 0,17,17,14,])    
MazeWorld.Map[58] = ([14,14,22, 0, 0, 0, 0,14,  14,17, 0,17, 0,17, 0,14,  14,25,25, 0, 0,25,25,14,  14, 0, 0, 0,18,18,18,14, 14, 0,17, 0, 0,17,17,14,])    
MazeWorld.Map[59] = ([14, 0,14,14, 0,14, 0,21,  21, 0, 0, 0, 0, 0, 0,21,  21, 0,25, 0, 0,25, 0,21,  21, 0, 0, 0, 0, 0, 0,21, 21, 0,17,17, 0, 0,17,14,])    
MazeWorld.Map[60] = ([14, 0, 0, 0, 0,14, 0,14,  14, 0,25, 0,25, 0,25,14,  14, 0,25, 0, 0,25, 0,14,  14, 0,18,18,18,18,18,14, 14, 0,17, 0, 0,17,17,14,])    
MazeWorld.Map[61] = ([14,14, 0,14, 0,14,14,14,  14, 0, 0, 0,13, 0, 0,14,  14, 0, 0, 0, 0, 0, 0,14,  14, 0,18, 5, 6, 7, 8,14, 14, 0, 0, 0, 0, 5, 1,14,])    
MazeWorld.Map[62] = ([14, 0, 0,14, 0, 0, 0,14,  14, 0, 0, 0,13, 0, 0,14,  14, 0, 0,25,25, 0, 0,14,  14, 0,18, 5, 6, 7, 8,14, 14, 0, 0, 0, 0, 0, 5,14,])    
MazeWorld.Map[63] = ([14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14,  14,14,14,14,14,14,14,14, 14,14,14,14,14,14,14,14,])    



def DeactivateMissiles():

  #Remove missiles from playfield
  Robot1Missile.alive     = 0
  Robot1Missile.exploding = 0
  Robot2Missile.alive     = 0
  Robot2Missile.exploding = 0
  Robot3Missile.alive     = 0
  Robot3Missile.exploding = 0
  
  HumanMissile1.alive     = 0
  HumanMissile2.exploding = 0

  MazeWorld.Playfield[Robot1Missile.h][Robot1Missile.v] = Empty
  MazeWorld.Playfield[Robot2Missile.h][Robot2Missile.v] = Empty
  MazeWorld.Playfield[Robot3Missile.h][Robot3Missile.v] = Empty
  MazeWorld.Playfield[HumanMissile1.h][HumanMissile1.v] = Empty
  MazeWorld.Playfield[HumanMissile2.h][HumanMissile2.v] = Empty
  
  
def DotZerkAdjustSpeed(Human,ShiftDirection):
  global CurrentGear
  print ("DZAS - BEFORE CurrentGear CurrentSpeed ShiftDirection",CurrentGear,Human.speed, ShiftDirection)
   
  if (ShiftDirection == 'down'):
    CurrentGear = CurrentGear -1
  else:
    CurrentGear = CurrentGear +1
  
  if (CurrentGear >= 5):
    CurrentGear = 5
  elif (CurrentGear <= 0):
    CurrentGear = 0 
    
  Human.speed = Gear[CurrentGear]
  print ("DZAS - AFTER CurrentGear CurrentSpeed ",CurrentGear,Human.speed)

  
def DotZerkDisplayDoors():
  Door1.Display()
  Door2.Display()
  Door3.Display()
  Door4.Display()
  

def DotZerkLockDoors():
  global DirectionOfTravel
  Door1.locked = 0
  Door2.locked = 0
  Door3.locked = 0
  Door4.locked = 0
  
  
  print ("DZLD - Direction of Travel:",DirectionOfTravel)
  if (DirectionOfTravel == 1):
    #Lock the door
    Door3.locked = 1
    print ("DZLD - Locking bottom door")
  elif (DirectionOfTravel == 2):
    Door4.locked = 1
    print ("DZLD - Locking left door")
  elif (DirectionOfTravel == 3):
    #Lock the door
    Door1.locked = 1
    print ("DZLD - Locking top door")
  elif (DirectionOfTravel == 4):
    Door2.locked = 1
    print ("DZLD - Locking right door")
  
  DotZerkDisplayDoors()
  
  
  
def DotZerkResetPlayfield(ShowFlash):
  print ("DZRP - Emptying playfield")
  for x in range (0,8):
    for y in range (0,8):
      #print ("XY",x,y)
      MazeWorld.Playfield[x][y] = Empty
      
  #Put items on Playfield
  MazeWorld.CopyMapToPlayfield()
  MazeWorld.Playfield[Human.h][Human.v] = Human
  PlaceRobotOnPlayfield(Robot1)
  PlaceRobotOnPlayfield(Robot2)
  
  MazeWorld.DisplayPlayfield(ShowFlash)
  print ("DZRP - Displayed Playfield")
  DotZerkLockDoors()
  DeactivateMissiles()

  MazeWorld.Playfield[3][0] = Door1
  MazeWorld.Playfield[7][3] = Door2
  MazeWorld.Playfield[3][7] = Door3
  MazeWorld.Playfield[0][3] = Door4

  
def PlaceRobotOnPlayfield(Robot):
  h = random.randint(1,6)
  v = random.randint(1,6)
  print ("PROP - HV",h,v)
  while (MazeWorld.Playfield[h][v].name <> 'empty'):
    print ("PROP - Looking:",MazeWorld.Playfield[h][v].name)
    h = random.randint(1,6)
    v = random.randint(1,6)
    print ("PROP - HV",h,v)

  Robot.h = h
  Robot.v = v
  MazeWorld.Playfield[h][v] = Robot
  print ("PROP - Robot placed HV",h,v)
  
  
def DotZerkExitRoom(DoorDirection):
  global DotZerkScore
  unicorn.off()
  #Scroll Right
  print ("DZER - DoorDirection:",DoorDirection)

  #Increase score
  DotZerkScore = DotZerkScore + 5
  DeactivateMissiles()
  print ("DZER - CurrentRoomH CurrentRoomV",MazeWorld.CurrentRoomH, MazeWorld.CurrentRoomV)
  
  if (DoorDirection == 1):
    MazeWorld.CurrentRoomV = MazeWorld.CurrentRoomV - 1

    ScrollH = MazeWorld.CurrentRoomH *8
    ScrollV = MazeWorld.CurrentRoomV *8
        
    #We display the window 8 times, moving it one column every time
    #this gives a neat scrolling effect
    for x in range (ScrollV+8,ScrollV-1,-1):
      print ("DZER X:",x)
      print ("DZER calling DisplayWindow ScrollH x:",ScrollH,x)
      MazeWorld.DisplayWindow(ScrollH,x)
      unicorn.show()
      time.sleep(0.1)
     
    #Move human to other side of the playfield
    Human.v = 6
    
  

  


  if (DoorDirection == 3):
    MazeWorld.CurrentRoomV = MazeWorld.CurrentRoomV + 1

    ScrollH = MazeWorld.CurrentRoomH *8
    ScrollV = MazeWorld.CurrentRoomV *8
        
    #We display the window 8 times, moving it one column every time
    #this gives a neat scrolling effect
    for x in range (ScrollV-8,ScrollV+1):
      print ("DZER X:",x)
      print ("DZER calling DisplayWindow ScrollH x:",ScrollH,x)
      MazeWorld.DisplayWindow(ScrollH,x)
      unicorn.show()
      time.sleep(0.1)
    
    #Move human to other side of the playfield
    Human.v = 1
    


  if (DoorDirection == 2):
    MazeWorld.CurrentRoomH = MazeWorld.CurrentRoomH + 1

    ScrollH = MazeWorld.CurrentRoomH *8
    ScrollV = MazeWorld.CurrentRoomV *8
        
    #We display the window 8 times, moving it one column every time
    #this gives a neat scrolling effect
    for x in range (ScrollH-8,ScrollH+1):
      print ("DZER X:",x)
      print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
      MazeWorld.DisplayWindow(x,ScrollV)
      unicorn.show()
      time.sleep(0.1)
    
    #Move human to other side of the playfield
    Human.h = 1

    
  
  elif (DoorDirection == 4):
    MazeWorld.CurrentRoomH = MazeWorld.CurrentRoomH -1
    ScrollH = MazeWorld.CurrentRoomH *8
    ScrollV = MazeWorld.CurrentRoomV *8
    print("DZER - ScrollHV",ScrollH,ScrollV)
    for x in range (ScrollH+8,ScrollH-1,-1):
      print ("DZER X:",x)
      print ("DZER calling DisplayWindow x ScrollV:",x,ScrollV)
      MazeWorld.DisplayWindow(x,ScrollV)
      unicorn.show()
      time.sleep(0.1)

    #Move human to other side of the playfield
    Human.h = 6

      
  
  DotZerkResetPlayfield(0)
  


def DotZerkExplodeMissile(Ship,Playfield,increment):
  
  Ship.r = Ship.r + increment
  Ship.g = 0 #Ship.g + increment
  Ship.b = 0 #Ship.b + increment

  #After explosion, reset colors
  if (Ship.r >= 400 or Ship.g >= 400 or Ship.b >= 400):
    if (Ship.name == 'HumanMissile'):
      Ship.r = HumanMissileR
      Ship.g = HumanMissileG
      Ship.b = HumanMissileB
    elif (Ship.name == 'RobotMissile'):
      Ship.r = RobotMissileR
      Ship.g = RobotMissileG
      Ship.b = RobotMissileB

    Ship.exploding = 0
    Ship.alive     = 0
    print ("+++++++++++++++++++++++++++++++++++++")
    print ("Missile Exploded")
    print ("+++++++++++++++++++++++++++++++++++++")
    Ship.Erase()
    Playfield[Ship.h][Ship.v].alive = 0
    Playfield[Ship.h][Ship.v] = Empty
    
      

  if (Ship.exploding == 1):
    r = Ship.r
    g = Ship.g
    b = Ship.b
    if (r > 255):
      r = 255
    if (g > 255):
      g = 255
    if (b > 255):
      b = 255
    unicorn.set_pixel(Ship.h,Ship.v,r,g,b)
#  print("DZEM - Ship.exploding: ",Ship.exploding)
#  print("DZEM - After: ",Ship.name, "HV",Ship.h,Ship.v," rgb",Ship.r,Ship.g,Ship.b)
  

def DotZerkExplodeRobot(Robot,Playfield,increment):
  global RobotsAlive
  global DotZerkScore
  
  Robot.r = Robot.r + increment
  Robot.g = Robot.g + increment
  Robot.b = 0 #Robot.b + increment

  #After explosion, reset colors
  if (Robot.r >= 400 or Robot.g >= 400 or Robot.b >= 400):
    Robot.r = SDLowRedR
    Robot.g = SDLowRedR
    Robot.b = SDLowRedR

    Robot.exploding = 0
    Robot.alive     = 0
    print ("+++++++++++++++++++++++++++++++++++++")
    print ("ROBOT Exploded")
    print ("+++++++++++++++++++++++++++++++++++++")
    Robot.Erase()
    Playfield[Robot.h][Robot.v].alive = 0
    Playfield[Robot.h][Robot.v] = Empty
    RobotsAlive = RobotsAlive -1
    DotZerkScore = DotZerkScore + 5


  if (Robot.exploding == 1):
    r = Robot.r
    g = Robot.g
    b = Robot.b
    if (r > 255):
      r = 255
    if (g > 255):
      g = 255
    if (b > 255):
      b = 255
    unicorn.set_pixel(Robot.h,Robot.v,r,g,b)  



def PrintDoorStatus():
  print ("=====THE DOORS===============================")
  print ("Door1 alive locked:",Door1.alive,Door1.locked)
  print ("Door2 alive locked:",Door2.alive,Door2.locked)
  print ("Door3 alive locked:",Door3.alive,Door3.locked)
  print ("Door4 alive locked:",Door4.alive,Door4.locked)
  print ("=============================================")


def DotZerkScanDot(h,v,Playfield):
# border
# empty
# wall

  #print ("DZSD - HV:",h,v)
  Item = 'Wall'
  OutOfBounds = CheckBoundary(h,v)
  #print ("DZSD - OutOfBounds:",OutOfBounds)
  
  if (OutOfBounds == 1):
    Item = 'border'
    #print ("DZSD - Border found HV: ",h,v)
  else:
    #FlashDot(h,v,0.005)
    #print ("DZSD - Not out of bounds")

    #Doors need to be unlocked to be visible
    #print ("DZSD - Name Scanned:",Playfield[h][v].name)
    
    if (h == 3 and v == 0):
      #print ("DZSD - Top door being examined")    
      if (Door1.alive == 1 and Door1.locked == 0):
        Item = 'Door'
    elif (h == 7 and v == 3):
      #print ("DZSD - right door being examined")    
      if (Door2.alive == 1 and Door2.locked == 0):
        Item = 'Door'
    elif (h == 3 and v == 7):
      #print ("DZSD - Bottom door being examined")    
      if (Door3.alive == 1 and Door3.locked == 0):
        Item = 'Door'
    elif (h == 0 and v == 3):
      #print ("DZSD - left door being examined")    
      if (Door4.alive == 1 and Door4.locked == 0):
        Item = 'Door'
    else:
      #print ("DZSD - Not a door...then what is it? ",Playfield[h][v].name)
      Item = Playfield[h][v].name
      
      
  if (Item == ''):
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    print ('REeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!')
    #time.sleep(5)  
  return Item


def DotZerkScanHuman(h,v,direction,Playfield):

  #Scans cannot go through walls.  If a wall is encountered (forward) than all subsequent items will be the wall
  

  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
  WallHit       = 0
#          12
#          11
#          10                             
#           9                             
#           8                             
#           7                            
#           6                              
#        2  3   4                            
#        1      5
                                           

  print("--------------------------------------------")     
  #print("DZSH - hv direction",h,v,direction)
  
  #1
  ScanDirection = TurnLeft(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(h,v,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  print ("DZSH1 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #2
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  print ("DZSH2 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #3
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH3 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #4
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #5
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #6
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #7
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #8
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #9
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #10
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #11
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #12
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  
  return ItemList;



def DotZerkScanStraightLine(h,v,direction,Playfield):
  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
  WallHit       = 0

#           7
#           6
#           5                             
#           4                             
#           3                             
#           2                            
#           1                              
                                           

  print ("")
  print("== DZ Scan Straight Line")     
  #print("DZSSL - hv direction",h,v,direction)
  
  #1
  ScanH, ScanV = CalculateDotMovement(h,v,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSSL - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #2
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSSL - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #3
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSSL - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #4
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #5
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #6
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #7
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  if (Item == 'Wall' or WallHit == 1):
    ItemList.append('Wall')
    WallHit = 1
  else:
    ItemList.append(Item)
  #print ("DZSH - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  return ItemList;



  

  
def DotZerkScanRobot(h,v,direction,Playfield):
  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
#          12
#          11
#          10                             
#           9                             
#           8                             
#           7                            
#           6                              
#        2  3   4                            
#        1      5
                                           

  print("--------------------------------------------")     
  #print("DZSH - hv direction",h,v,direction)
  
  #1
  ScanDirection = TurnLeft(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(h,v,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR1 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #2
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR2 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #3
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR3 - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #4
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #5
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #6
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanDirection = TurnRight(ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #7
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)

  #8
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #9
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #10
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #11
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  #12
  ScanH, ScanV = CalculateDotMovement(ScanH,ScanV,ScanDirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  ItemList.append(Item)
#  print ("DZSR - hv ScanH ScanV Item",h,v,ScanH,ScanV, Item)
  
  
  return ItemList;


  

  
  

      
def DotZerkMoveMissile(Missile,Ship,Playfield):

  #The ship being passed in is the object that launched the missile
  
  global Empty
  print ("DZMM - MoveMissile:",Missile.name)
  
  #Record the current coordinates
  h = Missile.h
  v = Missile.v

#  if (Ship.name <> "Human"):
#    FlashDot(h,v,0.01)
  
  #FF (one square in front of missile direction of travel)
  ScanH, ScanV = CalculateDotMovement(Missile.h,Missile.v,Missile.scandirection)
  Item = DotZerkScanDot(ScanH,ScanV,Playfield)
  
  print("DZMM Item: ",Item)
  
  #Priority
  # 1 Hit target
  # 2 See if we are hit by enemy missle
  # 3 Move forward

  print ("DZMM - Item Name", Item)

  
  #Don't blow up yourself
  if (Item == Ship.name):
    print ("DZMM - Abort missile!  Don't hit your own launch vehicle")
    Missile.exploding = 1
    Missile.alive = 0

    
  
  #See if other target ship is hit
  elif (Item  == 'Human' or Item == 'Robot' or Item == 'RobotMissile' or Item == "HumanMissile" ):
    #target hit, kill target
    print ("*********************************")
    print ("DZMM - Target Hit!")
    print ("DZMM - Item Name", Item)
    Playfield[ScanH][ScanV].alive = 0
    Playfield[ScanH][ScanV].exploding = 1
    Playfield[ScanH][ScanV]= Empty
    unicorn.set_pixel(ScanH,ScanV,0,0,0)
      
      
    print ("*********************************")
    Missile.h = ScanH
    Missile.v = ScanV
    Missile.Display()
    Missile.exploding = 1
    Missile.alive = 0
    
  
  
  
  #Missiles explode on walls
  elif (Item == 'border' or Item == 'Wall' or Item == 'Door'):
    print ("DZMM - Missile hit border/wall/door")
    Missile.alive  = 0
    Missile.exploding = 1
    Missile.Erase()
    
  #empty = move forward
  elif (Item == 'empty' and Missile.alive == 1):
    Missile.h = ScanH
    Missile.v = ScanV
    Playfield[ScanH][ScanV] = Missile
    Missile.Display()
    print ("DZMM - empty, moving forward")
    
  #Keep missiles away from outer walls
  if (Missile.h == 7):
    Missile.h = 6
  if (Missile.h == 0):
    Missile.h = 1
  if (Missile.v == 7):
    Missile.v = 6
  if (Missile.v == 0):
    Missile.v = 1
    
    
  #Erase missile's old position
  if ((h <> Missile.h or v <> Missile.v) or
     (Missile.alive == 0)):
    if (Playfield[h][v].name <> 'Wall' and Playfield[h][v].name <> 'Door'):
      Playfield[h][v] = Empty
      unicorn.set_pixel(h,v,0,0,0)
      print ("DZMM - Erasing Missile")
  unicorn.show()
  
  #Display Ship to avoid strange flicker when the objects are too close to each other
  Ship.Display()
  
  return 

  
def DotZerkMoveRobot(Robot,Playfield):
  print ("DZMR - Name Direction HV:",Robot.name,Robot.direction,Robot.h,Robot.v)
  
  h = Robot.h
  v = Robot.v
  direction = Robot.scandirection
  ItemList = []
  #Scan all around, make decision, move
  ItemList = DotZerkScanRobot(Robot.h,Robot.v,direction,Playfield)
  print("DZMR - ItemList: ",ItemList)    
  #get possible items, then prioritize

  #Priority
  # 1 Shoot Player
  

  #If player is detected, fire missile!
  if ("Human" in ItemList):
    if (Robot1Missile.alive == 0 and Robot1Missile.exploding == 0):
      print ("############################################")
      print ("DZMR - Firing missile at human")
      Robot1Missile.h, Robot1Missile.v = h,v
      Robot1Missile.direction     = direction
      Robot1Missile.scandirection = direction
      Robot1Missile.alive = 1
      Robot.direction     = ReverseDirection(Robot.direction)
      Robot.scandirection = ReverseDirection(Robot.scandirection)
      print ("DZMR - robot missile HV",Robot1Missile.h,Robot1Missile.v)
      print ("############################################")

    
    #We don't want both missiles firing at the same time, so we use elif
    elif (Robot2Missile.alive == 0 and Robot2Missile.exploding == 0):
      print ("############################################")
      print ("DZMR - Firing missile at human")
      Robot2Missile.h, Robot2Missile.v = h,v
      Robot2Missile.direction     = direction
      Robot2Missile.scandirection = direction
      Robot2Missile.alive = 1
      Robot.direction     = ReverseDirection(Robot.direction)
      Robot.scandirection = ReverseDirection(Robot.scandirection)
      print ("DZMR - robot missile HV",Robot2Missile.h,Robot2Missile.v)
      print ("############################################")
      
  direction = Robot.scandirection

  
  if ((ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'Door' or ItemList[1] == 'Robot')
  and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'Door' or ItemList[3] == 'Robot')
  and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'Door' or ItemList[1] == 'Robot')):
    print ("Reversing direction")
    direction = ReverseDirection(direction)
    Robot.h, Robot.v =  CalculateDotMovement(h,v,direction)
    
  #Left Corner
  elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'Door')
    and (ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'Door')
    and (ItemList[5] == 'empty')):
    print ("Turn right")
    direction = TurnRight(direction)
    Robot.h, Robot.v =  CalculateDotMovement(h,v,direction)

  #Right Corner
  elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'Door')
    and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'Door')
    and (ItemList[1] == 'empty')):
    print ("Turn left")
    direction = TurnLeft(direction)
    Robot.h, Robot.v =  CalculateDotMovement(h,v,direction)
    
  
  #middle of wall
  elif ((ItemList[1] == 'empty')
    and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'Door')
    and (ItemList[5] == 'empty')):
    
    print ("Turn left or right")
    direction = TurnLeftOrRight(direction)
    Robot.h, Robot.v =  CalculateDotMovement(h,v,direction)
    
  
  
  elif (ItemList[5] == 'empty'):
    print("Go straigt")
    Robot.h, Robot.v =  CalculateDotMovement(h,v,direction)
  
  elif (ItemList[1] == 'empty' and ItemList[5] == 'Wall'):
    print ("go straight")
    Robot.h, Robot.v =  CalculateDotMovement(h,v,direction)

    
  else:
    print ("Go straight")
    Robot.h, Robot.v =  CalculateDotMovement(h,v,direction)



  #Prevent Robot from going into the walls
  if (Robot.h >= 7):
    Robot.h = 6
  if (Robot.v >= 7):
    Robot.v = 6
  if (Robot.h <= 0):
    Robot.h = 1
  if (Robot.v <= 0):
    Robot.v = 1

  Robot.direction = direction
  Robot.scandirection = direction      
    
  print("DZMR - OldHV: ",h,v, " NewHV: ",Robot.h,Robot.v, "direction: ",Robot.direction)
  Playfield[Robot.h][Robot.v]= Robot
  Robot.Display()
  
  if ((h <> Robot.h or v <> Robot.v) or
     (Robot.alive == 0)):
    if (Playfield[h][v].name <> 'Wall' and Playfield[h][v].name <> 'Door'):
      Playfield[h][v] = Empty
      unicorn.set_pixel(h,v,0,0,0)
    print ("DZMR - Erasing Robot")
  unicorn.show()

  
  return 

  




def DotZerkMoveHuman(Human,Playfield):
  global ExitingRoom
  global RobotsAlive
  global CurrentGear
  
  #print ("")
  #print ("== DZ Move Human ==")
  #print ("DZMH - MoveHuman HV Direction:",Human.h,Human.v,Human.direction)
  #print ("DZMH - RobotsAlive:",RobotsAlive)
  h = Human.h
  v = Human.v
  oldh  = h
  oldv  = v
  ScanH = 0
  ScanV = 0
  direction = Human.scandirection
  ItemList = []

  PrintDoorStatus()
  
  #Scan left, right, behind looking for robots only
  print("DZMH - Scan Right")
  direction = TurnRight(direction)
  ItemList = DotZerkScanStraightLine(h,v,direction,Playfield)
  #print (ItemList)
  if ("Robot" in ItemList or "RobotMissile" in ItemList):
    #print ("Robot to the right HumanMissile2.alive:",HumanMissile2.alive,HumanMissile2.exploding)
    if (HumanMissile2.alive == 0 and HumanMissile2.exploding == 0):
      HumanMissile2.h, HumanMissile2.v = CalculateDotMovement(h,v,direction)
      HumanMissile2.alive              = 1
      HumanMissile2.scandirection      = direction
      HumanMissile2.direction          = direction
      HumanMissile2.exploding          = 0
      #print("DZMH - FireMissile2 alive scandirection exploding",HumanMissile2.alive,HumanMissile2.scandirection,HumanMissile2.exploding)
      DotZerkAdjustSpeed(Human,'up')
  
  #we don't want the human to shoot, turn around, then do this scan and shoot again.
  #Reverse shots only work with Missile1
  #print("DZMH - Scan behind")
  direction = TurnRight(direction)
  ItemList = DotZerkScanStraightLine(h,v,direction,Playfield)
  #print (ItemList)
  if ("Robot" in ItemList or "RobotMissile" in ItemList):
    #print ("Robot behind us HumanMissile2.alive exploding:",HumanMissile1.alive,HumanMissile1.exploding)
    if (HumanMissile1.alive == 0 and HumanMissile1.exploding == 0):
      HumanMissile1.h, HumanMissile1.v = CalculateDotMovement(h,v,direction)
      HumanMissile1.alive              = 1
      HumanMissile1.scandirection      = direction
      HumanMissile1.direction          = direction
      HumanMissile1.exploding          = 0
      #print("DZMH - FireMissile1 alive scandirection exploding",HumanMissile1.alive,HumanMissile1.scandirection,HumanMissile1.exploding)
      DotZerkAdjustSpeed(Human,'up')

  #print("DZMH - Scan Left")
  direction = TurnRight(direction)
  ItemList = DotZerkScanStraightLine(h,v,direction,Playfield)
  #print (ItemList)
  if ("Robot" in ItemList or "RobotMissile" in ItemList):
    #print ("Robot to the left HumanMissile2.alive:",HumanMissile2.alive,HumanMissile2.exploding)
    if (HumanMissile2.alive == 0 and HumanMissile2.exploding == 0):
      HumanMissile2.h, HumanMissile2.v = CalculateDotMovement(h,v,direction)
      HumanMissile2.alive              = 1
      HumanMissile2.scandirection      = direction
      HumanMissile2.direction          = direction
      HumanMissile2.exploding          = 0
      #print("DZMH - FireMissile2 alive scandirection exploding",HumanMissile2.alive,HumanMissile2.scandirection,HumanMissile2.exploding)
      DotZerkAdjustSpeed(Human,'up')
      
  #Back to original direction (we did a 360)      
  #print("DZMH - Scan in front")
  direction = TurnRight(direction)

  #Scan all around, make decision, move
  ItemList = DotZerkScanHuman(h,v,direction,Playfield)
  
  #print("DZMH - ItemList",ItemList)
  #print("DZMH - Human.name HV",Human.name,Human.h,Human.v)
  #get possible items, then prioritize

  #Priority
  # 1 Evade close objects
  # 2 Blast far objects
  # 3 Follow right hand rule (or left hand rule, possibly different per room?)

  #Prevent collision of Robot and Human
  if (ItemList[3] == 'Robot'):
    #print ("DZMH - Robot detected immediately in front of human")
    ScanH,ScanV = CalculateDotMovement(h,v,direction)
    Playfield[ScanH][ScanV].alive = 0
    Playfield[ScanH][ScanV].exploding = 1
  
  
  #If Robot is detected, fire missile!
  #and reverse direction
  if ("Robot" in ItemList or "RobotMissile" in ItemList):
    if (HumanMissile1.alive == 0 and HumanMissile1.exploding == 0):
      #print ("***********************************")
      #print ("DZMH - Robot/RobotMissile Detected ")
      #print ("***********************************")
      HumanMissile1.h, HumanMissile1.v = CalculateDotMovement(h,v,direction)
#      HumanMissile1.h, HumanMissile1.v = h,v
      HumanMissile1.alive = 1
      HumanMissile1.scandirection = direction
      HumanMissile1.exploding = 0
      direction = ReverseDirection(direction)
      #print ("DZMH - Launching missile HV",HumanMissile1.h,HumanMissile1.v)
      #print ("DZMH - missile direction",HumanMissile1.direction)
      DotZerkAdjustSpeed(Human,'up')
      DotZerkAdjustSpeed(Human,'up')
      DotZerkAdjustSpeed(Human,'up')

  
  #Behave differently if all robots are dead
  if (RobotsAlive == 0):
    #print ("DZMH - Robots dead")
    if ((ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'RobotMissile' or ItemList[1] == 'HumanMissile')
    and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile')
    and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile' or ItemList[5] == 'HumanMissile')):
      #print ("Reversing direction")
      direction = ReverseDirection(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'up')
      DotZerkAdjustSpeed(Human,'up')
      DotZerkAdjustSpeed(Human,'up')

    #Left Corner
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile')
      and (ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'RobotMissile' or ItemList[1] == 'HumanMissile')
      and (ItemList[5] == 'empty')):
      #print ("Turn right")
      direction = TurnRight(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)

    #Right Corner
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile')
      and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile')
      and (ItemList[1] == 'empty')):
      #print ("Turn left")
      direction = TurnLeft(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      
    
    #middle of wall
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall'  or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile')
      and (ItemList[5] == 'empty')
      and (ItemList[1] == 'empty')):
      #print ("DZMH - Middle of the wall, turning left or right")
      direction = TurnLeftOrRight(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      

    #three sides empty
    elif ((ItemList[3] == 'empty')
      and (ItemList[5] == 'empty')
      and (ItemList[1] == 'empty')):
      
      #print ("Turn left or right or straight")
      r = random.randint(0,3)
      if (r == 1 or r == 2):
        direction = TurnLeftOrRight(direction)
        Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      else:
        Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      
      

      
    elif (ItemList[1] == 'Door'):
      direction = TurnLeft(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      ExitingRoom = 1
      print("Opening Door1")    
    elif (ItemList[3] == 'Door'):
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      ExitingRoom = 1
      print("Opening Door3")    
    elif (ItemList[5] == 'Door'):
      direction = TurnRight(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      ExitingRoom = 1
      print("Opening Door5")    
      
    elif ((ItemList[1] == 'empty')
      and (ItemList[3] == 'border' or ItemList[3] == 'Wall'  or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile')
      and (ItemList[5] == 'empty')):
      
      print ("Turn left or right")
      direction = TurnLeftOrRight(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)

      
    
    elif (ItemList[5] == 'empty'):
      print("Go straigt")
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
    
    elif (ItemList[1] == 'empty' and (ItemList[5] == 'Wall'  or ItemList[5] == 'RobotMissile' or ItemList[5] == 'HumanMissile')):
      print ("go left")
      direction = TurnLeft(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      
    else:
      print ("Go straight")
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)

  
  elif (RobotsAlive >= 1):
    print ("DZMH - Robots Alive!")
    #Hit the road if you see a robot
    if (ItemList[1]  == 'Robot' 
     or ItemList[2]  == 'Robot' 
     or ItemList[3]  == 'Robot' 
     or ItemList[4]  == 'Robot' 
     or ItemList[5]  == 'Robot'
     or ItemList[6]  == 'Robot'
     or ItemList[7]  == 'Robot'
     or ItemList[8]  == 'Robot'
     or ItemList[9]  == 'Robot'
     or ItemList[10] == 'Robot'):
      print ("DZMH - Robot Detected - Reversing direction")
      direction = ReverseDirection(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'up')

        
    elif ((ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'RobotMissile'  or ItemList[1] == 'HumanMissile' or ItemList[1] == 'Door')
      and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile'  or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile'  or ItemList[5] == 'HumanMissile' or ItemList[5] == 'Door')):
      print ("DZMH - blocked on left front and right - Reversing direction")
      direction = ReverseDirection(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')

    #Left Corner
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[1] == 'border' or ItemList[1] == 'Wall' or ItemList[1] == 'RobotMissile' or ItemList[1] == 'HumanMissile' or ItemList[1] == 'Door')
      and (ItemList[5] == 'empty')):
      print ("DZMH - Left Corner - Turn right")
      direction = TurnRight(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')


    #Right Corner
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[5] == 'border' or ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile' or ItemList[5] == 'HumanMissile' or ItemList[5] == 'Door')
      and (ItemList[1] == 'empty')):
      print ("DZMH - Right Corner - Turn left")
      direction = TurnLeft(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')
      

    #middle of wall
    elif ((ItemList[3] == 'border' or ItemList[3] == 'Wall'  or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[5] == 'empty')
      and (ItemList[1] == 'empty')):
      print ("DZMH - Middle of the wall, turning left or right")
      direction = TurnLeftOrRight(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')

      
      
    elif ((ItemList[1] == 'empty')
      and (ItemList[3] == 'border' or ItemList[3] == 'Wall' or ItemList[3] == 'RobotMissile' or ItemList[3] == 'HumanMissile' or ItemList[3] == 'Door')
      and (ItemList[5] == 'empty')):
      
      print ("DZMH - Empty both sides - Turn left or right")
      direction = TurnLeftOrRight(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'down')

    
    
    elif (ItemList[5] == 'empty'):
      print("DZMH - Right side empty - Go straigt")
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'up')
    
    elif (ItemList[1] == 'empty' and (ItemList[5] == 'Wall' or ItemList[5] == 'RobotMissile' or ItemList[5] == 'HumanMissile' or ItemList[5] == 'Door')):
      print ("DZMH - Left is empty, right is blocked - turn left")
      direction = TurnLeft(direction)
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)

      
    else:
      print ("DZMH - Give up - Go straight")
      Human.h, Human.v =  CalculateDotMovement(h,v,direction)
      DotZerkAdjustSpeed(Human,'up')


  #Prevent Human from going into the walls (except for doors)

  
  
  
  #Don't let human hit outside walls
  if (Human.h == 7 and Human.v <> 3):
    Human.h = 6
  if (Human.h == 0 and Human.v <> 3):
    Human.h = 1
  if (Human.v == 7 and Human.h <> 3):
    Human.v = 6
  if (Human.v == 0 and Human.h <> 3):
    Human.v = 1
  
  
  if (Human.h == 3 and Human.v <= 0):
    if (Door1.locked == 1):
      Human.v = 1
      direction = TurnLeftOrRight(Human.direction)
      print("Stuck at door. new direction:",direction)
  if (Human.h >= 7 and Human.v == 3):
    if (Door2.locked == 1):
      Human.h = 6
      direction = TurnLeftOrRight(Human.direction)
      print("Stuck at door. new direction:",direction)
  if (Human.h == 3 and Human.v >= 7):
    if (Door3.locked == 1):
      Human.v = 6
      direction = TurnLeftOrRight(Human.direction)
      print("Stuck at door. new direction:",direction)
  if (Human.h <= 0 and Human.v == 3):
    if (Door4.locked == 1):
      Human.h = 1
      direction = TurnLeftOrRight(direction)
      print("Stuck at door. new direction:",Human.direction)
    
      

  Human.direction = direction
  Human.scandirection = direction      
  print ("DZMH - HumanDirection:",Human.direction)
    
  print("DZMH - OldHV: ",h,v, " NewHV: ",Human.h,Human.v, "direction: ",Human.direction)
  Playfield[Human.h][Human.v]= Human
  Human.Display()
  



  
  #If missiles alive, place on playfield
  if (HumanMissile1.alive == 1):
    Playfield[HumanMissile1.h][HumanMissile1.v]=HumanMissile1
  if (HumanMissile2.alive == 1):
    Playfield[HumanMissile2.h][HumanMissile2.v]=HumanMissile2
  
  if ((h <> Human.h or v <> Human.v) or
     (Human.alive == 0)):
    if (Playfield[h][v].name <> 'Wall' and Playfield[h][v].name <> 'Door'):
      Playfield[h][v] = Empty
      unicorn.set_pixel(h,v,0,0,0)
    print ("MPS - Erasing Player")
  unicorn.show()

  print("DZMH - Human.direction: ",Human.direction)

  if (Human.h == 0 or Human.h == 7 or Human.v == 0 or Human.v == 7):
    print("***************************************")
    print("***************************************")
    print("***************************************")
    print("***************************************")
    print("***************************************")

  return 

          
          
def PlayDotZerk():
  
  unicorn.off()  

  
  
  #Local variables
  moves       = 0
  Roommoves   = 500
  Finished    = 'N'
  LevelCount  = 1
  SleepTime   = MainSleep / 4
  Key         = ""
  
  #Global variables
  global ExitingRoom
  global RobotsAlive
  global DirectionOfTravel
  global DotZerkScore
  DotZerkScore = 0
  
  Human.lives = 3
  LifeCounter = Human.lives

  #Title
  ShowScrollingBanner("DotZerk",30,100,0,ScrollSleep)

  ShowLevelCount(Human.lives)
  
  
  
  
  
  
  
  
  
  
  #Main Game Loop
  while (Finished == 'N'):


  
    if (LifeCounter <> Human.lives):
      ShowLevelCount(Human.lives)
      LifeCounter = Human.lives

    
    
    #Reset Variables between rounds
    LevelFinished    = 'N'
    Human.alive      = 1
    Human.speed      = Gear[4]
    Roommoves        = 0
    
    
    Human.exploding  = 0
    HumanMissile1.exploding = 0
    HumanMissile2.exploding = 0
    HumanMissile1.speed = 5
    HumanMissile2.speed = 5
    HumanMissile1.alive = 0
    HumanMissile2.alive = 0
    #Robot1.h = 6
    #Robot1.v = 6

    #Fix walls and doors that accidentally blew up by missiles
    DoorCheckSpeed = 50
    
    
    Robot1.alive         = 1
    Robot1.direction     = 3
    Robot1.speed         = 20
    
    Robot2.alive         = 1
    Robot2.direction     = 3
    Robot2.speed         = 40
    
    #Robot3 is a killer, only appears to finish off Human if taking too long (bugs!)
    Robot3.alive         = 0
    Robot3.direction     = 1
    Robot3.speed         = 25
    
    
    RobotsAlive          = 2
    
    Robot1.scandirection = 3
    Robot2.scandirection = 3
    Robot1Missile.alive  = 0
    Robot2Missile.alive  = 0
    Robot3Missile.alive  = 0
    Robot4Missile.alive  = 0
    Robot1Missile.direction = 0
    Robot1Missile.scandirection = 0
    Robot1Missile.speed         = 7
    Robot2Missile.direction = 0
    Robot2Missile.scandirection = 0
    Robot2Missile.speed         = 7
    


    
    #Reset colors
    Robot1Missile.r = PlayerMissileR
    Robot1Missile.g = PlayerMissileG
    Robot1Missile.b = PlayerMissileB
    Robot2Missile.r = PlayerMissileR
    Robot2Missile.g = PlayerMissileG
    Robot2Missile.b = PlayerMissileB
    Robot3Missile.r = PlayerMissileR
    Robot3Missile.g = PlayerMissileG
    Robot3Missile.b = PlayerMissileB
    Robot4Missile.r = PlayerMissileR
    Robot4Missile.g = PlayerMissileG
    Robot4Missile.b = PlayerMissileB
    
    HumanMissile1.r = PlayerMissileR
    HumanMissile1.g = PlayerMissileG
    HumanMissile1.b = PlayerMissileB

    HumanMissile2.r = PlayerMissileR
    HumanMissile2.g = PlayerMissileG
    HumanMissile2.b = PlayerMissileB

    Robot1.r = SDLowRedR
    Robot1.g = SDLowRedG
    Robot1.b = SDLowRedB
    
    Robot2.r = SDLowRedR
    Robot2.g = SDLowRedG
    Robot2.b = SDLowRedB

    Robot3.r = SDMedYellowR
    Robot3.g = SDMedYellowG
    Robot3.b = SDMedYellowB


    ExitingRoom = 0
    
    
    #Show fancy effects only the first time through
    if(moves == 0):
      unicorn.set_pixel(Robot1.h,Robot1.v,0,0,0)
      unicorn.set_pixel(Robot2.h,Robot2.v,0,0,0)
      DotZerkResetPlayfield(ShowFlash=1)
    else:
      DotZerkResetPlayfield(ShowFlash=0)
    
    
    
    # Main timing loop
    while (LevelFinished == 'N' and Human.alive == 1):
      moves     = moves + 1
      Roommoves = Roommoves + 1
      
      
      #Check for keyboard input
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = PollKeyboard()
        if (Key == 'q'):
          LevelFinished = 'Y'
          Finished      = 'Y'
          Human.alive   = 0
          Human.lives   = 0
          return
      
      if (Roommoves >= 500 and Robot3.alive == 0):
        Robot3.alive = 1
        print ("*** Time to die, human! ***")
        Roommoves = 0
      
      if (Roommoves >= 5000):
        Human.alive = 0
        Human.exploding = 1
        print ("*** YOU TOOK TOO LONG ***")
        ShowScrollingBanner("THE HUMANOID HAS TERMINATED!",30,100,0,ScrollSleep)
        Roommoves = 0
      
      
      
      if (Human.alive == 1):
        #print ("M - Human HV speed alive exploding direction scandirection: ",Human.h, Human.v,Human.speed, Human.alive, Human.exploding, Human.direction,Human.ScanDirection)
        m,r = divmod(moves,Human.speed)
        if (r == 0):
          DotZerkMoveHuman(Human,MazeWorld.Playfield)
        
          
          print ("M - ExitingRoom: ",ExitingRoom)
          if (ExitingRoom == 1 and RobotsAlive == 0):
            #Turn off killer robot
            
            if (Robot3.alive == 1):
              ShowChickenTaunt(ScrollSleep * 0.75)

            Robot3.alive = 0
            DotZerkExitRoom(Human.direction)
            ExitingRoom = 0
            LevelFinished = 'Y'
            DirectionOfTravel = Human.direction
            
            

            

          print ("=================================================")
          for H in range(0,7):
            for V in range (0,7):
             if (MazeWorld.Playfield[H][V].name <> 'empty' and MazeWorld.Playfield[H][V].name <> 'Wall'):
               print ("Playfield: HV Name Alive Lives",H,V,MazeWorld.Playfield[H][V].name,MazeWorld.Playfield[H][V].alive, Human.lives )
          print ("Robot1.alive Robot2.alive RobotsAlive:",Robot1.alive,Robot2.alive,RobotsAlive)
          print ("Robot1.exploding Robot2.exploding:",Robot1.exploding,Robot2.exploding)
          print ("=================================================")
      


            
      
      if (Robot1.alive == 1):
        m,r = divmod(moves,Robot1.speed)
        if (r == 0):
          DotZerkMoveRobot(Robot1,MazeWorld.Playfield)
          
      if (Robot2.alive == 1):
        m,r = divmod(moves,Robot2.speed)
        if (r == 0):
          DotZerkMoveRobot(Robot2,MazeWorld.Playfield)

      if (Robot3.alive == 1):
        m,r = divmod(moves,Robot3.speed)
        if (r == 0):
          DotZerkMoveRobot(Robot3,MazeWorld.Playfield)
        
          

          
      #We should pass in the shooter's object as well
      #This will allow the missile to provide feedback      
      if (Robot1Missile.alive == 1 and Robot1Missile.exploding == 0):
        m,r = divmod(moves,Robot1Missile.speed)
        if (r == 0):
          DotZerkMoveMissile(Robot1Missile,Robot1,MazeWorld.Playfield)

      if (Robot2Missile.alive == 1 and Robot2Missile.exploding == 0):
        print ("2")
        m,r = divmod(moves,Robot2Missile.speed)
        if (r == 0):
          DotZerkMoveMissile(Robot2Missile,Robot2,MazeWorld.Playfield)

      if (Robot3Missile.alive == 1 and Robot3Missile.exploding == 0):
        print ("3")
        m,r = divmod(moves,Robot3Missile.speed)
        if (r == 0):
          DotZerkMoveMissile(Robot3Missile,Robot3,MazeWorld.Playfield)

      if (Robot4Missile.alive == 1 and Robot4Missile.exploding == 0):
        print ("4")
        m,r = divmod(moves,Robot4Missile.speed)
        if (r == 0):
          DotZerkMoveMissile(Robot4Missile,Robot4,MazeWorld.Playfield)
          
      if (HumanMissile1.alive == 1 and HumanMissile1.exploding == 0):
        print ("5")
        m,r = divmod(moves,HumanMissile1.speed)
        if (r == 0):
          DotZerkMoveMissile(HumanMissile1,Human,MazeWorld.Playfield)

      if (HumanMissile2.alive == 1 and HumanMissile2.exploding == 0):
        m,r = divmod(moves,HumanMissile2.speed)
        if (r == 0):
          DotZerkMoveMissile(HumanMissile2,Human,MazeWorld.Playfield)

          

      m,r = divmod(moves,DoorCheckSpeed)
      if (r== 0):
        MazeWorld.CopyMapToPlayfield()
        DotZerkDisplayDoors()  

        
             
          

        

      #Check for exploding objects
      if (Robot1.exploding == 1):
        print("------> Robot1.exploding: ",Robot1.exploding)
        DotZerkExplodeRobot(Robot1,MazeWorld.Playfield,20)


      #Check for exploding objects
      if (Robot2.exploding == 1):
        print("------> Robot2.exploding: ",Robot2.exploding)
        DotZerkExplodeRobot(Robot2,MazeWorld.Playfield,20)

      #Check for exploding objects
      if (Robot3.exploding == 1):
        print("------> Robot3.exploding: ",Robot3.exploding)
        DotZerkExplodeRobot(Robot3,MazeWorld.Playfield,20)

      if (HumanMissile1.exploding == 1):
        print("------> HumanMissile1.exploding: ",HumanMissile1.exploding)
        DotZerkExplodeMissile(HumanMissile1,MazeWorld.Playfield,20)

      if (HumanMissile2.exploding == 1 ):
        print("------> HumanMissile2.exploding: ",HumanMissile2.exploding)
        DotZerkExplodeMissile(HumanMissile2,MazeWorld.Playfield,20)


      if (Robot1Missile.exploding == 1 ):
        #print("------> Robot1Missile.exploding: ",Robot1Missile.exploding)
        DotZerkExplodeMissile(Robot1Missile,MazeWorld.Playfield,20)

      if (Robot2Missile.exploding == 1 ):
        #print("------> Robot2Missile.exploding: ",Robot2Missile.exploding)
        DotZerkExplodeMissile(Robot2Missile,MazeWorld.Playfield,20)

      if (Robot3Missile.exploding == 1 ):
        #print("------> Robot3Missile.exploding: ",Robot3Missile.exploding)
        DotZerkExplodeMissile(Robot3Missile,MazeWorld.Playfield,20)
        

      #Make sure robot alive indicator is set
      #And boost human speed
      if (Robot1.alive == 0 and Robot2.alive == 0):
        RobotsAlive = 0

        
      #=================================
      #= End of level conditions       =
      #=================================
     
      if (Human.alive == 0):
        Human.lives = Human.lives - 1

        if (Human.lives <=0):
          Finished = 'Y'

        buffer = unicorn.get_pixels()
        HumanExplosion.Animate(Human.h-1,Human.v-1,'forward',0.025)
        unicorn.set_pixels(buffer)
        Human.Erase()
        moves=0
        

      #Display animation and clock every X seconds
      if (CheckElapsedTime(CheckTime) == 1):
        ScrollScreenShowDotZerkRobotTime('down',ScrollSleep)         



        
      time.sleep(MainSleep / 5)
  print ("M - The end?")    
  unicorn.off()

  if (Key <> "q"):
    ScoreString = str(DotZerkScore) 
    ShowScrollingBanner("Score",SDLowPurpleR,SDLowPurpleG,SDLowPurpleB,ScrollSleep)
    ShowScrollingBanner(ScoreString,SDLowGreenR,SDLowGreenG,SDLowGreenB,(ScrollSleep * 2))
    ShowScrollingBanner("GAME OVER",SDLowRedR,SDLowRedG,SDLowRedB,ScrollSleep)
















  
#--------------------------------------
#  Transitions and Sequences         --
#--------------------------------------

    

def ScrollScreenScrollBanner(message,r,g,b,direction,speed):
  
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
    ShowScrollingBanner(message,r,g,b,speed)
 
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

  if (direction == 'down'):
    for x in range(0,8):
      del ScreenCap[7]
      ScreenCap.insert(0,EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

    ShowScrollingBanner(message,r,g,b,speed)

    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)







def ShowAllAnimations(speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,SDLowRedR,SDLowRedG,SDLowRedB)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  for x in range(0,8):
    del ScreenCap[0]
    ScreenCap.append(EmptyCap[0])
    unicorn.set_pixels(ScreenCap)
    unicorn.show()
    time.sleep(speed)

  FrogSprite.LaserScan(0,0,speed/8)
  time.sleep(1)
  FrogSprite.LaserErase(0,0,speed/8)
  FrogSprite.Scroll(-8,0,"right",16,speed)
  FrogSprite.HorizontalFlip()
  FrogSprite.Scroll(8,0,"left",16,speed)
  FrogSprite.HorizontalFlip()

  ChickenRunning.LaserScan(0,0,speed/8)
  time.sleep(1)
  ChickenRunning.LaserErase(0,0,speed/8)
  ChickenRunning.HorizontalFlip()
  ChickenRunning.Scroll(-8,0,"right",16,speed)
  ChickenRunning.HorizontalFlip()
  ChickenRunning.Scroll(8,0,"left",16,speed)

  ChickenChasingWorm.ScrollAcrossScreen(0,0,'left',ScrollSleep)
  ChickenChasingWorm.HorizontalFlip()
  ChickenChasingWorm.ScrollAcrossScreen(0,0,'right',speed)
  ChickenChasingWorm.HorizontalFlip()
  

  DotZerkRobotWalking.LaserScan(0,0,speed/8)
  time.sleep(1)
  DotZerkRobotWalking.LaserErase(0,0,speed/8)
  DotZerkRobotWalking.ScrollAcrossScreen(0,0,'left',speed)
  DotZerkRobotWalking.HorizontalFlip()
  DotZerkRobotWalking.ScrollAcrossScreen(0,0,'right',speed)
  DotZerkRobotWalking.HorizontalFlip()

  DotZerkRobotWalkingSmall.LaserScan(0,2,speed/8)
  time.sleep(1)
  DotZerkRobotWalkingSmall.LaserErase(0,2,speed/8)
  DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,2,'left',speed)
  DotZerkRobotWalkingSmall.HorizontalFlip()
  DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,2,'right',speed)
  DotZerkRobotWalkingSmall.HorizontalFlip()
  
  TinyInvader.LaserScan(2,1,speed/8)
  time.sleep(1)
  TinyInvader.LaserErase(2,1,speed/8)
  TinyInvader.ScrollAcrossScreen(0,1,'left',speed)
  TinyInvader.HorizontalFlip()
  TinyInvader.ScrollAcrossScreen(0,1,'right',speed)
  TinyInvader.HorizontalFlip()
  
  SmallInvader.LaserScan(0,1,speed/8)
  time.sleep(1)
  SmallInvader.LaserErase(0,1,speed/8)
  SmallInvader.ScrollAcrossScreen(0,1,'left',speed)
  SmallInvader.HorizontalFlip()
  SmallInvader.ScrollAcrossScreen(0,1,'right',speed)
  SmallInvader.HorizontalFlip()

  SpaceInvader.LaserScan(-1,0,speed/8)
  time.sleep(1)
  SpaceInvader.LaserErase(-1,0,speed/8)
  SpaceInvader.ScrollAcrossScreen(0,0,'left',speed)
  SpaceInvader.HorizontalFlip()
  SpaceInvader.ScrollAcrossScreen(0,0,'right',speed)
  SpaceInvader.HorizontalFlip()
  
  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()

  LittleShipFlying.ScrollAcrossScreen(0,0,'left',speed)
  BigShipFlying.ScrollAcrossScreen(0,0,'left',speed)

  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()
  LittleShipFlying.ScrollAcrossScreen(0,0,'right',speed * 0.50)
  BigShipFlying.ScrollAcrossScreen(0,0,'right',speed * 0.50)

  #Reverse direction, bringing screen back down  
  for x in range(0,8):
    del ScreenCap[-1]
    ScreenCap.insert(0,Buffer[7-x])
    unicorn.set_pixels(ScreenCap)
    unicorn.show()
    time.sleep(speed)



def ShowLongIntro(speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,SDLowRedR,SDLowRedG,SDLowRedB)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  for x in range(0,8):
    del ScreenCap[0]
    ScreenCap.append(EmptyCap[0])
    unicorn.set_pixels(ScreenCap)
    unicorn.show()
    time.sleep(speed)

  
  ShowScrollingBanner("Arcade retro clock",SDLowYellowR,SDLowYellowG,SDLowYellowB,speed)
  ShowScrollingBanner("by Datagod",SDLowGreenR,SDLowGreenG,SDLowGreenB,speed)

  DotZerkRobotWalking.LaserScan(0,0,speed/8)
  time.sleep(0.5)
  ScrollScreenScrollBanner("multiple games",SDMedBlueR,SDMedBlueG,SDMedBlueB,'down',speed)
  time.sleep(0.5)
  DotZerkRobotWalking.LaserErase(0,0,speed/8)
  DotZerkRobotWalking.ScrollAcrossScreen(0,0,'left',speed)

  ShowScrollingBanner("cut scenes",SDLowPurpleR,SDLowPurpleG,SDLowPurpleB,speed)
  
  ChickenChasingWorm.ScrollAcrossScreen(0,0,'left',ScrollSleep)
  DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,2,'left',speed)


  TinyInvader.LaserScan(2,1,speed/8)
  time.sleep(0.5)
  ScrollScreenScrollBanner("aliens!",SDLowRedR,SDLowRedG,SDLowRedB,'up',speed)
  time.sleep(0.5)
  TinyInvader.LaserErase(2,1,speed/8)
  TinyInvader.ScrollAcrossScreen(0,1,'left',speed)
  SmallInvader.ScrollAcrossScreen(0,1,'left',speed)
  SpaceInvader.ScrollAcrossScreen(0,0,'left',speed)

  ShowScrollingBanner("epic space battles",SDLowOrangeR,SDLowOrangeG,SDLowOrangeB,speed)  
  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()

  LittleShipFlying.ScrollAcrossScreen(0,0,'left',speed)
  BigShipFlying.ScrollAcrossScreen(0,0,'left',speed)
  LittleShipFlying.HorizontalFlip()
  BigShipFlying.HorizontalFlip()

  ShowScrollingBanner("tells time too!",SDLowOrangeR,SDLowOrangeG,SDLowOrangeB,speed)  
  TheTime = CreateClockSprite(12)    
  TheTime.r = SDMedRedR
  TheTime.g = SDMedRedG
  TheTime.b = SDMedRedB
  TheTime.ScrollAcrossScreen(0,1,"left",speed)
  TheTime.ScrollAcrossScreen(0,1,"left",speed)
  
  
  ShowScrollingBanner("Ready Player One?      GO!",SDLowOrangeR,SDLowOrangeG,SDLowOrangeB,speed)  
 
  
  #Reverse direction, bringing screen back down  
  for x in range(0,8):
    del ScreenCap[-1]
    ScreenCap.insert(0,Buffer[7-x])
    unicorn.set_pixels(ScreenCap)
    unicorn.show()
    time.sleep(speed)

    
    
    
    

def ScrollScreenShowFrogTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
    ShowFrogTime(speed)
 
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

  if (direction == 'down'):
    for x in range(0,8):
      del ScreenCap[7]
      ScreenCap.insert(0,EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

    ShowFrogTime(speed)

    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

      
def ShowFrogTime(speed):
  TheTime = CreateClockSprite(12)
  TheTime.r = SDLowGreenR
  TheTime.g = SDLowGreenG
  TheTime.b = SDLowGreenB

  if (random.randint(0,2) == 1):
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    FrogSprite.LaserScan(0,0,speed/8)
    time.sleep(1)
    FrogSprite.LaserErase(0,0,speed/8)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
  else:
    FrogSprite.Scroll(-8,0,"right",16,speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    FrogSprite.HorizontalFlip()
    FrogSprite.Scroll(8,0,"left",16,speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
    

  
    

    
    


def ScrollScreenShowChickenWormTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
    ShowChickenWorm(speed)
 
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

  if (direction == 'down'):
    for x in range(0,8):
      del ScreenCap[7]
      ScreenCap.insert(0,EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

    ShowChickenWorm(speed)

    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

      
      

def ShowChickenWorm(speed):
 
  TheTime   = CreateClockSprite(12)
  TheTime.r = SDLowGreenR
  TheTime.g = SDLowGreenG
  TheTime.b = SDLowGreenB
    
  r = random.randint(0,2)
  if (r == 0):
    ChickenChasingWorm.ScrollAcrossScreen(0,0,'left',ScrollSleep)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
    ChickenChasingWorm.HorizontalFlip()
    ChickenChasingWorm.ScrollAcrossScreen(0,0,'right',speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    ChickenChasingWorm.HorizontalFlip()

  elif (r == 1):
    WormChasingChicken.ScrollAcrossScreen(0,0,'left',speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
    WormChasingChicken.HorizontalFlip()
    WormChasingChicken.ScrollAcrossScreen(0,0,'right',speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    WormChasingChicken.HorizontalFlip()

  elif (r == 2):
    ShowWorms(speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
  


def ShowChickenTaunt(speed):
  unicorn.off()

  ShowScrollingBanner("Chicken",100,100,0,speed * 0.8)
  ChickenRunning.ScrollAcrossScreen(0,0,'left',speed)
  DotZerkRobotWalking.ScrollAcrossScreen(0,0,'left',speed)
  #ShowScrollingBanner("fight like a robot",35,80,0,speed * 0.8)
  
    
    

def GetClockDot(time):
  #this is a list of hv coordinates around the outside of the unicorn hat
  #pass in a number from 1-60 to get the correct dot to display
  
  DotList = []
  DotList.append ([4,0]) #0 same as 60
  DotList.append ([4,0])
  DotList.append ([5,0])
  DotList.append ([6,0])
  DotList.append ([7,0])
  DotList.append ([7,1])
  DotList.append ([7,2])
  DotList.append ([7,3])
  DotList.append ([7,4])
  DotList.append ([7,5])
  DotList.append ([7,6])
  DotList.append ([7,7])
  DotList.append ([6,7])
  DotList.append ([5,7])
  DotList.append ([4,7])
  DotList.append ([3,7])
  DotList.append ([2,7])
  DotList.append ([1,7])
  DotList.append ([0,7])
  DotList.append ([0,6])
  DotList.append ([0,5])
  DotList.append ([0,4])
  DotList.append ([0,3])
  DotList.append ([0,2])
  DotList.append ([0,1])
  DotList.append ([0,0])
  DotList.append ([1,0])
  DotList.append ([2,0])
  DotList.append ([3,0])
  
  return DotList[time]


def DrawTinyClock(Minutes):
  print ("--DrawTinyClock--")
  print ("Minutes:",Minutes)
  unicorn.off()
  MinDate = datetime.now()
  MaxDate = datetime.now() + timedelta(minutes=Minutes)
  now     = datetime.now()
  Quit    = 0
  

  while (now >= MinDate and now <= MaxDate and Quit == 0):
    print ("--DrawTinyClock--")
    unicorn.off()
    ClockSprite = CreateClockSprite(2)
    ClockSprite.r = SDDarkRedR
    ClockSprite.g = SDDarkRedG
    ClockSprite.b = SDDarkRedB


    #Center the display
    h = 3 - (ClockSprite.width / 2)
    ClockSprite.Display(h,1)

    #break apart the time
    now = datetime.now()

    print ("Now:",now)
    print ("Min:",MinDate)
    print ("Max:",MaxDate)
    DrawClockMinutes()
    Quit = DrawClockSeconds()
    print("Quit:",Quit)
    now = datetime.now()

  unicorn.off()    
    
def DrawClockMinutes():

  #break apart the time
  now = datetime.now()
  mm  = now.minute
  print ("DrawClockMinutes minutes:",mm)  
  
  dots = int(28.0 / 60.0 * mm)

#  #Erase  
  for i in range(1,28):
    h,v = GetClockDot(i)
  unicorn.set_pixel(h,v,0,0,0)
  unicorn.show()

  
  for i in range(1,dots+1):
    print ("Setting minute dot:",i)
    h,v = GetClockDot(i)
    unicorn.set_pixel(h,v,SDDarkBlueR,SDDarkBlueG,SDDarkBlueB)
    unicorn.show()
  
  
  
  
def DrawClockSeconds():
  #break apart the time
  now = datetime.now()
  ss  = now.second
  
  print ("--DrawClockSeconds seconds:",ss,"--")  

  r = 0
  g = 0
  b = 0
  
   
  h = 0
  v = 0
  x = -1
  y = -1
  
  
  unicorn.set_pixel(3,0,0,0,0)


  for i in range(ss,61):
    
    #Erase dot 0/60
    DisplayDot =  int(28.0 / 60.0 * i)
    h,v = GetClockDot(DisplayDot)
    
    
    print ("Setting second dot:",i)
    #print ("xy hv:",x,y,h,v)
    if (x >= 0):
      #print ("writing old pixel")
      unicorn.set_pixel(x,y,r,g,b)

    
    #capture previous pixel
    x,y = h,v
    
    r,g,b = unicorn.get_pixel(h,v)
    unicorn.set_pixel(h,v,SDLowWhiteR,SDLowWhiteG,SDLowWhiteB)
    unicorn.show()
    time.sleep(0.005)

    unicorn.set_pixel(h,v,SDDarkPurpleR,SDDarkPurpleG,SDDarkPurpleB)
    unicorn.show()
    
    #Check for keyboard input
    Key = PollKeyboard()
    if (Key == 'q'):
      return 1
    

    
    time.sleep(0.995)
    
  print ("--end seconds--")
  return 0
  
  
  
def ScrollScreenShowDotZerkRobotTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
    ShowDotZerkRobotTime(speed)

    
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

  if (direction == 'down'):
    for x in range(0,8):
      del ScreenCap[7]
      ScreenCap.insert(0,EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

    ShowDotZerkRobotTime(speed)

    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
      

def ShowDotZerkRobotTime(speed):
  TheTime = CreateClockSprite(12)
  TheTime.r = SDLowGreenR
  TheTime.g = SDLowGreenG
  TheTime.b = SDLowGreenB
  
    
  r = random.randint(0,1)
  if (r == 0):
    DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,2,'left',speed)
    DotZerkRobotWalkingSmall.HorizontalFlip()
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
    DotZerkRobotWalkingSmall.ScrollAcrossScreen(0,2,'right',speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    DotZerkRobotWalkingSmall.HorizontalFlip()

  elif (r == 1):
    DotZerkRobotWalking.ScrollAcrossScreen(0,0,'left',speed)
    DotZerkRobotWalking.HorizontalFlip()
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
    DotZerkRobotWalking.ScrollAcrossScreen(0,0,'right',speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    DotZerkRobotWalking.HorizontalFlip()
  



def ShowDropShip(h,v,action,speed):
  unicorn.set_pixel(h,v,PlayerShipR,PlayerShipG,PlayerShipB)
  buffer1 = unicorn.get_pixels()
  unicorn.set_pixel(h,v,0,0,0)
  buffer2 = unicorn.get_pixels()
  
  if (action == 'pickup'):
    for y in range(-8,v-3):
      unicorn.set_pixels(buffer1)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer1)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer1)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer1)
    
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)

    print("Sleeping")
    for y in range(v-3,-10,-1):
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer2)
  else:
    for y in range(-8,v-3):
      unicorn.set_pixels(buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer2)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer2)

    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    DropShip.Animate(h-2,y+1,'forward',speed)
    print("Sleeping")
    
    for y in range(v-3,-10,-1):
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer1)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer1)
      DropShip.Animate(h-2,y,'forward',speed)
      unicorn.set_pixels(buffer1)



def ScrollScreenShowWormsTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
      ShowWorms(speed)
      ShowClock(speed)
  
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

      
      
      
      
def ScrollScreenShowSpaceInvaderTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
    ShowSpaceInvaderTime(speed)
    
  
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

      



      
def ScrollScreenShowWormsTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
    ShowWorms(speed)
    ShowClock(speed)
  
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
      
      

def ScrollScreenShowPacTime(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    

    ShowScrollingClock()
    
  
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
      
      

def ScrollScreenShowLittleShipTime(direction,speed):
  print ("ScrollScreenShowLittleShipTime")
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
    ShowLittleShipTime(speed)
  
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
      

def ScrollScreenShowBigShipTime(direction,speed):

  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
    ShowBigShipTime(speed)
  
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
      


      
def ScrollScreenShowTime(direction,speed):

  TheTime = CreateClockSprite(12)
  TheTime.r = SDLowGreenR
  TheTime.g = SDLowGreenG
  TheTime.b = SDLowGreenB
  

  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
  
    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

  if (direction == 'down'):
    for x in range(0,8):
      del ScreenCap[7]
      ScreenCap.insert(0,EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

    TheTime.ScrollAcrossScreen(0,1,"left",speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)

    #Reverse direction, bringing screen back down  
    for x in range(0,8):
      del ScreenCap[-1]
      ScreenCap.insert(0,Buffer[7-x])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)

      
      

def ScrollScreen(direction,speed):
  ScreenCap = unicorn.get_pixels()
  Buffer    = unicorn.get_pixels()
  EmptyCap = [[(0,0,0) for i in range(8)] for j in range(8)]

  for x in range (0,8):
    unicorn.set_pixel(x,3,99,99,200)
  
  #Delete top row, insert blank on bottom, pushing remaining up
  if (direction == 'up'):
    for x in range(0,8):
      del ScreenCap[0]
      ScreenCap.append(EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
    
  if (direction == 'down'):
    for x in range(0,8):
      del ScreenCap[7]
      ScreenCap.insert(0,EmptyCap[0])
      unicorn.set_pixels(ScreenCap)
      unicorn.show()
      time.sleep(speed)
  

  
  


      

def ShowBigShipTime(speed):
  print ("SHowBigShipTime")
  TheTime = CreateClockSprite(12)
  TheTime.r = SDLowGreenR
  TheTime.g = SDLowGreenG
  TheTime.b = SDLowGreenB
  
  BigShipFlying.ScrollAcrossScreen(-16,0,'right',speed)
  BigShipFlying.HorizontalFlip()
  TheTime.ScrollAcrossScreen(0,1,"right",speed)
  BigShipFlying.ScrollAcrossScreen(8,0,'left',speed)
  BigShipFlying.HorizontalFlip()
  TheTime.ScrollAcrossScreen(0,1,"left",speed)


def ShowLittleShipTime(speed):
  TheTime = CreateClockSprite(12)
  TheTime.r = SDLowGreenR
  TheTime.g = SDLowGreenG
  TheTime.b = SDLowGreenB
  
  LittleShipFlying.ScrollAcrossScreen(-15,0,'right',speed)
  LittleShipFlying.HorizontalFlip()
  TheTime.ScrollAcrossScreen(0,1,"right",speed)
  LittleShipFlying.ScrollAcrossScreen(8,0,'left',speed)
  LittleShipFlying.HorizontalFlip()
  TheTime.ScrollAcrossScreen(0,1,"left",speed)



def ShowSpaceInvaderTime(speed):
  TheTime = CreateClockSprite(12)
  TheTime.r = SDLowGreenR
  TheTime.g = SDLowGreenG
  TheTime.b = SDLowGreenB
  
  
  
  r = random.randint(0,2)
  if (r == 0):
    TinyInvader.ScrollAcrossScreen(0,1,'right',speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    TinyInvader.ScrollAcrossScreen(0,1,'left',speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
  elif (r == 1):
    SmallInvader.ScrollAcrossScreen(0,1,'right',speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    SmallInvader.ScrollAcrossScreen(0,1,'left',speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
  elif (r == 2):
    SpaceInvader.ScrollAcrossScreen(0,0,'right',speed)
    TheTime.ScrollAcrossScreen(0,1,"right",speed)
    SpaceInvader.ScrollAcrossScreen(0,0,'left',speed)
    TheTime.ScrollAcrossScreen(0,1,"left",speed)
  

  

def movesparkyDot(Dot):
  h = 0
  v = 0
  Dot.trail.append((Dot.h, Dot.v))
  ItemList = []
  #Scan all around, make decision, move
  ItemList = ScanLightDots(Dot.h,Dot.v,Dot.direction)
  
  #get possible items, then prioritize

  #empty = move forward
  if (ItemList[3] == 'empty'):
    Dot.h, Dot.v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    
    
  #if heading to boundary or wall
  elif (ItemList[3] == 'wall' or ItemList[3] <> 'empty' ):
    if (ItemList[1] == 'empty' and ItemList[5] == 'empty'):
      #print ("both empty picking random direction")
      Dot.direction = TurnLeftOrRight(Dot.direction)
      Dot.h, Dot.v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[1] == 'empty' and ItemList[5] <> 'empty'):
      #print ("left empty turning left")
      Dot.direction = TurnLeft(Dot.direction)
      Dot.h, Dot.v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    elif (ItemList[5] == 'empty' and ItemList[1] <> 'empty'):
      #print ("left empty turning right")
      Dot.direction = TurnRight(Dot.direction)
      Dot.h, Dot.v = CalculateDotMovement(Dot.h,Dot.v,Dot.direction)
    else:
      print ("you died")
      Dot.alive = 0
      Dot.trail.append((Dot.h, Dot.v))
      #Dot.ColorizeTrail()
      #Dot.EraseTrail()
  
  return Dot



def DrawSnake(h,v,r,g,b,snakedirection,snakespeed):
  print ("DrawSnake")
  moves     = 0
  SleepTime = MainSleep / 16

  #def __init__(self,h,v,r,g,b,direction,speed,alive,name,trail,score, maxtrail, erasespeed):
  SparkyDot = Dot(h,v,r,g,b,snakedirection,snakespeed,1,'Sparky',(0, 0), 0, 63,0.001)
  SparkyDot.Display()

  while (SparkyDot.alive == 1):
    moves = moves + 1
    m,r = divmod(moves,SparkyDot.speed)
    if (r == 0):
      movesparkyDot(SparkyDot)
      SparkyDot.Display()
      unicorn.show()
    time.sleep(SleepTime)

    
  time.sleep(MainSleep * 5)
  SparkyDot.EraseTrail('backward','noflash')
  unicorn.off()

  
  

def ShowBouncingSquare():
  WheelAnimatedSprite.Animate(0,0,0.05,'forward')
  WheelAnimatedSprite.Animate(0,0,0.05,'reverse')
  WheelAnimatedSprite.Animate(0,0,0.05,'forward')
  WheelAnimatedSprite.Animate(0,0,0.05,'reverse')
  WheelAnimatedSprite.Animate(0,0,0.05,'forward')
  WheelAnimatedSprite.Animate(0,0,0.05,'reverse')
  WheelAnimatedSprite.Animate(0,0,0.05,'forward')
  WheelAnimatedSprite.Animate(0,0,0.05,'reverse')
  WheelAnimatedSprite.Animate(0,0,0.05,'forward')




def ShowWorms(speed):
  print ("worms begin")
  #(width,height,r,g,b,frames,grid):
  Worm1 = AnimatedSprite(4,2,75,75,0,1,[])
  Worm1.grid.append([0,0,0,0,
                     1,1,1,1])
  Worm1.grid.append([0,0,1,0,
                     0,1,0,1])

  Worm1.Scroll(10,6,"left",15,ScrollSleep * 1.75)

  Worm2 = AnimatedSprite(5,2,0,100,0,1,[])
  Worm2.grid.append([0,0,0,0,0,
                     1,1,1,1,1])
  Worm2.grid.append([0,0,1,0,0,
                     0,1,0,1,0])
  
  Worm2.Scroll(7,3,"left",15,ScrollSleep * 1.75)
  
  
  Worms = AnimatedSprite(7,6,100,0,75,1,[])
  Worms.grid.append([0,0,0,0,0,0,0,
                     0,0,0,1,1,1,1,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,1,0,0,0,0,
                     0,1,0,1,0,0,0])

  Worms.grid.append([0,0,0,0,0,1,0,
                     0,0,0,0,1,0,1,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     0,0,0,0,0,0,0,
                     1,1,1,1,0,0,0])


  Worms.Scroll(7,1,"left",14,(ScrollSleep * 1.25))
  
  print ("worms end")


def ShowClock(speed):
  TheTime = CreateClockSprite(12)
  spritelen = len(TheTime.grid)
  TheTime.ScrollAcrossScreen(0,1,"right",speed)
  TheTime.ScrollAcrossScreen(0,1,"left",speed)
  

def CheckElapsedTime(seconds):
  global start_time
  elapsed_time = time.time() - start_time
  elapsed_hours, rem = divmod(elapsed_time, 3600)
  elapsed_minutes, elapsed_seconds = divmod(rem, 60)
  #print("Elapsed Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours),int(elapsed_minutes),elapsed_seconds),end="\r")

  if (elapsed_seconds >= seconds ):
    start_time = time.time()
    return 1
  else:
    return 0
  
  
  
  
  
  
#--------------------------------------
#  Dotster                           --
#--------------------------------------

def PlayDotster():
  
  unicorn.off()

  r,g,b = ColorList[14]

  #Draw Test Car
  unicorn.set_pixel(1,1,r,g,b)
  unicorn.set_pixel(1,2,r,g,b)
  unicorn.set_pixel(2,2,r,g,b)
  unicorn.set_pixel(3,2,r,g,b)
  unicorn.show()
  time.sleep(0.2)
  unicorn.off()
  unicorn.set_pixel (0,1,r,g,b)
  unicorn.set_pixel (1,2,r,g,b)
  unicorn.set_pixel (2,1,r,g,b)
  unicorn.show()
  time.sleep(0.2)
  unicorn.off() 
  unicorn.set_pixel(1,1,r,g,b)
  unicorn.set_pixel(1,2,r,g,b)
  unicorn.set_pixel(2,2,r,g,b)
  unicorn.set_pixel(3,2,r,g,b)
  unicorn.show()
  time.sleep(0.2)
  unicorn.off()
  unicorn.set_pixel (0,1,r,g,b)
  unicorn.set_pixel (1,2,r,g,b)
  unicorn.set_pixel (2,1,r,g,b)
  unicorn.show()
  time.sleep(0.2)
  unicorn.off() 
  unicorn.set_pixel(1,1,r,g,b)
  unicorn.set_pixel(1,2,r,g,b)
  unicorn.set_pixel(2,2,r,g,b)
  unicorn.set_pixel(3,2,r,g,b)
  unicorn.show()
  time.sleep(0.2)
  unicorn.off()
  unicorn.set_pixel (0,1,r,g,b)
  unicorn.set_pixel (1,2,r,g,b)
  unicorn.set_pixel (2,1,r,g,b)
  unicorn.show()
  time.sleep(0.2)
  unicorn.off() 
  unicorn.set_pixel(1,1,r,g,b)
  unicorn.set_pixel(1,2,r,g,b)
  unicorn.set_pixel(2,2,r,g,b)
  unicorn.set_pixel(3,2,r,g,b)
  unicorn.show()
  time.sleep(0.2)
  unicorn.off()
  unicorn.set_pixel (0,1,r,g,b)
  unicorn.set_pixel (1,2,r,g,b)
  unicorn.set_pixel (2,1,r,g,b)
  unicorn.show()
  time.sleep(0.2)
  unicorn.off() 
  unicorn.set_pixel(1,1,r,g,b)
  unicorn.set_pixel(1,2,r,g,b)
  unicorn.set_pixel(2,2,r,g,b)
  unicorn.set_pixel(3,2,r,g,b)

  unicorn.show()
  time.sleep(2)
  
  


  
#----------------------------------------------------------------------------
#--                                                                        --
#--                                                                        --
#--          RallyDot                                                      --
#--                                                                        --
#--                                                                        --
#----------------------------------------------------------------------------




# - the player car will not move, but the maze around him will
# - the playfield contains all objects, including cars walls enemies and bullets
# - we loop through the playfield, examining each object
    # - ignore empty
    # - ignore walls
    # - if player/enemy then give it a turn to use radar to find nearby items
        # - make a decision on what to to
        # - decisions are priority based
        # - shoot opponent
        # - run
        # - hide
    # - we still  use a clock/speed value to see if a player/enemy object is going to make a decision this turn
# - objects off screen will still move, but will not be visible
# - draw window function will be used to display the current visible sqare in the map (8x8)    




def ExaminePlayfield(RaceWorld):
  #The array is [V][H]
  print ("--Examine Playfield--")
  width  = RaceWorld.width
  height = RaceWorld.height
  h      = 0
  v      = 0
  Playfield = RaceWorld.Playfield
  
  #Iterate through playfield (left to right, top to bottom)
  for v in range (height):
    for h in range (width):
      print ("vh name: ",v,h,Playfield[v][h].name)

      
def TurnLeftOrRight8Way(direction):
  WhichWay = random.randint(1,4)
  #print ("WhichWay:",WhichWay)
  if (WhichWay == 1):
    #print ("turning W")
    direction = TurnLeft8Way(direction)
    direction = TurnLeft8Way(direction)
  elif (WhichWay == 2):
    #print ("turning NW")
    direction = TurnLeft8Way(direction)
  elif (WhichWay == 3):
    #print ("turning NE")
    direction = TurnRight8Way(direction)
  elif (WhichWay == 4):
    #print ("turning E")
    direction = TurnRight8Way(direction)
    direction = TurnRight8Way(direction)
    
  return direction;

      
def TurnLeftOrRightTwice8Way(direction):
  WhichWay = random.randint(1,2)
  #print ("WhichWay:",WhichWay)
  if (WhichWay == 1):
    direction = TurnLeft8Way(direction)
    direction = TurnLeft8Way(direction)
  elif (WhichWay == 2):
    direction = TurnRight8Way(direction)
    direction = TurnRight8Way(direction)
    
  return direction;


  
      
def ReverseDirection8Way(direction):
  if direction == 1:
    direction = 5
  elif direction == 2:
    direction = 6
  elif direction == 3:
    direction = 7
  elif direction == 4:
    direction = 8
  elif direction == 5:
    direction = 1
  elif direction == 6:
    direction = 2
  elif direction == 7:
    direction = 3
  elif direction == 8:
    direction = 4
  return direction;

  

def CalculateDotMovement8Way(h,v,Direction):
  #1N 2NE 3E 4SE 5S 6SW 7W 8NW
  # 8 1 2
  # 7 x 3
  # 6 5 4
  
  if (Direction == 1):
    v = v -1
  if (Direction == 2):
    h = h + 1
    v = v - 1
  if (Direction == 3):
    h = h + 1
  if (Direction == 4):
    h = h + 1
    v = v + 1
  if (Direction == 5):
    v = v + 1
  if (Direction == 6):
    h = h - 1
    v = v + 1
  if (Direction == 7):
    h = h - 1
  if (Direction == 8):
    h = h - 1
    v = v - 1
  return h,v;



def TurnRight8Way(direction):
  if direction == 1:
    direction = 2
  elif direction == 2:
    direction = 3
  elif direction == 3:
    direction = 4
  elif direction == 4:
    direction = 5
  elif direction == 5:
    direction = 6
  elif direction == 6:
    direction = 7
  elif direction == 7:
    direction = 8
  elif direction == 8:
    direction = 1
  #print "  new: ",direction
  return direction;
    

def TurnLeft8Way(direction):
  #print "ChangeDirection!"
  #print "  old: ",direction
  if direction == 1:
    direction = 8
  elif direction == 8:
    direction = 7
  elif direction == 7:
    direction = 6
  elif direction == 6:
    direction = 5
  elif direction == 5:
    direction = 4
  elif direction == 4:
    direction = 3
  elif direction == 3:
    direction = 2
  elif direction == 2:
    direction = 1
  #print ("  new: ",direction)
  return direction;



def ChanceOfTurning8Way(Direction,Chance):
  #print ("Chance of turning: ",Chance)
  if Chance > randint(1,100):
    if randint(0,1) == 0:
      Direction = TurnLeft8Way(Direction)
    else:
      Direction = TurnRight8Way(Direction)
  return Direction;


  

def RallyDotScanStraightLine(h,v,direction,Playfield):
 
  ScanDirection = direction
  ScanH         = 0
  ScanV         = 0
  Item          = ''
  ItemList      = ['NULL']
  WallHit       = 0
  count         = 0    #represents number of spaces to scan

#           7
#           6
#           5                             
#           4                             
#           3                             
#           2                            
#           1                              
                                           

  #print ("")
  #print("== RD Scan Straight Line")     
  #print("SSL - hv direction",h,v,direction)

  for count in range (8):
    ScanH, ScanV = CalculateDotMovement(h,v,ScanDirection)
    Item = Playfield[ScanV][ScanH].name
    
    if (Item == 'Wall' or WallHit == 1):
      ItemList.append('Wall')
      WallHit = 1
    else:
      ItemList.append(Item)
    #print ("RDSSL - count hv ScanH ScanV Item",count,h,v,ScanH,ScanV, Item)
    
  
  return ItemList;


  
def RallyDotScanAroundCar(Car,Playfield):
  # hv represent car location
  # ScanH and ScanV is where we are scanning
  
  #print ("== Scan around car ==")
  
  ScanDirection = Car.direction
  ScanH         = 0
  ScanV         = 0
  h             = Car.h
  v             = Car.v
  Item          = ''
  ItemList      = ['EmptyObject']
  count         = 0    #represents number of spaces to scan


#         8 1 2
#         7 x 3                             
#         6 5 4
        
  
  #FlashDot2(h,v,0.005)

  for count in range (8):
    ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
    

    Item = Playfield[ScanV][ScanH].name
    if (Item == 'Wall'):
      ItemList.append('Wall')
    else:
      ItemList.append(Item)
    #print ("RDSAC - count hv ScanH ScanV Item",count,h,v,ScanH,ScanV, Item)

    #Turn to the right
    ScanDirection = TurnRight8Way(ScanDirection)
    
  
  return ItemList;
  





def RallyDotBlowUp(Car,Playfield):
  # hv represent car location
  # ScanH and ScanV is where we are scanning
  
  #print ("== Scan around car ==")
  
  ScanDirection = Car.direction
  ScanH         = 0
  ScanV         = 0
  h             = Car.h
  v             = Car.v
  Item          = ''
  ItemList      = ['EmptyObject']
  count         = 0    #represents number of spaces to scan

#         8 1 2
#         7 x 3                             
#         6 5 4
        
  for count in range (8):
    #print ("ScanDirection: ",ScanDirection)
    ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)

    Item = Playfield[ScanV][ScanH].name
    if (Item == "Enemy"): 
        Playfield[ScanV][ScanH].exploding = 1
    if (Item == "Player"):
      #lives is used as health
      Playfield[ScanV][ScanH].lives = Playfield[ScanV][ScanH].lives -10


    #Turn to the right
    ScanDirection = TurnRight8Way(ScanDirection)

  #Remove exploding car from the playfield
  Playfield[v][h] == EmptyObject("EmptyObject")
   

  return;  
  


  
  
def IncreaseColor(Car):
  Car.r = Car.r + 20
    
  if (Car.r >= 255):
    Car.r = 255
 

def DecreaseColor(Car):
  Car.r = Car.r - 1
  
  if (Car.r <= 60):
    Car.r = 60

def TurnTowardsCarDestination(SourceCar):
  print ("Turning towards: ",SourceCar.name)
  if (SourceCar.h < SourceCar.dh):
    if (SourceCar.direction in (7,8,1,2)):
      SourceCar.direction = TurnRight8Way(SourceCar.direction)
    if (SourceCar.direction in (6,5,4)):
      SourceCar.direction = TurnLeft8Way(SourceCar.direction)
      
  if (SourceCar.h > SourceCar.dh):
    if (SourceCar.direction in (8,1,2,3)):
      SourceCar.direction = TurnLeft8Way(SourceCar.direction)
    if (SourceCar.direction in (6,5,4)):
      SourceCar.direction = TurnRight8Way(SourceCar.direction)


  if (SourceCar.v < SourceCar.dv):
    if (SourceCar.direction in (6,7,8,1)):
      SourceCar.direction = TurnLeft8Way(SourceCar.direction)
    if (SourceCar.direction in (2,3,4)):
      SourceCar.direction = TurnRight8Way(SourceCar.direction)
      
  if (SourceCar.v > SourceCar.dv):
    if (SourceCar.direction in (6,7,8)):
      SourceCar.direction = TurnRight8Way(SourceCar.direction)
    if (SourceCar.direction in (5,4,3,2)):
      SourceCar.direction = TurnLeft8Way(SourceCar.direction)
  return;


def TurnTowardsCar(SourceCar,TargetCar):
  if (SourceCar.h < TargetCar.h):
    if (SourceCar.direction in (7,8,1,2)):
      SourceCar.direction = TurnRight8Way(SourceCar.direction)
    if (SourceCar.direction in (6,5,4)):
      SourceCar.direction = TurnLeft8Way(SourceCar.direction)
      
  if (SourceCar.h > TargetCar.h):
    if (SourceCar.direction in (8,1,2,3)):
      SourceCar.direction = TurnLeft8Way(SourceCar.direction)
    if (SourceCar.direction in (6,5,4)):
      SourceCar.direction = TurnRight8Way(SourceCar.direction)


  if (SourceCar.v < TargetCar.v):
    if (SourceCar.direction in (6,7,8,1)):
      SourceCar.direction = TurnLeft8Way(SourceCar.direction)
    if (SourceCar.direction in (2,3,4)):
      SourceCar.direction = TurnRight8Way(SourceCar.direction)
      
  if (SourceCar.v > TargetCar.v):
    if (SourceCar.direction in (6,7,8)):
      SourceCar.direction = TurnRight8Way(SourceCar.direction)
    if (SourceCar.direction in (5,4,3,2)):
      SourceCar.direction = TurnLeft8Way(SourceCar.direction)
  return;

def TurnTowardsFuelIfThereIsRoom(Car,Playfield,FuelDots,ClosestFuel):
  ItemList = []
  ItemList = RallyDotScanAroundCar(Car,Playfield)          
  if (all("EmptyObject" == Item for Item in ItemList)):
    #print ("Scanners indicate emptiness all around")
    TurnTowardsCar(Car,FuelDots[ClosestFuel])
  elif (ItemList[1] == "Empty" 
    and ItemList[2] == "Empty" 
    and ItemList[3] == "Empty" 
    and ItemList[4] == "Empty" 
    and ItemList[5] == "Empty" 
    and (ItemList[8] == "Wall" or ItemList[7] == "Wall" or ItemList[6] == "Wall")):
    print ("Wall on left")
    TurnTowardsCar(Car,FuelDots[ClosestFuel])
  elif (ItemList[1] == "Empty" 
    and ItemList[8] == "Empty" 
    and ItemList[7] == "Empty" 
    and ItemList[6] == "Empty" 
    and ItemList[5] == "Empty" 
    and (ItemList[2] == "Wall" or ItemList[3] == "Wall" or ItemList[4] == "Wall")):
    print ("Wall on right")
    TurnTowardsCar(Car,FuelDots[ClosestFuel])

  
  return
      
def MoveCar(Car,Playfield):
  
  #print ("")
  #print ("== RD Move Car: ",Car.name," --")
  h = Car.h
  v = Car.v
  oldh  = h
  oldv  = v
  ScanH = 0
  ScanV = 0
  ItemList = []
  DoNothing = ""

  #SolidObjects
  SolidObjects = []
  SolidObjects.append("Wall")
  SolidObjects.append("Fuel")
  
  
  #print("Current Car hv direction:",h,v,Car.direction)
  
  ItemList = RallyDotScanAroundCar(Car,Playfield)
  #print (ItemList[1])

  
  # #Handle Enemy actions first
  if (Car.name == "Enemy"):
    #Decrease color if no player nearby
    #Increase if player nearby
    if ('Player' not in ItemList):
      DecreaseColor(Car)
    else:
      IncreaseColor(Car)

    if ("Player" in ItemList):
      if (ItemList[1] == 'Player'):
        #Deplete player car lives (health)
        ScanH,ScanV = CalculateDotMovement8Way(h,v,Car.direction)
        Playfield[ScanV][ScanH].lives = Playfield[ScanV][ScanH].lives - 1
      elif (ItemList[2] == 'Player'):
        #print("Turn NE")
        Car.direction = TurnRight8Way(Car.direction)
      elif (ItemList[3] == 'Player'):
        #print("Turn E")
        Car.direction = TurnRight8Way(Car.direction)
        Car.direction = TurnRight8Way(Car.direction)
      elif (ItemList[4] == 'Player'):
        #print("Turn SE")
        Car.direction = TurnRight8Way(Car.direction)
        Car.direction = TurnRight8Way(Car.direction)
        Car.direction = TurnRight8Way(Car.direction)
      elif (ItemList[5] == 'Player'):
        #print("Turn S")
        Car.direction = ReverseDirection8Way(Car.direction)
      elif (ItemList[8] == 'Player'):
        #print("Turn NW")
        Car.direction = TurnLeft8Way(Car.direction)
      elif (ItemList[7] == 'Player'):
        #print("Turn W")
        Car.direction = TurnLeft8Way(Car.direction)
        Car.direction = TurnLeft8Way(Car.direction)      
      elif (ItemList[6] == 'Player'):
        #print("Turn SW")
        Car.direction = TurnLeft8Way(Car.direction)
        Car.direction = TurnLeft8Way(Car.direction)      
        Car.direction = TurnLeft8Way(Car.direction)      

      

  #Handle Player actions
  if (Car.name == "Player"):
    #Handle Wall Movements
    if (ItemList[1] == "Wall"):
      #print ("--Wall found--")
      
      #When you hit the middle of a wall, go left or right (randomly)
      if (ItemList[3] == "EmptyObject" and ItemList[7] == "EmptyObject"):
        Car.direction = TurnLeftOrRightTwice8Way(Car.direction)
      
      #If you are surrounded, turn around
      elif (ItemList[3] == "Wall" and ItemList[7] == "Wall"):
        Car.direction = ReverseDirection8Way(Car.direction)
      
      elif (ItemList[8] == "EmptyObject"):
        Car.direction = TurnLeft8Way(Car.direction)
      elif (ItemList[7] == "EmptyObject"):
        Car.direction = TurnLeft8Way(Car.direction)
        Car.direction = TurnLeft8Way(Car.direction)
      elif (ItemList[2] == "EmptyObject"):
        Car.direction = TurnRight8Way(Car.direction)
      elif (ItemList[3] == "EmptyObject"):
        Car.direction = TurnRight8Way(Car.direction)
        Car.direction = TurnRight8Way(Car.direction)
    
    elif (ItemList[1] == "Enemy"):
      if (ItemList[2] <> "EmptyObject" and ItemList[8] <> "EmptyObject" and ItemList[5] == "EmptyObject"):
        Car.direction = ReverseDirection8Way(Car.direction)
      elif (ItemList[2] == "EmptyObject"):
        Car.direction = TurnRight8Way(Car.direction)    
      elif (ItemList[3] == "EmptyObject"):
        Car.direction = TurnRight8Way(Car.direction)    
        Car.direction = TurnRight8Way(Car.direction)    
      elif (ItemList[4] == "EmptyObject"):
        Car.direction = TurnRight8Way(Car.direction)    
        Car.direction = TurnRight8Way(Car.direction)    
        Car.direction = TurnRight8Way(Car.direction)    
      elif (ItemList[8] == "EmptyObject"):
        Car.direction = TurnLeft8Way(Car.direction)    
      elif (ItemList[7] == "EmptyObject"):
        Car.direction = TurnLeft8Way(Car.direction)    
        Car.direction = TurnLeft8Way(Car.direction)    
      elif (ItemList[6] == "EmptyObject"):
        Car.direction = TurnLeft8Way(Car.direction)    
        Car.direction = TurnLeft8Way(Car.direction)    
        Car.direction = TurnLeft8Way(Car.direction)    
    
    
    #Cars eat fuel
    elif ("Fuel" in ItemList):
      if (ItemList[1] == "Fuel"):
        DoNothing = "nothing"
      elif (ItemList[2] == "Fuel"):
        Car.direction = TurnRight8Way(Car.direction) 
      elif (ItemList[3] == "Fuel"):
        Car.direction = TurnRight8Way(Car.direction) 
        Car.direction = TurnRight8Way(Car.direction) 
      elif (ItemList[4] == "Fuel"):
        Car.direction = TurnRight8Way(Car.direction) 
        Car.direction = TurnRight8Way(Car.direction) 
        Car.direction = TurnRight8Way(Car.direction) 
      elif (ItemList[5] == "Fuel"):
        Car.direction = ReverseDirection8Way(Car.direction) 
      elif (ItemList[8] == "Fuel"):
        Car.direction = TurnLeft8Way(Car.direction) 
      elif (ItemList[7] == "Fuel"):
        Car.direction = TurnLeft8Way(Car.direction) 
        Car.direction = TurnLeft8Way(Car.direction) 
      elif (ItemList[6] == "Fuel"):
        Car.direction = TurnLeft8Way(Car.direction) 
        Car.direction = TurnLeft8Way(Car.direction) 
        Car.direction = TurnLeft8Way(Car.direction) 

      Fuelh, Fuelv = CalculateDotMovement8Way(h,v,Car.direction)
      Playfield[Fuelv][Fuelh].alive = 0
      Playfield[Fuelv][Fuelh] = EmptyObject("EmptyObject")
      Car.destination = ""
      Car.lives = Car.lives + 50
      #Car.ShiftGear("up")
      #if (Car.speed < 10):
      #  Car.speed = 10
    
    #Turn if following a wall and a corridor opens up
    elif(ItemList[7] == "Wall" and ItemList[8] == "EmptyObject"):
      Car.direction = TurnLeft8Way(Car.direction)
    elif(ItemList[3] == "Wall" and ItemList[2] == "EmptyObject"):
      Car.direction = TurnRight8Way(Car.direction)


      
  #Only move if the space decided upon is actually empty!
  ScanH,ScanV = CalculateDotMovement8Way(h,v,Car.direction)
  if (Playfield[ScanV][ScanH].name == "EmptyObject"):
    h = ScanH
    v = ScanV

    

  #print ("oldh oldv hv",oldh,oldv,h,v)  
  #IF the car actually moved, update the locations
  if (oldh <> h or oldv <> v):
    Car.h = h
    Car.v = v  
    Playfield[v][h] = Car
    Playfield[oldv][oldh] = EmptyObject("EmptyObject")



  return 



def CountFuelDotsLeft(FuelDots,FuelCount):
  FuelDotsLeft = 0
  for x in range (FuelCount):
    if (FuelDots[x].alive == 1):
      FuelDotsLeft = FuelDotsLeft + 1
  return FuelDotsLeft;

  
def CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld):
  width  = RaceWorld.width
  height = RaceWorld.height
  
   
  for x in range (FuelCount):
    finished = 'N'
    while (finished == 'N'):
      #Don't put fuel in border area
      h = random.randint(5,width-5)
      v = random.randint(5,height-5)
      
      name = RaceWorld.Playfield[v][h].name
      print ("Playfield name: ",name)
      
      print ("FuelDot x h v: ",x,h,v)
      if (name == "EmptyObject"):
        print ("Placing Fuel x name: ",x,FuelDots[x].name)
        RaceWorld.Playfield[v][h] = FuelDots[x]
        FuelDots[x].h = h
        FuelDots[x].v = v
        FuelDots[x].alive = 1
        finished = 'Y'
      else:
        print ("Spot occupied: ",name)  


def CopyEnemyCarsToPlayfield(EnemyCars,EnemyCount,RaceWorld):
  width  = RaceWorld.width
  height = RaceWorld.height
  
   
  for x in range (EnemyCount):
    finished = 'N'
    while (finished == 'N'):
      #Don't put fuel in border area
      h = random.randint(5,width-5)
      v = random.randint(5,height-5)
      
      name = RaceWorld.Playfield[v][h].name
      print ("Playfield name: ",name)
      
      print ("FuelDot x h v: ",x,h,v)
      if (name == "EmptyObject"):
        print ("Placing Fuel x name: ",x,EnemyCars[x].name)
        RaceWorld.Playfield[v][h] = EnemyCars[x]
        EnemyCars[x].h = h
        EnemyCars[x].v = v
        EnemyCars[x].alive = 1
        finished = 'Y'
      else:
        print ("Spot occupied: ",name)  





def GetDistanceBetweenCars(Car1,Car2):
  a = abs(Car1.h - Car2.h)
  b = abs(Car1.v - Car2.v)
  c = math.sqrt(a**2 + b**2)

  return c;  
        

  
        
def FindClosestFuel(Car,FuelDots,FuelCount):
  #We want the player car to journey towards the closes fuel dot
  #So far, this function points the car.   How do we make it journey there?
  ClosestX     = 0
  MinDistance  = 9999
  FuelDotsLeft = 0
  Distance = 0
  for x in range(FuelCount):
    if (FuelDots[x].alive == 1):
      FuelDotsLeft = FuelDotsLeft + 1
      Distance = GetDistanceBetweenCars(Car,FuelDots[x])
      if (Distance < MinDistance):
        MinDistance = Distance
        ClosestX = x

  # if (FuelDotsLeft >= 0): 
    # #FuelDots are car objects, so this works!
    # #TurnTowardsCar(Car,FuelDots[ClosestX])
    # #Make target dot brighter
    # FuelDots[ClosestX].r = 150
    # FuelDots[ClosestX].g = 150
    # FuelDots[ClosestX].b = 0
    
  return ClosestX, MinDistance, FuelDotsLeft;


def ScrollToCar(Car,RaceWorld):
  x = 0
  y = 0
  for x in range(Car.h-4):
    RaceWorld.DisplayWindow(x,0)
    time.sleep(0.05)
    
  for y in range(Car.v-3):
    RaceWorld.DisplayWindow(x,y)
    time.sleep(0.05)

  FlashDot(3,4,FlashSleep * 3)


def AdjustCarColor(Car):
  r = 60
  g = 0
  b = 0
  b = Car.lives
  if (b >= 255):
    b = 255
    r = min(255, r+1)
  if (b <= 100):
    b = 100
  Car.r = r
  Car.b = b        
        
def CreateRaceWorld(MapLevel):

  #The map is an array of a lists.  You can address each element has VH e.g. [V][H]
  #Copying the map to the playfield needs to follow the exact same shape

  #RaceWorld.Map[] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
  #RaceWorld.Map[] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,])


  if (MapLevel == 1):

    #Set world dimensions
    RaceWorld = GameWorld(name='Level1',
                          width        = 16,
                          height       = 24,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 1,
                          CurrentRoomV = 1,
                          DisplayH=1,
                          DisplayV=1)
    
    #Populate Map
    RaceWorld.Map[0]  = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[1]  = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[2]  = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map[3]  = ([  9, 9, 9,10,10, 9, 9,10, 9, 9, 9,10,10, 9, 9, 9,  ])  
    RaceWorld.Map[4]  = ([  9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[5]  = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[6]  = ([  9, 9, 9, 9, 0, 0,25,25, 0,25,25, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[7]  = ([  9, 9, 9, 9, 0, 0,25,25, 0,25,25, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[8]  = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[9]  = ([  9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[10] = ([  9, 9, 9, 9,25,25,25,25, 0,25,25, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[11] = ([  9, 9, 9, 9,25,25,25,25, 0,25,25, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[12] = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[13] = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[14] = ([  9, 9, 9,10, 0, 0,25,25, 0,25,25, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[15] = ([  9, 9, 9, 9, 0, 0,25,25, 0,25,25, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[16] = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[17] = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[18] = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[19] = ([  9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[20] = ([  9, 9, 9,10,10, 9, 9,10, 9, 9, 9,10,10, 9, 9, 9,  ])
    RaceWorld.Map[21] = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[22] = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[23] = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])

    RaceWorld.CopyMapToPlayfield()

  
  
  
  if (MapLevel == 2):
    #Set world dimensions
    RaceWorld = GameWorld(name='Level1',
                          width        = 32,
                          height       = 24,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 2,
                          CurrentRoomV = 2,
                          DisplayH=8,
                          DisplayV=8)
    
    #Populate Map
    RaceWorld.Map[0]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[1]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[2]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map[3]  = ([  9, 9, 9,10,10, 9, 9, 9,  9,10,10, 9, 9, 9, 9,10, 10, 9, 9, 9, 9,10,10, 9,  9, 9, 9,10,10, 9, 9, 9,  ])  
    RaceWorld.Map[4]  = ([  9, 9, 9,10, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[5]  = ([  9, 9, 9, 9, 0, 0,25,25, 25, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[6]  = ([  9, 9, 9, 9, 0, 0,25, 0, 25, 0, 0,25,25,25,25, 0,  0, 0, 0,25,25,25,25, 0,  0,25,25, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[7]  = ([  9, 9, 9, 9, 0, 0,25, 0, 25, 0, 0,25, 0, 0,25, 0,  0, 0, 0,25, 0, 0, 0, 0,  0, 0,25, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[8]  = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,25, 0, 0,25, 0,  0, 0, 0,25,25,25,25, 0,  0,25,25, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[9]  = ([  9, 9, 9,10, 0, 0, 0, 0,  0, 0, 0,25, 0, 0,25, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[10] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[11] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[12] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[13] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25, 25,25, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[14] = ([  9, 9, 9,10, 0,25, 0,25,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25,  0,25, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[15] = ([  9, 9, 9, 9, 0,25, 0,25,  0, 0,13,13,13, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25,  0,26, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[16] = ([  9, 9, 9, 9, 0,25,25,25,  0, 0,14,14,14, 0, 0, 0,  0, 0,14, 0, 0, 0, 0,25,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[17] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0,14, 0, 0, 0, 0,25,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[18] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,25,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[19] = ([  9, 9, 9,10, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[20] = ([  9, 9, 9,10,10, 9, 9, 9,  9,10,10, 9, 9, 9, 9,10, 10, 9, 9, 9, 9,10,10, 9,  9, 9, 9,10,10, 9, 9, 9,  ])
    RaceWorld.Map[21] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[22] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[23] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])

    RaceWorld.CopyMapToPlayfield()
    
    
    
    
  if (MapLevel == 3):
    #Set world dimentions
    RaceWorld = GameWorld(name='Level3',
                          width        = 32,
                          height       = 32,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 2,
                          CurrentRoomV = 2,
                          DisplayH=8,
                          DisplayV=8)

    RaceWorld.Map[0]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[1]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[2]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map[3]  = ([  9, 9, 9,10,10, 9, 9, 9,  9,10,10, 9, 9, 9, 9,10, 10, 9, 9, 9, 9,10,10, 9,  9, 9, 9,10,10, 9, 9, 9,  ])  
    RaceWorld.Map[4]  = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[5]  = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[6]  = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[7]  = ([  9, 9, 9, 9, 0,25,25,25, 25,25, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,25,25, 25,25,25, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[8]  = ([  9, 9, 9,10, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[9]  = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,25, 0, 0, 0, 0,  0, 0, 0, 0,25, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[10] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,26,26,26,26, 0,  0,26,26,26,26, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[11] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0,25,25,25,25,25, 0,  0,25,25,25,25,25, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[12] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[13] = ([  9, 9, 9,10, 0, 0, 0, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[14] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0,25, 0, 0, 5, 5, 0,  0, 5, 5, 0, 0,25, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[15] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0,25, 0, 0, 5, 5, 0,  0, 5, 5, 0, 0,25, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[16] = ([  9, 9, 9, 9,25,25,25, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0,25,25,25, 9, 9, 9, 9,  ])  
    RaceWorld.Map[17] = ([  9, 9, 9,10, 0, 0,25, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0,25, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[18] = ([  9, 9, 9, 9, 0, 0,25, 0,  0, 0,25, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,25, 0, 0,  0,25, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[19] = ([  9, 9, 9, 9, 0, 0,25, 0,  0, 0,25,25,25,25,25,25, 25,25,25,25,25,25, 0, 0,  0,25, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[20] = ([  9, 9, 9, 9, 0, 0,25, 0,  0, 0, 0,26,26,26,26, 0,  0, 0,26,26,26, 0, 0, 0,  0,25, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[21] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0,26,26, 0,  0, 0,26,26, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[22] = ([  9, 9, 9,10, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[23] = ([  9, 9, 9, 9, 0, 0,25,25, 25,25, 0, 0, 0, 0,17, 0,  0,17, 0, 0, 0, 0,25,25, 25,25, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[24] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,17, 0,  0,17, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[25] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,17, 0,  0,17, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[26] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[27] = ([  9, 9, 9,10,10, 9, 9, 9,  9,10,10, 9, 9, 9, 9,10, 10, 9, 9, 9, 9,10,10, 9,  9, 9, 9,10,10, 9, 9, 9,  ])
    RaceWorld.Map[28] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[29] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[30] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  ])

    RaceWorld.CopyMapToPlayfield()


  if (MapLevel == 4):

    #Set world dimensions
    RaceWorld = GameWorld(name='Level4',
                          width        = 16,
                          height       = 24,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 1,
                          CurrentRoomV = 1,
                          DisplayH=1,
                          DisplayV=1)
    
    #Populate Map
    RaceWorld.Map[0]  = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[1]  = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[2]  = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])  
    RaceWorld.Map[3]  = ([  9, 9, 9,10,10, 9, 9,10, 9, 9, 9,10,10, 9, 9, 9,  ])  
    RaceWorld.Map[4]  = ([  9, 9, 9,10,10, 0, 0, 0, 0, 0, 0,10,10, 9, 9, 9,  ])  
    RaceWorld.Map[5]  = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[6]  = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[7]  = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[8]  = ([  9, 9, 9, 9, 0, 0, 5, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[9]  = ([  9, 9, 9,10, 0,17, 2, 0, 0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[10] = ([  9, 9, 9, 9, 0, 0, 5, 2, 0, 2, 2, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[11] = ([  9, 9, 9, 9, 0, 0, 0, 2, 2, 2, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[12] = ([  9, 9, 9, 9, 0, 0, 0,22, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[13] = ([  9, 9, 9, 9, 0, 0,22, 0,21, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[14] = ([  9, 9, 9,10, 0, 0, 0, 0, 0, 0, 0, 0,10, 9, 9, 9,  ])  
    RaceWorld.Map[15] = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[16] = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[17] = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[18] = ([  9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9,  ])  
    RaceWorld.Map[19] = ([  9, 9, 9,10,10, 0, 0, 0, 0, 0, 0,10,10, 9, 9, 9,  ])  
    RaceWorld.Map[20] = ([  9, 9, 9,10,10, 9, 9,10, 9, 9, 9,10,10, 9, 9, 9,  ])
    RaceWorld.Map[21] = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[22] = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])
    RaceWorld.Map[23] = ([  9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  ])

    RaceWorld.CopyMapToPlayfield()


    
  if (MapLevel == 5):
    #Set world dimentions
    RaceWorld = GameWorld(name='Level4',
                          width        = 56,
                          height       = 56,
                          Map          = [[]],
                          Playfield    = [[]],
                          CurrentRoomH = 2,
                          CurrentRoomV = 2,
                          DisplayH=8,
                          DisplayV=8)
    
    RaceWorld.Map[0]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map[1]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map[2]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map[3]  = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map[4]  = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 2, 2, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[5]  = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 2, 2, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[6]  = ([  9, 9, 9, 9, 0, 0,25,25, 25,25,25,25,25,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[7]  = ([  9, 9, 9, 9, 0, 0,25, 0,  0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[8]  = ([  9, 9, 9, 9, 0, 0,25, 0,  0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0,27,26,26,26,26, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[9]  = ([  9, 9, 9, 9, 0, 0,25, 0,  0, 0, 0, 0, 0,25, 0, 0,  0, 0, 0,27,26,26,26,26, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[10] = ([  9, 9, 9, 9, 0, 0,25,25,  0, 0,25,25,25,25, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[11] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[12] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,27,26,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[13] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,27,26,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[14] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[15] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 0, 0, 0,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[16] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  1, 1, 0, 0, 0,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[17] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[18] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[19] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26,26,26,26,26,26,26,26, 26,26,26,26,26,26, 0, 0, 26, 0, 0, 0, 0, 0, 4, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[20] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0,26, 0,  0, 0, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[21] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26, 0, 0,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[22] = ([  9, 9, 9, 9,25, 0, 0, 0, 26, 0, 0,26,26,26,26,26, 26,26,26,26,26,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[23] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26, 0, 0,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[24] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26, 0, 0,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[25] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26, 0, 0,26,26,26,26,26, 26, 0, 0, 0, 0,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[26] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26, 0, 0, 0,26, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[27] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0,26, 0,  0, 0, 0, 0, 0,26,26,26, 26, 0, 0, 0, 0, 0,26, 0,  0,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[28] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26,26,26,26,26,26,26,26, 26,26,26,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,26, 0,  0,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[29] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,26, 0,  0,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[30] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,26, 0,  0,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[31] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,26,26,26,26,26, 26,26,26,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,26, 0,  0,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[32] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,26, 0,  0,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[33] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,26, 0,  0,26, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[34] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,26, 0, 0,26,26, 26, 0, 0,26,26,26,26,26, 26,26,26,26,26,26,26,26, 26,26, 0, 0,26,26,26,26, 26,26,26,26,26,26,26,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[35] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0,26, 0, 0,26, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[36] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0,26, 0, 0,26, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[37] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0,26,26,26, 0, 0, 26, 0, 0, 0, 0,26,26,26, 26,26,26,26,26,26,26, 0,  0,26, 0, 0,26, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[38] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0,26, 0, 0,26, 0, 0, 0,  0, 0,26,26,26, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[39] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0,26, 0, 0,26, 0, 0, 0,  0, 0,26,27,27, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[40] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0, 26,26,26, 0, 0,26,26,26, 26,26,26,26,26,26,26,26, 26,26, 0, 0,26, 0, 0, 0,  0, 0,26,27,27, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[41] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0,  0, 0,26, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,26, 0, 0, 0,  0, 0,26,27,27, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[42] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0,  0, 0,26, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26,26,26,26,26,  0, 0,26,27,27, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[43] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,26, 0,  0, 0,26, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0,26,27,27, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[44] = ([  9, 9, 9, 9,25, 0, 0, 0,  0, 0, 0, 0, 0, 0,26, 0,  0, 0,26, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0,26, 0, 0, 0, 0,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[45] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0,26, 0,  0, 0,26, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0,26, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[46] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26,26,26,26,26,26,26, 0,  0, 0,26, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0,26, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[47] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0,26, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0,26, 0, 0, 0, 0,  0, 0,26,26,26,26,26,26,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[48] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0,  0, 0,26, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0,26, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[49] = ([  9, 9, 9, 9, 0, 0, 0, 0, 26,26,26,26,26,26,26,26,  0, 0,26, 0, 0,26,26,26, 26,26,26,26,26,26,26,26, 26,26, 0, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[50] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[51] = ([  9, 9, 9, 9, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 4, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0,26, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 9, 9, 9, 9,])
    RaceWorld.Map[52] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map[53] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map[54] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,])
    RaceWorld.Map[55] = ([  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9, 9,])

    RaceWorld.CopyMapToPlayfield()

    
    
  return RaceWorld;

  

  
def PlayRallyDot():
  
  print ("")
  print ("")
  print ("----------------------")
  print ("-- Rally Dot      ----")
  print ("----------------------")
  print ("")
  
  #Local Variables
  LevelCount       = 0
  LevelFinished    = "N"
  m                = 0
  r                = 0
  moves            = 0
  MaxMoves         = 40000
  Finished         = 'N'
  Distance         = 0
  ClosestFuelDistance = 0
  Minx             = 0
  MinDistance      = 9999
  x                = 0
  y                = 0
  ItemList         = []
  CarOriginalSpeed = 0
  Diaganols        = [2,4,6,8]
  SpeedModifier    = 1.2
  EnemyRadarSpeed  = 20 * CPUModifier

  
  
  #Show Intro
  unicorn.off()
  #ShowScrollingBanner("Rally Dot", SDLowGreenR,SDLowGreenG,SDLowGreenB,ScrollSleep)
  
  
  #---------------------------------
  #-- Prepare World 1             --
  #---------------------------------

  #Create Player Car
  PlayerCar = CarDot(h=8,v=19,dh=3,dv=4,r=SDMedBlueR,g=SDMedBlueG,b=SDHighBlueB,direction=1,scandirection=1,gear=[1],
              speed=(5 * CPUModifier),currentgear=1,
              alive=1,lives=20, name="Player",score=0,exploding=0,radarrange=8,destination="")

  #Create FuelDots
  FuelCount    = 5
  FuelDotsLeft = FuelCount
  ClosestFuel  = 0
  FuelDots     = []
  FuelDots     = [CarDot(h=8,v=8,dh=-1,dv=-1,r=SDLowYellowR,g=SDLowYellowG,b=SDLowYellowB,direction=1,scandirection=1,gear=[],speed=1,currentgear=1,alive=1,lives=1, name="Fuel",score=0,exploding=0,radarrange=0,destination="") for i in xrange(FuelCount)]
  
  #Create RaceWorld, load map 1
  RaceWorld = CreateRaceWorld(1)
  CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld)
  
  #Create Enemy cars
  EnemyCarCount = 6
  EnemyCars = []
  EnemyCars = [CarDot(h=5,v=19,dh=-1,dv=-1,r=SDLowRedR,g=SDLowRedG,b=SDLowRedB,direction=2,scandirection=2,gear=[],speed=(5*CPUModifier),currentgear=1,
               alive=1,
               lives=5,
               name="Enemy",score=0,exploding=0,radarrange=3,destination="") for i in xrange(EnemyCarCount)]
  
  CopyEnemyCarsToPlayfield(EnemyCars,EnemyCarCount,RaceWorld)
    
  
  #Set Player car properties
  PlayerCar.h          = 8
  PlayerCar.v          = 19
  PlayerCar.speed      = 5 * CPUModifier
  CarOriginalSpeed     = PlayerCar.speed
  PlayerCar.radarrange = 12
  PlayerCar.lives      = 100
   
  
  #Display Intro
  #ShowLevelCount(1)
  #ScrollToCar(PlayerCar,RaceWorld)  
  
  #--------------------------------------------------------
  #-- MAIN TIMER LOOP                                    --
  #--------------------------------------------------------
    
  while (LevelFinished == 'N' or PlayerCar.lives <= 0):
    #Reset Variables
    moves = moves + 1
    Key   = ''
    LevelCount = LevelCount + 1


    #Check for keyboard input
    m,r = divmod(moves,KeyboardSpeed)
    if (r == 0):
      Key = PollKeyboard()
      if (Key == 'q'):
        LevelFinished = 'Y'
        Finished      = 'Y'
        return


    #--------------------------------
    #-- Player actions             --
    #--------------------------------

    if (PlayerCar.lives > 0):
      #print ("M - Car HV speed alive exploding direction scandirection: ",PlayerCar.h, PlayerCar.v,PlayerCar.speed, PlayerCar.alive, PlayerCar.exploding, PlayerCar.direction,PlayerCar.scandirection)
      m,r = divmod(moves,PlayerCar.speed)
      if (r == 0):
        #Find closest Fuel
        ClosestFuel,ClosestFuelDistance, FuelDotsLeft = FindClosestFuel(PlayerCar,FuelDots,FuelCount)
        #print ("destination: ",PlayerCar.destination)
        
        #If no destination yet, set to nearest fuel if it exists
        if (ClosestFuelDistance <= PlayerCar.radarrange 
            and FuelDotsLeft > 0 
            and PlayerCar.destination == ""):
          PlayerCar.destination = FuelDots[ClosestFuel].name

        
        #Perform radar check around car.  If no solid objects, then move towards destination
        if (FuelDotsLeft > 0 and PlayerCar.destination == "Fuel"):
          TurnTowardsFuelIfThereIsRoom(PlayerCar,RaceWorld.Playfield,FuelDots,ClosestFuel)
          
        #Move car and determine direction
        MoveCar(PlayerCar,RaceWorld.Playfield)
        direction = PlayerCar.direction
        AdjustCarColor(PlayerCar)

        #Adjust speed if diaganol
        if (PlayerCar.direction in Diaganols):
          PlayerCar.speed = CarOriginalSpeed * SpeedModifier
        else:
          PlayerCar.speed = CarOriginalSpeed

    #Player lost all health (lives)
    elif (PlayerCar.lives == 0):
      PlayerCar.lives = 100
      PlayerCar.h = (RaceWorld.width / 2) + 2
      PlayerCar.v = RaceWorld.height -5
      RaceWorld.Playfield[PlayerCar.v][PlayerCar.h] = PlayerCar
      ScrollToCar(PlayerCar,RaceWorld)  
  
          
    #--------------------------------
    #-- Enemy actions              --
    #--------------------------------

    #keep cars alive until they finish exploding
    #Remember, not everythign gets displayed so be careful with how the display module handles explosions and alive
    #maybe have a separate function to handle all exploding cars

    for x in range (EnemyCarCount):
      if (EnemyCars[x].alive == 1):
        m,r = divmod(moves,EnemyCars[x].speed)
        if (r == 0):
            
          #Check radar.  If player is near by, move towards
          m,r = divmod(moves,EnemyRadarSpeed)
          if (r == 0):
            Distance = GetDistanceBetweenCars(EnemyCars[x],PlayerCar)

            if (Distance < EnemyCars[x].radarrange):
              TurnTowardsCar(EnemyCars[x],PlayerCar)
              EnemyCars[x].destination = "PlayerCar"
              EnemyCars[x].speed = 8 * CPUModifier
            else:
              EnemyCars[x].speed = 4 * CPUModifier
              EnemyCars[x].destination = ""
  
          EnemyCars[x].direction = ChanceOfTurning8Way(EnemyCars[x].direction,10)
          MoveCar(EnemyCars[x],RaceWorld.Playfield)

          
          #Reduce enemy health and speed if they are overheated
          if (EnemyCars[x].name == "Enemy" and EnemyCars[x].r == 255):
            EnemyCars[x].lives = EnemyCars[x].lives -1
            EnemyCars[x].speed = EnemyCars[x].speed + 1

          #if they are out of health, they detonate
          if (EnemyCars[x].lives <= 0):
            EnemyCars[x].exploding = 1
            RallyDotBlowUp(EnemyCars[x],RaceWorld.Playfield)
            RaceWorld.DisplayExplodingObjects(PlayerCar.h-3,PlayerCar.v-4)
            EnemyCars[x].alive = 0
          
      #If car is now dead, remove from playfield
      if (EnemyCars[x].alive == 0):
        RaceWorld.Playfield[EnemyCars[x].v][EnemyCars[x].h] = EmptyObject("EmptyObject")
              
              



    #Check to see if cars are exploding.  If so, display explosions and make cars disappear.
#    for x in range (EnemyCarCount):
#      if (EnemyCars[x].exploding == 1):
#        RallyDotBlowUp(EnemyCars[x],RaceWorld.Playfield)
#    RaceWorld.DisplayExplodingObjects(PlayerCar.h-3,PlayerCar.v-4)
      

          
    
    #-----------------------------------------------------------
    #The cars move virtually on the playfield                 --
    #We can display the screen from any point of view we like --
    #For now we show what the player car is doing             --
    #-----------------------------------------------------------
    
    
    #These display coordinates are from the point of view of the entire playfield
    RaceWorld.DisplayWindow(PlayerCar.h-3,PlayerCar.v-4)
    
    
    
    #print ("moves",moves,"Carh Carv ", PlayerCar.h,PlayerCar.v,"Direction",PlayerCar.direction,"Destination ",PlayerCar.destination,ClosestFuel,"FuelDotsLeft",FuelDotsLeft,FuelDots[0].dh, FuelDots[0].dv,"PlayerCar.lives",PlayerCar.lives,"Player.b",PlayerCar.b,"      ",end="\r")
    sys.stdout.flush()

    #Display animation and clock every X seconds
    if (CheckElapsedTime(CheckTime) == 1):
      ScrollScreenShowTime('up',ScrollSleep)         

    
    #-------------------------
    #-- Load different maps --
    #-------------------------
    
    if (moves >= MaxMoves):
      FlashDot(3,4,FlashSleep * 2)
      unicorn.off()
      ShowScrollingBanner("Game Over",50,0,50,ScrollSleep  * 0.75)
      return

    if (moves == 5000 or FuelDotsLeft == 0):

      #---------------------------------
      #-- Prepare World 2             --
      #---------------------------------

      FlashDot(3,4,FlashSleep * 2)
      #Create RaceWorld, load map 2
      RaceWorld = CreateRaceWorld(2)
    
      #Create FuelDots
      FuelCount    = 10
      FuelDotsLeft = FuelCount
      ClosestFuel  = 0
      FuelDots     = []
      FuelDots     = [CarDot(h=8,v=8,dh=-1,dv=-1,r=SDLowYellowR,g=SDLowYellowG,b=SDLowYellowB,direction=1,scandirection=1,gear=[],speed=1,currentgear=1,alive=1,lives=1, name="Fuel",score=0,exploding=0,radarrange=0,destination="") for i in xrange(FuelCount)]
      CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld)

      #Create Enemy cars
      EnemyCarCount = 10
      EnemyCars = []
      EnemyCars = [CarDot(h=8,v=8,dh=-1,dv=-1,r=SDLowRedR,g=SDLowRedG,b=SDLowRedB,direction=2,scandirection=2,gear=[],speed=(4*CPUModifier),currentgear=1,alive=1,lives=100, name="Enemy",score=0,exploding=0,radarrange=4,destination="") for i in xrange(EnemyCarCount)]
      CopyEnemyCarsToPlayfield(EnemyCars,EnemyCarCount,RaceWorld)
      
      #Set Player car properties
      PlayerCar.h          = 16
      PlayerCar.v          = 19
      PlayerCar.speed      = 5 * CPUModifier
      CarOriginalSpeed     = PlayerCar.speed
      PlayerCar.radarrange = 12
   
      
      #Display Intro
      ShowLevelCount(2)
      ScrollToCar(PlayerCar,RaceWorld)  
        
      
      
    if (moves == 15000 or FuelDotsLeft == 0):

      #---------------------------------
      #-- Prepare World 3             --
      #---------------------------------

      FlashDot(3,4,FlashSleep * 2)
      #Create RaceWorld, load map 3
      RaceWorld = CreateRaceWorld(3)
    
      #Create FuelDots
      FuelCount = 10
      FuelDots = []
      FuelDots = [CarDot(h=8,v=8,dh=-1,dv=-1,r=SDLowYellowR,g=SDLowYellowG,b=SDLowYellowB,direction=1,scandirection=1,gear=[],speed=1,currentgear=1,alive=1,lives=1, name="Fuel",score=0,exploding=0,radarrange=4,destination="") for i in xrange(FuelCount)]
      CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld)

      #Create Enemy cars
      EnemyCarCount = 20
      EnemyCars = []
      EnemyCars = [CarDot(h=8,v=8,dh=-1,dv=-1,r=SDLowRedR,g=SDLowRedG,b=SDLowRedB,direction=2,scandirection=2,gear=[],
                  speed=(4 * CPUModifier),currentgear=1,
                  alive=1,
                  lives=5, name="Enemy",score=0,exploding=0,radarrange=4,destination="") for i in xrange(EnemyCarCount)]
      CopyEnemyCarsToPlayfield(EnemyCars,EnemyCarCount,RaceWorld)
    
      #Set Player car properties
      PlayerCar.h          = 16
      PlayerCar.v          = 26
      PlayerCar.speed      = 5 * CPUModifier
      CarOriginalSpeed     = PlayerCar.speed
      PlayerCar.radarrange = 12

      #Display Intro
      ShowLevelCount(3)
      ScrollToCar(PlayerCar,RaceWorld)  
  

      #---------------------------------
      #-- Prepare World 4            --
      #---------------------------------

      FlashDot(3,4,FlashSleep * 2)
      #Create RaceWorld, load map 3
      RaceWorld = CreateRaceWorld(4)
    
      #Create FuelDots
      FuelCount = 5
      FuelDots = []
      FuelDots = [CarDot(h=8,v=8,dh=-1,dv=-1,r=SDLowYellowR,g=SDLowYellowG,b=SDLowYellowB,direction=1,scandirection=1,gear=[],speed=1,currentgear=1,alive=1,lives=1, name="Fuel",score=0,exploding=0,radarrange=4,destination="") for i in xrange(FuelCount)]
      CopyFuelDotsToPlayfield(FuelDots,FuelCount,RaceWorld)

      #Create Enemy cars
      EnemyCarCount = 5
      EnemyCars = []
      EnemyCars = [CarDot(h=8,v=8,dh=-1,dv=-1,r=SDLowRedR,g=SDLowRedG,b=SDLowRedB,direction=2,scandirection=2,gear=[],
                  speed=(4 * CPUModifier),currentgear=1,
                  alive=1,
                  lives=5, name="Enemy",score=0,exploding=0,radarrange=4,destination="") for i in xrange(EnemyCarCount)]
      CopyEnemyCarsToPlayfield(EnemyCars,EnemyCarCount,RaceWorld)
    
      #Set Player car properties
      PlayerCar.h          = 8
      PlayerCar.v          = 19
      PlayerCar.speed      = 5 * CPUModifier
      CarOriginalSpeed     = PlayerCar.speed
      PlayerCar.radarrange = 12
      PlayerCar.lives      = 100
       

      #Display Intro
      ShowLevelCount(4)
      ScrollToCar(PlayerCar,RaceWorld)  

      
    time.sleep(MainSleep * 0.01 )
    
    
  





#--------------------------------------
#--            PacDot                --
#--------------------------------------


LoadConfigData()




def PlayPacDot(NumDots):  

#----------------------------
#-- PacDot                 --
#----------------------------

  global Ghost1Alive
  global Ghost1H
  global Ghost1V
  global Ghost2Alive
  global Ghost2H
  global Ghost2V
  global Ghost3Alive
  global Ghost3H
  global Ghost3V

  global PowerPills
  global moves     
  global MaxPacmoves
  global DotsEaten  
  global Pacmoves   
  global PowerPillActive
  global PowerPillmoves 
  global BlueGhostmoves 
  global StartGhostSpeed1
  global StartGhostSpeed2
  global StartGhostSpeed3
  global GhostSpeed1    
  global GhostSpeed2    
  global GhostSpeed3    
  global PacSpeed       
  global BlueGhostSpeed 
  global LevelCount     
  global PacPoints      
  global PacStuckMaxCount
  global PacStuckCount   
  global PacOldH         
  global PacOldV         

  #Pac Scoring
  global DotPoints       
  global BlueGhostPoints 
  global PillPoints      
  global PacDotScore     
  global PacDotGamesPlayed
  global PacDotHighScore  

  
  
  PowerPills  = 1
  moves       = 0
  MaxPacmoves = 12
  DotsEaten   = 0
  Pacmoves    = 0
  PowerPillActive = 0
  PowerPillmoves  = 0
  BlueGhostmoves = 50
  StartGhostSpeed1    = 1
  StartGhostSpeed2    = 2
  StartGhostSpeed3    = 3
  GhostSpeed1    = StartGhostSpeed1
  GhostSpeed2    = StartGhostSpeed2
  GhostSpeed3    = StartGhostSpeed3
  PacSpeed       = 1
  BlueGhostSpeed = 4
  LevelCount     = 1
  PacPoints      = 0
  PacStuckMaxCount = 20
  PacStuckCount    = 1
  PacOldH          = 0
  PacOldV          = 0

  #Pac Scoring
  DotPoints         = 1
  BlueGhostPoints   = 5
  PillPoints        = 10
  PacDotScore       = 0
  PacDotGamesPlayed = 0
  PacDotHighScore   = 0
  DotMatrix = [[0 for x in range(8)] for y in range(8)] 
  DotsRemaining = 0

  #Timers
  start_time = time.time()




  
  print ("")
  print ("P-A-C-D-O-T")
  print ("")
  print ("TEST")


  while 1 == 1:   

#    ThreeGhostPacSprite.HorizontalFlip()
#    ThreeGhostPacSprite.ScrollAcrossScreen(0,1,"left",ScrollSleep)
#    ShowScrollingBanner("pacdot",SDLowYellowR,SDLowYellowG,SDLowYellowB,ScrollSleep)
#    ThreeBlueGhostPacSprite.HorizontalFlip()
#    ThreeBlueGhostPacSprite.ScrollAcrossScreen(0,1,"right",ScrollSleep)
    
#    ThreeGhostPacSprite.HorizontalFlip()
#    ThreeBlueGhostPacSprite.HorizontalFlip()
    
    
      

    LevelString = str(LevelCount)
    
    
    unicorn.off()
   
    ShowLevelCount(LevelCount)

    DotMatrix = [[0 for x in range(8)] for y in range(8)] 
    
    #Reset Variables
    moves           = 0  
    PowerPillmoves  = 0
    PowerPillActive = 0
    PacStuckCount   = 0
    Ghost1H = 3
    Ghost1V = 7
    Ghost2H = 4
    Ghost2V = 7
    Ghost3H = 5
    Ghost3V = 7
    PacDotH = 3
    PacDotV = 0
    DotMatrix = [[0 for x in range(8)] for y in range(8)] 
    DotsRemaining = 0
    DotsEaten = 0
    Key           = ""
    unicorn.off()
    
     
    #DrawDotMatrix is newer than the previous method to draw the dots.  Old method should be removed.
    DotMatrix = DrawDots(NumDots)  
    DrawDotMatrix(DotMatrix)
    

    
    #DrawMaze()
    CurrentDirection1 = randint(1,4)
    CurrentDirection2 = randint(1,4)
    CurrentDirection3 = randint(1,4)
    CurrentDirection3 = randint(1,4)
    CurrentDirectionPacDot = randint(1,4)
    PowerPillActive = 0

    Ghost1Alive = 1
    Ghost2Alive = 1
    Ghost3Alive = 1 
   
    
    

    #decrement dots if PacDot starts out on one
    r,g,b = unicorn.get_pixel(PacDotH,PacDotV)
    if r == DotB and g == DotG and b == DotB:
      NumDots = NumDots -1
      #New method utilizes DotMatrix
      DotMatrix[PacDotH][PacDotV] = 0

    DotsRemaining = CountDotsRemaining(DotMatrix)
   
      
    Ghost1H,Ghost1V = DrawGhost(Ghost1H,Ghost1V,Ghost1R,Ghost1G,Ghost1B)
    Ghost2H,Ghost2V = DrawGhost(Ghost2H,Ghost2V,Ghost2R,Ghost2G,Ghost2B)
    Ghost3H,Ghost3V = DrawGhost(Ghost3H,Ghost3V,Ghost3R,Ghost3G,Ghost3B)
    PacDotH,PacDotV = DrawPacDot(PacDotH,PacDotV,PacR,PacG,PacB)

    DrawPowerPills(PowerPills)

    print ("moves: ",moves, "NumDots: ",NumDots," DotsEaten: ",DotsEaten," DotsRemaining: ",DotsRemaining, " ",end="\r")
    sys.stdout.flush()
    
    
    

    while ((moves < MaxMoves) and (DotsRemaining > 0) and (PacStuckCount <= PacStuckMaxCount)):
      DotsRemaining = CountDotsRemaining(DotMatrix)
      moves = moves + 1
      PacOldH = PacDotH
      PacOldV = PacDotV
      print ("moves: ",moves, "MaxMoves:",MaxMoves,"NumDots: ",NumDots," DotsEaten: ",DotsEaten," DotsRemaining: ",DotsRemaining, " ",end="\r")
      sys.stdout.flush()
      
      #Check for keyboard input
      Key = ''
      m,r = divmod(moves,KeyboardSpeed)
      if (r == 0):
        Key = PollKeyboard()
        if (Key == 'q'):
          moves = MaxMoves
          return

        
      if PowerPillActive == 1:
        PowerPillmoves = PowerPillmoves + 1
        GhostSpeed1 = BlueGhostSpeed
        GhostSpeed2 = BlueGhostSpeed
        GhostSpeed3 = BlueGhostSpeed

        if PowerPillmoves >= BlueGhostmoves:
          #Need to refresh dots
          DotsRemaining = CountDotsRemaining(DotMatrix)
          PowerPillActive = 0
          PowerPillmoves = 0
          if (Ghost1Alive == 0):
            Ghost1Alive = 1
            Ghost1H = 3
            Ghost1V = 7
          if (Ghost2Alive == 0):
            Ghost2Alive = 1
            Ghost2H = 4
            Ghost2V = 7
          if (Ghost3Alive == 0):
            Ghost3Alive = 1
            Ghost3H = 5
            Ghost3V = 7
          CurrentDirection1 = 4
          CurrentDirection2 = 1
          CurrentDirection2 = 2
          GhostSpeed1 = StartGhostSpeed1
          GhostSpeed2 = StartGhostSpeed2
          GhostSpeed3 = StartGhostSpeed3



      #print ("-- Red ghost --")

          
      #If the ghost speed divides evenly into the moves, the ghost gets to move
      #The lower the ghost speed indicator, the more often it will move
      if Ghost1Alive == 1:
        m,r = divmod(moves,GhostSpeed1)
        if (r == 0):
          Ghost1H, Ghost1V, CurrentDirection1 = MoveGhost(Ghost1H, Ghost1V,CurrentDirection1,Ghost1R,Ghost1G,Ghost1B)
          CurrentDirection1 = ChanceOfTurning(CurrentDirection1,10)
          Ghost1H,Ghost1V = DrawGhost(Ghost1H,Ghost1V,Ghost1R,Ghost1G,Ghost1B)

      if Ghost2Alive == 1:
        m,r = divmod(moves,GhostSpeed2)
        if (r == 0):
          Ghost2H, Ghost2V, CurrentDirection2 = MoveGhost(Ghost2H, Ghost2V,CurrentDirection2,Ghost2R,Ghost2G,Ghost2B)
          CurrentDirection2 = ChanceOfTurning(CurrentDirection2,25)
          Ghost2H,Ghost2V = DrawGhost(Ghost2H,Ghost2V,Ghost2R,Ghost2G,Ghost2B)

      if Ghost3Alive == 1:
        m,r = divmod(moves,GhostSpeed3)
        if (r == 0):
          Ghost3H, Ghost3V, CurrentDirection3 = MoveGhost(Ghost3H, Ghost3V,CurrentDirection3,Ghost3R,Ghost3G,Ghost3B)
          CurrentDirection3 = ChanceOfTurning(CurrentDirection3,40)
          Ghost3H,Ghost3V = DrawGhost(Ghost3H,Ghost3V,Ghost3R,Ghost3G,Ghost3B)

      #Move Pacman
      m,r = divmod(moves,PacSpeed)
      if (r == 0):
        CurrentDirectionPacDot = FollowScanner(PacDotH,PacDotV,CurrentDirectionPacDot)
        if Pacmoves > MaxPacmoves:
          CurrentDirectionPacDot = ChanceOfTurning(CurrentDirectionPacDot,100)
          Pacmoves = 0
        else:
          ChanceOfTurning(CurrentDirectionPacDot,15)
        
        PacDotH, PacDotV, CurrentDirectionPacDot, DotsEaten = MovePacDot(PacDotH, PacDotV,CurrentDirectionPacDot,PacR,PacG,PacB,DotsEaten)
        PacDotH,PacDotV = DrawPacDot(PacDotH,PacDotV,PacR,PacG,PacB)

      #print ("MinDots:",MinDots,"MaxDots:",MaxDots,"MaxMoves:",MaxMoves,"moves:",moves,"NumDots:", NumDots,"Eaten:",DotsEaten,"Pmoves:",Pacmoves,"G1Alive:",Ghost1Alive,"PPActv:",PowerPillActive, end="\r")
      sys.stdout.flush()
      unicorn.show()
      
      # If pacman is stuck, game over
      if (PacOldH == PacDotH and PacOldV == PacDotV):
        PacStuckCount = PacStuckCount + 1
      else:
        PacStuckCount = 0

      if (CheckElapsedTime(CheckTime) == 1):
        ScrollScreenShowTime('UP',ScrollSleep)
        PacLeftAnimatedSprite.Scroll(8,1,'left',13,ScrollSleep)

      #Count dots.  Sometimes the ghosts sit on a dot and it loses its color
      if (CheckElapsedTime(5) == 1):
        DotsRemaining = CountDotsRemaining(DotMatrix)

        
        
      time.sleep(MainSleep*1.5)


        
    
    
    #Show Game over or level count
    if (Key <>  "q"):
      if (DotsRemaining == 0):
        ScoreString = str(PacDotScore) 
        ScrollScreen('down',ScrollSleep)
        unicorn.off()
        PacLeftAnimatedSprite.Scroll(8,1,'left',13,ScrollSleep)
        ShowScrollingBanner("Score",0,100,100,ScrollSleep  * 0.75)
        ShowScrollingBanner(ScoreString,0,100,0,(ScrollSleep  * 0.75))
        NumDots = randint(MinDots,MaxDots)
        DotsEaten = 0
        DotsRemaining = NumDots
        LevelCount = LevelCount + 1
        
      else:
        #End of Maze Display
        FlashDot(Ghost1H,Ghost1V,FlashSleep)
        FlashDot(Ghost2H,Ghost2V,FlashSleep)
        FlashDot(Ghost3H,Ghost3V,FlashSleep)
        FlashDot(PacDotH,PacDotV,FlashSleep)

        PacDotGamesPlayed = PacDotGamesPlayed + 1
        ScrollScreen('down',ScrollSleep)
        ThreeGhostPacSprite.ScrollAcrossScreen(0,1,"right",ScrollSleep)
        #ThreeGhostSprite.ScrollAcrossScreen(0,1,"right",ScrollSleep)

        ScoreString = str(PacDotScore) 
        ShowScrollingBanner("Score",0,100,100,ScrollSleep * 0.75)
        ShowScrollingBanner(ScoreString,0,100,0,(ScrollSleep * 0.75 ))
        ShowScrollingBanner("GAME OVER",100,0,0,ScrollSleep * 0.75)
        unicorn.off()
        unicorn.show()
        #LevelCount = 1
        if (PacDotScore > PacDotHighScore):
          PacDotHighScore = PacDotScore
        PacDotScore = 0
        ScoreString = str(PacDotHighScore) 
        unicorn.off()
        ShowScrollingBanner("High Score",0,90,90,ScrollSleep * 0.75)
        ShowScrollingBanner(ScoreString,0,100,0,(ScrollSleep * 0.75))

        ScoreString = str(PacDotGamesPlayed) 
        ShowScrollingBanner("Games",0,100,100,ScrollSleep * 0.75)
        ShowScrollingBanner(ScoreString,0,100,0,(ScrollSleep * 0.75))

        #Play other games
        return
    else:
      return

    
#--------------------------------------
# VirusWorld                         --
#--------------------------------------

# Ideas:
# - Mutations happen
# - if virus is mutating, track that in the object itself
# - possible mutations: speed, turning eraticly
# - aggression, defence can be new attributes
# - need a new object virus dot
# - when a virus conquers an area, remove part of the wall and scroll to the next area
# - areas may have dormant viruses that are only acivated once in a while
# - 




class VirusWorld(object):
#Started out as an attempt to make cars follow shapes.  I was not happy with the results so I converted into a petri dish of viruses
  def __init__(self,name,width,height,Map,Playfield,CurrentRoomH,CurrentRoomV,DisplayH, DisplayV):
    self.name      = name
    self.width     = width
    self.height    = height
    self.Map       = ([[]])
    self.Playfield = ([[]])
    self.CurrentRoomH = 0
    self.CurrentRoomV = 0
    self.DisplayH     = 0
    self.DisplayV     = 0

    self.Map       = [[0 for i in xrange(self.width)] for i in xrange(self.height)]
    self.Playfield = [[EmptyObject('EmptyObject') for i in xrange(self.width)] for i in xrange(self.height)]



  def CopyMapToPlayfield(self):
    #This function is run once to populate the playfield with wall objects, based on the map drawing
    #XY is actually implemented as YX.  Counter intuitive, but it works.

    width  = self.width 
    height = self.height
    Cars   = []
    VirusName = ""
   
    #print ("RD - CopyMapToPlayfield - Width Height: ", width,height)
    x = 0
    y = 0
    
    
    #print ("width height: ",width,height)
    
    for y in range (0,height):
      #print ("-------------------")
      #print (*self.Map[y])
  
      for x in range(0,width):
        #print ("RD xy color: ",x,y, self.Map[y][x])
        SDColor = self.Map[y][x]
  
        if (SDColor == 1):
          r = 45
          g = 45
          b = 45
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,1,'Wall')


        elif (SDColor == 2):
          r = 60
          g = 60
          b = 60
                                    #(h,v,r,g,b,alive,lives,name):
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,10,'Wall')
          #print ("Copying wallbreakable to playfield hv: ",y,x)

        elif (SDColor == 3):
          r = 75
          g = 75
          b = 75
                                    #(h,v,r,g,b,alive,lives,name):
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,10,'Wall')
          #print ("Copying wallbreakable to playfield hv: ",y,x)

        elif (SDColor == 4):
          r = 45
          g = 45
          b = 75
                                    #(h,v,r,g,b,alive,lives,name):
          self.Playfield[y][x] = Wall(x,y,r,g,b,1,walllives,'WallBreakable')
          #print ("Copying wallbreakable to playfield hv: ",y,x)

        elif (SDColor >=5):
          r,g,b =  ColorList[SDColor]
          VirusName = str(r)+str(g)+str(b)
          
          #(h,v,dh,dv,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding,radarrange,destination,mutationtype,mutationrate, mutationfactor, replicationrate):
          
          self.Playfield[y][x] = Virus(x,y,x,y,r,g,b,1,1,       VirusStartSpeed   ,1,10,VirusName,0,0,10,'West',0,mutationrate,0,replicationrate)
          self.Playfield[y][x].direction = random.randint(1,8)
          Cars.append(self.Playfield[y][x])
        else:
          #print ("EmptyObject")
          self.Playfield[y][x] = EmptyObject('EmptyObject')
    return Cars;


  def DisplayWindow(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64)    
    #Displays what is on the playfield currently, including walls, cars, etc.
    r = 0
    g = 0
    b = 0
    count = 0
        

    for V in range(0,8):
      for H in range (0,8):
         
        name = self.Playfield[v+V][h+H].name
        #print ("Display: ",name,V,H)
        if (name == "EmptyObject"):
          r = 0
          g = 0
          b = 0          

        else:
          r = self.Playfield[v+V][h+H].r
          g = self.Playfield[v+V][h+H].g
          b = self.Playfield[v+V][h+H].b
          
        #Our map is an array of arrays [v][h] but we draw h,v
        unicorn.set_pixel(H,V,r,g,b)
    
    unicorn.show()


  def CountVirusesInWindow(self,h,v):
    #This function accepts h,v coordinates for the entire map (e.g. 1,8  20,20,  64,64) 
    #and counts how many items are in the area
    count = 0
        
    for V in range(0,8):
      for H in range (0,8):
         
        name = self.Playfield[v+V][h+H].name
        #print ("Display: ",name,V,H)
        if (name not in ("EmptyObject","Wall","WallBreakable")):
          count = count + 1
    return count;





class Virus(object):
  
  def __init__(self,h,v,dh,dv,r,g,b,direction,scandirection,speed,alive,lives,name,score,exploding,radarrange,destination,mutationtype,mutationrate,mutationfactor,replicationrate):

    self.h               = h         # location on playfield (e.g. 10,35)
    self.v               = v         # location on playfield (e.g. 10,35)
    self.dh              = dh        # location on display   (e.g. 3,4) 
    self.dv              = dv        # location on display   (e.g. 3,4) 
    self.r               = r
    self.g               = g
    self.b               = b
    self.direction       = direction      #direction of travel
    self.scandirection   = scandirection  #direction of scanners, if equipped
    self.speed           = speed
    self.alive           = 1
    self.lives           = 3
    self.name            = name
    self.score           = 0
    self.exploding       = 0
    self.radarrange      = 20
    self.destination     = ""
    self.mutationtype    = mutationtype
    self.mutationrate    = mutationrate   #high number, greater chance 
    self.mutationfactor  = mutationfactor #used to impact amount of mutation
    self.replicationrate = replicationrate    

  def Display(self):
    if (self.alive == 1):
      unicorn.set_pixel(self.h,self.v,self.r,self.g,self.b)
     # print("display HV:", self.h,self.v)
      unicorn.show()
  
      
  def Erase(self):
    unicorn.set_pixel(self.h,self.v,0,0,0)
    unicorn.show()



  def AdjustSpeed(self, increment):
    speed = self.speed
    speed = self.speed + increment
    if (speed > VirusBottomSpeed):
      speed = VirusBottomSpeed
    elif (speed < VirusTopSpeed):
      speed = VirusTopSpeed

    self.speed = speed
    return;


  def Mutate(self):
    x              = 0
    mutationtypes  = 6  #number of possible mutations
                        # direction
                        #   - left 1,2
                        #   - left 1,2,3
                        #   - right 1,2
                        #   - left 1,2,3
                        # speed up
                        # speed down
    mutationrate   = self.mutationrate
    mutationtype   = self.mutationtype
    mutationfactor = self.mutationfactor
    speed          = self.speed
    MinSpeed       = 1 * CPUModifier
    MaxSpeed       = 5 * CPUModifier   #higher = slower!
    MinBright      = 45
    MaxBright      = 200
    r              = 0
    g              = 0
    b              = 0
    name           = 0


    #print ("--Virus mutation!--")
    mutationtype = random.randint(1,mutationtypes)

    #Mutations can be deadly
    if (random.randint(1,mutationdeathrate) == 1):
      self.alive = 0
      self.lives = 0
      self.speed = 999999
      self.name  = "EmptyObject"
      self.r     = 0
      self.g     = 0
      self.b     = 0
  
    #Directional Behavior - turns left a little
    if (mutationtype == 1):
      mutationfactor       = random.randint(1,2)

    #Directional Behavior - turns left a lot
    elif (mutationtype == 2):
      mutationfactor       = random.randint(2,3)

    #Directional Behavior - turns right a little
    elif (mutationtype == 3):
      mutationfactor       = random.randint(1,2)

    #Directional Behavior - turns right a lot
    elif (mutationtype == 4):
      mutationfactor       = random.randint(2,3)

    #Speed up
    elif (mutationtype == 5):
      mutationfactor = random.randint(MinSpeed,MaxSpeed)
      self.AdjustSpeed(mutationfactor * -1)
      print ("Mutation: speed up", self.speed, mutationfactor)
      if (speed < 1):
        speed = 1

    #Speed down
    elif (mutationtype == 6):
      mutationfactor = random.randint(MinSpeed,MaxSpeed)
      self.AdjustSpeed(mutationfactor * 1)
      print ("Mutation: slow down", self.speed, mutationfactor)



    #Mutations get a new name and color
    x = random.randint(1,7)
    if (x == 1):
      #Big Red
      r = random.randint(MinBright,MaxBright)
      g = 0
      b = 0
      
    if (x == 2):
      #booger
      r = 0
      g = random.randint(MinBright,MaxBright)
      b = 0

    if (x == 3):
      #BlueWhale
      r = 0
      g = 0
      b = random.randint(MinBright,MaxBright)

    if (x == 4):
      #pinky
      r = random.randint(MinBright,MaxBright)
      g = 0
      b = random.randint(MinBright,MaxBright)

    if (x == 5):
      #MellowYellow
      r = random.randint(MinBright,MaxBright)
      g = random.randint(MinBright,MaxBright)
      b = 0

    if (x == 6):
      #undead
      r = 0
      g = random.randint(MinBright,MaxBright)
      b = random.randint(MinBright,MaxBright)

    if (x == 7):
      #swamp mix
      r = random.randint(MinBright,MaxBright)
      g = random.randint(MinBright,MaxBright)
      b = random.randint(MinBright,MaxBright)
      
    #Update common properties
    self.r              = r
    self.g              = g
    self.b              = b
    self.name           = "" + str(self.r)+str(self.g)+str(self.b)
    self.mutationtype   = mutationtype
    self.mutationfactor = mutationfactor
    print ("TheSpeed: ",self.speed)
    


def VirusWorldScanAround(Virus,Playfield):
  # hv represent car location
  # ScanH and ScanV is where we are scanning
  
  #print ("== Scan in Front of Virus ==")
  
  ScanDirection = Virus.direction
  ScanH         = 0
  ScanV         = 0
  h             = Virus.h
  v             = Virus.v
  Item          = ''
  ItemList      = ['EmptyObject']
  count         = 0    #represents number of spaces to scan

#         2 1 3
#         5 x 6                              
#           4   
  
  #FlashDot2(h,v,0.005)

  #Scan in front
  ScanH, ScanV = CalculateDotMovement8Way(h,v,Virus.direction)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  
  #Scan left diagonal
  ScanDirection = TurnLeft8Way(Virus.direction)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  #Scan right diagonal
  ScanDirection = TurnRight8Way(Virus.direction)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  #Scan behind
  ScanDirection = ReverseDirection8Way(Virus.direction)
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)
  
  #Scan left
  ScanDirection = TurnLeft8Way(TurnLeft8Way(Virus.direction))
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)


  #Scan right
  ScanDirection = TurnRight8Way(TurnRight8Way(Virus.direction))
  ScanH, ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
  ItemList.append(Playfield[ScanV][ScanH].name)


  return ItemList;
  

def SpreadInfection(Virus1,Virus2,direction):
  #print ("Spread Infection: ",Virus1.name, Virus2.name)
  
  #for some reason, my wall checks still let the odd wall slip past.  This will take care of it.
  if (Virus2.name == "WallBreakable"):
    #print ("Wallbreakable is immune from infections but does sustain damage",Virus2.lives)
    Virus2.lives = Virus2.lives -1
    if (Virus2.lives <= 0):
      Virus2.alive = 0
      Virus2.lives = 0

  else:
    Virus2.name = Virus1.name
    Virus2.r    = Virus1.r   
    Virus2.g    = Virus1.g   
    Virus2.b    = Virus1.b   
    Virus2.direction      = direction
    Virus2.speed          = Virus1.speed
    Virus2.mutationtype   = Virus1.mutationtype
    Virus2.mutationrate   = Virus1.mutationrate
    Virus2.mutationfactor = Virus1.mutationfactor
    
    #Infected virus slows down, attempt to increase clumping
    Virus2.AdjustSpeed(+ClumpingSpeed)

  
def ReplicateVirus(Virus,DinnerPlate):
  ItemList  = []
  ItemList  = VirusWorldScanAround(Virus,DinnerPlate.Playfield)
  h         = Virus.h
  v         = Virus.v
  ScanV     = 0
  ScanH     = 0
  direction = Virus.direction
  scandirection = 0
  VirusCopy = EmptyObject("EmptyObject")
  

  print ("--Replication in progress--")
  
  if (ItemList[5] == "EmptyObject" or
      ItemList[6] == "EmptyObject"):
  
    if (ItemList[5] == "EmptyObject"):
      print ("Open space to the left")
      scandirection  = TurnLeft8Way(TurnLeft8Way(direction))
      print ("direction scandirection",direction,scandirection)

    elif (ItemList[6] == "EmptyObject"):
      print ("Open space to the right")
      scandirection = TurnRight8Way(TurnRight8Way(direction))

    ScanH,ScanV = CalculateDotMovement8Way(h,v,scandirection)
    VirusCopy = copy.deepcopy(Virus)
    VirusCopy.v = ScanV
    VirusCopy.h = ScanH
    VirusCopy.AdjustSpeed(ReplicationSpeed)
    DinnerPlate.Playfield[ScanV][ScanH] = VirusCopy

  
  else:
    print ("No room at the inn.  Sorry folks!")
    print ("--Replication terminated--")
    
  return VirusCopy;
  

def MoveVirus(Virus,Playfield):
  #print ("== MoveVirus : ",Virus.name," hv dh dv alive--",Virus.h,Virus.v,Virus.dh,Virus.dv,Virus.alive)
  
  #print ("")
  h = Virus.h
  v = Virus.v
  oldh  = h
  oldv  = v
  ScanH = 0
  ScanV = 0
  ItemList = []
  DoNothing = ""
  ScanDirection = 1
  WallInFront    = EmptyObject("EmptyObject")
  VirusInFront   = EmptyObject("EmptyObject")
  VirusInRear    = EmptyObject("EmptyObject")
  VirusLeftDiag  = EmptyObject("EmptyObject")
  VirusRightDiag = EmptyObject("EmptyObject")
  
  #Infection / mutation modiefers
  #We need a random chance of mutation
  #  possibilities: 
  #  - mutate into another color
  #  - vastly increase/decrease speed
  #  - change direction
  #  - happens right before last move 
  
  InfectionSpeedModifier = -1
 

  #print("Current Virus vh direction:",v,h,Virus.direction)
  ItemList = VirusWorldScanAround(Virus,Playfield)
  #print (ItemList)
  

  #Grab breakable wall object
  if (ItemList[1] == "WallBreakable"):
    ScanH,ScanV = CalculateDotMovement8Way(h,v,Virus.direction)
    WallInFront = Playfield[ScanV][ScanH]


  #Grab potential viruses in scan zones NW N NE S
  #Grab Virus in front
  if (ItemList[1] <> "Wall" and ItemList[1] <> "WallBreakable" and ItemList[1] <> "EmptyObject"):
    ScanH,ScanV = CalculateDotMovement8Way(h,v,Virus.direction)
    VirusInFront = Playfield[ScanV][ScanH]
    #print ("ScanFront    ",VirusInFront.name,VirusLeftDiag.name,VirusRightDiag.name,VirusInRear.name)

  #Grab Virus left diagonal
  if (ItemList[2] <> "Wall" and ItemList[1] <> "WallBreakable" and ItemList[2] <> "EmptyObject"):
    ScanDirection = TurnLeft8Way(Virus.direction)
    ScanH,ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
    VirusLeftDiag = Playfield[ScanV][ScanH]
    #print ("ScanLeftDiag ",VirusInFront.name,VirusLeftDiag.name,VirusRightDiag.name,VirusInRear.name)

  #Grab Virus right diagonal
  if (ItemList[3] <> "Wall" and ItemList[1] <> "WallBreakable" and ItemList[3] <> "EmptyObject"):
    ScanDirection = TurnRight8Way(Virus.direction)
    ScanH,ScanV = CalculateDotMovement8Way(h,v,ScanDirection)
    VirusRightDiag = Playfield[ScanV][ScanH]
    #print ("ScanRightDiag",VirusInFront.name,VirusLeftDiag.name,VirusRightDiag.name,VirusInRear.name)
  
        
  if (ItemList[4] <> "Wall" and ItemList[1] <> "WallBreakable" and ItemList[4] <> "EmptyObject"):
    ScanDirection = ReverseDirection8Way(Virus.direction)
    ScanH,ScanV   = CalculateDotMovement8Way(h,v,ScanDirection)
    VirusInRear     = Playfield[ScanV][ScanH]
    #print ("ScanRear",VirusInFront.name,VirusLeftDiag.name,VirusRightDiag.name,VirusInRear.name)
  

  #Infect Viruss
  #If different virus, take it over
  #else follow it


  #Add damage to breakable walls
  if (WallInFront.name == "WallBreakable"):
    #print ("Wall in front: ",WallInFront.name, WallInFront.lives)
    WallInFront.lives = WallInFront.lives -1
    if (WallInFront.lives <= 0):
      Playfield[WallInFront.v][WallInFront.h] = EmptyObject("EmptyObject")


  #print ("Thing in front:",VirusInFront.name, WallInFront.name)
        
  #Check front Virus
  if (VirusInFront.name <> "EmptyObject"):
    if (VirusInFront.name <> Virus.name):
      SpreadInfection(Virus,VirusInFront,Virus.direction)
      #VirusInFront.AdjustSpeed(InfectionSpeedModifier)

  #Check left diagonal Virus
  if (VirusLeftDiag.name <> "EmptyObject"):
    if (VirusLeftDiag.name <> Virus.name):
      SpreadInfection(Virus,VirusLeftDiag,(TurnLeft8Way(Virus.direction)))


  #Check right diagonal Virus
  if (VirusRightDiag.name <> "EmptyObject"):
    if (VirusRightDiag.name <> Virus.name):
      SpreadInfection(Virus,VirusRightDiag,(TurnRight8Way(Virus.direction)))


  #Check rear Virus
  if (VirusInRear.name <> "EmptyObject"):
    #If different virus, take it over 
    #make it follow
    if (VirusInRear.name <> Virus.name):
      SpreadInfection(Virus,VirusInRear,Virus.direction)


  #We follow other virus of the same name
  if (VirusInFront.name == Virus.name):
    Virus.direction = VirusInFront.direction
  elif (VirusLeftDiag.name == Virus.name):
    Virus.direction = VirusLeftDiag.direction
  elif (VirusRightDiag.name == Virus.name):
    Virus.direction = VirusRightDiag.direction
  elif (VirusInRear.name == Virus.name):
    Virus.direction = VirusInRear.direction


  #If no viruses around, increase speed and wander around
  if (all("EmptyObject" == Item for Item in ItemList)):
    Virus.AdjustSpeed(-1)
  

  #print ("Viruss: ",Virus.name, VirusInFront.name, VirusLeftDiag.name, VirusRightDiag.name, VirusInRear.name)

  
  #If no viruses around, check for walls
  if (all("EmptyObject" == name for name in (VirusInFront.name, VirusLeftDiag.name, VirusRightDiag.name, VirusInRear.name))):
    

    if (ItemList[1] == "WallBreakable"):
      Virus.direction = TurnLeftOrRight8Way(Virus.direction)

    elif((ItemList[1] == "Wall" or ItemList[1] == "WallBreakable") 
      and ItemList[2] == "EmptyObject" 
      and ItemList[3] == "EmptyObject"):
      Virus.direction = TurnLeftOrRight8Way(Virus.direction)

    elif((ItemList[1] == "Wall" or ItemList[1] == "WallBreakable") 
      and(ItemList[2] == "Wall" or ItemList[2] == "WallBreakable") 
      and ItemList[3] == "EmptyObject"):
      Virus.direction = TurnRight8Way(Virus.direction)

    elif((ItemList[1] == "Wall" or ItemList[1] == "WallBreakable")
      and ItemList[2] == "EmptyObject" 
      and(ItemList[3] == "Wall" or ItemList[3] == "WallBreakable")):
      Virus.direction = TurnLeft8Way(Virus.direction)

    elif((ItemList[1] == "Wall" or ItemList[1] == "WallBreakable")
     and (ItemList[2] == "Wall" or ItemList[2] == "WallBreakable")
     and (ItemList[3] == "Wall" or ItemList[3] == "WallBreakable")):
      Virus.direction = TurnLeftOrRightTwice8Way(ReverseDirection8Way(Virus.direction))
 

  #-----------------------------------------
  #-- Mutations                           --
  #-----------------------------------------

  #Mutate virus
  #print ("MV - mutationrate type factor",Virus.mutationrate, Virus.mutationtype, Virus.mutationfactor)
  if (random.randint(0,Virus.mutationrate) == 1):
    Virus.Mutate()
    if (Virus.alive == 0):
      print ("Virus died!")
      Virus.lives = 0
      Virus.speed = 1
      Virus.mutationtype   = 0
      Virus.mutationfactor = 0
      Playfield[Virus.v][Virus.h] = EmptyObject("EmptyObject")



  if(Virus.mutationtype > 0):
    # 1-4 is direction based
    if (Virus.mutationtype in(1,2)):
      for x in range(1,Virus.mutationfactor):
        #print ("VM - mutation turning left")
        Virus.direction = TurnLeft8Way(Virus.direction)
    elif (Virus.mutationtype in(3,4)):
      for x in range(1,Virus.mutationfactor):
        #print ("VM - mutation turning right")
        Virus.direction = TurnRight8Way(Virus.direction)
    if (Virus.mutationtype == 5):
      #print ("VM - mutation setting speed up",Virus.mutationfactor)
      Virus.AdjustSpeed(Virus.mutationfactor)
    if (Virus.mutationtype == 6):
      #print ("VM - mutation setting slow",Virus.mutationfactor)
      Virus.AdjustSpeed(Virus.mutationfactor)
    

  if (Virus.alive == 1):  
    #Only move if the space decided upon is actually empty!
    ScanH,ScanV = CalculateDotMovement8Way(h,v,Virus.direction)
    if (Playfield[ScanV][ScanH].name == "EmptyObject"):
      #print ("Spot moving to is empty ScanV ScanH",ScanV,ScanH)
      #print ("Virus moved!!!!!!!!!!!!!")
      Virus.h = ScanH
      Virus.v = ScanV

      #print ("Making Empty oldv oldh vh ",oldv,oldh,v,h)
      Playfield[ScanV][ScanH] = Virus
      Playfield[oldv][oldh] = EmptyObject("EmptyObject")
      #print ("Old spot:",Playfield[oldv][oldh].name)
    else:
      #print ("spot moving to is not empty: ",Playfield[ScanV][ScanH].name, ScanV,ScanH)
      #Introduce some instability into the virus
      if (random.randint(0,InstabilityFactor) == 1):
        Virus.direction = TurnLeftOrRight8Way(Virus.direction)
        Virus.AdjustSpeed(random.randint(-5,3))
  else:
    print ("Virus died during mutation.  No movement possible.")
  return 



def PlayVirusWorld():      

  finished     = 'N'
  moves        = 0
  VirusSpeed   = 100
  Viruses      = []
  VirusCount   = 0
  Virus        = EmptyObject("EmptyObject")
  VirusDeleted = 0
  
  
  #Camera Path
  CameraPath     =  [[0 for i in xrange(3)] for i in xrange(47)]
  CameraPath[0]  = ([1,1,ScrollSpeedLong])
  CameraPath[1]  = ([2,1,ScrollSpeedShort])
  CameraPath[2]  = ([3,1,ScrollSpeedShort])
  CameraPath[3]  = ([4,1,ScrollSpeedShort])
  CameraPath[4]  = ([5,1,ScrollSpeedShort])
  CameraPath[5]  = ([6,1,ScrollSpeedShort])
  CameraPath[6]  = ([7,1,ScrollSpeedShort])
  CameraPath[7]  = ([8,1,ScrollSpeedShort])
  CameraPath[8]  = ([9,1,ScrollSpeedLong])
  CameraPath[9]  = ([10,1,ScrollSpeedShort])
  CameraPath[10] = ([11,1,ScrollSpeedShort])
  CameraPath[11] = ([12,1,ScrollSpeedShort])
  CameraPath[12] = ([13,1,ScrollSpeedShort])
  CameraPath[13] = ([14,1,ScrollSpeedShort])
  CameraPath[14] = ([15,1,ScrollSpeedShort])
  CameraPath[15] = ([16,1,ScrollSpeedLong])
  CameraPath[16] = ([16,2,ScrollSpeedShort])
  CameraPath[17] = ([16,3,ScrollSpeedShort])
  CameraPath[18] = ([16,4,ScrollSpeedShort])
  CameraPath[19] = ([16,5,ScrollSpeedShort])
  CameraPath[20] = ([16,6,ScrollSpeedShort])
  CameraPath[21] = ([16,7,ScrollSpeedShort])
  CameraPath[22] = ([16,8,ScrollSpeedShort])
  CameraPath[23] = ([16,9,ScrollSpeedLong])
  CameraPath[24] = ([15,9,ScrollSpeedShort])
  CameraPath[25] = ([14,9,ScrollSpeedShort])
  CameraPath[26] = ([13,9,ScrollSpeedShort])
  CameraPath[27] = ([12,9,ScrollSpeedShort])
  CameraPath[28] = ([11,9,ScrollSpeedShort])
  CameraPath[29] = ([10,9,ScrollSpeedShort])
  CameraPath[30] = ([9,9,ScrollSpeedShort])
  CameraPath[31] = ([8,9,ScrollSpeedLong])
  CameraPath[32] = ([7,9,ScrollSpeedShort])
  CameraPath[33] = ([6,9,ScrollSpeedShort])
  CameraPath[34] = ([5,9,ScrollSpeedShort])
  CameraPath[35] = ([4,9,ScrollSpeedShort])
  CameraPath[36] = ([3,9,ScrollSpeedShort])
  CameraPath[37] = ([2,9,ScrollSpeedShort])
  CameraPath[38] = ([1,9,ScrollSpeedLong])
  CameraPath[39] = ([1,8,ScrollSpeedShort])
  CameraPath[40] = ([1,7,ScrollSpeedShort])
  CameraPath[41] = ([1,6,ScrollSpeedShort])
  CameraPath[42] = ([1,5,ScrollSpeedShort])
  CameraPath[43] = ([1,4,ScrollSpeedShort])
  CameraPath[44] = ([1,3,ScrollSpeedShort])
  CameraPath[45] = ([1,2,ScrollSpeedShort])
  CameraPath[46] = ([1,1,ScrollSpeedShort])


  PathCount     = len(CameraPath)
  PathPosition  = 0
  PositionSpeed = 100

  CameraH         = 0
  CameraV         = 0
  CameraDirection = 0
  CameraSpeed     = 5
  VirusesInWindow = 0
  
  CameraH, CameraV, CameraSpeed = CameraPath[0]
  


  #The map is an array of a lists.  You can address each element has VH e.g. [V][H]
  #Copying the map to the playfield needs to follow the exact same shape

  #Set world dimensions
  # DinnerPlate = VirusWorld(name='TestBanner',
                           # width        = 24,
                           # height       = 16,
                           # Map          = [[]],
                           # Playfield    = [[]],
                           # CurrentRoomH = 1,
                           # CurrentRoomV = 1,
                           # DisplayH=1,
                           # DisplayV=1)
    
  # #Populate Map
  # DinnerPlate.Map[0]  = ([  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ])
  # DinnerPlate.Map[1]  = ([  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ])
  # DinnerPlate.Map[2]  = ([  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ])
  # DinnerPlate.Map[3]  = ([  0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, ])
  # DinnerPlate.Map[4]  = ([  0, 0, 0, 1, 9, 0, 0, 0, 0, 0, 0, 5, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, ])
  # DinnerPlate.Map[5]  = ([  0, 0, 0, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 1, 0, 0, 0, ])
  # DinnerPlate.Map[6]  = ([  0, 0, 0, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 1, 0, 0, 0, ])
  # DinnerPlate.Map[7]  = ([  0, 0, 0, 1, 0, 5, 5, 0, 0, 0, 0, 0, 0, 5, 5, 0, 0, 0, 0, 0, 1, 0, 0, 0, ])
  # DinnerPlate.Map[8]  = ([  0, 0, 0, 1, 0, 5, 5, 0, 1, 1, 1, 0, 0, 5, 5, 0, 0, 0, 0, 0, 1, 0, 0, 0, ])
  # DinnerPlate.Map[9]  = ([  0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 5, 5, 0, 0, 0, 0, 0, 1, 0, 0, 0, ])
  # DinnerPlate.Map[10] = ([  0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, ])
  # DinnerPlate.Map[11] = ([  0, 0, 0, 1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, ])
  # DinnerPlate.Map[12] = ([  0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, ])
  # DinnerPlate.Map[13] = ([  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ])
  # DinnerPlate.Map[14] = ([  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ])
  # DinnerPlate.Map[15] = ([  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ])
  # Viruses    = DinnerPlate.CopyMapToPlayfield()
  # VirusCount = len(Viruses)

  DinnerPlate = VirusWorld(name='TestBanner',
                           width        = 24,
                           height       = 32,
                           Map          = [[]],
                           Playfield    = [[]],
                           CurrentRoomH = 1,
                           CurrentRoomV = 1,
                           DisplayH=1,
                           DisplayV=1)

  #Populate Map
  #                         0                    7  8                   15 16                   23
  DinnerPlate.Map[0]  = ([  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ])
  DinnerPlate.Map[1]  = ([  1, 1, 1, 3, 3, 1, 1, 3, 0, 0, 1, 1, 3, 3, 1, 1, 3, 3, 1, 1, 3, 3, 1, 1, ])
  DinnerPlate.Map[2]  = ([  1, 1, 4, 4, 4, 4, 4, 1, 0, 0, 1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, ])
  DinnerPlate.Map[3]  = ([  1, 1, 4, 0, 0, 4, 4, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 7, 7, 4, 3, ])
  DinnerPlate.Map[4]  = ([  1, 1, 4, 5, 5, 5, 5, 0, 4, 4, 4, 4, 4, 5, 5, 4, 4, 4, 4, 4, 7, 7, 4, 3, ])
  DinnerPlate.Map[5]  = ([  1, 1, 4, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 1, ])
  DinnerPlate.Map[6]  = ([  1, 1, 4, 4, 4, 4, 4, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, ])
  DinnerPlate.Map[7]  = ([  1, 1, 4, 4, 4, 4, 4, 1, 0, 0, 1, 4, 4, 4, 4, 4, 4, 4, 1, 4, 4, 1, 4, 3, ])
  DinnerPlate.Map[8]  = ([  1, 1, 1, 1, 4, 4, 1, 3, 0, 0, 1, 1, 3, 3, 1, 1, 1, 3, 1, 4, 4, 1, 1, 3, ])
  DinnerPlate.Map[9]  = ([  1, 3, 4, 1, 4, 4, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 4, 4, 1, 3, 1, ])
  DinnerPlate.Map[10] = ([  1, 3, 4, 1, 4, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, ])
  DinnerPlate.Map[11] = ([  1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,11,16, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, ])
  DinnerPlate.Map[12] = ([  1, 1, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0,12,15, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, ])
  DinnerPlate.Map[13] = ([  1, 3, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0,13,14, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, ])
  DinnerPlate.Map[14] = ([  1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, ])
  DinnerPlate.Map[15] = ([  1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, ])
  DinnerPlate.Map[16] = ([  1, 1, 1, 3, 3, 1, 1, 3, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 3, 3, 1, 3, 3, ])
  DinnerPlate.Map[17] = ([  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ])
  DinnerPlate.Map[18] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ])
  DinnerPlate.Map[19] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, ])
  DinnerPlate.Map[20] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, ])
  DinnerPlate.Map[21] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ])
  DinnerPlate.Map[22] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ])
  DinnerPlate.Map[23] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, ])
  DinnerPlate.Map[24] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, ])
  DinnerPlate.Map[25] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ])
  DinnerPlate.Map[26] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ])
  DinnerPlate.Map[27] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, ])
  DinnerPlate.Map[28] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, ])
  DinnerPlate.Map[29] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ])
  DinnerPlate.Map[30] = ([  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ])
  DinnerPlate.Map[31] = ([  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ])
  Viruses    = DinnerPlate.CopyMapToPlayfield()
  VirusCount = len(Viruses)




  ShowScrollingBanner("Outbreak!",SDLowYellowR,SDLowYellowG,SDLowYellowB,ScrollSleep *0.8)



  
  while (finished == "N" and moves < 50000):
    moves = moves + 1

    #--------------------------------
    #Check for keyboard input      --
    #--------------------------------
    #If we do this too often, the terminal window (if using telnet) will flicker
    m,r = divmod(moves,KeyboardSpeed)
    if (r == 0):
      Key = PollKeyboard()
      if (Key == 'q'):
        LevelFinished = 'Y'
        Finished      = 'Y'
        return

      #print ("moves CameraH, CameraV",moves,CameraH,CameraV,"                           ",end="\r")      


    

    #--------------------------------
    #-- Virus actions              --
    #--------------------------------

    firstname = Viruses[0].name
    
    
    
    #It seems that Python determines the "VirusCount-1" value once, and does not re-evaluate.  When some of the virises die, 
    #this thorws off the loop and counts.  I will deal with this internally.
    #for x in range (0,VirusCount-1):

    #Changed the for loop to a while loop
    x = 0
    while (x < VirusCount):
      VirusDeleted = 0


      #print ("Looping x VirusCount: ",x,VirusCount)
      #-------------------------
      #-- Check for dominance --  
      #-------------------------

      #If all viruses are the same, display the mutation
      #FlashDot(Viruses[x].h-1,Viruses[x].v-1,0.01)
      #print ("VirusName[x] speed: ",x,Viruses[x].name, Viruses[x].speed)
      #print ("VirusCount x:",VirusCount,x )
      if (Viruses[x].name <> firstname):
        nextname = Viruses[x].name

      
      #----------------------
      #-- Movement         --  
      #----------------------
      #print ("Speed:",Viruses[x].speed)
      m,r = divmod(moves,Viruses[x].speed)
      if (r == 0):
        #print ("Virus name alive x:",Viruses[x].name,Viruses[x].alive,x)
        if (Viruses[x].alive == 1):
          MoveVirus(Viruses[x],DinnerPlate.Playfield)
        else:
          print ("*** Removing virus from the list: ",x)
          del Viruses[x]
          VirusCount = VirusCount -1
          #print ("VirusCount:",VirusCount)
          VirusDeleted = 1
          
  
      if (VirusDeleted == 0):
        #----------------------
        #-- Replication      --  
        #----------------------
        if (random.randint(0,Viruses[x].replicationrate) == 1):
          
          Virus = ReplicateVirus(Viruses[x],DinnerPlate)
          if (Virus.name <> "EmptyObject"):
            print("Virus replicated")
            Viruses.append(Virus)
            VirusCount = len(Viruses)

      #End while loop
      x = x + 1
      
      



    #----------------------------
    #-- Scroll Display Window  --  
    #----------------------------
    m,r = divmod(moves,CameraSpeed)
    if (r == 0):
      PathPosition = PathPosition + 1
      if (PathPosition == PathCount):
        PathPosition = 0
      CameraH, CameraV, CameraSpeed =  CameraPath[PathPosition]
     
      #print ("PathPosition CameraH CameraV:",PathPosition,CameraH,CameraV)
      
      VirusesInWindow = DinnerPlate.CountVirusesInWindow(CameraH, CameraV)
      #print ("VirusesInWindow: ",VirusesInWindow)
      if ( VirusesInWindow == 0):
        #print ("No viruses in the window, scrolling past")
        CameraSpeed = ScrollSpeedShort
   



 
   #if (firstname == nextname):
    #  unicorn.off()
      #ShowScrollingBanner("Mutation # " ,SDLowYellowR, SDLowYellowG,SDLowYellowB,ScrollSleep * 0.8)
      #ShowScrollingBanner(firstname,SDLowGreenR, SDLowGreenG,SDLowGreenB,ScrollSleep)
    #  nextname = ""
   
    #print ("moves CameraH, CameraV",moves,CameraH,CameraV,"                           ",end="\r")      
    #time.sleep(MainSleep * 0.15)    
    DinnerPlate.DisplayWindow(CameraH, CameraV)

    #Display animation and clock every X seconds
    if (CheckElapsedTime(CheckTime) == 1):
      ScrollScreenShowTime('up',ScrollSleep)         
   
    #End game if all viruses dead
    VirusCount = len(Viruses)
    if (VirusCount == 0):
      finished = "Y"


  unicorn.off()
  
  ShowScrollingBanner("Infection Cured!",SDLowYellowR,SDLowYellowG,SDLowYellowB,ScrollSleep *0.8)
  ShowScrollingBanner("Score: " + str(moves) ,SDLowGreenR,SDLowGreenG,SDLowGreenB,ScrollSleep *0.8)
  unicorn.off()
  return





  
#------------------------------------------------------------------------------
# R E T R O   C L O C K                                                      --
#------------------------------------------------------------------------------




  
#--------------------------------------
# M A I N   P R O C E S S I N G      --
#--------------------------------------


NumDots = randint(MinDots,MaxDots)





TheRandomMessage = random_message('IntroMessages.txt')

print ("--------------------------------------")
print ("WELCOME TO THE ARCADE RETRO CLOCK")
print ("")
print ("BY DATAGOD")
print ("--------------------------------------")
print ("")
print ("")


print(TheRandomMessage)
ShowScrollingBanner(TheRandomMessage,SDLowYellowR,SDLowYellowG,SDLowYellowB,ScrollSleep *0.8)


#ShowLongIntro(ScrollSleep * 0.8)






# Check for time, show clock, or play games
while (1==1):
  now = datetime.now()
  hh  = now.hour
  print ("--CurrentTime--")
  print ("",now, hh)
  print ("TinyClockStartHH TinyClockHours",TinyClockStartHH,TinyClockHours)

#  if (hh >= TinyClockStartHH and hh <= 24):
#    DrawTinyClock(TinyClockHours*60)

  PlayPacDot(NumDots)
  PlayVirusWorld()
  PlayDotInvaders()
  PlayDotZerk()
  PlaySpaceDot()
  PlayWormDot()
  PlayLightDot()
  PlayRallyDot()



