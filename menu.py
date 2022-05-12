import pygame
import pygame.font as font
import pygame.gfxdraw as gfx
import pygame.time as time
class menu:
    title = pygame.Surface((500,100))
    newgamedark = pygame.Surface((100,50))
    newgamelight = pygame.Surface((100, 50))
    quitdark = pygame.Surface((100, 50))
    quitlight = pygame.Surface((100, 50))
    selection = 1
    quitting = False
    starting = False
    surf = pygame.Surface((0,0))
    counter = 0
    secondaryfont = None
    
    def __init__(self,surf,levels):
        font.init()
        mainfont = font.Font(font.get_default_font(),100)
        #mainfont = font.Font("lucon.ttf", 100)
        self.secondaryfont = font.Font(font.get_default_font(), 50)
        self.title = mainfont.render("SOMETHING",True,(255,255,255))
        gfx.rectangle(self.title,pygame.Rect(0,0,self.title.get_width(),100),(255,0,0))
        self.newgamedark = self.secondaryfont.render("New Game",True,(100,100,100))
        self.newgamelight = self.secondaryfont.render("New Game", True, (255, 255, 255))
        self.quitdark = self.secondaryfont.render("Exit", True, (100, 100, 100))
        self.quitlight = self.secondaryfont.render("Exit", True, (255, 255, 255))
        surf.blit(self.title,(0,0))
        self.surf = surf
        while not self.quitting and not self.starting:
            self.think()
        if self.quitting:
            pygame.quit()
            quit()
        else:
            pass

    def think(self):
        self.counter += 1
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                self.quitting = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    if self.selection > 1:
                        self.selection -= 1
                if e.key == pygame.K_DOWN:
                    if self.selection < 2:
                        self.selection += 1
                if e.key == 13:
                    if self.selection == 1:
                        self.starting = True
                    if self.selection == 2:
                        self.quitting = True
        self.surf.fill((0,0,0))
        self.surf.blit(self.title,(0,0))
        if self.selection == 1:
            color = 255 - (time.get_ticks() / 10 % 100)
            self.newgamelight = self.secondaryfont.render("New Game", True, (color, color, color))
            self.surf.blit(self.newgamelight,(0,110))
        else:
            self.surf.blit(self.newgamedark, (0, 110))
        if self.selection == 2:
            color = 255 - (time.get_ticks() / 10 % 100)
            self.newgamelight = self.secondaryfont.render("Exit", True, (color, color, color))
            self.surf.blit(self.quitlight, (0, 170))
        else:
            self.surf.blit(self.quitdark, (0, 170))
        pygame.display.flip()
