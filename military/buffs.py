from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Buff:
    name: str
    source: str  # unit / building / doctrine / tech

    # pasywne modyfikatory statystyk
    modifiers: Dict[str, float] = field(default_factory=dict)

    # reakcje na zdarzenia
    triggers: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # aura wpływająca na inne jednostki
    aura: Optional[dict] = None

    # aktywne efekty (leczenie, morale, czyszczenie)
    active_effect: Optional[dict] = None

    duration: Optional[int] = None

    def tick(self) -> bool:
        if self.duration is not None:
            self.duration -= 1
            return self.duration > 0
        return True
