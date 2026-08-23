import os
import sys

from src.core import ui
from src.core import save as save_sys
from src.screens import title, char_create, hub
from src.entities.unit import Player


def _seed_from_env():
    s = os.environ.get("TENSURA_SEED", "").strip()
    if s.isdigit():
        import random
        random.seed(int(s))


def new_state(hero, slot=1):
    return {
        "hero": hero,
        "world": {"zone": "sealed_cave", "floor": 1, "day": 1, "phase": 0, "slot": slot,
                  "phase_name": "Cave Awakening", "bosses_slain": [], "unlocked_zones": [],
                  "flags": {}, "recruit_pool": None, "deepest_floor": 1},
        "roster": [],
        "captures": [],
        "kingdom": None,
        "postgod": None,
    }


def load_state(data):
    hero = Player.from_dict(data["player"])
    world = dict(data.get("world", {}))
    world.setdefault("zone", "sealed_cave")
    world.setdefault("floor", 1)
    world.setdefault("day", 1)
    world.setdefault("phase", 0)
    world.setdefault("slot", 1)
    world.setdefault("phase_name", "Cave Awakening")
    world.setdefault("bosses_slain", [])
    world.setdefault("unlocked_zones", [])
    world.setdefault("flags", {})
    world.setdefault("recruit_pool", None)
    world.setdefault("deepest_floor", 6)
    kingdom = None
    if data.get("kingdom"):
        from src.systems.kingdom import Kingdom
        kingdom = Kingdom.from_dict(data["kingdom"])
    postgod = data.get("postgod") or None
    return {
        "hero": hero,
        "world": world,
        "roster": list(data.get("roster", [])),
        "captures": list(data.get("captures", [])),
        "kingdom": kingdom,
        "postgod": postgod,
    }


def main():
    _seed_from_env()
    mode, data = title.title_screen()
    if mode == "quit":
        print("Farewell, nameless one.")
        return
    if mode == "load":
        state = load_state(data)
        ui.voice(f"Save data loaded. Welcome back, [{state['hero'].name}].")
        ui.pause()
    else:
        slots = save_sys.list_slots()
        free = next((s["slot"] for s in slots if s.get("empty")), 1)
        hero = char_create.char_create()
        state = new_state(hero, slot=free)
        save_sys.save_game({"player": hero.to_dict(), "world": dict(state["world"])}, slot=free)
    hub.hub_loop(state)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Progress not lost - it was never saved.")
