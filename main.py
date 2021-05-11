import pygame
import os
import random
import time

#initializing fonts
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)

#   GAME WINDOW
WIN = pygame.display.set_mode((WIDTH,HEIGHT))

pygame.display.set_caption("Space Shooter")


#   LOADING IMAGES

#enemy ships
RED_SPACE_SHIP = pygame.image.load(os.path.join('assets','pixel_ship_red_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets','pixel_ship_green_small.png'))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join('assets','pixel_ship_blue_small.png'))


#player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets','pixel_ship_yellow.png'))

#lasers

RED_LASER = pygame.image.load(os.path.join('assets','pixel_laser_red.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets','pixel_laser_green.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets','pixel_laser_blue.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assets','pixel_laser_yellow.png'))

#background image

BG = pygame.image.load(os.path.join('assets','background-black.png'))

#scaling background to fit window
BG = pygame.transform.scale(BG,(WIDTH,HEIGHT))


#creating laser class
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img, (self.x, self.y))

    def move(self,vel):
        self.y += vel
    
    def off_screen(self,height):
        return not (self.y <= height and self.y >= 0)

    def collision(self,obj):
        return collide(obj,self)


#creating ship class

class Ship:
    COOLDOWN = 30 #HALF A SECOND 
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None    
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0  #keeps up from spamming lasers

    def draw(self,window):
        window.blit(self.ship_img, (self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

            

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0

        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

#player class, inherits from ship
class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)    #lets us ships initialization method on Player
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER

        #making a mask for collisions
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health


    def move_lasers(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:       #for each laser player has
            laser.move(vel)             #move the laser
            if laser.off_screen(HEIGHT):    #if laser is off screen
                self.lasers.remove(laser)   #then remove it
            else:
                for obj in objs:        #if not off screen, for each object in object list
                    if laser.collision(obj):    #if we collide
                        objs.remove(obj)        #then remove the object
                        if laser in self.lasers:
                            self.lasers.remove(laser)   #remove the laser

    def healthbar(self,window):
        pygame.draw.rect(window,RED,(self.x,self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(),10))
        pygame.draw.rect(window,GREEN,(self.x,self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health),10))


    def draw(self,window):
        super().draw(window)
        self.healthbar(window)


#enemy ship class
class Enemy(Ship):
    #creating a map/dict that will allow us to type a string
    #and get correct images
    COLOR_MAP = {"red" : (RED_SPACE_SHIP,RED_LASER),
                 "green" : (GREEN_SPACE_SHIP, GREEN_LASER),
                 "blue" : (BLUE_SPACE_SHIP, BLUE_LASER)
    
    }
    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]

        self.mask = pygame.mask.from_surface(self.ship_img)

    #function to move enemy
    def move(self,vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
        

#collide function

def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None



# main game loop
def main():
    run = True
    FPS = 60    #frames per second
    level = 0   #game level
    lives = 5   #user lives

    enemies = []    #list of enemies

    wave_length = 5     #amount of enemies per round
    enemy_vel = 1

    main_font = pygame.font.SysFont('comicsans',50) #main game font 

    lost_font = pygame.font.SysFont('comicsans',60)

    player_vel = 5
    laser_vel = 5
    #creating ship object
    player = Player(300,630)

    clock = pygame.time.Clock() #initializing clock object

    lost = False

    lost_count = 0

    #redraw window function
    #now all local variables within main are accessible
    #without need to pass parameters

    def redraw_window():
        WIN.blit(BG,(0,0))

        #draw font

        lives_label = main_font.render(f'Lives: {lives}',1,WHITE)   #rendering lives font
        level_label = main_font.render(f'Level: {level}',1,WHITE)   #render level font

        WIN.blit(lives_label,(10,10))
                                    #setting this up dynamically
        WIN.blit(level_label,(WIDTH - level_label.get_width() - 10,10))

        #draw enemies first
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render('You Lost!', 1, WHITE)
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))


        pygame.display.update() #refresh display


    while run:
        clock.tick(FPS)     #this dictates how fast this game will run
        redraw_window()

        # checking if we lose
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:    #showing for 3 seconds
                run = False

            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5

            for i in range (wave_length):   #trying to spawn enemies at differnt locations
                enemy = Enemy(random.randrange(50,WIDTH - 100), random.randrange(-1500,-100),random.choice(['red','blue','green']))
                enemies.append(enemy)
        
        #checking if user quits
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed() #returns dict of keys pressed
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:     #left control
            player.x -= player_vel

        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:    #right control
            player.x += player_vel 

        if keys[pygame.K_UP] and player.y - player_vel > 0:       #up control
            player.y -= player_vel
                                                    #50 = width of our ship
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:   #down control
            player.y += player_vel

        if keys[pygame.K_SPACE]:
            player.shoot()


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0,3*FPS) == 1: #pretty much 1 in 2 chance
                enemy.shoot()

            if collide(enemy,player):   #player and enemy colliding
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

            

        player.move_lasers(-laser_vel, enemies)
        #player needs negative velocity so they go upward


def main_menu():
    title_font = pygame.font.SysFont('comicsans',70)
    run = True
    while run:
        WIN.blit(BG,(0,0))
        title_label = title_font.render('Press the mouse button to begin...',1,WHITE)
        WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

        
main_menu()






