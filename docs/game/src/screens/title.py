# auto-webified build (async input bridge) - do not edit
from src.core import ui
from src.core import save as save_sys

def slot_lines(s):
    if s.get('empty'):
        return f"Slot {s['slot']}: --- empty ---"
    return f"Slot {s['slot']}: {ui.BW}{s['name']}{ui.RESET} Lv{s['level']} {s['race']} - {s['phase']}  [{ui.DIM}{s['saved_at']}{ui.RESET}]"

async def how_to_play():
    ui.clear()
    lines = ['You are a weak monster in the Great Jura Forest. Devour, name, build, ascend.', '', f'{ui.BY}THE LOOP{ui.RESET}', '  Explore -> Battle (menu JRPG, speed order) -> Devour / Spare kills', '  Devour steals skills. Skills gain MASTERY by use; combine mastered', '  pairs via Great Sage Synthesis for new skills.', '', f'{ui.BY}NAMING{ui.RESET}', '  Spare foes or recruit at the goblin village, then NAME them - it burns', '  your magicules (scar heals slowly). Named monsters evolve and fight', '  beside you (Roster menu, up to 3 active). Their growth feeds you.', '', f'{ui.BY}KINGDOM{ui.RESET}', '  After founding your village: Tempest Governance builds districts,', '  sets jobs/taxes, crafts gear, trades with Dwargon/Blumund/Guild/Church.', '  Rest advances the day: income, population, events, sieges.', '', f'{ui.BY}ASCENSION{ui.RESET}', '  Trials & Conquests holds hunts, rival demon lords, and war duels.', '  Harvest souls -> Demon Lord Awakening cascades to all named allies.', '  Repel the Empire, defeat the Administrator MICHAEL, become GOD -', '  then farm Dimensional Gates forever: relics, essence, prestige.', '', f'{ui.DIM}Save often. The grind is eternal.{ui.RESET}']
    for l in ui.panel(' HOW TO PLAY ', lines, ui.C):
        print(l)
    await ui.pause()

async def title_screen():
    while True:
        ui.title_banner()
        slots = save_sys.list_slots()
        for l in ui.panel(' SAVE SLOTS ', [slot_lines(s) for s in slots], ui.DIM):
            print(l)
        print()
        c = await ui.choose('MAIN MENU', ['New Game', 'Continue', 'How to Play', 'Delete Save', 'Quit'])
        if c == 0:
            return ('new', None)
        elif c == 1:
            si = await ui.choose('Load which slot?', [slot_lines(s) for s in slots], allow_cancel=True)
            if si is None:
                continue
            data = save_sys.load_game(slots[si]['slot'])
            if not data:
                await ui.pause(ui.R + 'Empty or corrupted slot.' + ui.RESET)
                continue
            return ('load', data)
        elif c == 2:
            await how_to_play()
        elif c == 3:
            si = await ui.choose('Delete which slot?', [slot_lines(s) for s in slots], allow_cancel=True)
            if si is not None:
                save_sys.delete_slot(slots[si]['slot'])
        else:
            return ('quit', None)
