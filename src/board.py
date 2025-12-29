import pygame
import pathlib
import os
from imageloader.imageloader import ImageLoader
from functools import lru_cache
import sys

imagePath = os.path.abspath(r"C:\Users\Olivier\temp\dndtestpictures")
imageLoader = ImageLoader(imagePath)

RASTER_SPACING = 25
BACKGROUND_IMAGE_NAME = 'attempt'


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
            
    def clicked(self, position, _):
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
        
    def clicked(self, position, type):
        global RASTER_SPACING
        if self.rect.collidepoint(position):
            if type == 1:
                RASTER_SPACING = RASTER_SPACING + 1
            else:
                RASTER_SPACING = RASTER_SPACING - 1
        return False
            
class Background_image_button():
    def __init__(self, name, pos):
        self.image = pygame.Surface((40,40))
        self.image.fill('blue')
        self.rect = self.image.get_rect(center = pos)
        self.name = name
        
    def clicked(self, position, type):
        global BACKGROUND_IMAGE_NAME
        if self.rect.collidepoint(position):
            BACKGROUND_IMAGE_NAME = self.name
            return True
        else:
            return False    
    
class Background():
    def __init__(self, name, width, height):
        self.width = width
        self.height = height
        self.image = self.get_background(name)
        self.cover = pygame.Surface((width, height))
        self.cover.fill('black')
        self.cover.set_colorkey('white')
        self.mask = pygame.Surface((width, height))  # store what has been seen because vision is a circle
        self.mask.fill('black')
        
        self.buttons = [Button((20,20))]
        print(imageLoader._images)
        for x, image in enumerate(imageLoader._images):
            self.buttons.append(Background_image_button(image, (20,x*80+80)))

    # get the background image
    # @lru_cache
    def get_background(self, name='attempt'):
        background = getattr(imageLoader, name)
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
        return background
        
    def draw_background(self, screen):
        screen.blit(self.image, (0,0))
        self.draw_raster(screen)
        background.draw_player_vision(150, player.rect.centerx, player.rect.centery)
        screen.blit(background.cover, (0,0))
        for button in self.buttons:
            screen.blit(button.image, (button.rect.centerx, button.rect.centery))
    
    def draw_raster(self, screen):
        global RASTER_SPACING
        spacing = self.height//RASTER_SPACING
        for i in range(0, self.width, spacing):
            pygame.draw.line(screen, (0,0,0), (i, 0), (i,self.height), 3)
            
        for j in range(0, self.height, spacing):
            pygame.draw.line(screen, (0,0,0), (0, j), (self.width,j), 3)
                 
    def draw_player_vision(self, size, x,y):
        pygame.draw.circle(self.mask, 'white', (x,y), size)
        self.cover.blit(self.mask, (0,0))
        
    def clicked(self, position, type):
        for button in self.buttons:
            clicked = button.clicked(position, type)
            if clicked:
                self.image = self.get_background(button.name)
                self.mask.fill('black')
                break


pygame.init()
screenInfo = pygame.display.Info()

screen = pygame.display.set_mode([screenInfo.current_w, screenInfo.current_h])
clock = pygame.time.Clock()

# group setup

player = Player()
background = Background('attempt', screenInfo.current_w, screenInfo.current_h)
clickables = [player, background]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for clickable in clickables:
                clickable.clicked(event.pos, event.button)
        

    screen.fill('white')
    
    player.update()
    background.draw_background(screen)

    screen.blit(player.image, (player.rect.left, player.rect.top))
    pygame.display.update()
    
    
    clock.tick(60)