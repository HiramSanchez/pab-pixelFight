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
BLUE = (0, 0, 255)
# Game Variablesd
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
WINS_TEXT ="wins"
VICTORY_TEXT ="victory!"
FIGHT_TEXT ="FIGHT!"
count_font = pygame.font.Font("assets\\fonts\\HelvetiPixel.ttf", 80)
score_font = pygame.font.Font("assets\\fonts\\HelvetiPixel.ttf", 40)
# Draw centered text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    text_rect = img.get_rect(center=(x, y))
    screen.blit(img, text_rect)
# Draw skulls according to deaths
def draw_skulls(player,player_score, x, y):
    # 2 skulls max
    for i in range(min(player_score, 2)):
        if player == 1:
            screen.blit(skull_icon, (x - i * (skull_icon.get_width() + 5), y))
        elif player ==2:
            flipped_skull = pygame.transform.flip(skull_icon, True, False)
            screen.blit(flipped_skull, (x + i * (flipped_skull.get_width() + 5), y))
# Draw & Scale Background
def draw_bg():
    scale_bg = pygame.transform.scale(bg_image,(SCREEN_WIDTH,SCREEN_HEIGHT))
    screen.blit(scale_bg,(0,0))

# Draw UI Bars - health (type 1) & Energy (type 2)
def draw_UI_bar(type, fighter_name, health, energy, x, y, flip=False):
    if type == 1:
        ratio = health / 100
        pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
        pygame.draw.rect(screen, RED, (x, y, 400, 30))
        name_img = score_font.render(fighter_name, True, WHITE)
        if flip:
            # IF Player 1, Bar reduces to the Right
            name_rect = name_img.get_rect(midleft=(x + 5, y + 15))
            pygame.draw.rect(screen, GREEN, (x + (400 * (1 - ratio)), y, 400 * ratio, 30))
        else:
            # IF Player 2, Bar reduces to the Left
            name_rect = name_img.get_rect(midright=(x + 400 - 5, y + 15))
            pygame.draw.rect(screen, GREEN, (x, y, 400 * ratio, 30))
        screen.blit(name_img, name_rect)
    elif type == 2:
        ratio = energy / 100
        pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 204, 24))
        if flip:
            # IF Player 2, Bar grows to the left
            pygame.draw.rect(screen, BLUE, (x + (200 * (1 - ratio)), y, 200 * ratio, 20))
        else:
            # IF Player 1, Bar grows to the right
            pygame.draw.rect(screen, BLUE, (x, y, 200 * ratio, 20))
            
    
#===========================#
#==#  Fighter Variables  #==#
#===========================#
# Scale  Player 1
FIGHTER1_NAME = "Bam"
FIGHTER1_SIZE = 266.7
FIGHTER1_SCALE = 0.9
FIGHTER1_OFFSET = [94,65]
FIGHTER1_DATA = [FIGHTER1_SIZE, FIGHTER1_SCALE, FIGHTER1_OFFSET, FIGHTER1_NAME]
# Scale  Player 2
FIGHTER2_NAME = "Onichan"
FIGHTER2_SIZE = 128
FIGHTER2_SCALE = 2
FIGHTER2_OFFSET =[44,38]
FIGHTER2_DATA = [FIGHTER2_SIZE, FIGHTER2_SCALE, FIGHTER2_OFFSET, FIGHTER2_NAME]
# Animation Steps
PLAYER1_ANIMATION_STEPS = [6,8,8,12,6,4,3,2,2,4]
PLAYER2_ANIMATION_STEPS = [5,6,7,8,4,4,4,4,3,6]
# Load sprites
player_1_sheet = pygame.image.load("assets\\images\\fighters\\"+FIGHTER1_NAME+"\\spritesheet.png").convert_alpha()
player_2_sheet = pygame.image.load("assets\\images\\fighters\\"+FIGHTER2_NAME+"\\spritesheet.png").convert_alpha()
# Create two instances of Players
fighter_1 = Player(1, 200, 310, False, FIGHTER1_DATA, player_1_sheet, PLAYER1_ANIMATION_STEPS)
fighter_2 = Player(2, 700, 310, True, FIGHTER2_DATA, player_2_sheet, PLAYER2_ANIMATION_STEPS)

#=====================#
#==#  Battle Loop  #==#
#=====================#
run = True
while run:
    
    # Add framerate
    clock.tick(FPS)
    # Draw elements
    draw_bg()
    draw_UI_bar(1,FIGHTER1_NAME,fighter_1.health, fighter_1.energy, 20, 20, flip=True)
    draw_UI_bar(1,FIGHTER2_NAME,fighter_2.health, fighter_2.energy, 580, 20)
    draw_UI_bar(2,FIGHTER1_NAME,fighter_1.health, fighter_1.energy, 20, 55)
    draw_UI_bar(2,FIGHTER2_NAME,fighter_2.health, fighter_2.energy, 780, 55, flip=True)
    draw_skulls(1,score[0], 388, 60)   # Skulls for player 1
    draw_skulls(2,score[1], 580, 60)  # Skulls for player 2
    
    if fighter_1.frozen or fighter_2.frozen:
        if fighter_1.frozen:
            freeze_overlay = pygame.Surface((128,128), pygame.SRCALPHA)
            freeze_overlay.fill((0, 0, 255, 100))
            
        

    # Count & "FIGHT!" screen logic
    if intro_count > 0:
        draw_text(str(intro_count), count_font, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        if pygame.time.get_ticks() - last_count_update >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()
    elif not fight_displayed:
        # Show "FIGHT!" at start each round
        draw_text(FIGHT_TEXT, count_font, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 180)
        fight_display_start = pygame.time.get_ticks()
        fight_displayed = True
    elif pygame.time.get_ticks() - fight_display_start < show_fight_time:
        # Keep showing "FIGHT!" while time asigned
        draw_text(FIGHT_TEXT, count_font, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 180)
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
            winner_name = FIGHTER2_NAME
            round_over = True
            round_over_time = pygame.time.get_ticks()
        elif fighter_2.alive == False:
            score[1] += 1 # Increase dead count
            winner_name = FIGHTER1_NAME
            round_over = True
            round_over_time = pygame.time.get_ticks()
    else:
        if score[0] == 3 or score[1] == 3:
            # Show "victory!" & close game AFTER cooldown
            draw_text(winner_name, count_font, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 180)
            draw_text("victory!", count_font, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 130)
            pygame.display.update()
            pygame.time.wait(2000)  # wait 2 seconds before closing
            run = False  # Close Game
        else:
            # Show winner name + "wins" IF less than 3 wins
            draw_text(winner_name, count_font, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 180)
            draw_text(WINS_TEXT, count_font, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 130)

        
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