import json
import os
import time

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "saves")


def _web():
    from src.core import webbridge
    return webbridge.WEB


def _ls():
    from js import localStorage
    return localStorage


def _key(slot):
    return f"tensura_save_{slot}"


def _write_bytes(path, data: str):
    if _web():
        _ls().setItem(_key(path), data)
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)


def _read_bytes(path):
    if _web():
        v = _ls().getItem(_key(path))
        return v
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def slot_path(slot):
    if _web():
        return f"slot_{slot}"
    return os.path.join(SAVE_DIR, f"slot_{slot}.json")


def save_game(state, slot=1):
    state["saved_at"] = time.strftime("%Y-%m-%d %H:%M")
    data = json.dumps(state, ensure_ascii=False)
    tmp = slot_path(slot)
    try:
        _write_bytes(tmp + ".tmp", data)
        if _web():
            _ls().setItem(_key(slot), data)
            _ls().removeItem(_key(tmp) + ".tmp")
        else:
            os.replace(tmp + ".tmp", tmp)
    except Exception:
        _write_bytes(slot_path(slot), data)
    return True


def load_game(slot):
    raw = _read_bytes(slot_path(slot))
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def list_slots():
    slots = []
    for i in (1, 2, 3):
        data = load_game(i)
        if data:
            p = data.get("player", {})
            slots.append({
                "slot": i,
                "name": p.get("name", "?"),
                "race": p.get("race_id", "?"),
                "level": p.get("level", 0),
                "phase": data.get("world", {}).get("phase_name", "?"),
                "saved_at": data.get("saved_at", "?"),
            })
        else:
            slots.append({"slot": i, "empty": True})
    return slots


def delete_slot(slot):
    if _web():
        _ls().removeItem(_key(slot))
        return True
    p = slot_path(slot)
    if os.path.exists(p):
        os.remove(p)
        return True
    return False
