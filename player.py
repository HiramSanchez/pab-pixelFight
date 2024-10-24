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
        self.hit = False
        self.alive = True
        self.attack_type = 0
        self.attack_cooldown = 0
        self.health = 100
        
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
                # walk
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                # jump
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y = -33
                    self.jump = True
                # attack
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(surface, target)
                    #determine used attack
                    if key [pygame.K_r]:
                        self.attack_type = 1
                    if key [pygame.K_t]:
                        self.attack_type = 2
            
            # player 2  
            if self.player == 2:
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                # jump
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -33
                    self.jump = True
                # attack
                if key[pygame.K_k] or key[pygame.K_l]:
                    self.attack(surface, target)
                    #determine used attack
                    if key [pygame.K_k]:
                        self.attack_type = 1
                    if key [pygame.K_l]:
                        self.attack_type = 2
                
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
        
        
    #===================# 
    #==#  Animation  #==#
    #===================#
    def update(self): #handle animation updates
        # Checks current action
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(9) #9: death
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
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True
            pygame.draw.rect(surface, (0,255,0), attacking_rect)
            
            
    #================#
    #==#  Update  #==#
    #================#
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()