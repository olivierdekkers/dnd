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
import math

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
            if  player.rect.centerx - player.previous_coordinate[0] or player.rect.centery - player.previous_coordinate[1]:
                viewsize=player.vision * self.raster_spacing / 20 * 2
                player_view = pygame.Surface((viewsize, viewsize))
                player_view.fill('black')
                player_view.set_colorkey('black')
                
                pygame.draw.circle(player_view, 'white', (viewsize/2,viewsize/2), viewsize/2)
                player_rect = self.image.get_rect(center=player.rect.center)
                mask = pygame.mask.from_surface(player_view)
                
                offset_x = viewsize/2-player.rect.left
                offset_y = viewsize/2-player.rect.top
                
                hit = mask.overlap(self.bg_mask, (offset_x, offset_y))
                
                overlapping_mask = mask.overlap_mask(self.bg_mask, (offset_x, offset_y))
                sizes = overlapping_mask.get_bounding_rects()
                
                overlapping_mask = mask.overlap_mask(self.inverted_bg_mask, (offset_x, offset_y))
                overlapping_mask_image = overlapping_mask.to_surface()
                overlapping_mask_image.set_colorkey('black')
                for size in sizes:
                        # pygame.draw.rect(overlapping_mask_image, 'red', size, width=1)
                        vectors = []
                        for point in [size.topleft, size.topright, size.bottomleft, size.bottomright]:
                            vectors.append((pygame.math.Vector2(point),pygame.math.Vector2(viewsize, 0).rotate_rad(math.atan2(point[1]-viewsize/2, point[0]-viewsize/2))))
                            
                            # pygame.draw.line(overlapping_mask_image, 'red', point, pygame.math.Vector2(500, 0).rotate_rad(math.atan2(point[1]-viewsize/2, point[0]-viewsize/2)), width=1)
                        a ,smallest, biggest, b = vectors# sorted(vectors, key=lambda x: ((x[0][0] - viewsize/2)**2 + (x[0][1] - viewsize/2)**2)**0.5)
                        pygame.draw.polygon(overlapping_mask_image, 'black', [smallest[0], biggest[0], biggest[0]+biggest[1], smallest[0]+smallest[1]])
                        pygame.draw.polygon(overlapping_mask_image, 'black', [a[0], b[0], b[0]+b[1], a[0]+a[1]])

                self.mask.blit(overlapping_mask_image,(player.rect.left-viewsize/2, player.rect.top-viewsize/2))
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