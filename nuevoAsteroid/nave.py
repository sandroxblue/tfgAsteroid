import numpy as np
from pygame.draw import line
from pygame.math import Vector2
from pygame.transform import rotozoom
from utiles import load_sound, load_sprite, GameObject, lineRect, checkOutOfBounds, MAXDIST
from bala import Bullet

UP = Vector2(0, -1)

class Spaceship(GameObject):
    MANEUVERABILITY = 10
    ACCELERATION = 0.03
    BULLET_SPEED = 5

    def __init__(self, position, create_bullet_callback):
        self.create_bullet_callback = create_bullet_callback
        self.laser_sound = load_sound("laser")
        self.direction = Vector2(UP)
        self.alive = True
        super().__init__(position, load_sprite("spaceship"), Vector2(0))
        self.lidar = self.actualizarLidar()

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)
        # for linea in self.lidar:
        #     line(surface, (255,255,255), self.position, linea)

    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
        bullet = Bullet(self.position, bullet_velocity)
        self.create_bullet_callback(bullet)
        self.laser_sound.play()

    def prepareMove(self, action):
        ##[nada, izq, der, recto, disparar]
        if np.array_equal(action, [1,0,0,0,0]):
            return 0
        elif np.array_equal(action, [0,1,0,0,0]):
            self.accelerate()
            return 0.1
        elif np.array_equal(action, [0,0,1,0,0]):
            self.rotate(False)
            return 0.05
        elif np.array_equal(action, [0,0,0,1,0]):
            self.rotate(True)
            return 0.05
        elif np.array_equal(action, [0,0,0,0,1]):
            self.shoot()
            return 0.1

    def actualizarLidar(self):
        lidar = []
        direction = self.direction
        for i in range(1,16):
            angle = 360/15
            rotated_direction = direction.rotate(angle * i)
            lidar.append(self.position + rotated_direction * MAXDIST)
        return lidar


    def checkRadar(self, asteroids, bullets):
        self.lidar = self.actualizarLidar()
        detectados = []
        x0, y0 = self.position - Vector2(self.radius)
        for linea in self.lidar:
            encontradoFin = [1,1,1] #[finmapa,asteroide, nave]
            x1, y1 = linea
            distancia = checkOutOfBounds(x0,y0,x1,y1)
            if distancia < MAXDIST:
                encontradoFin[0] = distancia/MAXDIST
            for a in asteroids:
                centerx, centery = a.position.xy
                pt1x, pt1y = (centerx - self.radius, centery - self.radius)
                pt2x, pt2y = (centerx - self.radius, centery + self.radius)
                pt3x, pt3y = (centerx + self.radius, centery + self.radius)
                pt4x, pt4y = (centerx + self.radius, centery - self.radius)
                if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                    distance = self.position.distance_to(a.position) - self.radius - a.radius
                    encontradoFin[1] = distance/MAXDIST

            for b in bullets:
                centerx, centery = b.position.xy
                pt1x, pt1y = (centerx - self.radius, centery - self.radius)
                pt2x, pt2y = (centerx - self.radius, centery + self.radius)
                pt3x, pt3y = (centerx + self.radius, centery + self.radius)
                pt4x, pt4y = (centerx + self.radius, centery - self.radius)
                if lineRect(x0, y0, x1, y1, pt1x, pt1y, pt2x, pt2y, pt3x, pt3y, pt4x, pt4y):
                    distance = self.position.distance_to(b.position) - self.radius - b.radius
                    encontradoFin[2] = distance/MAXDIST
            detectados.extend(encontradoFin)
        return detectados