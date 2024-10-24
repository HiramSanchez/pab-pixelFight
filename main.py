import pygame
from player import Player

#============================#
#==#  Create game window  #==#
#============================#
pygame.init()
# Window Set Up
SCREEN_WIDTH=1000
SCREEN_HEIGHT=600
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Fight")

#========================#
#==#  Game Variables  #==#
#========================#
 # Set Framerate
clock = pygame.time.Clock()
FPS = 60
# Colors
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)
# Game Variables
intro_count = 3
show_fight_time = 1000  # Time that "FIGHT!" shows in miliseconds
fight_displayed = False
fight_display_start = 0
last_count_update = pygame.time.get_ticks()
score = [0, 0] # player score [player1, player2]
round_over = False
ROUND_OVER_COOLDOWN =2000
# Load Assets
bg_image = pygame.image.load("assets\\images\\backgrounds\\battleground.png").convert_alpha()
skull_icon = pygame.image.load("assets\\images\\icons\\skull.png").convert_alpha()

#========================#
#==#  Draw on Screen  #==#
#========================#
# Constants
WIN_TEXT ="VICTORY"
FIGHT_TEXT ="FIGHT!"
count_font = pygame.font.Font("assets\\fonts\\HelvetiPixel.ttf", 80)
score_font = pygame.font.Font("assets\\fonts\\HelvetiPixel.ttf", 40)
# Draw text as required
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
# Draw skulls according to deaths
def draw_skulls(player,player_score, x, y):
    # 2 skulls max
    for i in range(min(player_score, 2)):
        if player == 1:
            screen.blit(skull_icon, (x - i * (skull_icon.get_width() + 5), y))
        elif player ==2:
            screen.blit(skull_icon, (x + i * (skull_icon.get_width() + 5), y))
# Draw & Scale Background
def draw_bg():
    scale_bg = pygame.transform.scale(bg_image,(SCREEN_WIDTH,SCREEN_HEIGHT))
    screen.blit(scale_bg,(0,0))
# Draw health bars
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, GREEN, (x, y, 400 * ratio, 30))
    
#===========================#
#==#  Fighter Variables  #==#
#===========================#
# Scale 
FIGHTER1_SIZE = 266.7
FIGHTER1_SCALE = 0.9
FIGHTER1_OFFSET = [94,65]
FIGHTER1_DATA = [FIGHTER1_SIZE, FIGHTER1_SCALE, FIGHTER1_OFFSET]
FIGHTER2_SIZE = 128
FIGHTER2_SCALE = 2
FIGHTER2_OFFSET =[44,38]
FIGHTER2_DATA = [FIGHTER2_SIZE, FIGHTER2_SCALE, FIGHTER2_OFFSET]
# Load sprites
player_1_sheet = pygame.image.load("assets\\images\\fighters\\bam\\spritesheet.png").convert_alpha()
player_2_sheet = pygame.image.load("assets\\images\\fighters\\onichan\\spritesheet.png").convert_alpha()
# Animation Steps
PLAYER1_ANIMATION_STEPS = [6,8,8,12,6,4,3,2,2,4]
PLAYER2_ANIMATION_STEPS = [5,6,7,8,4,4,4,4,3,6]
# Create two instances of Players
fighter_1 = Player(1, 200, 310, False, FIGHTER1_DATA, player_1_sheet, PLAYER1_ANIMATION_STEPS)
fighter_2 = Player(2, 700, 310, True, FIGHTER2_DATA, player_2_sheet, PLAYER2_ANIMATION_STEPS)

#===================#
#==#  Game Loop  #==#
#===================#
run = True
while run:
    
    # Add framerate
    clock.tick(FPS)
    # Draw elements
    draw_bg()
    draw_health_bar(fighter_1.health,20,20)
    draw_health_bar(fighter_2.health,580,20)
    draw_skulls(1,score[0], 388, 60)   # Skulls for player 1
    draw_skulls(2,score[1], 580, 60)  # Skulls for player 2

    # Count & "FIGHT!" screen logic
    if intro_count > 0:
        draw_text(str(intro_count), count_font, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        if pygame.time.get_ticks() - last_count_update >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()
    elif not fight_displayed:
        # Show "FIGHT!" at start each round
        draw_text(FIGHT_TEXT, count_font, YELLOW, SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 180)
        fight_display_start = pygame.time.get_ticks()
        fight_displayed = True
    elif pygame.time.get_ticks() - fight_display_start < show_fight_time:
        # Keep showing "FIGHT!" while time asigned
        draw_text(FIGHT_TEXT, count_font, YELLOW, SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 180)
    else:
        # When "FIGHT!" time has finished, allow movement
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
        fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
        
    # Update & Draw fighters
    fighter_1.update()
    fighter_2.update()
    fighter_1.draw(screen)
    fighter_2.draw(screen)
    
    # Score & Round Control Logic
    if round_over == False:
        if fighter_1.alive == False:
            score[0] += 1 # Increase dead count
            round_over = True
            round_over_time = pygame.time.get_ticks()
        elif fighter_2.alive == False:
            score[1] += 1 # Increase dead count
            round_over = True
            round_over_time = pygame.time.get_ticks()
    else:
        draw_text(WIN_TEXT, count_font, YELLOW, SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 - 180) # victory print
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3
            fight_displayed = False
            fighter_1 = Player(1, 200, 310, False, FIGHTER1_DATA, player_1_sheet, PLAYER1_ANIMATION_STEPS)
            fighter_2 = Player(2, 700, 310, True, FIGHTER2_DATA, player_2_sheet, PLAYER2_ANIMATION_STEPS)
    
    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False  
    pygame.display.update() # Update display          
pygame.quit() # Exit Pygame