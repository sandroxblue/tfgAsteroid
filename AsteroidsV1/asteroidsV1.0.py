#Primera versión de Asteroids V1. Tiene todas las mecánicas definidas y es jugable por 4 jugadores.

import pygame 
import random
import math
import numpy as np

pygame.init()
pygame.font.init()

WIDTH = 800
HEIGHT = 600
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

bg = pygame.image.load('sprites/fondo.png')
barricada = pygame.image.load('sprites/barricada.png')
my_font = pygame.font.SysFont('Comic Sans MS',30)

pygame.display.set_caption('Asteroids')
screen = pygame.display.set_mode([WIDTH,HEIGHT])

clock = pygame.time.Clock()

gameover = False

class Player(object):
    def __init__(self,number):
        self.number = number
        self.img = pygame.image.load("sprites/nave" + self.number + ".png")
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        if number == '1':
            self.x = 50
            self.y = 50
            self.angle = 270
            # self.angle = 225
        elif number == '2':
            self.x = WIDTH - 50
            self.y = 50
            self.angle = 135
        elif number == '3':
            self.x = 50
            self.y = HEIGHT - 50
            self.angle = 315
        elif number == '4':
            self.x = WIDTH -50
            self.y = HEIGHT - 50
            self.angle = 45
        self.rotatedSurface = pygame.transform.rotozoom(self.img, self.angle, 1)
        self.rotatedRect = self.rotatedSurface.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)

    def draw(self, screen):
        screen.blit(self.rotatedSurface, self.rotatedRect)

    def turnLeft(self):
        self.angle += 5
        self.rotatedSurface = pygame.transform.rotozoom(self.img, self.angle, 1)
        self.rotatedRect = self.rotatedSurface.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)

    def turnRight(self):
        self.angle -= 5
        self.rotatedSurface = pygame.transform.rotozoom(self.img, self.angle, 1)
        self.rotatedRect = self.rotatedSurface.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)

    def moveForward(self):
        self.x += self.cosine 
        self.y -= self.sine 
        self.rotatedSurface = pygame.transform.rotozoom(self.img, self.angle, 1)
        self.rotatedRect = self.rotatedSurface.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)


    def shoot(self):
        bullet = Bullet(self)
        return bullet

    def checkOffScreen(self):
        if self.x > WIDTH + self.w or self.x < 0 - self.w or self.y > HEIGHT + self.h or self.y < 0 - self.h:
            return True
        else:
            return False
    


 
class Bullet(object):
    def __init__(self,player):
        self.point = player.head
        self.x, self.y = self.point
        self.w = 4
        self.h = 4
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


def redrawGameScreen():
    gameover = False
    screen.blit(bg, (0,0))
    ganador = 0
    for p in playersAlive:
        if p not in deadPlayers:
            ganador = p.number
            p.draw(screen)
    for b in playerBullets:
        b.draw(screen)
    for a in asteroids:
        a.draw(screen)
    for b in barricades:
        b.draw(screen)
    if len(deadPlayers) >= 3:
        gameover = True
        if len(deadPlayers) == 3:
            text = my_font.render(f'Ha ganado el jugador {ganador}',False,WHITE)
        if len(deadPlayers) == 0:
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
count = 0
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
        count += 1

        if count % ticksForAsteroid == 0:
            if len(asteroids) < maxAsteroids:
                ran = random.choice([1,1,1,1,2,2,3])
                asteroids.append(Asteroid(ran))

        for p in playersAlive:
            if p not in deadPlayers:
                if (p.checkOffScreen()):
                    if p not in deadPlayers:
                        deadPlayers.append(p)
            
            for b in playerBullets:
                if b.x >= p.x and b.x <= p.x + p.w or b.x + b.w >= p.x and b.x + b.w <= p.x + p.w:
                    if b.y >= p.y and b.y <= p.y + p.h or b.y + b.h >= p.y and b.y + b.h <= p.y + p.h:
                        if b.number != p.number:
                            if p not in deadPlayers:
                                deadPlayers.append(p)
                            playerBullets.pop(playerBullets.index(b))

            for a in asteroids:
                if p.x >= a.x and p.x <= a.x + a.w or p.x + p.w >= a.x and p.x + p.w <= a.x + a.w:
                    if p.y >= a.y and p.y <= a.y + a.h or p.y + p.h >= a.y and p.y + p.h <= a.y + a.h:
                        if p not in deadPlayers:
                            deadPlayers.append(p)

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
                if p not in deadPlayers:
                    if p.x >= cc.x and p.x <= cc.x + cc.w or p.x + p.w >= cc.x and p.x + p.w <= cc.x + cc.w:
                        if p.y >= cc.y and p.y <= cc.y + cc.h or p.y + p.h >= cc.y and p.y + p.h <= cc.y + cc.h:
                            if p not in deadPlayers:
                                deadPlayers.append(p)

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
                        if playersAlive[0] not in deadPlayers:
                            playerBullets.append(playersAlive[0].shoot())
                if event.key == pygame.K_y:
                    if not gameover:
                        if playersAlive[1] not in deadPlayers:
                            playerBullets.append(playersAlive[1].shoot())
                if event.key == pygame.K_o:
                    if not gameover:
                        if playersAlive[2] not in deadPlayers:
                            playerBullets.append(playersAlive[2].shoot())
                if event.key == pygame.K_RSHIFT:
                    if not gameover:
                        if playersAlive[3] not in deadPlayers:
                            playerBullets.append(playersAlive[3].shoot())
        
        gameover = redrawGameScreen()
    
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

pygame.quit()

