import os
import sys
import textwrap

os.system("")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WIDTH = 100

R = "\033[31m"; G = "\033[32m"; Y = "\033[33m"; B = "\033[34m"
M = "\033[35m"; C = "\033[36m"; W = "\033[37m"
BR = "\033[91m"; BG = "\033[92m"; BY = "\033[93m"; BB = "\033[94m"
BM = "\033[95m"; BC = "\033[96m"; BW = "\033[97m"
DIM = "\033[2m"; BOLD = "\033[1m"; ITAL = "\033[3m"; RESET = "\033[0m"

VOICE_C = BM
SAGE_C = BC
GOLD_C = BY
HP_C = BG
MP_C = BB
XP_C = BY
ENEMY_C = BR
ALLY_C = BG
BORDER_C = C
TITLE_C = BM


def clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def pause(msg="Press Enter to continue..."):
    from src.core import webbridge
    if webbridge.WEB:
        if msg.startswith("Press Enter"):
            return
        webbridge.ask_pause(_strip_for_alert(msg))
        return
    try:
        input(DIM + msg + RESET)
    except KeyboardInterrupt:
        raise SystemExit(0)
    except EOFError:
        raise SystemExit(0)


def _strip_for_alert(s):
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\033":
            j = s.find("m", i)
            i = j + 1 if j != -1 else i + 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def wrap(text, width=WIDTH - 4, indent=""):
    if isinstance(text, (list, tuple)):
        lines = []
        for part in text:
            for ln in wrap(str(part), width, indent):
                lines.append(ln)
            lines.append("")
        while lines and lines[-1] == "":
            lines.pop()
        return lines
    lines = []
    for raw in text.split("\n"):
        if not raw.strip():
            lines.append("")
            continue
        wrapped = textwrap.wrap(raw, width=width, break_long_words=False)
        for i, ln in enumerate(wrapped):
            lines.append(indent + ln if i == 0 else indent + " " + ln)
    return lines


def strip_ansi(s):
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\033":
            j = s.find("m", i)
            i = j + 1 if j != -1 else i + 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def panel(title, body_lines, color=BORDER_C, width=WIDTH, align="left"):
    inner = width - 2
    top = f"{color}╔{'═' * inner}╗{RESET}"
    if title:
        t = f" {title} "
        t_plain = len(t)
        pad = max(0, inner - t_plain)
        left = pad // 2
        right = pad - left
        top = f"{color}╔{'═' * left}{RESET}{BOLD}{color}{t}{RESET}{color}{'═' * right}╗{RESET}"
    out = [top]
    for line in body_lines:
        plain_len = len(strip_ansi(line))
        fill = max(0, inner - plain_len)
        if align == "center":
            lp = fill // 2
            rp = fill - lp
            out.append(f"{color}║{RESET}{' ' * lp}{line}{' ' * rp}{color}║{RESET}")
        elif align == "right":
            out.append(f"{color}║{RESET}{' ' * fill}{line}{color}║{RESET}")
        else:
            out.append(f"{color}║{RESET} {line}{' ' * max(0, fill - 1)}{color}║{RESET}")
    out.append(f"{color}╚{'═' * inner}╝{RESET}")
    return out


def text_panel(title, text, color=BORDER_C, width=WIDTH):
    return panel(title, wrap(text, width - 4), color, width)


def bar(cur, mx, width=24, color=HP_C, show_nums=True):
    cur = max(0, min(cur, mx))
    frac = cur / mx if mx > 0 else 0.0
    filled = int(round(frac * width))
    blocks = "█" * filled + "░" * (width - filled)
    nums = f" {cur}/{mx}" if show_nums else ""
    return f"{color}{blocks}{RESET}{nums}"


def voice(lines, delay=True):
    body = []
    if isinstance(lines, str):
        lines = wrap(lines)
    body.append(f"{VOICE_C}{BOLD}«World Language»{RESET}")
    for ln in lines:
        body.append(f"{VOICE_C}{ln}{RESET}")
    for l in panel("SYSTEM ANNOUNCEMENT", body, VOICE_C):
        print(l)
    print()


def sage(lines):
    body = []
    if isinstance(lines, str):
        lines = wrap(lines)
    for ln in lines:
        body.append(f"{SAGE_C}{ITAL}{ln}{RESET}")
    for l in panel("Great Sage", body, SAGE_C):
        print(l)
    print()


def menu(prompt, options, allow_cancel=False, cancel_label="Back", color=GOLD_C):
    print(f"{color}{BOLD}{prompt}{RESET}")
    for i, opt in enumerate(options, 1):
        print(f"  {color}{i}.{RESET} {opt}")
    if allow_cancel:
        print(f"  {DIM}0.{RESET} {cancel_label}")
    from src.core import webbridge
    if webbridge.WEB:
        w = webbridge._js()
        plain = strip_ansi(prompt)
        opts = [f"{i}. {strip_ansi(o)}" for i, o in enumerate(options, 1)]
        if allow_cancel:
            opts.append(f"0. {cancel_label}")
        body = plain + "\n" + "\n".join(opts)
        while True:
            raw = w.prompt(body + "\n\nEnter number:")
            if raw is None:
                if allow_cancel:
                    return None
                continue
            try:
                n = int(raw)
            except ValueError:
                continue
            hi = len(options) + (1 if allow_cancel else 0)
            if 1 <= n <= len(options):
                return n
            if allow_cancel and n == 0:
                return None
    while True:
        try:
            raw = input(f"{color}> {RESET}").strip()
        except KeyboardInterrupt:
            print()
            return None if allow_cancel else 1
        except EOFError:
            raise SystemExit(0)
        if raw == "" and allow_cancel:
            return None
        if raw == "" and allow_cancel:
            return None
        try:
            n = int(raw)
        except ValueError:
            print(f"{R}Enter a number.{RESET}")
            continue
        hi = len(options) + (1 if allow_cancel else 0)
        if 1 <= n <= len(options):
            return n
        if allow_cancel and n == 0:
            return None
        print(f"{R}Choose 1-{hi}.{RESET}")


def choose(prompt, options, allow_cancel=False, cancel_label="Back"):
    n = menu(prompt, options, allow_cancel, cancel_label)
    if n is None:
        return None
    return n - 1


def header(left, right="", color=C):
    right = right or ""
    gap = WIDTH - len(strip_ansi(left)) - len(strip_ansi(right)) - 4
    gap = max(1, gap)
    line = f"{color}┌─{left}{'─' * gap}{right}─┐{RESET}"
    print(line)


TITLE_ART = [
    " ████████╗███████╗███╗   ██╗███████╗██╗   ██╗██████╗  █████╗ ",
    " ╚══██╔══╝██╔════╝████╗  ██║██╔════╝██║   ██║██╔══██╗██╔══██╗",
    "    ██║   █████╗  ██╔██╗ ██║███████╗██║   ██║██████╔╝███████║",
    "    ██║   ██╔══╝  ██║╚██╗██║╚════██║██║   ██║██╔══██╗██╔══██║",
    "    ██║   ███████╗██║ ╚████║███████║╚██████╔╝██║  ██║██║  ██║",
    "    ╚═╝   ╚══════╝╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝",
]


def title_banner(subtitle="PATH OF THE REINCARNATED"):
    clear()
    for line in TITLE_ART:
        print(f"{TITLE_C}{line}{RESET}")
    pad = (WIDTH - len(subtitle)) // 2
    print(" " * pad + f"{GOLD_C}{BOLD}{subtitle}{RESET}")
    print()
