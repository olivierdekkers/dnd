import pygame
import pathlib
import os
from imageloader.imageloader import ImageLoader
from functools import lru_cache

pygame.init()
screenInfo = pygame.display.Info()
screen = pygame.display.set_mode([screenInfo.current_w, screenInfo.current_h])

imagePath = os.path.abspath(r"C:\Users\Olivier\Downloads")
imageLoader = ImageLoader(imagePath)

screen.fill((255,5,5))

running = True


# get the background image
@lru_cache
def get_background(name='attempt'):
    background = getattr(imageLoader, name)
    background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
    return background


def draw_raster(screen, width, height, spacing=25):
    spacing = height//spacing
    for i in range(0, width, spacing):
        pygame.draw.line(screen, (0,0,0), (i, 0), (i,height), 3)
        
    for j in range(0, height, spacing):
        pygame.draw.line(screen, (0,0,0), (0, j), (width,j), 3)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            

    screen.blit(get_background(), (0,0))
    draw_raster(screen, screen.get_width(), screen.get_height())
    # print(screen.get_width(), screen.get_height())
    # 2560 1440
    pygame.display.flip()