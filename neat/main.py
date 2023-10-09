import pygame
import random
import math
import neat
import numpy as np
import pickle

pygame.font.init()

WIDTH, HEIGHT = 900, 300
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Dinosaur Jump")

def load_and_scale(image_path, scale=0.7):
    image = pygame.image.load(image_path)
    return pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))

cactus_paths = [
    "../assets/smallcactus.png",
    "../assets/2smallcactus.png",
    "../assets/bigcactus.png",
    "../assets/2bigcactus.png",
    "../assets/3smallcactus.png",
    "../assets/3bigcactus.png",
]

cacti = list(map(load_and_scale, cactus_paths))

dino_paths = [
    "../assets/dino_run1.png",
    "../assets/dino_run2.png",
    "../assets/dino_jump.png",
]

dinos = list(map(lambda path: load_and_scale(path, scale=0.6), dino_paths))

class Dino:
    SPRITES = dinos
    DEFAULT_JUMP_HEIGHT = 65
    JUMP_ACCEL = -1.2
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.orig_y = y
        self.dino_index = 0
        self.dino = self.SPRITES[self.dino_index]
        self.jumping = False
        self.jump_height = self.DEFAULT_JUMP_HEIGHT
        self.alive = True
        
    def jump(self):
        self.jumping = True
    
    def update(self, game_speed):
        if self.jumping:
            if self.jump_height > -self.DEFAULT_JUMP_HEIGHT:
                if self.jump_height >= 0:
                    self.y -= (self.jump_height ** 2) * 0.002 * (game_speed ** 0.25)
                    # self.y -= (self.jump_height ** 2) * 0.002
                else:
                    self.y += (self.jump_height ** 2) * 0.002 * (game_speed ** 0.25)
                    # self.y += (self.jump_height ** 2) * 0.002
                
                self.jump_height += self.JUMP_ACCEL * (game_speed ** 0.25)
                self.dino_index = 2
            
            else:
                self.jump_height = self.DEFAULT_JUMP_HEIGHT
                self.y = self.orig_y
                self.jumping = False
                self.dino_index = 0
            
        if self.dino_index != 2:
            self.dino_index = int(not self.dino_index)
            
        self.dino = self.SPRITES[self.dino_index]

    
    def draw(self, win, game_speed):
        if self.alive: 
            self.update(game_speed)
            win.blit(self.dino, (self.x, self.y))
            # win.blit(self.get_mask().to_surface(), (self.x, self.y))
    
    def get_mask(self):
        return pygame.mask.from_surface(self.dino)
        
    def get_rect(self):
        rect = self.dino.get_rect()
        rect.x = self.x
        rect.y = self.y
        return rect


class Cactus:
    SPRITES = cacti
    WEIGHTS = [11, 10, 9, 4, 5, 3]
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cactus = self.get_cactus()
    
    def get_cactus(self):
        return random.choices(self.SPRITES, weights=self.WEIGHTS, k=5)[random.randint(0, 4)]
    
    def update(self, game_speed):
        self.x -= game_speed 
    
    def draw(self, win, game_speed):
        self.update(game_speed)
        win.blit(self.cactus, (self.x, self.y-self.cactus.get_height()))
        # win.blit(self.get_mask().to_surface(), (self.x, self.y-self.cactus.get_height()))
    
    def get_rect(self):
        rect = self.cactus.get_rect()
        rect.x = self.x
        rect.y = self.y
        return rect
    
    def get_mask(self):
        return pygame.mask.from_surface(self.cactus)
    
    def get_dims(self):
        return [self.cactus.get_height(), self.cactus.get_width()]
    
    def check_collision(self, dino):
        dino_rect = dino.get_rect()
        cactus_rect = self.get_rect()
        return pygame.Rect.colliderect(dino_rect, cactus_rect)
        # cactus_mask = self.get_mask()
        # dino_mask = dino.get_mask()
        # offset = (self.x - dino.x, self.y - round(dino.y))
        # o = dino_mask.overlap(cactus_mask, offset)
        # if o:
        #     return True
        # return False

    
gen = 0
def main(genomes, config, debug=True):
    global gen
    
    gen += 1
    road = load_and_scale("../assets/road.png", 1)

    road_width = road.get_width()
    road_tiles = math.ceil(WIDTH/road_width) + 1
    road_location = random.randint(-road_width, 0)
    if debug: road_rect = road.get_rect()
    
    dinos = []
    cactus = Cactus(road_width + 10, HEIGHT-60)
    cactus2 = Cactus(road_width + 10 + random.randint(625, 650), HEIGHT-60)
    game_speed = 0.5
    
    nets = []
    dinos = []
    ge = []
    # dino_outs = []
    
    for _, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        dinos.append(Dino(100, HEIGHT-110))
        ge.append(genome)
        # dino_outs.append(deque([], maxlen=100))

    clock = pygame.time.Clock()
    font = pygame.font.Font("../font/PressStart2P-Regular.ttf", 18)
    cac1_passed = False
    cac2_passed = False
    
    max_score = 0
    while True and len(dinos) > 0:
        # clock.tick(30)
        game_speed += 0.00001
        game_speed = max(5, game_speed)
        WIN.fill((255, 255, 255))
        for i in range(road_tiles):
            WIN.blit(road, ((i*road_width) + road_location, HEIGHT-80))
            if debug: 
                road_rect.y = HEIGHT-80
                road_rect.x = (i * road_width) + road_location
                pygame.draw.rect(WIN, (0, 0, 255), road_rect, 1)

        road_location -= game_speed
        if abs(road_location) > road_width:
            road_location = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
        
        if cactus.x < -cactus.get_dims()[1]:
            cactus = Cactus(WIDTH+random.randint(600, 625), HEIGHT-60)
            cac1_passed = False
        
        if cactus2.x < -cactus2.get_dims()[1]:
            cactus2 = Cactus(WIDTH+random.randint(600, 625), HEIGHT-60)
            cac2_passed = False
        
        for index, dino in enumerate(dinos):
            ge[index].fitness += 0.01
            if ge[index].fitness > max_score:
                max_score = ge[index].fitness
            curr_cactus = [cactus, cactus2][np.argmin([cactus.x, cactus2.x])]
            output = nets[index].activate((curr_cactus.x - dino.x, curr_cactus.get_dims()[0], curr_cactus.get_dims()[1]))
            # output = nets[index].activate((cactus.x - dino.x, cactus.get_dims()[0], cactus.get_dims()[1], cactus2.x - dino.x, cactus2.get_dims()[0], cactus2.get_dims()[1]))
            if output[0] > 0.5: 
                dino.jump()
                ge[index].fitness -= 0.01
                        
            if cactus.check_collision(dino) or cactus2.check_collision(dino):
                dino.alive = False
                ge[index].fitness -= 2
                nets.pop(index)
                ge.pop(index)
                dinos.pop(index)
            
            if cactus.x < dino.x and not cac1_passed:
                ge[index].fitness += 1
                cac1_passed = True
            
            if cactus2.x < dino.x and not cac2_passed:
                ge[index].fitness += 1
                cac2_passed = True
                
            if dino.alive: dino.draw(WIN, game_speed)
            if debug:
                if dino.alive:
                    dino_rect = dino.get_rect()
                    dino_rect.x = dino.x
                    dino_rect.y = dino.y
                    pygame.draw.rect(WIN, (0, 255, 0), dino_rect, 1)

        cactus.draw(WIN, game_speed)
        cactus2.draw(WIN, game_speed)
        if debug:
            cactus_rect = cactus.get_rect()
            cactus_rect.x = cactus.x
            cactus_rect.y = cactus.y-cactus.get_dims()[0]
            cactus_rect2 = cactus.get_rect()
            cactus_rect2.x = cactus.x
            cactus_rect2.y = cactus.y-cactus.get_dims()[0]
            pygame.draw.rect(WIN, (255, 0, 0), cactus_rect2, 1)
            pygame.draw.rect(WIN, (255, 0, 0), cactus_rect, 1)
        
        generation_text = font.render(f"  Gen: {gen}", True, (100, 100, 100))
        alive_text = font.render(f"Alive: {len(dinos)}", True, (100, 100, 100))
        score_text = font.render(f"Best: {int(max_score*game_speed)}", True, (100, 100, 100))
        WIN.blit(generation_text, (WIDTH-generation_text.get_width()-25, 20))
        WIN.blit(alive_text, (WIDTH-alive_text.get_width()-25, 45))
        WIN.blit(score_text, (WIDTH-score_text.get_width()-25, 70))
        
        # if max_score * game_speed > 5000 or max_score > 100:
        #     pickle.dump(nets[0], open("winner.pickle", "wb"))
        #     break
        
        pygame.display.update()

def run():
    neat_config = "./neat-config.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, neat_config)
    
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(main, 200)
    pickle.dump(winner, open("winner.pickle", "wb"))
    print(f"\nBest Genome:\n {str(winner)}")

if __name__ == "__main__":
    run()