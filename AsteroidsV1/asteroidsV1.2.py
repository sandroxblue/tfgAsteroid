#Tercera versión de Asteroids V1. Tiene todas las mismas mecánicas que en la primera versión pero se le ha añadido el lídar y las balas son más grandes.
#Además, es posible pasar de un lado a otro del mapa atravesando los bordes.

import pygame
import random
import math
import numpy as np
from math3d import *

pygame.init()
pygame.font.init()

WIDTH = 800
HEIGHT = 600
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
MAXDIST = 300
RADS = math.radians(45)
NUM = 1/9

bg = pygame.image.load('sprites/fondo.png')
barricada = pygame.image.load('sprites/barricada.png')
my_font = pygame.font.SysFont('Comic Sans MS',30)

pygame.display.set_caption('Asteroids')
screen = pygame.display.set_mode([WIDTH,HEIGHT])

clock = pygame.time.Clock()

gameover = False

class Player(pygame.sprite.Sprite):
    def __init__(self,number):
        super().__init__()
        self.number = number
        self.img = pygame.image.load("sprites/nave" + self.number + ".png")
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        if number == '1':
            self.x = 50
            self.y = 50
            self.angle = 225
            self.dir = vec2(1,1) 
        elif number == '2':
            self.x = WIDTH - 50
            self.y = 50
            self.angle = 135
            self.dir = vec2(-1,1)
        elif number == '3':
            self.x = 50
            self.y = HEIGHT - 50
            self.angle = 315
            self.dir = vec2(1,-1)
        elif number == '4':
            self.x = WIDTH -50
            self.y = HEIGHT - 50
            self.angle = 45
            self.dir = vec2(-1,-1)
        self.surface = pygame.transform.rotozoom(self.img, self.angle, 1)
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)
        self.cabeza = vec2(self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)
        self.face = vec2(self.rect.centerx,self.rect.centery)
        self.Q = self.face + self.dir * 30
        self.Q = orbit(self.Q, self.face, 0)
        self.Q -= self.face
        self.dir = normalize(self.Q)
        self.lidar = self.actualizarLidar()

    def draw(self, screen):
        screen.blit(self.surface, self.rect)
        #self.radar.surface.set_alpha(100)
        #screen.blit(self.radar.surface,self.radar.rect)

        # Rotate facing direction
        #self.Q = self.face + self.dir * 30
        #self.Q = orbit(Q, self.face, (math.pi / 4) * 0.01)
        #self.Q -= self.face
        #self.dir = normalize(Q)
        

        # Draw geometry
        self.Q = self.face + self.dir * MAXDIST
        
        for i in self.lidar:
            pygame.draw.line(screen, WHITE, pgConvert(self.face), pgConvert(i))

        #wpygame.draw.circle(screen, WHITE, pgConvert(self.cabeza), 4)

    def actualizarLidar(self):
        lidar = []

        for i in range(0,7,1):
            lidar.append(orbit(self.Q, self, RADS / 2 - i * RADS/14))
        
        lidar.append(self.face + self.dir * MAXDIST)
        
        for i in range(6,-1,-1):
            lidar.append(orbit(self.Q, self, -RADS / 2 + i * RADS/14))
        
        return lidar

    def turnLeft(self):
        self.angle += 5
        self.surface = pygame.transform.rotozoom(self.img, self.angle, 1)
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)
        self.cabeza = vec2(self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)
        self.face = vec2(self.rect.centerx,self.rect.centery)
        self.Q = self.face + self.dir * 30
        self.Q = orbit(self.Q, self.face, (math.pi / 4) * -NUM)
        self.Q -= self.face
        self.dir = normalize(self.Q)
        self.actualizarLidar()

    def turnRight(self):
        self.angle -= 5
        self.surface = pygame.transform.rotozoom(self.img, self.angle, 1)
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)
        self.cabeza = vec2(self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)
        self.face = vec2(self.rect.centerx,self.rect.centery)
        self.Q = self.face + self.dir * 30
        self.Q = orbit(self.Q, self.face, (math.pi / 4) * NUM)
        self.Q -= self.face
        self.dir = normalize(self.Q)
        self.actualizarLidar()

    def moveForward(self):
        self.x += self.cosine 
        self.y -= self.sine 
        self.surface = pygame.transform.rotozoom(self.img, self.angle, 1)
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)
        self.cabeza = vec2(self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)
        self.face = vec2(self.rect.centerx,self.rect.centery)
        self.actualizarLidar()

    def shoot(self):
        bullet = Bullet(self)
        return bullet

    def checkOffScreen(self):
        if self.x > WIDTH + self.w or self.x < 0 - self.w or self.y > HEIGHT + self.h or self.y < 0 - self.h:
            return True
        else:
            return False
    
    def checkRadar(self,players,asteroids,bullets,barricades):
        self.lidar = self.actualizarLidar()
        detectados = []
        j = 0
        for i in self.lidar:
            j += 1
            encontradoFin = ""
            distanciaFin = 500
            x0, y0 = self.face
            x1, y1 = i
            for p in players:
                if self.number != p.number:
                    pt1x, pt1y = (p.rect.centerx + p.w/2, p.rect.centery + p.h/2)
                    pt2x, pt2y = (p.rect.centerx - p.w/2, p.rect.centery + p.h/2)
                    pt3x, pt3y = (p.rect.centerx - p.w/2, p.rect.centery - p.h/2)
                    pt4x, pt4y = (p.rect.centerx + p.w/2, p.rect.centery - p.h/2)
                    if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                        distancia = math.sqrt((x0 - (pt1x+pt3x)/2)**2 + (y0 - (pt1y+pt3y)/2)**2)
                        if distancia < distanciaFin:
                            encontradoFin = "player"
                            distanciaFin = distancia
            for a in asteroids:
                pt1x, pt1y = (a.x, a.y)
                pt2x, pt2y = (a.x + a.w, a.y)
                pt3x, pt3y = (a.x + a.w, a.y + a.h)
                pt4x, pt4y = (a.x, a.y + a.h)
                if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                    distancia = math.sqrt((x0 - (pt1x+pt3x)/2)**2 + (y0 - (pt1y+pt3y)/2)**2)
                    if distancia < distanciaFin:
                        encontradoFin = "asteroide"
                        distanciaFin = distancia
            for b in bullets:
                if b.number != self.number:
                    pt1x, pt1y = (b.x, b.y)
                    pt2x, pt2y = (b.x + b.w, b.y)
                    pt3x, pt3y = (b.x + b.w, b.y + b.h)
                    pt4x, pt4y = (b.x, b.y + b.h)
                    if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                        distancia = math.sqrt((x0 - (pt1x+pt3x)/2)**2 + (y0 - (pt1y+pt3y)/2)**2)
                        if distancia < distanciaFin:
                            encontradoFin = "bala"
                            distanciaFin = distancia
            for r in barricades:
                pt1x, pt1y = (r.x, r.y)
                pt2x, pt2y = (r.x + r.w, r.y)
                pt3x, pt3y = (r.x + r.w, r.y + r.h)
                pt4x, pt4y = (r.x, r.y + r.h)
                if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                    distancia = math.sqrt((x0 - (pt1x+pt3x)/2)**2 + (y0 - (pt1y+pt3y)/2)**2)
                    if distancia < distanciaFin:
                        encontradoFin = "barricada"
                        distanciaFin = distancia
            detectados.append((encontradoFin,distanciaFin))
            if encontradoFin != "" :
                print(f"El jugador {self.number} ha detectado un/a {encontradoFin} con el rayo {j}")



# Simple helper function to comply with Pygame's drawing protocol
def pgConvert(v: vec2) -> tuple:
    return (int(v.x), int(v.y))

# Orbits v around w, returning a new instance
def orbit(v, w, angle=math.pi / 4):
    s = math.sin(angle)
    c = math.cos(angle)

    Q = +v
    Q.x -= w.x
    Q.y -= w.y

    newx = Q.x * c - Q.y * s
    newy = Q.x * s + Q.y * c

    Q.x = newx + w.x
    Q.y = newy + w.y

    return Q

def isInTriangle(player,p):
    l = player.vRotatedRect.left
    t = player.vRotatedRect.top
    p1 = np.array([l,t])
    p2 = np.array([l+player.vW,t])
    p3 = np.array([l+player.vW//2,t-player.vH])
    if sameSide(p,p1, p2,p3) and sameSide(p,p2, p1,p3) and sameSide(p,p3, p1,p2):
        return True
    else:
         return False

def sameSide(p1,p2,a,b):
    cp1 = np.dot(b-a, p1-a)
    cp2 = np.dot(b-a, p2-a)
    if cp1 * cp2 >= 0:
        return True
    else:
         return False

# function SameSide(p1,p2, a,b)
#     cp1 = CrossProduct(b-a, p1-a)
#     cp2 = CrossProduct(b-a, p2-a)
#     if DotProduct(cp1, cp2) >= 0 then return true
#     else return false

# function PointInTriangle(p, a,b,c)
#     if SameSide(p,a, b,c) and SameSide(p,b, a,c)
#         and SameSide(p,c, a,b) then return true
#     else return false


 
class Bullet(object):
    def __init__(self,player):
        self.point = player.head
        self.x, self.y = self.point
        self.w = 7
        self.h = 7
        self.c = player.cosine
        self.s = player.sine
        self.xv = self.c * 10
        self.yv = self.s * 10
        self.number = player.number
    
    def move(self):
        self.x += self.xv
        self.y -= self.yv

    def draw(self, screen):
        pygame.draw.rect(screen, (255,255,255), [self.x, self.y, self.w, self.h])

    def checkOffScreen(self):
        if (self.x < -10) or (self.x > WIDTH + 10) or (self.y < -10) or (self.y > HEIGHT + 10):
             return True
        else:
            return False


class Asteroid(object):
    def __init__(self,rank):
        self.img = pygame.image.load("sprites/meteorito" + str(rank) + ".png")
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.spawnPoint = random.choice([(random.randrange(0,WIDTH-self.w),random.choice([-1 * self.h - 5, HEIGHT + 5])),(random.choice([-1 * self.w - 5, WIDTH + 5]), random.randrange(0,HEIGHT - self.h))])
        self.x, self.y = self.spawnPoint
        if self.x < WIDTH//2:
            self.xdir = 1
        else:
            self.xdir = -1
        if self.y < HEIGHT//2:
            self.ydir = 1
        else:
            self.ydir = -1

        self.xv = self.xdir * random.randrange(1,3)
        self.yv = self.ydir * random.randrange(1,3)
    
    def move(self):
        self.x += self.xv
        self.y += self.yv

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def checkOffScreen(self):
        if (self.x < -self.w and self.xdir == -1) or (self.x > WIDTH + self.w and self.xdir == 1) or (self.y < - self.h and self.ydir == -1) or (self.y > HEIGHT + self.h and self.ydir == 1):
            return True
        else:
            return False


class Barricade(object):
    def __init__(self, option):

        self.img = pygame.image.load("sprites/barricada.png")
        self.w = self.img.get_width()
        self.h = self.img.get_height()

        if option == 1:
            self.x = self.w 
            self.y = HEIGHT//2 
        elif option == 2:
            self.x = WIDTH//2
            self.y = self.h
        elif option == 3:
            self.x = WIDTH//2
            self.y = HEIGHT - self.h
        elif option == 4:
            self.x = WIDTH - self.w
            self.y = HEIGHT//2
        else:
            self.x = WIDTH//2 
            self.y = HEIGHT//2 
        self.x -= self.w//2
        self.y -= self.h//2
        self.rect = pygame.Rect(self.x,self.y,self.w,self.h)
    def draw(self, screen):
        screen.blit(self.img, self.rect)

def lineRect(x1, y1, x2, y2, rx1, ry1, rx2, ry2, rx3, ry3, rx4, ry4):

  # check if the line has hit any of the rectangle's sides
  # uses the Line/Line function below
    left =   lineLine(x1,y1,x2,y2, rx1,ry1,rx2,ry2)
    right =  lineLine(x1,y1,x2,y2, rx2,ry2,rx3,ry3)
    top =    lineLine(x1,y1,x2,y2, rx3,ry3,rx4,ry4)
    bottom = lineLine(x1,y1,x2,y2, rx4,ry4,rx1,ry1)
  # if ANY of the above are true, the line
  # has hit the rectangle
    if left or right or top or bottom:
        return True
    else:
        return False



def lineLine(x1, y1, x2, y2, x3, y3, x4, y4):
    # calculate the direction of the lines
    if ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)) != 0:
        uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))

        # if uA and uB are between 0-1, lines are colliding
        if uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1 :
            return True
    return False


def redrawGameScreen(): 
    gameover = False
    screen.blit(bg, (0,0))
    for p in playersAlive:
        p.draw(screen)
    for b in playerBullets:
        b.draw(screen)
    for a in asteroids:
        a.draw(screen)
    for b in barricades:
        b.draw(screen)
    if len(playersAlive) < 2:
        gameover = True
        if len(playersAlive) == 1:
            text = my_font.render(f'Ha ganado el jugador {playersAlive[0].number}',False,WHITE)
        if len(playersAlive) == 0:
            text = my_font.render(f'Empate!',False,WHITE)
        screen.blit(text,(WIDTH//2  - 150,50))
    pygame.display.update() 
    return gameover

player1 = Player('1')
player2 = Player('2')
player3 = Player('3')
player4 = Player('4')

players = [player1, player2, player3, player4]
playersAlive = [player1, player2, player3, player4]
deadPlayers = []

playerBullets = []

asteroids = []
maxAsteroids = 10
count = 1
ticksForAsteroid = 50

barricades = []
nBarricades= random.choice([0,1,2,3])
initBarricades = random.choices([[1,4],[2,3],[5]],k=nBarricades)
for i in initBarricades:
    for j in i:
        barricades.append(Barricade(j))


run = True

while run:
    if not gameover:

        clock.tick(60)
        #HAce que aparezcan asteroides:
        count += 1

        if count % ticksForAsteroid == 0:
            if len(asteroids) < maxAsteroids:
                ran = random.choice([1,1,1,1,2,2,3])
                asteroids.append(Asteroid(ran))


        for p in playersAlive:
            p.checkRadar(playersAlive,asteroids,playerBullets,barricades)
            if p.x < 0:
                p.x = WIDTH
            if p.x > WIDTH + p.w:
                p.x = 0
            if p.y < 0:
                p.y = HEIGHT
            if p.y > HEIGHT:
                p.y = 0

            
            for b in playerBullets:
                if b.x >= p.x and b.x <= p.x + p.w or b.x + b.w >= p.x and b.x + b.w <= p.x + p.w:
                    if b.y >= p.y and b.y <= p.y + p.h or b.y + b.h >= p.y and b.y + b.h <= p.y + p.h:
                        if b.number != p.number:
                            deadPlayers.append(p)
                            playersAlive.pop(playersAlive.index(p))
                            playerBullets.pop(playerBullets.index(b))

            for a in asteroids:
                if p.x >= a.x and p.x <= a.x + a.w or p.x + p.w >= a.x and p.x + p.w <= a.x + a.w:
                    if p.y >= a.y and p.y <= a.y + a.h or p.y + p.h >= a.y and p.y + p.h <= a.y + a.h:
                        deadPlayers.append(p)
                        playersAlive.pop(playersAlive.index(p))
            
            

        for b in playerBullets:
            b.move()
            if b.checkOffScreen():
                playerBullets.pop(playerBullets.index(b))
        
        for a in asteroids:
            a.move()
            if a.checkOffScreen():
                asteroids.pop(asteroids.index(a))
            
            for b in playerBullets:                                                             
                if b.x >= a.x and b.x <= a.x + a.w or b.x + b.w >= a.x and b.x + b.w <= a.x + a.w:
                    if b.y >= a.y and b.y <= a.y + a.h or b.y + b.h >= a.y and b.y + b.h <= a.y + a.h:
                        asteroids.pop(asteroids.index(a))
                        playerBullets.pop(playerBullets.index(b))
            
        for cc in barricades:
            
            for b in playerBullets:
                if b.x >= cc.x and b.x <= cc.x + cc.w or b.x + b.w >= cc.x and b.x + b.w <= cc.x + cc.w:
                    if b.y >= cc.y and b.y <= cc.y + cc.h or b.y + b.h >= cc.y and b.y + b.h <= cc.y + cc.h:
                        playerBullets.pop(playerBullets.index(b))

            for p in playersAlive:
                if p.x >= cc.x and p.x <= cc.x + cc.w or p.x + p.w >= cc.x and p.x + p.w <= cc.x + cc.w:
                    if p.y >= cc.y and p.y <= cc.y + cc.h or p.y + p.h >= cc.y and p.y + p.h <= cc.y + cc.h:
                        deadPlayers.append(p)
                        playersAlive.pop(playersAlive.index(p))

            for a in asteroids:
                if a.x >= cc.x and a.x <= cc.x + cc.w or a.x + a.w >= cc.x and a.x + a.w <= cc.x + cc.w:
                    if a.y >= cc.y and a.y <= cc.y + cc.h or a.y + a.h >= cc.y and a.y + a.h <= cc.y + cc.h:
                        asteroids.pop(asteroids.index(a))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            playersAlive[3].turnLeft()
        if keys[pygame.K_RIGHT]:
            playersAlive[3].turnRight()
        if keys[pygame.K_UP]:
            playersAlive[3].moveForward()
        if keys[pygame.K_j]:
            playersAlive[2].turnLeft()
        if keys[pygame.K_l]:
            playersAlive[2].turnRight()
        if keys[pygame.K_i]:
            playersAlive[2].moveForward()
        if keys[pygame.K_f]:
            playersAlive[1].turnLeft()
        if keys[pygame.K_h]:
            playersAlive[1].turnRight()
        if keys[pygame.K_t]:
            playersAlive[1].moveForward()
        if keys[pygame.K_a]:
            playersAlive[0].turnLeft()
        if keys[pygame.K_d]:
            playersAlive[0].turnRight()
        if keys[pygame.K_w]:
            playersAlive[0].moveForward()
        
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if not gameover:
                        playerBullets.append(playersAlive[0].shoot())
                if event.key == pygame.K_y:
                    if not gameover:
                        playerBullets.append(playersAlive[1].shoot())
                if event.key == pygame.K_o:
                    if not gameover:
                        playerBullets.append(playersAlive[2].shoot())
                if event.key == pygame.K_RSHIFT:
                    if not gameover:
                        playerBullets.append(playersAlive[3].shoot())
        
    
        gameover = redrawGameScreen()
    
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

pygame.quit()

