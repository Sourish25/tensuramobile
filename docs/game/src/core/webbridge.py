# auto-webified build (async input bridge) - do not edit
"""Web runtime bridge. When WEB is True (Pyodide browser), input flows through
JS prompts and stdout is streamed to the DOM. Terminal behavior is untouched."""
WEB = False

def set_web(on=True):
    global WEB
    WEB = on

def _js():
    from js import window
    return window

async def ask_text(label):
    if WEB:
        v = await ask_line(label)
        return v if v is not None else ''
    return input(label)

async def ask_pause(label):
    if WEB:
        await _pause_js(label if label else 'Continue')
        return
    input(label)

async def ask_int(prompt, lo, hi):
    if WEB:
        w = _js()
        while True:
            raw = await ask_line(f'{prompt} [{lo}-{hi}]')
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
            print('Enter a number.')
            continue
        if lo <= n <= hi:
            return n
        print(f'Choose {lo}-{hi}.')

async def ask_line(prompt=''):
    if WEB:
        from js import tensuraPrompt
        v = await tensuraPrompt(prompt)
        return v if v is not None else ''
    return input(prompt)

async def ask_menu(prompt, options, allow_cancel, cancel_label='Back'):
    if WEB:
        from js import tensuraMenu
        v = await tensuraMenu(prompt, list(options), bool(allow_cancel), cancel_label)
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
    while True:
        raw = input(prompt + ' ' if prompt else '> ')
        try:
            n = int(raw)
        except ValueError:
            continue
        if 1 <= n <= len(options):
            return n
        if allow_cancel and n == 0:
            return None

async def _pause_js(label):
    if WEB:
        from js import tensuraPause
        await tensuraPause(label)
        return
    input(label)

def push_battle(payload_json):
    if WEB:
        from js import tensuraBattle
        tensuraBattle(payload_json)
