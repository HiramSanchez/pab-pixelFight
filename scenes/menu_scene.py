import pygame

from scenes.base import Scene, SceneId
from settings import BLUE, CYAN, DARKGRAY, GRAY, SCREEN_HEIGHT, SCREEN_WIDTH


class MenuScene(Scene):
    def __init__(self, context):
        super().__init__(context)
        button_width, button_height = 280, 40
        button_x = (SCREEN_WIDTH - button_width) // 2
        self.button_height = button_height
        self.play_rect = pygame.Rect(
            button_x,
            (6 * SCREEN_HEIGHT - button_height) // 10,
            button_width,
            button_height,
        )
        self.controls_rect = pygame.Rect(
            button_x,
            (7 * SCREEN_HEIGHT - button_height) // 10,
            button_width,
            button_height,
        )
        self.exit_rect = pygame.Rect(
            button_x,
            (8 * SCREEN_HEIGHT - button_height) // 10,
            button_width,
            button_height,
        )
        self.back_rect = pygame.Rect(70, 502, 80, 28)
        self.background = context.assets.image(
            "images/backgrounds/scrolling.png",
            alpha=False,
        )
        self.controls_image = context.assets.image(
            "images/backgrounds/controls.png"
        )
        self.x_position = 0
        self.controls_visible = False

    def enter(self, payload=None):
        super().enter(payload)
        self.x_position = 0
        self.controls_visible = False

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.play_rect.collidepoint(event.pos):
            self.request_transition(SceneId.SELECTION)
        elif self.controls_rect.collidepoint(event.pos):
            self.controls_visible = True
        elif self.exit_rect.collidepoint(event.pos):
            self.request_transition(SceneId.QUIT)
        elif self.back_rect.collidepoint(event.pos):
            self.controls_visible = False

    def update(self, delta_time):
        self.x_position -= 0.2
        if self.x_position <= -self.background.get_width():
            self.x_position = 0

    def draw_button(self, rect, label):
        mouse_position = pygame.mouse.get_pos()
        color = CYAN if rect.collidepoint(mouse_position) else GRAY
        pygame.draw.rect(self.context.screen, color, rect)
        self.context.draw_text(
            label,
            "button",
            BLUE,
            rect.centerx,
            rect.centery,
        )

    def draw(self):
        screen = self.context.screen
        screen.blit(self.background, (self.x_position, 0))
        screen.blit(
            self.background,
            (self.x_position + self.background.get_width(), 0),
        )
        self.context.draw_text(
            "Pixel Fight",
            "title",
            CYAN,
            SCREEN_WIDTH / 2,
            (3 * SCREEN_HEIGHT - self.button_height) // 10,
        )
        self.draw_button(self.play_rect, "Play")
        self.draw_button(self.controls_rect, "Controls")
        self.draw_button(self.exit_rect, "Exit")

        if self.controls_visible:
            screen.blit(
                self.controls_image,
                (
                    SCREEN_WIDTH // 2 - self.controls_image.get_width() // 2,
                    SCREEN_HEIGHT // 2 - self.controls_image.get_height() // 2,
                ),
            )
            color = (
                BLUE
                if self.back_rect.collidepoint(pygame.mouse.get_pos())
                else DARKGRAY
            )
            self.context.draw_text(
                "< Back",
                "small_button",
                color,
                self.back_rect.centerx,
                self.back_rect.centery,
            )
