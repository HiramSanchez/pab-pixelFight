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
# Timer variables
ROUND_TIME_LIMIT = 14 * 1000  # 90 seconds in milliseconds + 4 of intro
round_start_time = pygame.time.get_ticks()
time_left = ROUND_TIME_LIMIT / 1000  # Initialize with total seconds
# Colors
GREEN = (23,193,36)
RED = (163,41,41)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLUE = (4, 28, 49)
CYAN = (15,158,234)
# Game Variables
intro_count = 3
show_fight_time = 1000  # Time that "FIGHT!" shows in miliseconds
fight_displayed = False
fight_display_start = 0
last_count_update = pygame.time.get_ticks()
score = [0, 0] # player score [player1, player2]
round_over = False
ROUND_OVER_COOLDOWN =2000
# Text Variables
max_text_visible = True
max_last_blink_time = pygame.time.get_ticks()
MAX_BLINK_INTERVAL = 500
# Load Assets
bg_image = pygame.image.load("assets\\images\\backgrounds\\battleground.png").convert_alpha()
skull_icon = pygame.image.load("assets\\images\\icons\\skull.png").convert_alpha()

#===========================#
#==#  Fighter Variables  #==#
#===========================#
# Scale  Player 1
FIGHTER1_NAME = "Bam"
FIGHTER1_SIZE = 266.7
FIGHTER1_SCALE = 0.9
FIGHTER1_OFFSET = [94,65]
FIGHTER1_FREEZE_OFFSET = [-85,-60]
FIGHTER1_DATA = [FIGHTER1_SIZE, FIGHTER1_SCALE, FIGHTER1_OFFSET, FIGHTER1_NAME]
# Scale  Player 2
FIGHTER2_NAME = "Onichan"
FIGHTER2_SIZE = 128
FIGHTER2_SCALE = 2
FIGHTER2_OFFSET =[44,38]
FIGHTER2_FREEZE_OFFSET = [-88,-75]
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

# Draw Timer 
def draw_timer(time_left):
    time_text = f"{int(time_left):02}"
    if time_left <= ((ROUND_TIME_LIMIT/1000)-3):
        draw_text(time_text, count_font, WHITE, SCREEN_WIDTH / 2, 35)

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
        pygame.draw.rect(screen, BLUE, (x, y, 200, 20))
        if flip:
            # IF Player 2, Bar grows to the left
            pygame.draw.rect(screen, CYAN, (x + (200 * (1 - ratio)), y, 200 * ratio, 20))
        else:
            # IF Player 1, Bar grows to the right
            pygame.draw.rect(screen, CYAN, (x, y, 200 * ratio, 20))
            
# Draw blinking MAX if Full energy       
def draw_max_energy_text(player, energy, x, y):
    global max_text_visible, max_last_blink_time

    # Verifica si la energía está al máximo
    if energy >= 100:
        current_time = pygame.time.get_ticks()
        # Alterna la visibilidad cada intervalo de tiempo
        if current_time - max_last_blink_time >= MAX_BLINK_INTERVAL:
            max_text_visible = not max_text_visible
            max_last_blink_time = current_time
        # Dibuja "MAX" si es visible en este momento
        if max_text_visible:
            if player == 1:
                # Mostrar a la derecha de la barra de energía
                draw_text("MAX", score_font, CYAN, x + 240, y + 10)
            elif player == 2:
                # Mostrar a la izquierda de la barra de energía
                draw_text("MAX", score_font, CYAN, x - 40, y + 10)
            
#=====================#
#==#  Battle Loop  #==#
#=====================#
run = True
while run:
    
    # Add framerate
    clock.tick(FPS)
    
    # Draw & Update timer
    elapsed_time = pygame.time.get_ticks() - round_start_time
    time_left = max(0, (ROUND_TIME_LIMIT - elapsed_time) / 1000)
    
    # Draw elements
    draw_bg()
    draw_timer(time_left)
    draw_UI_bar(1,FIGHTER1_NAME,fighter_1.health, fighter_1.energy, 20, 20, flip=True)
    draw_UI_bar(1,FIGHTER2_NAME,fighter_2.health, fighter_2.energy, 580, 20)
    draw_UI_bar(2,FIGHTER1_NAME,fighter_1.health, fighter_1.energy, 20, 55)
    draw_UI_bar(2,FIGHTER2_NAME,fighter_2.health, fighter_2.energy, 780, 55, flip=True)
    draw_skulls(1,score[0], 388, 60)   # Skulls for player 1
    draw_skulls(2,score[1], 580, 60)  # Skulls for player 2
    draw_max_energy_text(1, fighter_1.energy, 20, 55)
    draw_max_energy_text(2, fighter_2.energy, 780, 55)
    
    # Verify if time over
    if time_left == 0 and not round_over:
        # Check winner
        if fighter_1.health > fighter_2.health:
            winner_name = FIGHTER1_NAME
            score[1] += 1  # Player 1 wins
        elif fighter_2.health > fighter_1.health:
            winner_name = FIGHTER2_NAME
            score[0] += 1  # Player 2 wins
        else:
            winner_name = "Draw" # Draw
        round_over = True
        round_over_time = pygame.time.get_ticks()

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
            round_start_time = pygame.time.get_ticks()  # Reestart timer
            round_over = False
            intro_count = 3
            fight_displayed = False
            fighter_1 = Player(1, 200, 310, False, FIGHTER1_DATA, player_1_sheet, PLAYER1_ANIMATION_STEPS)
            fighter_2 = Player(2, 700, 310, True, FIGHTER2_DATA, player_2_sheet, PLAYER2_ANIMATION_STEPS)
     
    # Manage frozen status        
    if fighter_1.frozen or fighter_2.frozen:
        if fighter_1.frozen:
            frozenChar = fighter_1
            frozenOffset = FIGHTER1_FREEZE_OFFSET
        elif fighter_2.frozen:
            frozenChar = fighter_2
            frozenOffset = FIGHTER2_FREEZE_OFFSET
        # Create Blue mask 
        enemy_mask = pygame.mask.from_surface(frozenChar.image)
        blue_effect = pygame.Surface(frozenChar.image.get_size(), pygame.SRCALPHA)
        for x in range(blue_effect.get_width()):
            for y in range(blue_effect.get_height()):
                if enemy_mask.get_at((x, y)):  # mask if pixel
                    blue_effect.set_at((x, y), (15,158,234, 100))  # add transparent blue
        # flip if char flips
        if frozenChar.flip:
            flipped_blue_effect = pygame.transform.flip(blue_effect, True, False)
            screen.blit(flipped_blue_effect, (frozenChar.rect.x + frozenOffset[0], frozenChar.rect.y + frozenOffset[1]))
        elif frozenChar.flip == False:    
            screen.blit(blue_effect, (frozenChar.rect.x + frozenOffset[0], frozenChar.rect.y + frozenOffset[1]))
    
    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False  
    pygame.display.update() # Update display          
pygame.quit() # Exit Pygame