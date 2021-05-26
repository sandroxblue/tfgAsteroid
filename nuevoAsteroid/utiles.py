import random
import math
from pygame.image import load
from pygame.math import Vector2
from pygame.mixer import Sound
from intersections import intersectLines

MAXDIST = 300
WIDTH = 800
HEIGHT = 600

def load_sprite(name, with_alpha=True):
    path = f"sprites/{name}.png"
    loaded_sprite = load(path)
    if with_alpha:
        return loaded_sprite.convert_alpha()
    else:
        return loaded_sprite.convert()


def load_sound(name):
    path = f"sounds/{name}.wav"
    return Sound(path)


def wrap_position(position, surface):
    x, y = position
    w, h = surface.get_size()
    return Vector2(x % w, y % h)


def get_random_position(surface):
    return Vector2(
        random.randrange(surface.get_width()),
        random.randrange(surface.get_height()),
    )


def get_random_velocity(min_speed, max_speed):
    speed = random.uniform(min_speed, max_speed)
    angle = random.randrange(0, 360)
    return Vector2(speed, 0).rotate(angle)


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


def checkOutOfBounds(x0, y0, x1, y1):
    dist = MAXDIST
    if x1 < 0 or y1 < 0:
        a = intersectLines((x0,y0), (x1,y1), (0,0), (0,HEIGHT))
        b = intersectLines((x0,y0), (x1,y1), (0,0), (WIDTH,0))
        if x1 < 0 and y1 > 0:
            dist = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            #print(f"choco con el fin del mundo en {a[0]},{a[1]} y yo estoy en {x0},{y0}, dist total= {dist}")
        elif x1 > 0 and y1 < 0:
            dist = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            #print(f"choco con el fin del mundo en {b[0]},{b[1]} y yo estoy en {x0},{y0}, dist total= {dist}")
        else:
            distA = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            distB = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            dist = min(distA, distB)
    if x1 > WIDTH or y1 > HEIGHT:
        a = intersectLines((x0,y0), (x1,y1), (0,HEIGHT), (WIDTH,HEIGHT))
        b = intersectLines((x0,y0), (x1,y1), (WIDTH,0), (WIDTH,HEIGHT))
        if x1 > WIDTH and y1 < HEIGHT:
            dist = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            #print(f"choco con el fin del mundo en {a[0]},{a[1]} y yo estoy en {x0},{y0}, dist total= {dist}")
        elif x1 < WIDTH and y1 > HEIGHT:
            dist = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            #print(f"choco con el fin del mundo en {b[0]},{b[1]} y yo estoy en {x0},{y0}, dist total= {dist}")
        else:
            distA = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            distB = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            dist = min(distA, distB)
    return dist

def getOutOfBounds(x0, y0, x1, y1):
    dist = MAXDIST
    a = -1
    b = -1
    if x1 < 0 or y1 < 0:
        a = intersectLines((x0,y0), (x1,y1), (0,0), (0,HEIGHT))
        b = intersectLines((x0,y0), (x1,y1), (0,0), (WIDTH,0))
        if x1 < 0 and y1 > 0:
            dist = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            return a[0],a[1],dist
        elif x1 > 0 and y1 < 0:
            dist = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            return b[0],b[1],dist
        else:
            distA = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            distB = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            dist = min(distA, distB)
            if distA < distB:
                return a[0],a[1],dist
            else: return b[0],b[1],dist
    if x1 > WIDTH or y1 > HEIGHT:
        a = intersectLines((x0,y0), (x1,y1), (0,HEIGHT), (WIDTH,HEIGHT))
        b = intersectLines((x0,y0), (x1,y1), (WIDTH,0), (WIDTH,HEIGHT))
        if x1 < WIDTH and y1 > HEIGHT:
            dist = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            return a[0],a[1],dist
        elif x1 > WIDTH and y1 < HEIGHT:
            dist = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            return b[0],b[1],dist
        else:
            distA = math.sqrt((x0 - a[0])**2 + (y0 - a[1])**2)
            distB = math.sqrt((x0 - b[0])**2 + (y0 - b[1])**2)
            dist = min(distA, distB)
            if distA < distB:
                return a[0],a[1],dist
            else: return b[0],b[1],dist
    return a,b,dist

class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius