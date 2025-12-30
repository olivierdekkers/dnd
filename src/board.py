"""

Known issues:
    player vision isn't tied to the raster scaling
    
Next upgrades:
    range indicator
"""


import pygame
import pathlib
import os
from imageloader.imageloader import ImageLoader
from functools import lru_cache
import sys

imagePath = os.path.abspath(r"C:\Users\Olivier\temp\dndtestpictures")
imageLoader = ImageLoader(imagePath)

RASTER_SPACING = 25


class Player():
    def __init__(self):
        self.image = pygame.Surface((40,40))
        self.image.fill('red')
        self.rect = self.image.get_rect(center = (300,300))
        self.status = None
        
        self.vision = pygame.Surface((100,100))
        self.vision.fill('black')
        self.vision_rect = self.vision.get_rect(center = (300,300))
        pygame.draw.circle(self.vision, 'white', (50,50), 50)
        
    def update(self):
        if pygame.mouse.get_pos() and self.status == 'clicked':
            self.rect.center = pygame.mouse.get_pos()
            
    def clicked(self, position, type, player):
        if self.rect.collidepoint(position):
            if self.status != 'clicked':
                self.status = 'clicked'
            else:
                self.status = None
            return True
        else:
            return False
            
class Button():
    def __init__(self, pos):
        self.image = pygame.Surface((40,40))
        self.image.fill('blue')
        self.rect = self.image.get_rect(center = pos)
        
    def clicked(self, position, type, player):
        global RASTER_SPACING
        if self.rect.collidepoint(position):
            if type == 1:
                RASTER_SPACING = RASTER_SPACING + 1
            else:
                RASTER_SPACING = RASTER_SPACING - 1
        return False
            

class Background():
    def __init__(self, name, width, height, button_location):
        global RASTER_SPACING
        self.width = width
        self.height = height
        self.image = self.get_background(name)
        self.cover = pygame.Surface((width, height))
        self.cover.fill('black')
        self.cover.set_colorkey('white')
        self.mask = pygame.Surface((width, height))  # store what has been seen because vision is a circle
        self.mask.fill('black')
        self.raster_spacing = RASTER_SPACING
        
        self.buttonimage =  pygame.transform.scale(self.image, (150, 150))
        self.rect = self.buttonimage.get_rect(center = button_location)
        
        self.lastKnownPlayerPosition = None

    # get the background image
    # @lru_cache
    def get_background(self, name='attempt'):
        background = getattr(imageLoader, name)
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
        return background
        
    def draw_background(self, screen, player):
        screen.blit(self.image, (0,0))
        self.draw_raster(screen)
        self.draw_player_vision(150, player.rect.left, player.rect.top)
        screen.blit(self.cover, (0,0))
    
    def draw_raster(self, screen):
        global RASTER_SPACING
        self.raster_spacing = RASTER_SPACING
        spacing = self.height//RASTER_SPACING
        for i in range(0, self.width, spacing):
            pygame.draw.line(screen, (0,0,0), (i, 0), (i,self.height), 3)
            
        for j in range(0, self.height, spacing):
            pygame.draw.line(screen, (0,0,0), (0, j), (self.width,j), 3)
                 
    def draw_player_vision(self, size, x,y):
        pygame.draw.circle(self.mask, 'white', (x,y), size)
        self.cover.blit(self.mask, (0,0))
        
    def clicked(self, position, type):
        global RASTER_SPACING
        if self.rect.collidepoint(position):
            RASTER_SPACING = self.raster_spacing
            return True
        else:
            return False   

class BackgroundManager:
    def __init__(self, imageLoader, screeninfo):
        self.activeBackground = None
        self.backgrounds = []
                
        for x, image in enumerate(imageLoader._images):
            self.backgrounds.append(Background(image, screenInfo.current_w, screenInfo.current_h, (75,x*200+200)))
            
    def clicked(self, position, type, player):
        for background in self.backgrounds:
            if background.clicked(position, type):
                if self.activeBackground:
                    self.activeBackground.lastKnownPlayerPosition = player.rect.center
                if background.lastKnownPlayerPosition:
                    player.rect.center = background.lastKnownPlayerPosition
                self.activeBackground = background
                
    def draw_background(self, screen, player):
        if self.activeBackground:
            self.activeBackground.draw_background(screen, player)
        for background in self.backgrounds:
            screen.blit(background.buttonimage, (background.rect.left, background.rect.top))
        
pygame.init()
screenInfo = pygame.display.Info()

screen = pygame.display.set_mode([screenInfo.current_w, screenInfo.current_h])
clock = pygame.time.Clock()

# group setup

player = Player()
scaler = Button((20,20))
backgroundmanager = BackgroundManager(imageLoader, screenInfo)
clickables = [player, scaler, backgroundmanager]



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for clickable in clickables:
                clickable.clicked(event.pos, event.button, player)
        

    screen.fill('grey')
    
    player.update()

    backgroundmanager.draw_background(screen, player)
    screen.blit(player.image, (player.rect.left, player.rect.top))
    screen.blit(scaler.image, (scaler.rect.left, scaler.rect.top))

    pygame.display.update()
    
    
    clock.tick(60)