import pygame
import neat
import time
import random
import os
import pickle
import easygui

"""  Resources """

screen_width = 600
screen_height = 800

""" gloabal variables """
GEN_COUNTER = 0

# Get number of max generations
validate = False
while (validate == False):
    maxGen = easygui.enterbox("Enter max number of allowed generations\n (above 30 is recommended)","Bird Trainer")

    if int(maxGen) >= 1:
        validate = True

# Get score goal
validate = False
while (validate == False):
    goalScore = easygui.enterbox("Enter goal score (above 100 is recommended)", "Bird Trainer")

    if int(goalScore) >= 1:
        validate = True

# window
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bird Trainer")

# Images
""" Bird Imahes """
Bird_Imags = [pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird" + str(x) + ".png"))) for x in range(1,4)]

""" Background Image"""
BG_image = pygame.transform.scale(pygame.image.load(os.path.join("images","bg.png")).convert_alpha(), (600, 900))

""" Pipe """
pipe_image = pygame.transform.scale2x(pygame.image.load(os.path.join("images","pipe.png")).convert_alpha())

""" Base """
base_image = pygame.transform.scale2x(pygame.image.load(os.path.join("images","base.png")).convert_alpha())

""" Pygame window """

pygame.display.set_icon(Bird_Imags[0])

# Fonts
pygame.font.init()
myFont = pygame.font.SysFont(None, 50)


""" Classes """
class Bird:
    
    # Bird physics
    MAX_ROTATION = 25
    ROT_VELOCITY = 20
    ANIMATION_TIME = 5
    img = Bird_Imags[0]

    def __init__(self, y, x):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        

    """ Make bird jump method """
    def jump(self):

        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
    
    """ Move bird method"""
    def move(self):

        # keep track of jumps
        self.tick_count += 1

        # pixels move calculation (displacement formula)
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2

        # control velocity (terminal velocity)
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16
        
        if displacement < 0:
            displacement -= 2
        
        # move bird
        self.y = self.y + displacement

        # go up
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        
        # go down
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VELOCITY
    
    """ draw bird depending on animation time method """
    def draw(self, win):
        self.img_count += 1

        if self.img_count <= self.ANIMATION_TIME:
            self.img = Bird_Imags[0]

        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = Bird_Imags[1]
        
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = Bird_Imags[2]

        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = Bird_Imags[1]
        
        elif self.img_count <= self.ANIMATION_TIME*4+1:
            self.img = Bird_Imags[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = Bird_Imags[1]
            self.img_count = self.ANIMATION_TIME*2
        

        # rotate image
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft= (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    """ ruturn bird mask for collision """
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


""" Pipe Class """
class Pipe():

    pipe_gap = 200
    pipe_vel = 5

    def __init__(self, x):
        self.x = x
        self.height = 100
        

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(pipe_image, False, True)
        self.PIPE_BOTTOM = pipe_image

        self.passed = False
        self.set_hight()
    
    def set_hight(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.pipe_gap
    
    def move(self):
        self.x -= self.pipe_vel

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
    
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # how far away are bottom and top
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # find collision point
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)  # collision with pipe bottom 
        top_point = bird_mask.overlap(top_mask, top_offset)  # collision with pipe top

        # returns true if collision is detected
        if bottom_point or top_point:
            return True
        
        else:
            return False


""" Class for based """
class Base:

    VELOCITY = 5
    WIDTH = base_image.get_width()
    img = base_image

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))



""""" Display screen method """""
def draw_window(win, birds, pipes, base, score, generation):
    
    win.blit(BG_image, (0,0))

    # for loop to draw bases
    for pipe in pipes:
        pipe.draw(win)

    # draw score
    score_text = myFont.render("Score: " + str(score), 1, (255,255,255))
    win.blit(score_text, (screen_width - 10 - score_text.get_width(), 10))

    # draw goal
    goal_text = myFont.render("Goal: " + goalScore, 1, (255,255,255))
    win.blit(goal_text, (screen_width - 10 - score_text.get_width(), 50))

    # draw generation
    gen_text = myFont.render(f"Generation: {str(generation)} / {maxGen}", 1, (255,255,255))
    win.blit(gen_text, (10,10))

    # draw population
    popu_text = myFont.render("Population: " + str(len(birds)), 1, (255,255,255))
    win.blit(popu_text, (10,50))

    # draw base
    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()

""" 
    Fitness function to evaluate birds
    genomes: nueron networks that control birds
    config: configuration for neuron networks
"""
def fitness(genomes, config):

    """ Get custome score goal """
    

    # Increase counter each time a new generation is created 
    global GEN_COUNTER
    GEN_COUNTER += 1

    """ Objects """
    # bird object list
    birds = []

    # base object
    myBase = Base(730)

    # pipe object
    myPipes = [Pipe(700)]

    # clock
    clock = pygame.time.Clock() 

    # game total score
    score = 0

    """ NEAT lists """
    nets = []
    ge = []

    # create neuron network
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                

        # difine which pipe to look at
        pipe_index = 0
        if len(birds) > 0:
            if len(myPipes) > 1 and birds[0].x > myPipes[0].x + myPipes[0].PIPE_TOP.get_width():
                pipe_index = 1
                
        # no birds left, quit running game/generation
        else:
            run = False
            break

        # move birds    
        for x, bird in enumerate(birds):
            bird.move()

            # set fitness
            ge[x].fitness += 0.1 # every second bird is alive, gain 0.1 fitness

            # active neuron network input
            # pass distance between bird and pipes
            output = nets[x].activate((bird.y, abs(bird.y - myPipes[pipe_index].height), abs(bird.y - myPipes[pipe_index].bottom)))

            # output action if fitness is >= fitness range
            if output[0] > 0.5:
                bird.jump()

        """ Variables """
        # check when to add new pipe flag
        add_pipe = False

        # diplay/move pipes
        remove_pipe = []

        """ Move images """
        for pipe in myPipes:
            
            for x, bird in enumerate(birds):

                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipe.append(pipe)

            pipe.move()

        if add_pipe:

            # increase points when bird pass a pipe
            score += 1

            # increase fitness when a bird pass a pipe
            for g in ge:
                g.fitness += 5
            
            # pipe generation length
            myPipes.append(Pipe(700))
        
        for r in remove_pipe:
            myPipes.remove(r)

        """ If bird touches the floor, end game """
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        myBase.move()

        # Save best bird after achieve score goal
        if score > int(goalScore):

            storeBird = easygui.boolbox("Training complete! Save bird in pkl file?", "Bird Trainer", ("Yes", "No"))

            if storeBird:

                birdName = easygui.enterbox("Enter file name", "Bird Trainer")
                pickle.dump(nets[0],open(f"{birdName}.pickle", "wb"))
                easygui.msgbox("Bird saved! Good bye.")
                quit()

            else:
                easygui.msgbox("Bird was NOT saved! Good bye.")
                quit()


        draw_window(win, birds, myPipes, myBase, score, GEN_COUNTER)

def run(config_path):

    # create configuration object
    config = neat.config.Config(neat.DefaultGenome, 
                                neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, 
                                neat.DefaultStagnation,
                                config_path)

    # create population based on the above configuration
    population = neat.Population(config)

    # stats reporters to give output above generation, fitness, etc
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Initial training
    population.run(fitness, int(maxGen))     

# init game
if __name__ == "__main__":

    # get this file path
    local_dir = os.path.dirname(__file__)

    # join/find config file
    config_path = os.path.join(local_dir, "config-feedforward.txt")

    run(config_path)

    easygui.msgbox("Training failed! Try again", "Bird Trainer")