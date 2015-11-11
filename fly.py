



import os, pygame
import random
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound


class Bat(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) 
        self.image, self.rect = load_image('bat.png', -1)
        self.punching = 0

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos
        if self.punching:
            self.rect.move_ip(5, 10)

    def punch(self, target):
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        self.punching = 0


class Fly(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('fly.png', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 20, 20
        self.move = 15
        self.dizzy = 0

    def update(self):
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
	l = [2,-2]
	self.x= random.choice(l)
	self.y=random.choice(l)
        newpos = self.rect.move((self.x, self.y))
        if self.rect.left  < self.area.left :
            self.x = self.x + 2
            newpos = self.rect.move((self.x, self.y))   
        if self.rect.right > self.area.right :
            self.x = self.x - 2
            newpos = self.rect.move((self.x, self.y))
        if self.rect.top  < self.area.top:
            self.y = self.y + 2
            newpos = self.rect.move((self.x, self.y))
        if self.rect.bottom  > self.area.bottom:
            self.y = self.y - 2
            newpos = self.rect.move((self.x, self.y))
        self.rect = newpos

    def _spin(self):
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image
    def punch(self, target):
        "returns true if the fist collides with the target"
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)









def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 360))
    pygame.display.set_caption('Fly swatter')
    pygame.mouse.set_visible(0)


    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    youwin = pygame.image.load("data/youwin.png").convert_alpha()
    gameover = pygame.image.load("data/gameover.png").convert_alpha()
    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("Swat the fly 3 times in 30 seconds", 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2)
        background.blit(text, textpos)
    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()
    whiff_sound = load_sound('whiff.wav')
    punch_sound = load_sound('punch.wav')
    fly = Fly()
    bat = Bat()
    allsprites = pygame.sprite.RenderPlain((bat, fly))
    hit_c = 0
    start_ticks=pygame.time.get_ticks()
    while 1:
        seconds=(pygame.time.get_ticks()-start_ticks)/1000
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                if bat.punch(fly):
                    punch_sound.play() 
                    fly.punched()
                    hit_c += 1
                else:
                    whiff_sound.play() 
            elif event.type is MOUSEBUTTONUP:
                bat.unpunch()

        
        if hit_c >= 3:
            if pygame.font:
                font = pygame.font.Font(None, 36)
                text = font.render("You win. Congrats", 1, (10, 10, 10))
                textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/2)
                youwin.blit(text, textpos)
            screen.blit(youwin, (0, 0))
	elif seconds > 30:
            if pygame.font:
                font = pygame.font.Font(None, 36)
                text = font.render("Sorry, Time out", 1, (10, 10, 10))
                textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/2)
                gameover.blit(text, textpos)
	    screen.blit(gameover, (0, 0))
        else:
	    allsprites.update()
            screen.blit(background, (0, 0))
            allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__': main()
