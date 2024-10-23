import pygame
from player import Player

pygame.init()

#============================#
#==#  Create game window  #==#
#============================#
# Window Set Up
SCREEN_WIDTH=1000
SCREEN_HEIGHT=600
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Fight")
 # Set Framerate
clock = pygame.time.Clock()
FPS = 60
# Define colors
GREEN = (0,255,0)
RED = (255,0,0)
WHITE = (255,255,255)
# Define fighter variables
FIGHTER1_SIZE = 266.7
FIGHTER1_SCALE = 0.9
FIGHTER1_OFFSET = [94,65]
FIGHTER1_DATA = [FIGHTER1_SIZE, FIGHTER1_SCALE, FIGHTER1_OFFSET]
FIGHTER2_SIZE = 128
FIGHTER2_SCALE = 2
FIGHTER2_OFFSET =[44,38]
FIGHTER2_DATA = [FIGHTER2_SIZE, FIGHTER2_SCALE, FIGHTER2_OFFSET]
# Load data
player_1_sheet = pygame.image.load("assets\\images\\fighters\\bam\\spritesheet.png").convert_alpha()
player_2_sheet = pygame.image.load("assets\\images\\fighters\\onichan\\spritesheet.png").convert_alpha()
bg_image = pygame.image.load("assets\\images\\backgrounds\\battleground.png").convert_alpha()
# Define steps of each animation
PLAYER1_ANIMATION_STEPS = [6,8,8,12,6,4,3,2,2,4]
PLAYER2_ANIMATION_STEPS = [5,6,7,8,4,4,4,4,3,6]
# Drawing & Scaling Background
def draw_bg():
    scale_bg = pygame.transform.scale(bg_image,(SCREEN_WIDTH,SCREEN_HEIGHT))
    screen.blit(scale_bg,(0,0))
# Drawing health bars
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, GREEN, (x, y, 400 * ratio, 30))
# Create two instances of Players
fighter_1 = Player(1, 200, 310, False, FIGHTER1_DATA, player_1_sheet, PLAYER1_ANIMATION_STEPS)
fighter_2 = Player(2, 700, 310, True, FIGHTER2_DATA, player_2_sheet, PLAYER2_ANIMATION_STEPS)

#===================#
#==#  Game Loop  #==#
#===================#
run = True
while run:
    clock.tick(FPS) # Add framerate
    # Draw bg
    draw_bg()
    # Draw health bar
    draw_health_bar(fighter_1.health,20,20)
    draw_health_bar(fighter_2.health,580,20)
    # Move fighters
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2)
    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1)
    # Update fighters
    fighter_1.update()
    fighter_2.update()
    # Draw fighters
    fighter_1.draw(screen)
    fighter_2.draw(screen)
    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False  
    pygame.display.update() # Update display          
pygame.quit() # Exit Pygame