import pygame

class Player():
    
    #========================#
    #==#  Initialization  #==#
    #========================#
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.jump = False
        self.running = False
        self.attacking = False
        self.blocking = False
        self.hit = False
        self.alive = True
        self.attack_type = 0
        self.attack_cooldown = 0
        self.health = 50
        self.energy = 0
        
    #======================#
    #==#  Load Sprites  #==#
    #======================#
    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list
    
    #==============#
    #==#  Draw  #==#
    #==============#
    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        pygame.draw.rect(surface, (255,0,0), self.rect)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
    
    #==================#
    #==#  Movement  #==#
    #==================#
    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        JUMP_HEIGHT = -30
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0
        
        # get pressed key
        key = pygame.key.get_pressed()
        
        # Controlls
        if self.attacking == False and self.alive == True and round_over == False:
            
            # player 1
            if self.player == 1:
                # block
                if key[pygame.K_1]:
                    self.blocking = True
                else:
                    self.blocking = False
                if not self.blocking:
                    # walk
                    if key[pygame.K_a]:
                        dx = -SPEED
                        self.running = True
                    if key[pygame.K_d]:
                        dx = SPEED
                        self.running = True
                    # jump
                    if key[pygame.K_w] and self.jump == False:
                        self.vel_y = JUMP_HEIGHT
                        self.jump = True
                    # attack
                    self.handle_attacks(key, surface, target)
            
            # player 2  
            if self.player == 2:
                # block
                if key[pygame.K_m]:
                    self.blocking = True
                else:
                    self.blocking = False
                if not self.blocking:
                    # walk
                    if key[pygame.K_LEFT]:
                        dx = -SPEED
                        self.running = True
                    if key[pygame.K_RIGHT]:
                        dx = SPEED
                        self.running = True
                    # jump
                    if key[pygame.K_UP] and self.jump == False:
                        self.vel_y = JUMP_HEIGHT
                        self.jump = True
                    # attack
                    self.handle_attacks(key, surface, target)
                
        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y
            
        # limit screen area
        if self.rect.left + dx < 0: # X axis
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width -self.rect.right
        if self.rect.bottom + dy > screen_height - 110: # Y axis
            self.vel_y = 0
            self.jump = False # restart jump delay
            dy = screen_height - 110 - self.rect.bottom
             
        # ensure player face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True
        
        # apply attack cooldown
        if self.attack_cooldown >0:
            self.attack_cooldown -= 1
        
        # update position
        self.rect.x += dx
        self.rect.y += dy
        
    #========================# 
    #==#  Handle Attacks  #==#
    #========================#
    def handle_attacks(self, key, surface, target):
        if self.player == 1: # P1 Attack controls
            if key[pygame.K_2] or key[pygame.K_3]:
                if key[pygame.K_2]:
                    self.attack_type = 1
                elif key[pygame.K_3]:
                    self.attack_type = 2
                self.attack(surface, target)    
        elif self.player == 2: # P2 Attack controls 
            if key[pygame.K_COMMA] or key[pygame.K_PERIOD]:
                if key[pygame.K_COMMA]:
                    self.attack_type = 1
                elif key[pygame.K_PERIOD]:
                    self.attack_type = 2
                self.attack(surface, target)
        
    #===================# 
    #==#  Animation  #==#
    #===================#
    def update(self): #handle animation updates
        # Checks current action
        if self.energy >= 100:
            self.energy = 100
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(9) #9: death
        elif self.blocking:
            self.update_action(7) #7: block
        elif self.hit == True:
            self.update_action(8) #8: hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(4) #4: attack 1
            elif self.attack_type == 2:
                self.update_action(5) #5: attack 2
        elif self.jump == True:
            self.update_action(3) #3: jump
        elif self.running == True:
            self.update_action(2) #2: run
        else:
            self.update_action(0) #0: idle
        
        # updates image
        animation_cooldown = 60 #sprite speed
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown: # Checks time to update
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # Checks if the animation finished
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.alive== False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0 # restart sprite
                # Checks if the attack was excecuted
                if self.action == 4 or self.action == 5:
                    self.attacking = False
                    self.attack_cooldown = 30 # attack cooldown
                # Checks if damage was taken
                if self.action == 8:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 30 # hurt cooldown
            
            
    #================#
    #==#  Attack  #==#
    #================#
    def attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
                # Config range and attack according to attack type
            if self.attack_type == 1:
                # Attack Type 1: Low Range More Damage
                attack_width = self.rect.width * 1.5  
                damage = 10 
            elif self.attack_type == 2:
                # Attack Type 2: More Range Low Damage
                attack_width = self.rect.width * 2
                damage = 5

            # Creates attack area
            attacking_rect = pygame.Rect(
                self.rect.centerx - (attack_width * self.flip),
                self.rect.y,
                attack_width,
                self.rect.height
            )

            # Check if collision happened
            if attacking_rect.colliderect(target.rect):
                if target.blocking:
                    self.energy += 10
                else:
                    target.health -= damage
                    target.hit = True
                    self.energy += 20

            # Draw hit area on green for debug
            pygame.draw.rect(surface, (0, 255, 0), attacking_rect)
            
            
    #================#
    #==#  Update  #==#
    #================#
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()