import pygame
import pathlib
import os
from imageloader.imageloader import ImageLoader
from functools import lru_cache
import sys
import math
import numpy as np

imagePath = os.path.abspath(r"C:\Users\Olivier\temp\raytrace")
imageLoader = ImageLoader(imagePath)

viewsize = 500

class Rect(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((viewsize, viewsize))
        self.image.fill('black')
        self.image.set_colorkey('black')
        
        pygame.draw.circle(self.image, 'grey', (viewsize/2,viewsize/2), viewsize/2)
        self.rect = self.image.get_rect(topleft = (1500,1500))
        self.mask = pygame.mask.from_surface(self.image)
        # self.mask.invert()

pygame.init()
screenInfo = pygame.display.Info()

screen = pygame.display.set_mode([1000,1000])
screen.fill('blue')
bg = getattr(imageLoader, 'maze')
bg = pygame.transform.scale(bg, (screen.get_width(), screen.get_height()))
bg_mask = pygame.mask.from_surface(bg)
inverted_bg_mask = pygame.mask.from_surface(bg)
inverted_bg_mask.invert()

screen.blit(bg, (0,0))


clock = pygame.time.Clock()

rect = Rect()
group = pygame.sprite.Group([rect])


line_image = pygame.Surface((viewsize,viewsize))
line_image.set_colorkey('black')
line_width = 1

def PointsInCircum(radius, center_x, center_y, num_points):
    points = []
    for i in range(num_points):
        angle = i * 2 * np.pi / num_points
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        points.append((round(x), round(y)))
    return points

positions = PointsInCircum(viewsize/2-0.6, viewsize/2, viewsize/2, 1000)
print(min(positions, key=lambda x: x[0]))
print(min(positions, key=lambda x: x[1]))
print(max(positions, key=lambda x: x[0]))
print(max(positions, key=lambda x: x[1]))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if  pygame.mouse.get_pos():
        previous_coordinate = rect.rect.center
        rect.rect.center = pygame.mouse.get_pos()
    # screen.blit(rect.image, (rect.rect.left, rect.rect.top))
    
    if  rect.rect.centerx - previous_coordinate[0] or rect.rect.centery - previous_coordinate[1]:
        offset_x = 0 - rect.rect.left
        offset_y = 0 - rect.rect.top
        hit = rect.mask.overlap(inverted_bg_mask, (offset_x, offset_y))
        print(offset_x, offset_y)
        if hit:
            overlapping_mask = rect.mask.overlap_mask(inverted_bg_mask, (offset_x, offset_y))
            overlapping_mask_image = overlapping_mask.to_surface()
            overlapping_mask_image.set_colorkey('black')
                    
            for x,y in positions:
                if overlapping_mask_image.get_at((x,y))[0] != 0 and overlapping_mask_image.get_at((x,y))[1] != 0:
                    line_image.fill('black')
                    pygame.draw.line(line_image, 'white',(x,y), (viewsize/2,viewsize/2), line_width)
                    if not pygame.mask.from_surface(line_image).overlap(bg_mask, (offset_x,offset_y)):
                        screen.blit(line_image, (rect.rect.left, rect.rect.top))
                    else:
                        pygame.draw.line(overlapping_mask_image, 'black',(x,y), (viewsize/2,viewsize/2), line_width)
        
            # screen.blit(overlapping_mask_image, (rect.rect.left, rect.rect.top))
    pygame.display.update()
    clock.tick(60)