"""Web runtime bridge. When WEB is True (Pyodide browser), input flows through
JS prompts and stdout is streamed to the DOM. Terminal behavior is untouched."""

WEB = False


def set_web(on=True):
    global WEB
    WEB = on


def _js():
    from js import window
    return window


def ask_text(label):
    if WEB:
        v = _js().prompt(label)
        return v if v is not None else ""
    return input(label)


def ask_pause(label):
    if WEB:
        if label:
            _js().alert(label.replace("\x1b", ""))
        return
    input(label)


def ask_int(prompt, lo, hi):
    if WEB:
        w = _js()
        while True:
            raw = w.prompt(f"{prompt} [{lo}-{hi}]")
            if raw is None:
                continue
            try:
                n = int(raw)
            except ValueError:
                continue
            if lo <= n <= hi:
                return n
    while True:
        raw = input(prompt)
        try:
            n = int(raw)
        except ValueError:
            print("Enter a number.")
            continue
        if lo <= n <= hi:
            return n
        print(f"Choose {lo}-{hi}.")
