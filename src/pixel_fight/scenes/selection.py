import time

import pygame

from pixel_fight.scenes.base import Scene, SceneId
from pixel_fight.settings import (
    CYAN,
    FIGHTERS,
    GRAY,
    GREEN,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)


class SelectionScene(Scene):
    def __init__(self, context):
        super().__init__(context)
        self.background = context.assets.image(
            "images/backgrounds/scrolling.png",
            alpha=False,
        )
        self.back_rect = pygame.Rect(200, 507, 80, 28)
        for fighter in FIGHTERS:
            context.assets.fighter_image(fighter, "pick.png")
            context.assets.idle_frames(fighter)
        self.enter()

    def enter(self, payload=None):
        super().enter(payload)
        self.selected_fighter_1 = 0
        self.selected_fighter_2 = 3
        self.elapsed_time = 0
        self.frame_index = 0
        self.x_position = 0
        self.text_visible = True
        self.last_blink_time = self.context.now()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.selected_fighter_1 = (
                    self.selected_fighter_1 - 1
                ) % len(FIGHTERS)
            elif event.key == pygame.K_s:
                self.selected_fighter_1 = (
                    self.selected_fighter_1 + 1
                ) % len(FIGHTERS)
            elif event.key == pygame.K_UP:
                self.selected_fighter_2 = (
                    self.selected_fighter_2 - 1
                ) % len(FIGHTERS)
            elif event.key == pygame.K_DOWN:
                self.selected_fighter_2 = (
                    self.selected_fighter_2 + 1
                ) % len(FIGHTERS)
            elif event.key == pygame.K_RETURN:
                self.request_transition(
                    SceneId.BATTLE,
                    (
                        FIGHTERS[self.selected_fighter_1],
                        FIGHTERS[self.selected_fighter_2],
                    ),
                )
            elif event.key == pygame.K_ESCAPE:
                self.request_transition(SceneId.MENU)
        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.back_rect.collidepoint(event.pos)
        ):
            self.request_transition(SceneId.MENU)

    def update(self, delta_time):
        self.x_position -= 2
        if self.x_position <= -self.background.get_width():
            self.x_position = 0

        self.elapsed_time += delta_time
        if self.elapsed_time >= 100:
            self.frame_index += 1
            self.elapsed_time = 0

        now = self.context.now()
        if now - self.last_blink_time >= 500:
            self.text_visible = not self.text_visible
            self.last_blink_time = now

    def draw_character_list(self):
        for index, fighter in enumerate(FIGHTERS):
            image = self.context.fonts["button"].render(
                fighter["name"],
                True,
                WHITE,
            )
            rect = image.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 100 + index * 60,
                )
            )
            self.context.screen.blit(image, rect)

            if index == self.selected_fighter_1 == self.selected_fighter_2:
                color = GREEN if time.time() % 0.5 < 0.25 else CYAN
                pygame.draw.rect(
                    self.context.screen,
                    color,
                    rect.inflate(10, 10),
                    3,
                )
            elif index == self.selected_fighter_1:
                pygame.draw.rect(
                    self.context.screen,
                    GREEN,
                    rect.inflate(10, 10),
                    3,
                )
            elif index == self.selected_fighter_2:
                pygame.draw.rect(
                    self.context.screen,
                    CYAN,
                    rect.inflate(10, 10),
                    3,
                )

    def draw_fighter(self, fighter, x, y):
        self.context.screen.blit(
            self.context.assets.fighter_image(fighter, "pick.png"),
            (x, y),
        )
        frames = self.context.assets.idle_frames(fighter)
        self.context.screen.blit(
            frames[self.frame_index % len(frames)],
            (x, y),
        )

    def draw(self):
        screen = self.context.screen
        screen.blit(self.background, (self.x_position, 0))
        screen.blit(
            self.background,
            (self.x_position + self.background.get_width(), 0),
        )
        self.context.draw_text(
            "Choose a fighter",
            "count",
            GRAY,
            SCREEN_WIDTH / 2,
            80,
        )
        self.context.draw_text(
            "Player 1:",
            "button",
            GREEN,
            SCREEN_WIDTH / 4,
            180,
        )
        self.context.draw_text(
            "Player 2:",
            "button",
            CYAN,
            3 * SCREEN_WIDTH / 4,
            180,
        )
        self.draw_character_list()

        self.draw_fighter(
            FIGHTERS[self.selected_fighter_1],
            SCREEN_WIDTH / 2 - 314,
            236,
        )
        self.draw_fighter(
            FIGHTERS[self.selected_fighter_2],
            SCREEN_WIDTH / 2 + 186,
            236,
        )

        self.context.draw_text(
            "Press 'Enter' to fight",
            "button",
            GRAY,
            (11 * SCREEN_WIDTH / 16) - 12,
            520,
        )
        if self.text_visible:
            self.context.draw_text(
                "Press 'Enter' to fight",
                "button",
                WHITE,
                (11 * SCREEN_WIDTH / 16) - 12,
                520,
            )

        color = (
            WHITE if self.back_rect.collidepoint(pygame.mouse.get_pos()) else GRAY
        )
        self.context.draw_text(
            "< Back",
            "button",
            color,
            self.back_rect.centerx,
            self.back_rect.centery,
        )
