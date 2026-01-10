# usefull bits of code:

@lru_cache 
def PointsInCircum(radius, center_x, center_y, num_points):
    points = []
    for i in range(num_points):
        angle = i * 2 * np.pi / num_points
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        points.append((round(x), round(y)))
    return points  
    
    
    
    
 # draw player vision based on corners of bounding rect:
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