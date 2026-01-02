"""
    fix if there are no changes to the background you don't need to blit it again
    so if there are no changes to the raster or player vision you don't need to repaint it

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


class Player():
    def __init__(self):
        self.image = pygame.Surface((40,40))
        self.image.fill('red')
        self.rect = self.image.get_rect(center = (300,300))
        self.status = None
        
        self.vision = 60
        
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
            

class Background():
    def __init__(self, name, width, height, button_location):
        self.width = width
        self.height = height
        self.image = self.get_background(name)
        
        self.cover = pygame.Surface((width, height))
        self.cover.fill('black')
        self.cover.set_colorkey('white')
        self.mask = pygame.Surface((width, height))  # store what has been seen because vision is a circle
        self.mask.fill('black')
        self.raster_spacing = 50
        
        self.buttonimage =  pygame.transform.scale(self.image, (150, 150))
        self.rect = self.buttonimage.get_rect(center = button_location)
        
        self.scaler_image =  pygame.Surface((40,40))
        self.scaler_image.fill('blue')
        self.scaler_rect = self.scaler_image.get_rect(center=(40,40))
        self.big_scaler_rect = self.scaler_image.get_rect(center=(90,40))
        
        self.lastKnownPlayerPosition = None

    # get the background image
    # @lru_cache
    def get_background(self, name='attempt'):
        background = getattr(imageLoader, name)
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
        return background
    def draw_background(self, screen, player):
        screen.blit(self.image, (0,0))
        self.draw_raster(screen,self.raster_spacing)
        self.draw_player_vision(player)
        screen.blit(self.cover, (0,0))
        screen.blit(self.scaler_image, (self.scaler_rect.left, self.scaler_rect.top))
        screen.blit(self.scaler_image, (self.big_scaler_rect.left, self.big_scaler_rect.top))

    def draw_raster(self, screen, raster_spacing):
        for i in range(0, self.width, raster_spacing):
            pygame.draw.line(screen, (0,0,0), (i, 0), (i,self.height), 3)
            
        for j in range(0, self.height, raster_spacing):
            pygame.draw.line(screen, (0,0,0), (0, j), (self.width,j), 3)
       
    def draw_player_vision(self, player):
        # how far in feet * how many spaces there are / conversion from feet to squares * 2 for both directions
        pygame.draw.circle(self.mask, 'white', player.rect.center, player.vision * self.raster_spacing / 20 * 2)
        self.cover.blit(self.mask, (0,0))
        
    def scaler_clicked(self, position, type, player):
        if self.scaler_rect.collidepoint(position):
            if type == 1:
                self.raster_spacing += 1
            else:
                self.raster_spacing -= 1
            return True
        return False
        
    def big_scaler_clicked(self, position, type, player):
        if self.big_scaler_rect.collidepoint(position):
            if type == 1:
                self.raster_spacing += 5
            else:
                self.raster_spacing -= 5
                
            if self.raster_spacing < 1:
                self.raster_spacing = 1
            return True
        return False
        
    def clicked(self, position, type, player):
        if self.rect.collidepoint(position):
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
        if self.activeBackground and self.activeBackground.scaler_clicked(position, type, player):
            return
        if self.activeBackground and self.activeBackground.big_scaler_clicked(position, type, player):
            return
        for background in self.backgrounds:
            if background.clicked(position, type, player):
                if self.activeBackground:
                    self.activeBackground.lastKnownPlayerPosition = player.rect.center
                if background.lastKnownPlayerPosition:
                    player.rect.center = background.lastKnownPlayerPosition
                self.activeBackground = background
                return
                
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
backgroundmanager = BackgroundManager(imageLoader, screenInfo)
clickables = [player, backgroundmanager]


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

    pygame.display.update()
    
    
    clock.tick(60)