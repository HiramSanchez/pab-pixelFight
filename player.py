import pygame

class Player:

    #========================#
    #==#  Initialization  #==#
    #========================#
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps):
        self.player = player
        self.size = data["size"]
        self.image_scale = data["scale"]
        self.offset = data["offset"]
        self.fighter_name = data["name"]
        self.flip = flip

        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()

        # Gameplay rect (hitbox)
        self.rect = pygame.Rect((x, y, 80, 180))

        # Movement
        self.vel_y = 0
        self.jump = False
        self.running = False

        # Combat state
        self.attacking = False
        self.blocking = False
        self.hit = False
        self.alive = True

        # Attack
        self.attack_type = 0
        self.attack_cooldown = 0

        # Stats
        self.health = 100
        self.energy = 10

        # Spec Moves / Status
        self.dashing = False
        self.dash_speed = 20
        self.dash_duration = 200
        self.dash_start_time = 0

        self.frozen = False
        self.frozen_duration = 3000
        self.freeze_start_time = 0

        self.burned = False
        self.burn_start_time = 0
        self.burn_interval = 2000
        self.burn_ticks = 0

        # Freeze visuals control (NEW)
        self._freeze_frame_locked = False
        self._locked_action = 0
        self._locked_frame_index = 0


    #======================#
    #==#  Load Sprites  #==#
    #======================#
    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, frames_in_row in enumerate(animation_steps):
            temp_img_list = []
            for x in range(frames_in_row):
                temp_img = sprite_sheet.subsurface(
                    x * self.size, y * self.size, self.size, self.size
                )
                temp_img_list.append(
                    pygame.transform.scale(
                        temp_img,
                        (self.size * self.image_scale, self.size * self.image_scale),
                    )
                )
            animation_list.append(temp_img_list)
        return animation_list


    #==============#
    #==#  Draw  #==#
    #==============#
    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(
            img,
            (
                self.rect.x - (self.offset[0] * self.image_scale),
                self.rect.y - (self.offset[1] * self.image_scale),
            ),
        )


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

        key = pygame.key.get_pressed()

        # Mientras frozen: NO input / NO dash start. Solo gravedad y límites.
        if self.attacking == False and self.alive == True and round_over == False and self.frozen == False:

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
                    self.handle_spec_attacks(key, surface, target)

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
                    self.handle_spec_attacks(key, surface, target)

        # Spec Move: Dash (si ya está dashing, se mueve aunque no haya input)
        if self.dashing:
            if pygame.time.get_ticks() - self.dash_start_time < self.dash_duration:
                dx = self.dash_speed if not self.flip else -self.dash_speed
            else:
                self.dashing = False
                self.attack_cooldown = 30

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # limit screen area
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        # ensure player face each other
        self.flip = target.rect.centerx < self.rect.centerx

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # update position
        self.rect.x += dx
        self.rect.y += dy


    #========================#
    #==#  Handle Attacks  #==#
    #========================#
    def handle_attacks(self, key, surface, target):
        if self.player == 1:
            if key[pygame.K_2] or key[pygame.K_3]:
                if key[pygame.K_2]:
                    self.attack_type = 1
                elif key[pygame.K_3]:
                    self.attack_type = 2
                self.attack(surface, target)

        elif self.player == 2:
            if key[pygame.K_COMMA] or key[pygame.K_PERIOD]:
                if key[pygame.K_COMMA]:
                    self.attack_type = 1
                elif key[pygame.K_PERIOD]:
                    self.attack_type = 2
                self.attack(surface, target)

    def handle_spec_attacks(self, key, surface, target):
        # CHANGE: >= 100 (robusto)
        if (
            (key[pygame.K_4] and self.player == 1 and self.energy >= 100)
            or (key[pygame.K_SLASH] and self.player == 2 and self.energy >= 100)
        ):
            if self.fighter_name == "Bam":
                self.attack_type = 3
                self.dash_attack(surface, target)
            else:
                self.attack_type = 3
                self.freeze_attack(surface, target)


    #===================#
    #==#  Animation  #==#
    #===================#
    def update(self):
        now = pygame.time.get_ticks()

        # Clamp
        if self.energy >= 100:
            self.energy = 100
        if self.health >= 100:
            self.health = 100

        # Death
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(9)  # death

        # Freeze timing (mover aquí es más estable)
        if self.frozen:
            if now - self.freeze_start_time >= self.frozen_duration:
                self.frozen = False
                self._freeze_frame_locked = False  # libera frame lock

        # ===== Freeze animation lock (NEW) =====
        # Si está congelado:
        # - bloquea el frame actual (o si está en hit, bloquea el último frame de hit)
        # - NO avanza frame_index
        if self.frozen:
            if not self._freeze_frame_locked:
                # Si ya está en hit, congela en el último frame de hit para efecto "estatua"
                if self.hit or self.action == 8:
                    self._locked_action = 8
                    self._locked_frame_index = len(self.animation_list[8]) - 1
                else:
                    # congela en el frame actual (acción actual)
                    self._locked_action = self.action
                    self._locked_frame_index = self.frame_index

                self._freeze_frame_locked = True

            self.action = self._locked_action
            self.frame_index = max(0, min(self._locked_frame_index, len(self.animation_list[self.action]) - 1))
            self.image = self.animation_list[self.action][self.frame_index]
            return  # IMPORTANT: no seguir con lógica normal de animación

        # ===== Normal state machine =====
        if not self.alive:
            self.update_action(9)
        elif self.blocking:
            self.update_action(7)
        elif self.hit:
            self.update_action(8)
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(4)
            elif self.attack_type == 2:
                self.update_action(5)
            elif self.attack_type == 3:
                self.update_action(6)
        elif self.jump:
            self.update_action(3)
        elif self.running:
            self.update_action(2)
        else:
            self.update_action(0)

        # update frames
        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if now - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = now

        # animation end handling
        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

                # attack finished
                if self.action in (4, 5, 6):
                    self.attacking = False
                    self.attack_cooldown = 30

                # hit finished
                if self.action == 8:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 30


    #=================#
    #==#  Attacks  #==#
    #=================#
    def dash_attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.dashing = True
            self.dash_start_time = pygame.time.get_ticks()
            self.energy -= 100

            attack_width = self.rect.width * 3.25
            attacking_rect = pygame.Rect(
                self.rect.centerx - (attack_width * self.flip),
                self.rect.y,
                attack_width,
                self.rect.height,
            )

            if attacking_rect.colliderect(target.rect):
                if not target.blocking:
                    if self.fighter_name == "Bam":
                        target.health -= 35
                        target.hit = True

    def attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True

            if self.attack_type == 1:
                attack_width = self.rect.width * 1.5
                damage = 10
            else:
                attack_width = self.rect.width * 1.9
                damage = 6

            attacking_rect = pygame.Rect(
                self.rect.centerx - (attack_width * self.flip),
                self.rect.y,
                attack_width,
                self.rect.height,
            )

            if attacking_rect.colliderect(target.rect):
                if target.blocking:
                    self.energy += 10
                else:
                    target.health -= damage
                    target.hit = True
                    self.energy += 20

    def freeze_attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attack_width = self.rect.width * 1.5
            damage = 15
            healDamage = 20
            healSelf = 15
            self.energy -= 100

            attacking_rect = pygame.Rect(
                self.rect.centerx - (attack_width * self.flip),
                self.rect.y,
                attack_width,
                self.rect.height,
            )

            if attacking_rect.colliderect(target.rect):
                if not target.blocking:
                    if self.fighter_name == "Onichan":
                        target.frozen = True
                        target.freeze_start_time = pygame.time.get_ticks()
                        target.health -= damage
                        target.hit = True

                    elif self.fighter_name == "Starlight":
                        target.health -= healDamage
                        self.health += healSelf
                        target.hit = True

                    elif self.fighter_name == "Raruto":
                        target.burned = True
                        target.burn_start_time = pygame.time.get_ticks()
                        target.burn_ticks = 0
                        target.hit = True


    #================#
    #==#  Update  #==#
    #================#
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
