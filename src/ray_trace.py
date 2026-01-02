import pygame
import pathlib
import os
from imageloader.imageloader import ImageLoader
from functools import lru_cache
import sys
from itertools import chain

imagePath = os.path.abspath(r"C:\Users\Olivier\temp\raytrace")
imageLoader = ImageLoader(imagePath)

viewsize = 100

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
background = getattr(imageLoader, 'maze')
background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
bg_mask = pygame.mask.from_surface(background)
inverted_bg_mask = pygame.mask.from_surface(background)
inverted_bg_mask.invert()

screen.blit(background, (0,0))


clock = pygame.time.Clock()

rect = Rect()
group = pygame.sprite.Group([rect])


line_image = pygame.Surface((viewsize,viewsize))
line_image.set_colorkey('black')
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if  pygame.mouse.get_pos():
        rect.rect.center = pygame.mouse.get_pos()
    # screen.blit(rect.image, (rect.rect.left, rect.rect.top))
    
    offset_x = 0 - rect.rect.left
    offset_y = 0 - rect.rect.top
    hit = rect.mask.overlap(inverted_bg_mask, (offset_x, offset_y))
    if hit:
        
        overlapping_mask = rect.mask.overlap_mask(inverted_bg_mask, (offset_x, offset_y))
        overlapping_mask_image = overlapping_mask.to_surface()
        overlapping_mask_image.set_colorkey('black')
                
        for x in range(viewsize):
            for y in range(viewsize//2):
                if overlapping_mask_image.get_at((x,y))[0] != 0 and overlapping_mask_image.get_at((x,y))[1] != 0:
                    line_image.fill('black')
                    pygame.draw.line(line_image, 'white',(x,y), (viewsize/2,viewsize/2), 3)
                    if not pygame.mask.from_surface(line_image).overlap(bg_mask, (offset_x,offset_y)):
                        pygame.draw.line(overlapping_mask_image, 'red',(x,y), (viewsize/2,viewsize/2), 3)
                    else:
                        overlapping_mask_image.set_at((x,y), 'black')

                if overlapping_mask_image.get_at((x,viewsize- y -1 ))[0] != 0 and overlapping_mask_image.get_at((x ,viewsize - y -1 ))[1] != 0:
                    line_image.fill('black')
                    pygame.draw.line(line_image, 'white',(x,viewsize - y -1 ), (viewsize/2,viewsize/2), 3)
                    if not pygame.mask.from_surface(line_image).overlap(bg_mask, (offset_x,offset_y)):
                        pygame.draw.line(overlapping_mask_image, 'red',(x,viewsize - y -1 ), (viewsize/2,viewsize/2), 3)
                    else:
                        overlapping_mask_image.set_at((x,viewsize - y -1 ), 'black')
        
        screen.blit(overlapping_mask_image, (rect.rect.left, rect.rect.top))
    pygame.display.update()
    clock.tick(60)