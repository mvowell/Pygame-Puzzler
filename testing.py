import pygame
import pygame.gfxdraw as gfx
pygame.init()
window = pygame.display.set_mode((500,500))
quitting = False
image = pygame.image.load("testing.jpg")
angle = 0
clock = pygame.time.Clock()
while not quitting:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            quitting = True
    window.fill((0,0,0))
    block = pygame.Surface((60,30))
    gfx.box(block,pygame.Rect(0,0,30,30),(0,0,255))
    gfx.box(block, pygame.Rect(30, 0, 30, 30), (255, 255, 0))
    block = pygame.Surface.convert_alpha(block)
    rotated = pygame.transform.rotate(image,angle)
    window.blit(rotated,(0,0))
    pygame.display.flip()
    clock.tick(60)
    angle += 1

