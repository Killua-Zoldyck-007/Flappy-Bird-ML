import pygame
import time
import os
import random
import math
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
DEBUG = False
STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (int(self.x), int(self.y))).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

counter=0

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        global counter
        if 26 > counter > 20:
            if counter%2:
                self.height = 50
            else:
                self.height = 450
        else:
            self.height = random.randrange(50, 450)
        if counter==26:
            print('#'*60)
            for num, bird in enumerate(birds):
                print(f'Bird{num}: (Weights: {bird.weights[0]},{bird.weights[1]},{bird.weights[2]}), Rig: {bird.rig}, Min output to jump: {bird.outmin}, Max output to jump: {bird.outmax}')
            print('#'*60)
        counter+=1
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score, gen):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(text, ((WIN_WIDTH - 10 - text.get_width())//2, 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)

    pygame.display.update()

class NeuroBird:
    fitness = 0
    function = lambda _,x: abs(x)
    def __init__(self, weights, rig, outmin, outmax):
        self.bird = Bird(230, 250)
        self.weights = weights
        self.rig = rig
        self.outmin = outmin
        self.outmax = outmax
    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except:
            return getattr(self.bird,name)
    def activate(self, inputs):
        return self.function(sum(map(lambda z:z[0]*z[1], zip(inputs,self.weights)))+self.rig)

birds = []
def main(genomes):
    global counter
    global GEN
    global birds
    counter=0
    GEN += 1

    birds = genomes[:]
    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('Flappy Bird ML')
    clock = pygame.time.Clock()
    genlist = []

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            bird.fitness += 0.1

            output = bird.activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if bird.outmax > output > bird.outmin:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    bird.fitness -= 1
                    genlist.append(birds.pop(x))

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in birds:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                genlist.append(birds.pop(x))

        base.move()
        draw_window(win, birds, pipes, base, score, GEN)
    print(f'GEN: {GEN}, Score: {score}')
    
    return genlist

def breed(a,b):
    if DEBUG:
        print('$'*30)
        print(f'(Weights: {a.weights[0]},{a.weights[1]},{a.weights[2]}), Rig: {a.rig}, Min output to jump: {a.outmin}, Max output to jump: {a.outmax}')
        print(f'(Weights: {b.weights[0]},{b.weights[1]},{b.weights[2]}), Rig: {b.rig}, Min output to jump: {b.outmin}, Max output to jump: {b.outmax}')
        print('$'*30)
    genomes = []
    for i in range(20):
        weight1 = random.randrange(int((min(a.weights[0],b.weights[0])-1)*1000),int((max(a.weights[0],b.weights[0])+1)*1000))/1000
        weight2 = random.randrange(int((min(a.weights[1],b.weights[1])-1)*1000),int((max(a.weights[1],b.weights[1])+1)*1000))/1000
        weight3 = random.randrange(int((min(a.weights[2],b.weights[2])-1)*1000),int((max(a.weights[2],b.weights[2])+1)*1000))/1000
        rig = random.randrange(int((min(a.rig,b.rig)-100)*1000),int((max(a.rig,b.rig)+100)*1000))/1000
        outmin = random.randrange(int((min(a.outmin,b.outmin)-100)*1000),int((max(a.outmin,b.outmin)+100)*1000))/1000
        outmax = random.randrange(int((min(a.outmax,b.outmax)-100)*1000),int((max(a.outmax,b.outmax)+100)*1000))/1000
        genomes.append(NeuroBird((weight1,weight2,weight3),rig, outmin, outmax))
    return genomes

def run():
    ini = 1
    while 1:
        if ini:
            ini = 0
            genomes = []
            for i in range(20):
                genomes.append(NeuroBird((random.randrange(-1000,1001)/1000,)*3,random.randrange(-200000,-100001)/1000,random.randrange(100000,200001)/1000,random.randrange(4000000,4500001)/1000))
            genlist = sorted(main(genomes), key=lambda x: getattr(x, 'fitness'))[::-1]
            newgenlist = breed(genlist[0],genlist[1])
        else:
            genlist = sorted(main(newgenlist), key=lambda x: getattr(x, 'fitness'))[::-1]
            newgenlist = breed(genlist[0],genlist[1])

if __name__ == '__main__':
    run()
