from src.core import ui
from src.data import races as races_data
from src.entities.unit import Player


def char_create():
    ui.title_banner()
    intro = ("You died on Earth. The World Language whispers across the void, "
             "and your soul is cast into the Great Jura Forest of another world - "
             "as a monster. Weak. Nameless. Hungry.")
    for l in ui.text_panel(" PROLOGUE ", intro, ui.M):
        print(l)
    print()
    ui.pause()

    ui.clear()
    ui.header("CHARACTER CREATION", "Choose your reincarnation")
    race_ids = list(races_data.RACES.keys())
    opts = []
    for rid in race_ids:
        r = races_data.RACES[rid]
        col = races_data.COLORS[r["color"]]
        opts.append(f"{col}{r['glyph']} {r['name']}{ui.RESET} - {r['desc']}")
    ri = ui.choose("What are you reborn as?", opts)
    rid = race_ids[ri]

    name = ""
    while not name.strip():
        from src.core import webbridge
        name = (webbridge.ask_text("Name your monster:") or "").strip()[:16]
        if not name.strip():
            print(ui.R + "A nameless thing cannot exist." + ui.RESET)

    hero = Player(name, rid)

    ui.voice([
        f"Confirmed. Individual [{name}] has been reincarnated.",
        f"Race: {races_data.RACES[rid]['name']}.",
        f"Unique characteristics granted: "
        f"{', '.join(_skill_names(races_data.RACES[rid]['intrinsics']))}.",
    ])

    latent = races_data.RACES[rid]["latent_unique"]
    from src.data.skills import get_skill
    hint = " and ".join(get_skill(l)["name"] for l in latent if get_skill(l))
    for l in ui.panel(" GREAT SAGE (dormant) ",
                      [f"A voice stirs within you...", f"Something sleeps in your soul: {hint}."],
                      ui.C):
        print(l)

    return hero


def _skill_names(sids):
    from src.data.skills import get_skill
    out = []
    for sid in sids:
        s = get_skill(sid)
        out.append(s["name"] if s else sid)
    return out
