import pygame
import pathlib
import os
from imageloader.imageloader import ImageLoader

pygame.init()
screenInfo = pygame.display.Info()
screen = pygame.display.set_mode([screenInfo.current_w, screenInfo.current_h])

imagePath = os.path.abspath(r"C:\Users\Olivier\Pictures\Saved Pictures")
imageLoader = ImageLoader(imagePath)

screen.fill((255,5,5))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    var = getattr(imageLoader, 'blob')
    screen.blit(var, (0,0))
    screen.blit(var, (-500,-50))
    pygame.display.flip()
    breakpoint()