#Asteroids V2. Versión optimizada para un solo jugador.

import pygame

from nave import Spaceship
from asteroide import Asteroid
from utiles import get_random_position, load_sprite, WIDTH, HEIGHT

class AsteroidAI:
    MIN_ASTEROID_DISTANCE = 300

    def __init__(self, w= WIDTH, h=HEIGHT):
        pygame.init()
        pygame.display.set_caption('Asteroids')
        self.screen = pygame.display.set_mode((w, h))
        self.background = load_sprite("space", False)
        self.clock = pygame.time.Clock()
        self.timer = pygame.time.Clock()
        self.totalTtime = 0
        self.reset()

    def reset(self):
        self.timer.tick()
        self.gameOver = False
        self.asteroids = []
        self.bullets = []
        self.player = Spaceship((400, 300), self.bullets.append)
        self.players = [self.player]
        self.time = 0
        self.score = 0

        for _ in range(6):
            while True:
                position = get_random_position(self.screen)
                if (
                    position.distance_to(self.player.position)
                    > self.MIN_ASTEROID_DISTANCE
                ):
                    break

            self.asteroids.append(Asteroid(position, self.asteroids.append))

    def play_step(self, action):
        self.reward = 0
        for player in self.players:
            if player.alive:
                player.prepareMove(action)
                player.move(self.screen)
                player.checkRadar(self.asteroids, self.bullets)

        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        for player in self.players:
            if player.alive:
                for asteroid in self.asteroids:
                    if asteroid.collides_with(player):
                        self.reward = -1000
                        player.alive = False
                        break

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if asteroid.collides_with(bullet):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    self.reward += 1000
                    self.score += 1
                    asteroid.split()
                    break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

        self.checkGameOver()
        self._draw()
        self.time = self.time/1000

        return self.reward, self.time, self.gameOver, self.score

    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        for player in self.players:
            if player.alive:
                player.draw(self.screen)
        for game_object in self._get_game_objects():
            game_object.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(60)

    def _get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets]
        return game_objects

    def checkGameOver(self):
        nDead = 0
        for player in self.players:
            if not player.alive:
                nDead += 1
                self.gameOver = True
                self.timer.tick()
                self.time = self.timer.get_time()
        if not self.asteroids and nDead < len(self.players):
            self.gameOver = True
            self.reward = 10000
            self.timer.tick()
            self.time = self.timer.get_time()

run = True
asteroid = AsteroidAI()
while run:

    if not asteroid.gameOver:
        move = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            asteroid.play_step([0,0,1,0,0])
            move = True
        if keys[pygame.K_d]:
            asteroid.play_step([0,0,0,1,0])
            move = True
        if keys[pygame.K_w]:
            asteroid.play_step([0,1,0,0,0])
            move = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if not asteroid.gameOver:
                        asteroid.play_step([0,0,0,0,1])
                        move = True

        if move == False:
            asteroid.play_step([1,0,0,0,0])

    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

pygame.quit()