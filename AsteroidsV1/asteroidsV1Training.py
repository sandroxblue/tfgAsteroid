#Cuarta versión de Asteroids V1. Es la versión adaptada para el uso de agentes inteligentes.

import pygame
import random
import math
import numpy as np
import intersections
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
RADS = math.radians(360)
NUM = 1/9
SPEED = 20
RECHARGE_TIME = 50

gameover = False

barricada = pygame.image.load('sprites/barricada.png')
my_font = pygame.font.SysFont('Comic Sans MS',30)

# reset
# reward
# play(action)
# game_iteration
# is_collision

class Player(pygame.sprite.Sprite):
    def __init__(self,number):
        super().__init__()
        self.number = number
        self.img = pygame.image.load("sprites/nave" + str(self.number + 1) + ".png")
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        if number == 0:
            self.x = 250
            self.y = 200
            self.angle = 225
            self.dir = vec2(1,1) 
        elif number == 1:
            self.x = WIDTH - 250
            self.y = 200
            self.angle = 135
            self.dir = vec2(-1,1)
        elif number == 2:
            self.x = 250
            self.y = HEIGHT - 200
            self.angle = 315
            self.dir = vec2(1,-1)
        elif number == 3:
            self.x = WIDTH -250
            self.y = HEIGHT - 200
            self.angle = 45
            self.dir = vec2(-1,-1)
        self.surface = pygame.transform.rotozoom(self.img, self.angle, 1)
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)
        self.centroRadar = vec2(self.rect.centerx,self.rect.centery)
        self.Q = self.centroRadar + self.dir * 30
        self.Q = orbit(self.Q, self.centroRadar, 0)
        self.Q -= self.centroRadar
        self.dir = normalize(self.Q)
        self.lidar = self.actualizarLidar()
        self.last_shoot = -RECHARGE_TIME
        self.alive = True

    def draw(self, screen):
        screen.blit(self.surface, self.rect)
        self.Q = self.centroRadar + self.dir * MAXDIST
        #for i in self.lidar:
        #    pygame.draw.line(screen, WHITE, pgConvert(self.centroRadar), pgConvert(i))

    def actualizarLidar(self):
        lidar = []

        for i in range(0,7,1):
            lidar.append(orbit(self.Q, self, RADS / 2 - i * RADS/14))
        
        lidar.append(self.centroRadar + self.dir * MAXDIST)
        
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
        self.centroRadar = vec2(self.rect.centerx,self.rect.centery)
        self.Q = self.centroRadar + self.dir * 30
        self.Q = orbit(self.Q, self.centroRadar, (math.pi / 4) * -NUM)
        self.Q -= self.centroRadar
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
        self.centroRadar = vec2(self.rect.centerx,self.rect.centery)
        self.Q = self.centroRadar + self.dir * 30
        self.Q = orbit(self.Q, self.centroRadar, (math.pi / 4) * NUM)
        self.Q -= self.centroRadar
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
        self.centroRadar = vec2(self.rect.centerx,self.rect.centery)
        self.actualizarLidar()

    def shoot(self, actual_shoot):
        if actual_shoot - self.last_shoot > RECHARGE_TIME:
            bullet = Bullet(self)
            self.last_shoot = actual_shoot
            return (True, bullet)
        else:
            return (False, None)

    def move(self, action, playerBullets, time):
        ##[nada, recto, izq, der, disparar]
        if np.array_equal(action, [1,0,0,0,0]):
            return 0
        elif np.array_equal(action, [0,1,0,0,0]):
            self.moveForward()
            return 1
        elif np.array_equal(action, [0,0,1,0,0]):
            self.turnLeft()
            return 0.5
        elif np.array_equal(action, [0,0,0,1,0]):
            self.turnRight()
            return 0.5
        else:
            disparo = self.shoot(time)
            if disparo[0] == True:
                playerBullets.append(disparo[1])
                return 0.3
            else:
                return 0.1
        ##[recto, izq, der, disparar]
        # if np.array_equal(action, [1,0,0,0]):
        #     self.moveForward()
        # elif np.array_equal(action, [0,1,0,0]):
        #     self.turnLeft()
        # elif np.array_equal(action, [0,0,1,0]):
        #     self.turnRight()
        # else:
        #     disparo = self.shoot(score)
        #     if disparo[0] == True:
        #         playerBullets.append(disparo[1])
        #     else:
        #         pass

    def checkOffScreen(self):
        if self.x > WIDTH + self.w or self.x < 0 or self.y > HEIGHT + self.h or self.y < 0:
            return True
        else:
            return False
    
    #one-hot de las clases y añadir las paredes a la lista
    def checkRadar(self,players,asteroids,bullets,barricades):
        self.lidar = self.actualizarLidar()
        detectados = []
        for i in self.lidar:
            encontradoFin = [0,0,0,0,0] #[finMapa, nave, asteroide, bala, barricada]
            distanciaFin = MAXDIST
            x0, y0 = self.centroRadar
            x1, y1 = i
            distancia = checkOutOfBounds(x0,y0,x1,y1)
            if distancia < distanciaFin:
                encontradoFin = [1,0,0,0,0]
                distanciaFin = distancia
            for p in players:
                if self.number != p.number and p.alive == True:
                    pt1x, pt1y = (p.rect.centerx + p.w/2, p.rect.centery + p.h/2)
                    pt2x, pt2y = (p.rect.centerx - p.w/2, p.rect.centery + p.h/2)
                    pt3x, pt3y = (p.rect.centerx - p.w/2, p.rect.centery - p.h/2)
                    pt4x, pt4y = (p.rect.centerx + p.w/2, p.rect.centery - p.h/2)
                    if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                        distancia = calcularDistancia(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y)
                        if distancia < distanciaFin:
                            encontradoFin = [0,1,0,0,0]
                            distanciaFin = distancia
            for a in asteroids:
                pt1x, pt1y = (a.x, a.y)
                pt2x, pt2y = (a.x + a.w, a.y)
                pt3x, pt3y = (a.x + a.w, a.y + a.h)
                pt4x, pt4y = (a.x, a.y + a.h)
                if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                    distancia = calcularDistancia(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y)
                    if distancia < distanciaFin:
                        encontradoFin = [0,0,1,0,0]
                        distanciaFin = distancia
            for b in bullets:
                if b.number != self.number:
                    pt1x, pt1y = (b.x, b.y)
                    pt2x, pt2y = (b.x + b.w, b.y)
                    pt3x, pt3y = (b.x + b.w, b.y + b.h)
                    pt4x, pt4y = (b.x, b.y + b.h)
                    if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                        distancia = calcularDistancia(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y)
                        if distancia < distanciaFin:
                            encontradoFin = [0,0,0,1,0]
                            distanciaFin = distancia
            for r in barricades:
                pt1x, pt1y = (r.x, r.y)
                pt2x, pt2y = (r.x + r.w, r.y)
                pt3x, pt3y = (r.x + r.w, r.y + r.h)
                pt4x, pt4y = (r.x, r.y + r.h)
                if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                    distancia = calcularDistancia(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y)
                    if distancia < distanciaFin:
                        encontradoFin = [0,0,0,0,1]
                        distanciaFin = distancia
            for i in range(0, len(encontradoFin)):
                if encontradoFin[i] == 1:
                    encontradoFin[i] = 1 -distanciaFin/MAXDIST
            detectados.extend(encontradoFin)
        return detectados


def checkOutOfBounds(x0, y0, x1, y1):
    dist = MAXDIST
    if x1 < 0 or y1 < 0:
        a = intersections.intersectLines((x0,y0), (x1,y1), (0,0), (0,HEIGHT))
        b = intersections.intersectLines((x0,y0), (x1,y1), (0,0), (WIDTH,0))
        if x1 < 0 and y1 > 0:
            dist = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            #print(f"choco con el fin del mundo en {a[0]},{a[1]} y yo estoy en {x0},{y0}, dist total= {dist}")
        if x1 > 0 and y1 < 0:
            dist = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            #print(f"choco con el fin del mundo en {b[0]},{b[1]} y yo estoy en {x0},{y0}, dist total= {dist}")
        else:
            distA = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            distB = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            dist = min(distA, distB)
    if x1 > WIDTH or y1 > HEIGHT:
        a = intersections.intersectLines((x0,y0), (x1,y1), (0,HEIGHT), (WIDTH,HEIGHT))
        b = intersections.intersectLines((x0,y0), (x1,y1), (WIDTH,0), (WIDTH,HEIGHT))
        if x1 > WIDTH and y1 < HEIGHT:
            dist = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            #print(f"choco con el fin del mundo en {a[0]},{a[1]} y yo estoy en {x0},{y0}, dist total= {dist}")
        if x1 < WIDTH and y1 > HEIGHT:
            dist = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            #print(f"choco con el fin del mundo en {b[0]},{b[1]} y yo estoy en {x0},{y0}, dist total= {dist}")
        else:
            distA = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            distB = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            dist = min(distA, distB)
    return dist

def calcularDistancia(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
    a = intersections.intersectLines((x0,y0), (x1,y1), (pt1x,pt1y), (pt2x,pt2y))
    b = intersections.intersectLines((x0,y0), (x1,y1), (pt2x,pt2y), (pt3x,pt3y))
    c = intersections.intersectLines((x0,y0), (x1,y1), (pt3x,pt3y), (pt4x,pt4y))
    d = intersections.intersectLines((x0,y0), (x1,y1), (pt4x,pt4y), (pt1x,pt1y))
    distA = MAXDIST
    distB = MAXDIST
    distC = MAXDIST
    distD = MAXDIST
    if(a[0] > pt1x and a[0] < pt2x):
        distA = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
    if(b[1] > pt2y and b[1] < pt3y):
        distB = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
    if(c[0] < pt3x and c[0] > pt4x):
        distC = math.sqrt((x0 - c[0])**2 + (y0 - c[1])**2)
    if(d[1] < pt4y and d[1] > pt1y):
        distD = math.sqrt((x0 - d[0])**2 + (y0 - d[1])**2)
    # print(f"objeto con coordenadas {pt1x},{pt1y} {pt2x},{pt2y} {pt3x},{pt3y} {pt4x},{pt4y}")
    # print(f"choco con algo en las coords{((a[0],a[1]),(b[0],b[1]),(c[0],c[1]),(d[0],d[1]))}, yo estoy en {x0},{y0}, distancias {(distA,distB,distC,distD)}")
    return min((distA,distB,distC,distD))

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
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
    
    def move(self):
        self.x += self.xv
        self.y -= self.yv
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

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
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if self.x < WIDTH//2:
            self.xdir = 1
        else:
            self.xdir = -1
        if self.y < HEIGHT//2:
            self.ydir = 1
        else:
            self.ydir = -1

        self.xv = self.xdir * random.uniform(0.2,1.0)
        self.yv = self.ydir * random.uniform(0.1,1.0)
    
    def move(self):
        self.x += self.xv
        self.y += self.yv
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

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
    left =   lineLine(x1,y1,x2,y2, rx1,ry1,rx2,ry2)
    right =  lineLine(x1,y1,x2,y2, rx2,ry2,rx3,ry3)
    top =    lineLine(x1,y1,x2,y2, rx3,ry3,rx4,ry4)
    bottom = lineLine(x1,y1,x2,y2, rx4,ry4,rx1,ry1)
    if left or right or top or bottom:
        return True
    else:
        return False

def lineLine(x1, y1, x2, y2, x3, y3, x4, y4):
    if ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)) != 0:
        uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        if uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1 :
            return True
    return False

# def collides(a,b):
#     if a.x >= b.x and a.x <= b.x + b.w or a.x + a.w >= b.x and a.x + a.w <= b.x + b.w:
#         if a.y >= b.y and a.y <= b.y + b.h or a.y + a.h >= b.y and a.y + a.h <= b.y + b.h:
#             return True
#     return False

def collides(a,b):
    if a.rect.centerx - a.w/2 >= b.x and a.rect.centerx <= b.x + b.w or a.rect.centerx + a.w/2 >= b.x and a.rect.centerx <= b.x + b.w:
        if a.rect.centery - a.h/2 >= b.y and a.rect.centery <= b.y + b.h or a.rect.centery + a.h/2 >= b.y and a.rect.centery <= b.y + b.h:
            return True
    return False

def kill(elemento, lista):
    if elemento in lista:
        indice = lista.index(elemento)
        lista.pop(indice)

class AsteroidAI:

    def __init__(self, w= WIDTH, h=HEIGHT):
        pygame.display.set_caption('Asteroids')
        self.screen = pygame.display.set_mode((w,h))
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load('sprites/fondo.png')
        self.reset()

    def reset(self):
        self.gameovers = [False,False,False,False]
        self.time = 0
        self.player0 = Player(0)
        self.player1 = Player(1)
        self.player2 = Player(2)
        self.player3 = Player(3)
        self.players = [self.player0,self.player1,self.player2,self.player3]
        self.playerBullets = []
        self.asteroids = []
        self.maxAsteroids = 50
        self.count = 1
        self.ticksForAsteroid = 20
        self.barricades = []
        self.nBarricades= random.choice([0,1,2,3])
        self.initBarricades = random.choices([[1,4],[2,3],[5]],k=self.nBarricades)
        for i in self.initBarricades:
            for j in i:
                self.barricades.append(Barricade(j))
        self.run = True
        self.frame_iteration = 0

    def redrawGameScreen(self): 
        self.screen.blit(self.bg, (0,0))
        for p in self.players:
            if p.alive == True:
                p.draw(self.screen)
        for b in self.playerBullets:
            b.draw(self.screen)
        for a in self.asteroids:
            a.draw(self.screen)
        for b in self.barricades:   
            b.draw(self.screen)
        pygame.display.flip()

    def checkGameOver(self):
        nDead = 0
        for player in self.players:
            if player.alive != True:
                nDead += 1
                self.gameovers[player.number] = True
        if nDead == 3:
            for player in self.players:
                if player.alive == True:
                    self.rewards[player.number] += 100
        if nDead == 4 or self.frame_iteration > 300 * 1000:
            self.gameovers = [True, True, True, True]

    def play_step(self, actions):
        self.rewards = [0,0,0,0]
        self.frame_iteration += 1
        for player in self.players:
            player.checkRadar(self.players,self.asteroids,self.playerBullets,self.barricades)
            if player.alive == True:
                self.rewards[player.number] += player.move(actions[player.number], self.playerBullets,self.time)
        self.time += 1

        self.count += 1
        if self.count % self.ticksForAsteroid == 0:
            if len(self.asteroids) < self.maxAsteroids:
                ran = random.choice([1,1,1,1,1,2,2,2,3,3])
                self.asteroids.append(Asteroid(ran))

        for p in self.players:
            if (p.checkOffScreen()):
                p.alive = False
                self.rewards[p.number] += -100
            
            for b in self.playerBullets:
                if collides(b, p):
                    if p.alive == True and b.number != p.number:
                        p.alive = False
                        kill(b, self.playerBullets)
                        self.rewards[p.number] += -100
                        self.rewards[b.number] += 500

            for a in self.asteroids:
                if collides(p,a):
                    p.alive = False
                    self.rewards[p.number] += -100
            
            
        for b in self.playerBullets:
            b.move()
            if b.checkOffScreen():
                kill(b, self.playerBullets)
        
        for a in self.asteroids:
            a.move()
            if a.checkOffScreen():
                kill(a, self.asteroids)
            
            for b in self.playerBullets:
                if collides(b,a):    
                    kill(a, self.asteroids)     
                    kill(b, self.playerBullets)
                    self.rewards[p.number] += 100
            
        for cc in self.barricades:

            for b in self.playerBullets:
                if collides(b, cc):
                    kill(b, self.playerBullets)

            for p in self.players:
                if collides(p,cc):
                    p.alive = False
                    self.rewards[p.number] += -100

            for a in self.asteroids:
                if collides(a, cc):
                    kill(a, self.asteroids)


        self.checkGameOver()
        self.clock.tick(SPEED)
        self.redrawGameScreen()

        return self.rewards, self.time/25, self.gameovers

# asteroid = AsteroidAI()
# while asteroid.run: 

#     asteroid.play_step([[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]])

#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             asteroid.run = False

# pygame.quit()

