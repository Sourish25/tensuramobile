import sys

from src.core import webbridge
webbridge.set_web(True)


class JsStream:
    def __init__(self):
        self.buf = []

    def write(self, s):
        self.buf.append(s)
        if "\n" in s:
            from js import tensuraPush
            tensuraPush("".join(self.buf))
            self.buf = []

    def flush(self):
        if self.buf:
            from js import tensuraPush
            tensuraPush("".join(self.buf))
            self.buf = []


def boot():
    sys.stdout = JsStream()
    try:
        sys.stderr = JsStream()
    except Exception:
        pass
    import game
    game.main()
