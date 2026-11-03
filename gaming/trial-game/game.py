#!/usr/bin/python3

import pygame as pg

# Pygame initialization
pg.init()
screen = pg.display.set_mode((1280, 720))
clock = pg.time.Clock()
running = True

while running:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            runnung = False

    screen.fill("purple")

    pg.display.flip()

    clock.tick(60)

pygame.quit()
