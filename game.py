import pygame

from asset_manager import AssetManager
from scenes import SceneId
from scenes.battle_scene import BattleScene
from scenes.menu_scene import MenuScene
from scenes.selection_scene import SelectionScene
from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH


class GameContext:
    def __init__(self, screen, assets, time_source=None):
        self.screen = screen
        self.assets = assets
        self.now = time_source or pygame.time.get_ticks
        self.fonts = {
            "timer": assets.font("fonts/HelvetiPixel.ttf", 80),
            "button": assets.font("fonts/HelvetiPixel.ttf", 40),
            "small_button": assets.font("fonts/HelvetiPixel.ttf", 30),
            "title": assets.font("fonts/PixelTimesNewRoman.ttf", 120),
            "count": assets.font("fonts/PixelTimesNewRoman.ttf", 80),
            "score": assets.font("fonts/PixelTimesNewRoman.ttf", 40),
        }

    def draw_text(self, text, font_name, color, x, y):
        image = self.fonts[font_name].render(text, True, color)
        self.screen.blit(image, image.get_rect(center=(x, y)))


class Game:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pixel Fight")

        self.clock = pygame.time.Clock()
        self.context = GameContext(screen, AssetManager())
        self.scenes = {
            SceneId.MENU: MenuScene(self.context),
            SceneId.SELECTION: SelectionScene(self.context),
            SceneId.BATTLE: BattleScene(self.context),
        }
        self.current_scene = self.scenes[SceneId.MENU]
        self.current_scene.enter()
        self.running = True

    def activate(self, transition):
        if transition.target is SceneId.QUIT:
            self.running = False
            return
        self.current_scene = self.scenes[transition.target]
        self.current_scene.enter(transition.payload)

    def process_transition(self):
        transition = self.current_scene.take_transition()
        if transition is not None:
            self.activate(transition)

    def run(self):
        try:
            while self.running:
                delta_time = self.clock.tick(FPS)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                    self.current_scene.handle_event(event)

                if not self.running:
                    break

                self.process_transition()
                if not self.running:
                    break
                self.current_scene.update(delta_time)
                self.process_transition()
                if not self.running:
                    break
                self.current_scene.draw()
                pygame.display.update()
        finally:
            pygame.quit()
