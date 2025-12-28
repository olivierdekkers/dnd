import pygame
import pathlib
import os
from imageloader.imageloader import ImageLoader
from functools import lru_cache
import sys

imagePath = os.path.abspath(r"C:\Users\Olivier\Downloads")
imageLoader = ImageLoader(imagePath)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40,40))
        self.image.fill('red')
        self.rect = self.image.get_rect(center = (300,300))
        
        self.vision = pygame.Surface((100,100))
        self.vision.fill('black')
        self.vision_rect = self.vision.get_rect(center = (300,300))
        pygame.draw.circle(self.vision, 'white', (50,50), 50)
        
    def update(self):
        if a := pygame.mouse.get_pos():
            self.rect.center = a
    
class Background(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.image = self.get_background('attempt').convert_alpha()
        self.cover = pygame.Surface((width, height))
        self.cover.fill('black')
        self.cover.set_colorkey('white')
        self.mask = pygame.Surface((width, height))
        self.mask.fill('black')

    # get the background image
    @lru_cache
    def get_background(self, name='attempt'):
        background = getattr(imageLoader, name)
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
        self.draw_raster(background, self.width, self.height)
        return background
    
    def draw_raster(self, screen, width, height, spacing=25):
        spacing = height//spacing
        for i in range(0, width, spacing):
            pygame.draw.line(screen, (0,0,0), (i, 0), (i,height), 3)
            
        for j in range(0, height, spacing):
            pygame.draw.line(screen, (0,0,0), (0, j), (width,j), 3)
            
            
    def draw_player_vision(self, size, x,y):
        pygame.draw.circle(self.mask, 'white', (x,y), size)
        
        self.cover.blit(self.mask, (0,0))


pygame.init()
screenInfo = pygame.display.Info()

screen = pygame.display.set_mode([screenInfo.current_w, screenInfo.current_h])
clock = pygame.time.Clock()

# group setup

player = pygame.sprite.GroupSingle(Player())
background = pygame.sprite.GroupSingle(Background(screenInfo.current_w, screenInfo.current_h))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('white')
    
    player.update()
    #player.draw(screen)
    screen.blit(background.sprite.image, (0,0)) 
    
    background.sprite.draw_player_vision(150, player.sprite.rect.centerx, player.sprite.rect.centery)
    # background.sprite.cover.blit(player.sprite.vision, (player.sprite.vision_rect.left, player.sprite.vision_rect.top))
    screen.blit(background.sprite.cover, (0,0))
    
    screen.blit(player.sprite.image, (player.sprite.rect.left, player.sprite.rect.top))
    pygame.display.update()
    
    
    clock.tick(60)