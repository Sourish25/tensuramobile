"""Headless smoke test for the webified payload.

Copies docs/game to a temp dir, injects a fake `js` module whose tensuraPrompt
returns scripted answers, then runs game_web.boot() under asyncio. Reaching the
hub menu proves title -> char_create -> hub all work through the async bridge.
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
        "1",          # title: New Game
        "",           # prologue pause (Enter)
        "1",          # race choose
        "WebTest",    # name
    ]

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
    fake_js.window = fake_js  # webbridge._js() imports window; self-ref covers .prompt/.alert
    fake_js.prompt = lambda *a, **k: None
    fake_js.alert = lambda *a, **k: None

    async def tensuraPrompt(prompt=""):
        if not answers:
            raise TestDone("script exhausted (reached live gameplay)")
        v = answers.pop(0)
        await asyncio.sleep(0)
        return v

    def tensuraPush(chunk=""):
        pass

    fake_js.tensuraPrompt = tensuraPrompt
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
        print(f"SMOKE TEST PASS: {e} (after {4 - len(answers)} scripted inputs)")
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
