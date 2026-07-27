import pygame
from settings import PLAYER_CONTROLS
from status_effect import BurnEffect, TimedEffect


MOVE_SPEED = 10
GRAVITY = 2
JUMP_VELOCITY = -30
GROUND_OFFSET = 110
ATTACK_COOLDOWN_FRAMES = 30
ANIMATION_COOLDOWN_MS = 50
STARTING_HEALTH = 100
STARTING_ENERGY = 10
MAX_STAT_VALUE = 100
SPECIAL_ENERGY_COST = 100

ACTION_IDLE = 0
ACTION_UNUSED = 1
ACTION_RUN = 2
ACTION_JUMP = 3
ACTION_ATTACK_1 = 4
ACTION_ATTACK_2 = 5
ACTION_SPECIAL = 6
ACTION_BLOCK = 7
ACTION_HIT = 8
ACTION_DEATH = 9

ATTACK_NONE = 0
ATTACK_NORMAL_1 = 1
ATTACK_NORMAL_2 = 2
ATTACK_SPECIAL = 3


class Player:

    #========================#
    #==#  Initialization  #==#
    #========================#
    def __init__(
        self,
        player,
        x,
        y,
        flip,
        data,
        sprite_sheet,
        animation_steps,
        animation_list=None,
        controls=None,
    ):
        self.player = player
        self.controls = controls or PLAYER_CONTROLS[player]
        self.size = data["size"]
        self.image_scale = data["scale"]
        self.offset = data["offset"]
        self.fighter_name = data["name"]
        self.flip = flip

        if animation_list is None:
            self.animation_list = self.load_images(sprite_sheet, animation_steps)
        else:
            self.animation_list = animation_list
        self.action = ACTION_IDLE
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
        self.attack_type = ATTACK_NONE
        self.attack_cooldown = 0

        # Stats
        self.health = STARTING_HEALTH
        self.energy = STARTING_ENERGY

        # Spec Moves / Status
        self.dash_effect = TimedEffect(duration_ms=200)
        self.dash_speed = 1200

        self.freeze_effect = TimedEffect(duration_ms=3000)

        self.burn_effect = BurnEffect(
            interval_ms=2000,
            max_ticks=3,
            damage_per_tick=10,
        )

        # Freeze visuals control (NEW)
        self._freeze_frame_locked = False
        self._locked_action = 0
        self._locked_frame_index = 0

    @property
    def dashing(self):
        return self.dash_effect.active

    @property
    def frozen(self):
        return self.freeze_effect.active

    @property
    def burned(self):
        return self.burn_effect.active

    @property
    def burn_ticks(self):
        return self.burn_effect.ticks_applied

    def apply_freeze(self, now):
        self.freeze_effect.start(now)

    def apply_burn(self, now):
        self.burn_effect.start(now)

    def cancel_dash(self):
        self.dash_effect.clear()


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
    def move(
        self,
        screen_width,
        screen_height,
        surface,
        target,
        round_over,
        delta_time_ms=1000 / 60,
    ):
        dx = 0
        dy = 0

        self.running = False
        self.attack_type = ATTACK_NONE

        keys = pygame.key.get_pressed()
        if self.can_accept_input(round_over):
            dx = self.handle_input(keys, surface, target)

        dx = self.update_dash(dx, round_over, delta_time_ms)
        dy = self.apply_gravity(dy)
        dx, dy = self.limit_movement(dx, dy, screen_width, screen_height)
        self.update_facing(target)
        self.update_attack_cooldown()
        self.rect.x += dx
        self.rect.y += dy

    def can_accept_input(self, round_over):
        return (
            not self.attacking
            and self.alive
            and not round_over
            and not self.frozen
        )

    def handle_input(self, keys, surface, target):
        self.blocking = bool(keys[self.controls.block])
        if self.blocking:
            return 0

        dx = 0
        if keys[self.controls.left]:
            dx = -MOVE_SPEED
            self.running = True
        if keys[self.controls.right]:
            dx = MOVE_SPEED
            self.running = True

        if keys[self.controls.jump] and not self.jump:
            self.vel_y = JUMP_VELOCITY
            self.jump = True

        self.handle_attacks(keys, surface, target)
        self.handle_spec_attacks(keys, surface, target)
        return dx

    def update_dash(self, dx, round_over, delta_time_ms):
        if not self.dashing:
            return dx

        now = pygame.time.get_ticks()
        if self.frozen or not self.alive or round_over:
            self.cancel_dash()
            return dx
        if self.dash_effect.update(now):
            self.attack_cooldown = ATTACK_COOLDOWN_FRAMES
            return dx

        dash_distance = self.dash_speed * (delta_time_ms / 1000)
        return -dash_distance if self.flip else dash_distance

    def apply_gravity(self, dy):
        self.vel_y += GRAVITY
        return dy + self.vel_y

    def limit_movement(self, dx, dy, screen_width, screen_height):
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        ground_y = screen_height - GROUND_OFFSET
        if self.rect.bottom + dy > ground_y:
            self.vel_y = 0
            self.jump = False
            dy = ground_y - self.rect.bottom
        return dx, dy

    def update_facing(self, target):
        self.flip = target.rect.centerx < self.rect.centerx

    def update_attack_cooldown(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    #========================#
    #==#  Handle Attacks  #==#
    #========================#
    def handle_attacks(self, keys, surface, target):
        if keys[self.controls.attack_1] or keys[self.controls.attack_2]:
            if keys[self.controls.attack_1]:
                self.attack_type = ATTACK_NORMAL_1
            elif keys[self.controls.attack_2]:
                self.attack_type = ATTACK_NORMAL_2
            self.attack(surface, target)

    def handle_spec_attacks(self, keys, surface, target):
        if keys[self.controls.special] and self.energy >= MAX_STAT_VALUE:
            self.attack_type = ATTACK_SPECIAL
            if self.fighter_name == "Bam":
                self.dash_attack(surface, target)
            else:
                self.freeze_attack(surface, target)


    #===================#
    #==#  Animation  #==#
    #===================#
    def update(self, now=None, round_active=True):
        if now is None:
            now = pygame.time.get_ticks()

        if round_active:
            self.health -= self.burn_effect.update(now)

        self.clamp_stats()
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(ACTION_DEATH)

        if self.freeze_effect.update(now):
            self._freeze_frame_locked = False

        if not round_active or not self.alive:
            self.cancel_dash()

        if self.lock_frozen_frame():
            return

        self.select_animation_action()
        self.advance_animation(now)
        self.finish_animation()

    def clamp_stats(self):
        if self.energy >= MAX_STAT_VALUE:
            self.energy = MAX_STAT_VALUE
        if self.health >= MAX_STAT_VALUE:
            self.health = MAX_STAT_VALUE

    def lock_frozen_frame(self):
        if not self.frozen:
            return False

        if not self._freeze_frame_locked:
            if self.hit or self.action == ACTION_HIT:
                self._locked_action = ACTION_HIT
                self._locked_frame_index = (
                    len(self.animation_list[ACTION_HIT]) - 1
                )
            else:
                self._locked_action = self.action
                self._locked_frame_index = self.frame_index
            self._freeze_frame_locked = True

        self.action = self._locked_action
        self.frame_index = max(
            0,
            min(
                self._locked_frame_index,
                len(self.animation_list[self.action]) - 1,
            ),
        )
        self.image = self.animation_list[self.action][self.frame_index]
        return True

    def select_animation_action(self):
        if not self.alive:
            self.update_action(ACTION_DEATH)
        elif self.blocking:
            self.update_action(ACTION_BLOCK)
        elif self.hit:
            self.update_action(ACTION_HIT)
        elif self.attacking:
            if self.attack_type == ATTACK_NORMAL_1:
                self.update_action(ACTION_ATTACK_1)
            elif self.attack_type == ATTACK_NORMAL_2:
                self.update_action(ACTION_ATTACK_2)
            elif self.attack_type == ATTACK_SPECIAL:
                self.update_action(ACTION_SPECIAL)
        elif self.jump:
            self.update_action(ACTION_JUMP)
        elif self.running:
            self.update_action(ACTION_RUN)
        else:
            self.update_action(ACTION_IDLE)

    def advance_animation(self, now):
        self.image = self.animation_list[self.action][self.frame_index]
        if now - self.update_time > ANIMATION_COOLDOWN_MS:
            self.frame_index += 1
            self.update_time = now

    def finish_animation(self):
        if self.frame_index < len(self.animation_list[self.action]):
            return
        if not self.alive:
            self.frame_index = len(self.animation_list[self.action]) - 1
            return

        self.frame_index = 0
        if self.action in (ACTION_ATTACK_1, ACTION_ATTACK_2, ACTION_SPECIAL):
            self.attacking = False
            self.attack_cooldown = ATTACK_COOLDOWN_FRAMES
        if self.action == ACTION_HIT:
            self.hit = False
            self.attacking = False
            self.attack_cooldown = ATTACK_COOLDOWN_FRAMES


    #=================#
    #==#  Attacks  #==#
    #=================#
    def dash_attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.dash_effect.start(pygame.time.get_ticks())
            self.energy -= SPECIAL_ENERGY_COST

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

            if self.attack_type == ATTACK_NORMAL_1:
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
            self.energy -= SPECIAL_ENERGY_COST

            attacking_rect = pygame.Rect(
                self.rect.centerx - (attack_width * self.flip),
                self.rect.y,
                attack_width,
                self.rect.height,
            )

            if attacking_rect.colliderect(target.rect):
                if not target.blocking:
                    if self.fighter_name == "Onichan":
                        target.apply_freeze(pygame.time.get_ticks())
                        target.health -= damage
                        target.hit = True

                    elif self.fighter_name == "Starlight":
                        target.health -= healDamage
                        self.health += healSelf
                        target.hit = True

                    elif self.fighter_name == "Raruto":
                        target.apply_burn(pygame.time.get_ticks())
                        target.hit = True


    #================#
    #==#  Update  #==#
    #================#
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
