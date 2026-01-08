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

viewsize = 1000

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

screen = pygame.display.set_mode([1300,1300])
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
    
def numpy_intersection(line1, line2):
    A1, B1 = line1
    A2, B2 = line2
    A = np.array([[B1[0] - A1[0], A2[0] - B2[0]],
                   [B1[1] - A1[1], A2[1] - B2[1]]])
    b = np.array([A2[0] - A1[0], A2[1] - A1[1]])
    
    if np.linalg.det(A) == 0:
        raise ValueError('The lines do not intersect.')
    
    t = np.linalg.solve(A, b)
    intersection_x = A1[0] + t[0] * (B1[0] - A1[0])
    intersection_y = A1[1] + t[0] * (B1[1] - A1[1])
    return intersection_x, intersection_y


# positions = PointsInCircum(viewsize/2-0.6, viewsize/2, viewsize/2, 1000)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if  pygame.mouse.get_pos():
        previous_coordinate = rect.rect.center
        rect.rect.center = pygame.mouse.get_pos()
    
    if  rect.rect.centerx - previous_coordinate[0] or rect.rect.centery - previous_coordinate[1]:
        offset_x = 0 - rect.rect.left
        offset_y = 0 - rect.rect.top
        hit = rect.mask.overlap(bg_mask, (offset_x, offset_y))
        if hit:
            overlapping_mask = rect.mask.overlap_mask(bg_mask, (offset_x, offset_y))
            
            sizes = overlapping_mask.get_bounding_rects()
            overlapping_mask = rect.mask.overlap_mask(inverted_bg_mask, (offset_x, offset_y))
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

            screen.blit(overlapping_mask_image, (rect.rect.left, rect.rect.top))
    pygame.display.flip()
    clock.tick(60)