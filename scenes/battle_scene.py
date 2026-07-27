import pygame

from player import Player
from round_rules import apply_score, match_winner, resolve_round
from scenes.base import Scene, SceneId
from settings import (
    BLUE,
    CYAN,
    GREEN,
    RED,
    ROUND_OVER_COOLDOWN,
    ROUND_TIME_LIMIT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOW_FIGHT_TIME,
    WHITE,
    YELLOW,
)
from status_effect import active_tints


class BattleScene(Scene):
    def __init__(self, context):
        super().__init__(context)
        self.background = pygame.transform.scale(
            context.assets.image("images/backgrounds/battleground.png"),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
        )
        self.skull = context.assets.image("images/icons/skull.png")
        self.flipped_skull = pygame.transform.flip(self.skull, True, False)
        self.fighter_1_data = None
        self.fighter_2_data = None
        self.paused = False
        self.paused_at = None

    def enter(self, payload=None):
        super().enter(payload)
        if payload is None:
            return
        self.fighter_1_data, self.fighter_2_data = payload
        self.player_1_animations = self.context.assets.fighter_animations(
            self.fighter_1_data
        )
        self.player_2_animations = self.context.assets.fighter_animations(
            self.fighter_2_data
        )
        self.score = [0, 0]
        self.max_text_visible = True
        self.max_last_blink_time = self.context.now()
        self.match_over = False
        self.paused = False
        self.paused_at = None
        self.reset_round()

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or self.fighter_1_data is None:
            return

        if event.key in (pygame.K_ESCAPE, pygame.K_p):
            if self.paused:
                self.resume()
            else:
                self.paused = True
                self.paused_at = self.context.now()
            return

        if not self.paused:
            return
        if event.key == pygame.K_r:
            self.enter((self.fighter_1_data, self.fighter_2_data))
        elif event.key == pygame.K_s:
            self.request_transition(SceneId.SELECTION)
        elif event.key == pygame.K_m:
            self.request_transition(SceneId.MENU)

    def resume(self):
        pause_duration = self.context.now() - self.paused_at
        self.round_start_time += pause_duration
        self.last_count_update += pause_duration
        if self.fight_displayed:
            self.fight_display_start += pause_duration
        if self.round_over:
            self.round_over_time += pause_duration
        self.max_last_blink_time += pause_duration

        for fighter in (self.fighter_1, self.fighter_2):
            fighter.update_time += pause_duration
            for effect in (
                fighter.dash_effect,
                fighter.freeze_effect,
                fighter.burn_effect,
            ):
                if effect.started_at is not None:
                    effect.started_at += pause_duration

        self.paused = False
        self.paused_at = None

    def create_players(self):
        self.fighter_1 = Player(
            1,
            200,
            310,
            False,
            self.fighter_1_data,
            None,
            self.fighter_1_data["animation_steps"],
            self.player_1_animations,
        )
        self.fighter_2 = Player(
            2,
            700,
            310,
            True,
            self.fighter_2_data,
            None,
            self.fighter_2_data["animation_steps"],
            self.player_2_animations,
        )

    def reset_round(self):
        now = self.context.now()
        self.round_start_time = now
        self.round_over = False
        self.intro_count = 3
        self.fight_displayed = False
        self.fight_display_start = 0
        self.last_count_update = now
        self.round_over_time = 0
        self.winner_name = None
        self.create_players()

    def update_intro_and_movement(self, now, delta_time):
        if self.intro_count > 0:
            if now - self.last_count_update >= 1000:
                self.intro_count -= 1
                self.last_count_update = now
            return

        if not self.fight_displayed:
            self.fight_display_start = now
            self.fight_displayed = True
            return

        if now - self.fight_display_start < SHOW_FIGHT_TIME:
            return

        if self.time_left > 0:
            self.fighter_1.move(
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                self.context.screen,
                self.fighter_2,
                self.round_over,
                delta_time,
            )
            self.fighter_2.move(
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                self.context.screen,
                self.fighter_1,
                self.round_over,
                delta_time,
            )

    def resolve_active_round(self, now):
        result = resolve_round(
            self.fighter_1.health,
            self.fighter_2.health,
            time_expired=self.time_left == 0,
        )
        if result is None:
            return

        self.score = apply_score(self.score, result)
        if result.winner_index == 0:
            self.winner_name = self.fighter_1_data["name"]
        elif result.winner_index == 1:
            self.winner_name = self.fighter_2_data["name"]
        else:
            self.winner_name = "No One"

        self.round_over = True
        self.round_over_time = now
        self.match_over = match_winner(self.score) is not None

    def update(self, delta_time):
        if self.fighter_1_data is None:
            return
        if self.paused:
            return

        now = self.context.now()
        elapsed_time = now - self.round_start_time
        self.time_left = max(0, (ROUND_TIME_LIMIT - elapsed_time) / 1000)

        if not self.round_over:
            self.update_intro_and_movement(now, delta_time)

        self.fighter_1.update(now, round_active=not self.round_over)
        self.fighter_2.update(now, round_active=not self.round_over)

        if not self.round_over:
            self.resolve_active_round(now)

        if not self.round_over:
            return

        if now - self.round_over_time < ROUND_OVER_COOLDOWN:
            return

        if self.match_over:
            self.request_transition(SceneId.MENU)
        else:
            self.reset_round()

    def draw_bar(self, bar_type, fighter_name, data, x, y, flip=False):
        screen = self.context.screen
        ratio = data / 100
        if bar_type == 1:
            pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
            pygame.draw.rect(screen, RED, (x, y, 400, 30))
            name_image = self.context.fonts["score"].render(
                fighter_name,
                True,
                WHITE,
            )
            if flip:
                name_rect = name_image.get_rect(midleft=(x + 5, y + 15))
                pygame.draw.rect(
                    screen,
                    GREEN,
                    (x + 400 * (1 - ratio), y, 400 * ratio, 30),
                )
            else:
                name_rect = name_image.get_rect(midright=(x + 395, y + 15))
                pygame.draw.rect(
                    screen,
                    GREEN,
                    (x, y, 400 * ratio, 30),
                )
            screen.blit(name_image, name_rect)
        elif bar_type == 2:
            pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 204, 24))
            pygame.draw.rect(screen, BLUE, (x, y, 200, 20))
            if flip:
                pygame.draw.rect(
                    screen,
                    CYAN,
                    (x + 200 * (1 - ratio), y, 200 * ratio, 20),
                )
            else:
                pygame.draw.rect(screen, CYAN, (x, y, 200 * ratio, 20))

    def draw_skulls(self, player, score, x, y):
        for index in range(min(score, 2)):
            if player == 1:
                self.context.screen.blit(
                    self.skull,
                    (x - index * (self.skull.get_width() + 5), y),
                )
            else:
                self.context.screen.blit(
                    self.flipped_skull,
                    (x + index * (self.flipped_skull.get_width() + 5), y),
                )

    def draw_max_energy(self, player, energy, x, y):
        if energy < 100:
            return
        now = self.paused_at if self.paused else self.context.now()
        if now - self.max_last_blink_time >= 500:
            self.max_text_visible = not self.max_text_visible
            self.max_last_blink_time = now
        if self.max_text_visible:
            text_x = x + 240 if player == 1 else x - 40
            self.context.draw_text("MAX", "score", CYAN, text_x, y + 10)

    def draw_hud(self):
        if self.time_left <= (ROUND_TIME_LIMIT / 1000) - 3:
            self.context.draw_text(
                f"{int(self.time_left):02}",
                "timer",
                YELLOW,
                SCREEN_WIDTH / 2,
                35,
            )
        self.draw_bar(
            1,
            self.fighter_1_data["name"],
            self.fighter_1.health,
            20,
            20,
            flip=True,
        )
        self.draw_bar(
            1,
            self.fighter_2_data["name"],
            self.fighter_2.health,
            580,
            20,
        )
        self.draw_bar(
            2,
            self.fighter_1_data["name"],
            self.fighter_1.energy,
            20,
            55,
        )
        self.draw_bar(
            2,
            self.fighter_2_data["name"],
            self.fighter_2.energy,
            780,
            55,
            flip=True,
        )
        self.draw_skulls(1, self.score[0], 388, 60)
        self.draw_skulls(2, self.score[1], 580, 60)
        self.draw_max_energy(1, self.fighter_1.energy, 20, 55)
        self.draw_max_energy(2, self.fighter_2.energy, 780, 55)
        self.draw_state_indicators(self.fighter_1, 120)
        self.draw_state_indicators(self.fighter_2, 880)

    def draw_state_indicators(self, fighter, x):
        labels = []
        if fighter.burned:
            labels.append(("BURN", RED))
        if fighter.frozen:
            labels.append(("FROZEN", CYAN))
        for index, (label, color) in enumerate(labels):
            self.context.draw_text(
                label,
                "small_button",
                color,
                x,
                105 + index * 28,
            )

    def draw_status_effects(self, fighter, fighter_data):
        for color in active_tints(fighter.burned, fighter.frozen):
            overlay = self.context.assets.status_overlay(
                fighter.image,
                color,
                fighter.flip,
            )
            self.context.screen.blit(
                overlay,
                (
                    fighter.rect.x + fighter_data["freeze_offset"][0],
                    fighter.rect.y + fighter_data["freeze_offset"][1],
                ),
            )

    def draw_round_text(self, now):
        if self.intro_count > 0:
            self.context.draw_text(
                str(self.intro_count),
                "timer",
                YELLOW,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 3,
            )
        elif (
            self.fight_displayed
            and now - self.fight_display_start < SHOW_FIGHT_TIME
        ):
            self.context.draw_text(
                "FIGHT!",
                "count",
                YELLOW,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 180,
            )

        if self.round_over:
            self.context.draw_text(
                self.winner_name,
                "count",
                YELLOW,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 180,
            )
            result_text = "victory!" if self.match_over else "wins"
            self.context.draw_text(
                result_text,
                "count",
                YELLOW,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 130,
            )

    def draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.context.screen.blit(overlay, (0, 0))
        self.context.draw_text(
            "PAUSED",
            "count",
            YELLOW,
            SCREEN_WIDTH / 2,
            190,
        )
        options = (
            "Esc / P - Resume",
            "R - Restart match",
            "S - Character select",
            "M - Main menu",
        )
        for index, option in enumerate(options):
            self.context.draw_text(
                option,
                "small_button",
                WHITE,
                SCREEN_WIDTH / 2,
                290 + index * 45,
            )

    def draw(self):
        if self.fighter_1_data is None:
            return
        self.context.screen.blit(self.background, (0, 0))
        self.draw_hud()
        self.fighter_1.draw(self.context.screen)
        self.fighter_2.draw(self.context.screen)
        self.draw_status_effects(self.fighter_1, self.fighter_1_data)
        self.draw_status_effects(self.fighter_2, self.fighter_2_data)
        now = self.paused_at if self.paused else self.context.now()
        self.draw_round_text(now)
        if self.paused:
            self.draw_pause_overlay()
