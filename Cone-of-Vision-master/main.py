"""
Cone of Vision
Ian S. Woodley

This is a quick demonstration of a 2D "cone-of-vision" test that AI
may perform to detect a player. This was inspired by my love for
stealth games, particularly Dishonored.

Built with Python v3.5.0 using Pygame and Google's 'math3d' library.

Note: 'Q' is used to indicate a temporary vector.
"""

import math
import pygame as pg
from math3d import *

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

# Initialization
pg.display.init()
pg.font.init()
pg.display.set_caption("Press p to pause")
screen = pg.display.set_mode((800, 600))
font = pg.font.SysFont("Arial", 22)
msg = font.render("Enemy sighted!", True, (255, 200, 0))
clock = pg.time.Clock()
running = True
paused = False

# Vectors/constants
player = vec2(400, 300)
playerDir = vec2(0, -1)
rads = math.radians(45)
maxDist = 300

# Main loop
while running:
    # Update deltaTime
    if paused:
        dt = 0
        clock.tick(0)
    else:
        dt = clock.tick() / 1000

    # Handle input
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            running = False
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_p:
                paused = not paused
            if ev.key in (pg.K_ESCAPE, pg.K_q):
                running = False

    screen.fill((100, 100, 100))
    enemy = vec2(*pg.mouse.get_pos())
    
    # Rotate facing direction
    Q = player + playerDir * 30
    Q = orbit(Q, player, (math.pi / 4) * dt)
    Q -= player
    playerDir = normalize(Q)
    end = player + playerDir * maxDist

    # Draw geometry
    Q = player + playerDir * maxDist
    left = orbit(Q, player, rads / 2)
    right = orbit(Q, player, -rads / 2)
    
    pg.draw.line(screen, (255, 255, 0), pgConvert(player), pgConvert(left))
    pg.draw.line(screen, (255, 255, 0), pgConvert(player), pgConvert(right))
    pg.draw.line(screen, (255, 255, 0), pgConvert(left), pgConvert(end))
    pg.draw.line(screen, (255, 255, 0), pgConvert(right), pgConvert(end))

    pg.draw.circle(screen, (0, 50, 200), pgConvert(enemy), 16)
    pg.draw.circle(screen, (255, 0, 0),  pgConvert(player), 16)
    pg.draw.circle(screen, (255, 255, 0), pgConvert(left), 16)
    pg.draw.circle(screen, (255, 255, 0), pgConvert(right), 16)
    pg.draw.circle(screen, (255, 255, 0), pgConvert(end), 16)
    
    # Perform vision test, draw message
    A = player + playerDir
    A -= player
    B = enemy - player

    cosangle = dot(A, B) / (length(A) * length(B))
    theta = math.acos(cosangle)

    if theta <= rads / 2 and length(B) <= maxDist:
        screen.blit(msg, (0, 0))

    # Flip buffer for rendering
    pg.display.flip()
# Shutdown
pg.display.quit()
pg.quit()
