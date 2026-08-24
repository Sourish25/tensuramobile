"""Headless smoke test for the webified payload.

Copies docs/game to a temp dir, injects a fake `js` module (menus, pauses,
prompts, battle HUD) driven by a scripted answer list, then runs
game_web.boot() under asyncio. Passing requires surviving character creation
AND several explore/battle loops through the touch-UI bridge.
"""
import asyncio
import shutil
import sys
import tempfile
import types
from pathlib import Path


class TestDone(Exception):
    pass


def run():
    real_stdout = sys.stdout
    root = Path(__file__).resolve().parent.parent
    payload = root / "docs" / "game"
    tmp = Path(tempfile.mkdtemp(prefix="tensura_webtest_"))
    dst = tmp / "game"
    shutil.copytree(payload, dst)

    answers = [
        "1",          # title menu: New Game
        "",           # prologue pause (tap continue)
        "1",          # race menu
        "WebTest",    # name prompt
    ]
    # keep tapping option 1 + continue: explores, battles, accepts defaults
    answers += ["1", ""] * 40

    consumed = {"n": 0}

    def take():
        if not answers:
            raise TestDone("script exhausted (reached live gameplay)")
        consumed["n"] += 1
        return answers.pop(0)

    fake_js = types.ModuleType("js")

    class FakeLocalStorage:
        def __init__(self):
            self.store = {}

        def setItem(self, k, v):
            self.store[k] = str(v)

        def getItem(self, k):
            return self.store.get(k)

        def removeItem(self, k):
            self.store.pop(k, None)

    fake_js.localStorage = FakeLocalStorage()
    fake_js.window = fake_js
    fake_js.prompt = lambda *a, **k: None
    fake_js.alert = lambda *a, **k: None

    async def tensuraPrompt(prompt=""):
        return take()

    async def tensuraMenu(prompt="", options=None, allow_cancel=False,
                          cancel_label="Back"):
        return take()

    async def tensuraPause(label=""):
        take()
        return ""

    def tensuraBattle(payload_json=""):
        pass

    def tensuraPush(chunk=""):
        pass

    fake_js.tensuraPrompt = tensuraPrompt
    fake_js.tensuraMenu = tensuraMenu
    fake_js.tensuraPause = tensuraPause
    fake_js.tensuraBattle = tensuraBattle
    fake_js.tensuraPush = tensuraPush
    sys.modules["js"] = fake_js

    sys.path.insert(0, str(dst))
    import os
    os.chdir(dst)

    import game_web

    try:
        asyncio.run(game_web.boot())
    except TestDone as e:
        sys.stdout = real_stdout
        used = consumed["n"]
        if used < 10:
            print(f"SMOKE TEST FAIL: only {used} interactions - never got "
                  f"deep into gameplay")
            return 1
        print(f"SMOKE TEST PASS: {e} ({used} interactions, battles survived)")
        return 0
    except BaseException as e:
        sys.stdout = real_stdout
        import traceback
        traceback.print_exc()
        print("SMOKE TEST FAIL: unexpected exception:", type(e).__name__, e)
        return 1
    finally:
        sys.path.pop(0)
    sys.stdout = real_stdout
    print("SMOKE TEST FAIL: game.main returned before script exhausted")
    return 1


if __name__ == "__main__":
    sys.exit(run())
