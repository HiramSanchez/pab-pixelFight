from dataclasses import dataclass


BURN_TINT = (255, 0, 0, 50)
FREEZE_TINT = (15, 158, 234, 50)


def active_tints(burned, frozen):
    tints = []
    if burned:
        tints.append(BURN_TINT)
    if frozen:
        tints.append(FREEZE_TINT)
    return tuple(tints)


@dataclass
class TimedEffect:
    duration_ms: int
    started_at: int | None = None
    active: bool = False

    def start(self, now):
        self.started_at = now
        self.active = True

    def clear(self):
        self.started_at = None
        self.active = False

    def update(self, now):
        if not self.active:
            return False
        if now - self.started_at < self.duration_ms:
            return False
        self.clear()
        return True


@dataclass
class BurnEffect:
    interval_ms: int = 2000
    max_ticks: int = 3
    damage_per_tick: int = 10
    started_at: int | None = None
    ticks_applied: int = 0
    active: bool = False

    def start(self, now):
        self.started_at = now
        self.ticks_applied = 0
        self.active = True

    def clear(self):
        self.started_at = None
        self.ticks_applied = 0
        self.active = False

    def update(self, now):
        if not self.active:
            return 0

        elapsed = max(0, now - self.started_at)
        ticks_due = min(elapsed // self.interval_ms, self.max_ticks)
        new_ticks = max(0, ticks_due - self.ticks_applied)
        self.ticks_applied += new_ticks

        if self.ticks_applied >= self.max_ticks:
            self.active = False

        return new_ticks * self.damage_per_tick
