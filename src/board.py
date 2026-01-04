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
import numpy as np

imagePath = os.path.abspath(r"C:\Users\Olivier\temp\dndtestpictures")
imageLoader = ImageLoader(imagePath)


class Player():
    def __init__(self):
        self.image = pygame.Surface((40,40))
        self.image.fill('red')
        self.rect = self.image.get_rect(center = (300,300))
        self.previous_coordinate = self.rect.center
        self.status = None
        
        self.vision = 60
        
    def update(self):
        if pygame.mouse.get_pos() and self.status == 'clicked':
            self.previous_coordinate = self.rect.center
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

@lru_cache 
def PointsInCircum(radius, center_x, center_y, num_points):
    points = []
    for i in range(num_points):
        angle = i * 2 * np.pi / num_points
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        points.append((round(x), round(y)))
    return points  

class Background():
    def __init__(self, name, width, height, button_location):
        self.image, width, height = self.get_background(name, width, height)
        self.width = width
        self.height = height
        self.cover = pygame.Surface((width, height))
        self.cover.fill((0,0,0))
        self.cover.set_alpha(230)
        self.cover.set_colorkey('white')
        self.mask = pygame.Surface((width, height))  # store what has been seen because vision is a circle
        self.mask.fill((0,0,0))
        self.raster_spacing = 50
        
        self.buttonimage =  pygame.transform.scale(self.image, (150, 150))
        self.rect = self.buttonimage.get_rect(center = button_location)
        
        self.scaler_image =  pygame.Surface((40,40))
        self.scaler_image.fill('blue')
        self.scaler_rect = self.scaler_image.get_rect(center=(40,40))
        self.big_scaler_rect = self.scaler_image.get_rect(center=(90,40))
        
        if hasattr(imageLoader, name+'_wall'):
            bg = getattr(imageLoader, name+'_wall')
            bg = pygame.transform.scale(bg, (width, height))
            self.bg_mask = pygame.mask.from_surface(bg)
            self.inverted_bg_mask = pygame.mask.from_surface(bg)
            self.inverted_bg_mask.invert()
        else:
            self.bg_mask = None
            self.inverted_bg_mask = None
        
        self.lastKnownPlayerPosition = None

    # get the background image
    # @lru_cache
    def get_background(self, name, width, height):
        background = getattr(imageLoader, name)
        
        ratio = background.get_width() / background.get_height()
        height = round(height*0.9)
        width = round(height * ratio)
        
        background = pygame.transform.scale(background, (width, height))
        return background, width, height
        
    def draw_background(self, screen, player):
        screen.blit(self.image, (0,0))
        self.draw_raster(screen,self.raster_spacing)
        self.draw_player_vision(player, screen)
        screen.blit(self.cover, (0,0))
        screen.blit(self.scaler_image, (self.scaler_rect.left, self.scaler_rect.top))
        screen.blit(self.scaler_image, (self.big_scaler_rect.left, self.big_scaler_rect.top))

    def draw_raster(self, screen, raster_spacing):
        for i in range(0, self.width, raster_spacing):
            pygame.draw.line(screen, (0,0,0), (i, 0), (i,self.height), 3)
            
        for j in range(0, self.height, raster_spacing):
            pygame.draw.line(screen, (0,0,0), (0, j), (self.width,j), 3)
       
    def draw_player_vision(self, player, screen):
        # how far in feet * how many spaces there are / conversion from feet to squares * 2 for both directions
        if self.bg_mask:
            player_mask = pygame.Surface((player.vision * self.raster_spacing / 20 * 2, player.vision * self.raster_spacing / 20 * 2))
            rect = player_mask.get_rect(center = player.rect.center)
            viewsize=player.vision * self.raster_spacing / 20 * 2
            pygame.draw.circle(player_mask, 'white', (player.vision * self.raster_spacing / 20, player.vision * self.raster_spacing / 20), viewsize)
            player_mask = pygame.mask.from_surface(player_mask)
            
            line_image = pygame.Surface((viewsize,viewsize))
            line_image.set_colorkey('black')
            line_width = 1
            if  player.rect.centerx - player.previous_coordinate[0] or player.rect.centery - player.previous_coordinate[1]:
                offset_x = 0 - rect.left
                offset_y = 0 - rect.top
                hit = player_mask.overlap(self.inverted_bg_mask, (offset_x, offset_y))
                if hit:
                    overlapping_mask = player_mask.overlap_mask(self.inverted_bg_mask, (offset_x, offset_y))
                    overlapping_mask_image = overlapping_mask.to_surface()
                    overlapping_mask_image.set_colorkey('black')
                    for x,y in PointsInCircum(viewsize/2-0.6, viewsize/2, viewsize/2, 1000):
                        if overlapping_mask_image.get_at((x,y))[0] != 0 and overlapping_mask_image.get_at((x,y))[1] != 0:
                            line_image.fill('black')
                            pygame.draw.line(line_image, 'white',(x,y), (viewsize/2,viewsize/2), line_width)
                            if not pygame.mask.from_surface(line_image).overlap(self.bg_mask, (offset_x,offset_y)):
                                self.mask.blit(line_image, (rect.left, rect.top))
                            else:
                                pygame.draw.line(overlapping_mask_image, 'black',(x,y), (viewsize/2,viewsize/2), line_width)
        else:
            pygame.draw.circle(self.mask, 'white', (player.rect.left, player.rect.top), player.vision * self.raster_spacing / 20 *2 )
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
        
        for x, image in enumerate([image for image in imageLoader._images if '_wall' not in image]):
            if image != 'attempt_wall':
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
            if pygame.display.get_window_size() != (self.activeBackground.width, self.activeBackground.height):
                screen = pygame.display.set_mode((self.activeBackground.width, self.activeBackground.height))
            self.activeBackground.draw_background(screen, player)
        for background in self.backgrounds:
            screen.blit(background.buttonimage, (background.rect.left, background.rect.top))
        
pygame.init()
screenInfo = pygame.display.Info()

screen = pygame.display.set_mode([1000, 1000])
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