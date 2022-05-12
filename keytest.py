import pygame
import pygame.font as font

# Keytest
# this is a small pygame testing env to see which keys correspond to which keycodes
# it is kind of useless, but I wrote it anyway just because

pygame.init()
quitting = False
window = pygame.display.set_mode((600,50))
fontdef = font.Font(font.get_default_font(),20)
mainclock = pygame.time.Clock()
while not quitting:
    events = pygame.event.get()
    keys = []
    for e in events:
        if e.type == pygame.QUIT:
            quitting = True
        elif e.type == pygame.KEYDOWN:
            keys.append(e.key)
    textimg = fontdef.render(str(keys),True,(255,255,255))
    window.fill((0,0,0))
    window.blit(textimg,(0,0))
    pygame.display.flip()
    mainclock.tick(5)
