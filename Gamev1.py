# WS 320x240 display example
from machine import Pin,SPI,PWM
import framebuf
import utime
import math
import random

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

class LCD_1inch3(framebuf.FrameBuffer): # For 320x240 display
    def __init__(self):
        self.width = 320
        self.height = 240
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,100000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.RED   =   0x07E0
        self.GREEN =   0x001f
        self.BLUE  =   0xf800
        self.WHITE =   0xffff
        self.BALCK =   0x0000
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x3f)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xEF)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
        
class Player():
    def __init__(self,xpos,ypos, width, height):
        #self.collidable = True
        #self.damageable = True
        self.bounce = False
        #self.HP = 10
        self.colour = (50,50,200)
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        self.f_vel = [0.0,0.0]
        self.vel = [0,0]
    def clone(self):
        return(Player(self.xpos, self.ypos, self.width, self.height))
    #moves in x direction
        
    def checkCollisionL(self, colis_obj):
        lside_x_same = self.xpos == colis_obj.xpos+colis_obj.width
        side_y_same = (self.ypos < colis_obj.ypos+colis_obj.height) and (self.ypos+self.height > colis_obj.ypos)
        if(lside_x_same and side_y_same):
            return True
        return False
    def checkCollisionR(self, colis_obj):
        rside_x_same = self.xpos+self.width == colis_obj.xpos
        side_y_same = (self.ypos < colis_obj.ypos+colis_obj.height) and (self.ypos+self.height > colis_obj.ypos)
        if(rside_x_same and side_y_same):
            return True
        return False
    def checkCollisionT(self, colis_obj):
        bottom_x_same = (self.xpos+self.width > colis_obj.xpos) and (self.xpos < colis_obj.xpos+colis_obj.width)
        top_y_same = self.ypos == (colis_obj.ypos+colis_obj.height)
        if(bottom_x_same and top_y_same):
            return True
        return False
    def checkCollisionB(self, colis_obj):
        bottom_x_same = (self.xpos+self.width > colis_obj.xpos) and (self.xpos < colis_obj.xpos+colis_obj.width)
        bottom_y_same = (self.ypos+self.height == colis_obj.ypos)
        if(bottom_x_same and bottom_y_same):
            return True
        return False
        
    #returns maximum translation possible given a velocity before a collision occurs
    def checkCollision(self, colis_obj):
        velx = self.vel[0]
        vely = self.vel[1]
        p_clone = player.clone()
        x_translation = 0
        y_translation = 0
        if(velx >= 0):
            for i in range(velx+1):
                for obj in objects:
                    r_collision = p_clone.checkCollisionR(obj)
                    if(r_collision):
                        velx = 0
                    else:
                        p_clone.xpos = self.xpos + i
                if(velx == 0):
                    break
                x_translation = i
        else:
            for i in range(abs(velx)+1):
                for obj in objects:
                    l_collision = p_clone.checkCollisionL(obj)
                    if(l_collision):
                        velx = 0
                    else:
                        p_clone.xpos = self.xpos - i
                if(velx == 0):
                    break
                x_translation = i*-1
        if(vely >= 0):
            for i in range(vely+1):
                for obj in objects:
                    b_collision = p_clone.checkCollisionB(obj)
                    if(b_collision):
                        vely = 0
                    else:
                        p_clone.ypos = self.ypos + i
                if(vely == 0):
                    self.bounce = True
                    self.f_vel[1] = 0
                    break
                y_translation = i
        else:
            for i in range(abs(vely)+1):
                for obj in objects:
                    t_collision = p_clone.checkCollisionT(obj)
                    if(t_collision):
                        vely = 0
                    else:
                        p_clone.ypos = self.ypos - i
                if(vely == 0):
                    self.f_vel[1] = 0
                    break
                y_translation = i*-1
        return x_translation, y_translation
        
def moveX(obj, dirx, c):
    obj.xpos += dirx
    #left side with black
    LCD.fill_rect(obj.xpos-dirx,obj.ypos,dirx,obj.height,colour(0,0,0))
    #right side with black
    LCD.fill_rect(obj.xpos+obj.width,obj.ypos,-dirx,obj.height,colour(0,0,0))
#moves in y direction
def moveY(obj, diry, c):
    obj.ypos += diry
    #fill top with black
    LCD.fill_rect(obj.xpos,obj.ypos-diry,obj.width,diry,colour(0,0,0))
    #bottom with black
    LCD.fill_rect(obj.xpos,obj.ypos+obj.height,obj.width,-diry,colour(0,0,0))
    
def move(obj, translation, c):
    moveX(obj, translation[0], c)
    moveY(obj, translation[1], c)
    LCD.fill_rect(obj.xpos,obj.ypos,obj.width,obj.height,colour(c[0],c[1],c[2]))
    
class CollisionObject():
    def __init__(self,xpos,ypos,width,height):
        #self.collidable = True
        #self.damageable = False
        self.colour = (50,50,100)
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        LCD.fill_rect(xpos,ypos,width,height,colour(self.colour[0],self.colour[1],self.colour[2]))
        
def colour(R,G,B):
    mix1 = ((R&0xF8)*256) + ((G&0xFC)*8) + ((B&0xF8)>>3)
    return  (mix1 & 0xFF) *256  + int((mix1 & 0xFF00) /256)

pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(32768)#max 65535

LCD = LCD_1inch3()
LCD.fill(LCD.WHITE)
LCD.show()
LCD.fill(0)

#set up buttons
key0 = Pin(15,Pin.IN,Pin.PULL_UP)
key1 = Pin(17,Pin.IN,Pin.PULL_UP)
key2 = Pin(2 ,Pin.IN,Pin.PULL_UP)
key3= Pin(3 ,Pin.IN,Pin.PULL_UP)

#moves player and checks for collisions
def translate(player, objects_array):
    translation = player.checkCollision(objects_array)
    if(player.bounce):
        player.f_vel[1] = -6
        player.bounce = False
    move(player, translation, player.colour)
    
#creates a collision object of random size in a random location
def randomObject():
    y_coor = random.randint(30, 210)
    width = random.randint(40, 160)
    height = random.randint(5, 40)
    next_dist = random.randint(20+width, 80+width)
    return CollisionObject(320, y_coor, width, height), next_dist
    
def inRange(objects_array):
    max_x = 0
    for i in objects_array:
        if i.xpos > max_x:
            max_x = i.xpos
    return max_x

def move_world(objects_array):
    for i in objects_array:
        move(i, [-2,0], i.colour)
        #remove object if it has left screen
        if i.xpos + i.width < 0:
            objects_array.remove(i)
    
#init objects and variables
random.seed()
gravity = 0.18
terminal_vel = 4
player = Player(40,100,25,25)
obj1 = CollisionObject(30, 190, 100, 20)
objects = [obj1]
vel = 2
done = False
next_dist = 0
#main loop
while(not done):
    s_time = utime.ticks_us()
    move_world(objects)
    if(player.f_vel[1] % 1 == 0):
        if(player.vel[1] < terminal_vel or player.f_vel[1] < terminal_vel):
            player.vel[1] = int(player.f_vel[1])
    player.f_vel[1] += gravity
    if(player.vel[1] < terminal_vel):
        player.vel[1] += gravity
    if(key1.value() == 0):
        player.vel[0] = vel
    elif(key0.value() == 0):
        player.vel[0] = vel *-1
    else:
        player.vel[0] = 0
    translate(player, objects)
    if(320- inRange(objects) > next_dist):
        new_obj, next_dist = randomObject()
        objects.append(new_obj)
    #time loop took in micro-seconds (10^-6seconds)
    if(240-player.ypos < 0):
        done = True
    t_taken = utime.ticks_diff(utime.ticks_us(), s_time)
    LCD.show()
    utime.sleep_ms(int(1000/50 -t_taken/1000))

LCD.text("Game Over",40,60,colour(255,0,0))
LCD.show()
