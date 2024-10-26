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
ROUND_TIME_LIMIT = 154 * 1000  # 90 seconds in milliseconds + 4 of intro
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

#======================#
#==#  Fighter List  #==#
#======================#

fighters = [
    {"name": "Raruto", "size": 128, "scale": 1.6, "offset": [34, 15], "freeze_offset": [-55,-23], "animation_steps":[6, 8, 8, 10, 3, 4, 4, 2, 3, 4]},
    {"name": "Starlight", "size": 128, "scale": 2.1, "offset": [45, 41], "freeze_offset": [-95,-87], "animation_steps":[7, 7, 8, 8, 4, 10, 10, 7, 3, 6]},
    {"name": "Onichan", "size": 128, "scale": 2, "offset": [44, 38], "freeze_offset": [-88,-75], "animation_steps":[5, 6, 7, 8, 4, 4, 4, 4, 3, 6]},
    {"name": "Bam", "size": 266, "scale": 0.9, "offset": [94, 65], "freeze_offset": [-85,-60], "animation_steps":[6, 8, 8, 12, 6, 4, 3, 2, 2, 4]}
]

# Show Fighter List
def draw_character_selection(selected, x, y):
    for i, fighter in enumerate(fighters):
        color = GREEN if i == selected else WHITE
        name_text = score_font.render(fighter["name"], True, color)
        screen.blit(name_text, (x, y + i * 50))

# Selector main loop
def character_selection_screen():
    selected_fighter_1 = 0  # P1 Selected index
    selected_fighter_2 = 0  # P2 Selected index

    while True:
        screen.fill(CYAN)  # bg

        # Show fighter list for both
        draw_text("Player 1: Select your fighter", score_font, BLUE, SCREEN_WIDTH / 4, 50)
        draw_character_selection(selected_fighter_1, SCREEN_WIDTH / 4, 100)

        draw_text("Player 2: Select your fighter", score_font, BLUE, 3 * SCREEN_WIDTH / 4, 50)
        draw_character_selection(selected_fighter_2, 3 * SCREEN_WIDTH / 4, 100)
        
        draw_selected_image(screen, str(fighters[selected_fighter_1]['name']), 50, 100)  # Img P1
        draw_selected_image(screen, str(fighters[selected_fighter_2]['name']), 550, 100)  # Img P2   

        pygame.display.update()

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    selected_fighter_1 = (selected_fighter_1 - 1) % len(fighters)
                elif event.key == pygame.K_s:
                    selected_fighter_1 = (selected_fighter_1 + 1) % len(fighters)
                elif event.key == pygame.K_UP:
                    selected_fighter_2 = (selected_fighter_2 - 1) % len(fighters)
                elif event.key == pygame.K_DOWN:
                    selected_fighter_2 = (selected_fighter_2 + 1) % len(fighters)
                elif event.key == pygame.K_RETURN:  # Start with enter
                    return fighters[selected_fighter_1], fighters[selected_fighter_2]     
                
# Image Selector func              
def load_character_image(character_name):
    try:
        path = "assets\\images\\fighters\\"+ character_name +"\\pick.png"
        return pygame.image.load(path).convert_alpha()
    except FileNotFoundError:
        print(f"Img not found for {character_name}")
        return None
# Draw Image - Selector
def draw_selected_image(screen, character_name, x, y):
    image = load_character_image(character_name)
    if image:
        screen.blit(image, (x, y))
    
#========================#
#==#  Draw on Screen  #==#
#========================#
# Constants
WINS_TEXT ="wins"
VICTORY_TEXT ="victory!"
FIGHT_TEXT ="FIGHT!"
count_font = pygame.font.Font("assets\\fonts\\PixelTimesNewRoman.ttf", 80)
score_font = pygame.font.Font("assets\\fonts\\PixelTimesNewRoman.ttf", 40)
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
def draw_UI_bar(type, fighter_name, data, x, y, flip=False):
    if type == 1:
        ratio = data / 100
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
        ratio = data / 100
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
  
#============================#
#==#  Fighters Variables  #==#
#============================#
 
fighter_1_data, fighter_2_data = character_selection_screen()     
# Load sprites
player_1_sheet = pygame.image.load("assets\\images\\fighters\\"+str(fighter_1_data['name'])+"\\spritesheet.png").convert_alpha()
player_2_sheet = pygame.image.load("assets\\images\\fighters\\"+fighter_2_data['name']+"\\spritesheet.png").convert_alpha()
# Create two instances of Players
fighter_1 = Player(1, 200, 310, False, fighter_1_data, player_1_sheet, fighter_1_data['animation_steps'])
fighter_2 = Player(2, 700, 310, True, fighter_2_data, player_2_sheet, fighter_2_data['animation_steps'])    

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
    draw_UI_bar(1,fighter_1_data['name'], fighter_1.health, 20, 20, flip=True)
    draw_UI_bar(1,fighter_2_data['name'], fighter_2.health, 580, 20)
    draw_UI_bar(2,fighter_1_data['name'], fighter_1.energy, 20, 55)
    draw_UI_bar(2,fighter_2_data['name'], fighter_2.energy, 780, 55, flip=True)
    draw_skulls(1,score[0], 388, 60)   # Skulls for player 1
    draw_skulls(2,score[1], 580, 60)  # Skulls for player 2
    draw_max_energy_text(1, fighter_1.energy, 20, 55)
    draw_max_energy_text(2, fighter_2.energy, 780, 55)
    
    # Verify if time over
    if time_left == 0 and not round_over:
        # Check winner
        if fighter_1.health > fighter_2.health:
            winner_name = fighter_1_data['name']
            score[1] += 1  # Player 1 wins
        elif fighter_2.health > fighter_1.health:
            winner_name = fighter_2_data['name']
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
            winner_name = fighter_2_data['name']
            round_over = True
            round_over_time = pygame.time.get_ticks()
        elif fighter_2.alive == False:
            score[1] += 1 # Increase dead count
            winner_name = fighter_1_data['name']
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
            fighter_1 = Player(1, 200, 310, False, fighter_1_data, player_1_sheet, fighter_1_data['animation_steps'])
            fighter_2 = Player(2, 700, 310, True, fighter_2_data, player_2_sheet, fighter_2_data['animation_steps'])
     
    # Manage frozen status        
    if fighter_1.frozen or fighter_2.frozen:
        if fighter_1.frozen:
            frozenChar = fighter_1
            frozenOffset = fighter_1_data['freeze_offset']
        elif fighter_2.frozen:
            frozenChar = fighter_2
            frozenOffset = fighter_2_data['freeze_offset']
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