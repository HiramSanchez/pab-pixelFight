from dataclasses import dataclass
from enum import Enum


class SceneId(Enum):
    MENU = "menu"
    SELECTION = "selection"
    BATTLE = "battle"
    QUIT = "quit"


@dataclass(frozen=True)
class SceneTransition:
    target: SceneId
    payload: object = None


class Scene:
    def __init__(self, context):
        self.context = context
        self._transition = None

    def enter(self, payload=None):
        self._transition = None

    def request_transition(self, target, payload=None):
        self._transition = SceneTransition(target, payload)

    def take_transition(self):
        transition = self._transition
        self._transition = None
        return transition

    def handle_event(self, event):
        pass

    def update(self, delta_time):
        pass

    def draw(self):
        pass
