import pygame
import random
import math
import time

pygame.font.init()

WIDTH, HEIGHT = 900, 300
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Dinosaur Jump")

def load_and_scale(image_path, scale=0.7):
    image = pygame.image.load(image_path)
    return pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))

cactus_paths = [
    "./assets/smallcactus.png",
    "./assets/2smallcactus.png",
    "./assets/bigcactus.png",
    "./assets/2bigcactus.png",
    "./assets/3smallcactus.png",
    "./assets/3bigcactus.png",
]

cacti = list(map(load_and_scale, cactus_paths))

dino_paths = [
    "./assets/dino_run1.png",
    "./assets/dino_run2.png",
    "./assets/dino_jump.png",
    "./assets/dino_crouch1.png",
    "./assets/dino_crouch2.png"
]

dinos = list(map(lambda path: load_and_scale(path, scale=0.6), dino_paths))

class Dino:
    SPRITES = dinos
    DEFAULT_JUMP_HEIGHT = 50
    JUMP_ACCEL = -0.8
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.orig_y = y
        self.dino_index = 0
        self.dino = self.SPRITES[self.dino_index]
        self.jumping = False
        self.jump_height = self.DEFAULT_JUMP_HEIGHT
        self.alive = True
        self.crouching = False
        self.jumping_down = False
        self.crouch_set = False
                
    def jump(self):
        self.jumping = True
    
    def crouch(self):
        if self.jumping:
            self.jumping_down = True
        else:
            self.crouching = True
        
    def uncrouch(self):
        if self.crouching:
            self.crouching = False
        
    def update(self, game_speed):
        if self.jumping:
            if self.jump_height >= -self.DEFAULT_JUMP_HEIGHT:
                if self.jump_height >= 0:
                    self.y -= (self.jump_height ** 2) * 0.002 * (game_speed ** 0.7)
                else:
                    if self.jumping_down:
                        self.y += (self.jump_height ** 2) * 0.008 * (game_speed ** 0.7)
                    else:
                        self.y += (self.jump_height ** 2) * 0.002 * (game_speed ** 0.7)
                
                if self.jumping_down:
                    self.jump_height += self.JUMP_ACCEL * 4 * (game_speed ** 0.7)
                else:    
                    self.jump_height += self.JUMP_ACCEL * (game_speed ** 0.7)
                self.dino_index = 2
            
            
            else:
                self.jump_height = self.DEFAULT_JUMP_HEIGHT
                self.y = self.orig_y
                self.dino_index = 0
                                                        
            if self.y == self.orig_y:
                self.jumping = False
                self.jumping_down = False
        
        elif self.crouching:
            if not self.crouch_set:
                self.dino_index = 4 if self.dino_index % 2 else 3
            self.crouch_set = True
        
        else:
            self.crouch_set = False
            self.dino_index = int(not self.dino_index)
        
        if self.dino_index in [3, 4]:
            self.dino_index = 4 if self.dino_index % 2 else 3
        
        print(self.crouching)
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

    
def main(debug=True):
    road = load_and_scale("./assets/road.png", 1)

    road_width = road.get_width()
    road_tiles = math.ceil(WIDTH/road_width) + 1
    road_location = random.randint(-road_width, 0)
    if debug: road_rect = road.get_rect()
    
    dino = Dino(100, HEIGHT-110)
    cactus = Cactus(road_width + 10, HEIGHT-60)
    cactus2 = Cactus(road_width + 10 + random.randint(625, 650), HEIGHT-60)
    game_speed = 10
    
    clock = pygame.time.Clock()
    font = pygame.font.Font("./font/PressStart2P-Regular.ttf", 18)
    max_score = 0
    time.sleep(1)
    while True and dino.alive:
        clock.tick(60)
        # game_speed += 0.00001
        # game_speed = min(5, game_speed)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    print("JUMP")
                    dino.jump()
                if event.key == pygame.K_DOWN:
                    if not dino.crouching:
                        print("CROUCH")
                        dino.crouch()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    print("UNCROUCH")
                    dino.uncrouch()
            
        max_score += 0.05
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
        
        if cactus2.x < -cactus2.get_dims()[1]:
            cactus2 = Cactus(WIDTH+random.randint(600, 625), HEIGHT-60)
        
        if cactus.check_collision(dino) or cactus2.check_collision(dino):
            dino.alive = False
                        
        dino.draw(WIN, game_speed)
        if debug:
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
        
        score_text = font.render(f"Score: {int(max_score*game_speed)}", True, (100, 100, 100))
        WIN.blit(score_text, (WIDTH-score_text.get_width()-25, 70))
        pygame.display.update()

def run():
    main()
    
if __name__ == "__main__":
    run()