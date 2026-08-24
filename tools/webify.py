"""Build-time webify: turns the sync terminal game into an async-input web build.

Seed patches rewrite the Pyodide input branches of ui.menu / ui.pause /
webbridge.ask_* to call an async bridge (webbridge.ask_line, which awaits the
JS tensuraPrompt promise). An AST pass then propagates async/await transitively
from those seeds across the whole payload, including instance methods reached
through constructor-tracked locals (b = Battle(); b.run()). A final verifier
asserts every call to an async function is awaited, failing the build otherwise.
Desktop sources are never modified.
"""
import ast
import json
import sys
from pathlib import Path

SEEDS = {
    "src.core.ui:menu",
    "src.core.ui:pause",
    "src.core.webbridge:ask_text",
    "src.core.webbridge:ask_pause",
    "src.core.webbridge:ask_int",
    "src.core.webbridge:ask_line",
    "src.screens.hub:_run_action",
}

TEXT_PATCHES = {
    "src/core/webbridge.py": [
        (
            '        v = _js().prompt(label)\n        return v if v is not None else ""',
            '        v = ask_line(label)\n        return v if v is not None else ""',
        ),
        (
            '        if label:\n            _js().alert(label.replace("\\x1b", ""))\n        return',
            '        ask_line(label if label else "Press Enter to continue...")\n        return',
        ),
        (
            '            raw = w.prompt(f"{prompt} [{lo}-{hi}]")',
            '            raw = ask_line(f"{prompt} [{lo}-{hi}]")',
        ),
    ],
    "src/core/ui.py": [
        (
            "WIDTH = 100",
            "WIDTH = 64",
        ),
        (
            '            raw = w.prompt(body + "\\n\\nEnter number:")',
            '            raw = webbridge.ask_line("")',
        ),
        (
            '        if msg.startswith("Press Enter"):\n'
            "            return\n"
            "        webbridge.ask_pause(_strip_for_alert(msg))\n"
            "        return",
            "        webbridge.ask_pause(msg)\n        return",
        ),
    ],
    "src/screens/hub.py": [
        (
            "        actions[c][1]()",
            "        _run_action(actions[c][1])",
        ),
    ],
}

ASK_LINE = '''

async def ask_line(prompt=""):
    if WEB:
        from js import tensuraPrompt
        v = await tensuraPrompt(prompt)
        return v if v is not None else ""
    return input(prompt)
'''

HUB_RUN_ACTION = '''

async def _run_action(fn):
    import inspect
    r = fn()
    if inspect.isawaitable(r):
        r = await r
    return r
'''


def _modname(rel):
    m = rel[:-3].replace("/", ".")
    if m.endswith(".__init__"):
        m = m[: -len(".__init__")]
    return m


class _Info:
    def __init__(self, rel, tree):
        self.rel = rel
        self.tree = tree
        self.imports = {}
        self.funcs = set()    # qualified names: "Cls.meth", "fn"
        self.classes = set()  # qualified names


def _collect(mods):
    for mod, info in mods.items():
        tree = info.tree
        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    imports[a.asname or a.name.split(".")[0]] = a.name
            elif isinstance(node, ast.ImportFrom):
                m = node.module or ""
                if node.level:
                    base = mod.split(".")
                    base = base[: len(base) - node.level]
                    m = ".".join(base + ([m] if m else []))
                for a in node.names:
                    if a.name != "*":
                        imports[a.asname or a.name] = (m, a.name)
        info.imports = imports

        def walk_defs(node, prefix):
            for ch in ast.iter_child_nodes(node):
                if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    info.funcs.add(prefix + ch.name)
                    walk_defs(ch, prefix + ch.name + ".")
                elif isinstance(ch, ast.ClassDef):
                    info.classes.add(prefix + ch.name)
                    walk_defs(ch, prefix + ch.name + ".")
        walk_defs(tree, "")


def _make_resolver(mods, allfuncs, allclasses, fnvarmaps):
    modnames = set(mods)

    def resolve(mod, call, caller_qual, varmap=None):
        f = call.func
        if isinstance(f, ast.Name):
            nm = f.id
            imp = mods[mod].imports.get(nm)
            if isinstance(imp, tuple):
                cand = imp[0] + ":" + imp[1]
                return cand if cand in allfuncs or cand in allclasses else None
            cand = mod + ":" + nm
            return cand if cand in allfuncs or cand in allclasses else None
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            alias, attr = f.value.id, f.attr
            if alias in ("self", "cls") and caller_qual and "." in caller_qual:
                cls = caller_qual.split(".")[0]
                cand = mod + ":" + cls + "." + attr
                return cand if cand in allfuncs else None
            if varmap and alias in varmap:
                cand = varmap[alias] + "." + attr
                return cand if cand in allfuncs else None
            imp = mods[mod].imports.get(alias)
            if isinstance(imp, str):
                cand = imp + ":" + attr
                return cand if cand in allfuncs or cand in allclasses else None
            if isinstance(imp, tuple):
                candmod = imp[0] + "." + imp[1]
                if candmod in modnames:
                    cand = candmod + ":" + attr
                    return cand if cand in allfuncs or cand in allclasses else None
                return None
        return None

    return resolve


def _qual_stack_fn(node, name):
    return (node[-1] + "." + name) if node else name


def _scan_varmap(fn_node, mod, resolve):
    vm = {}

    def rec(n):
        for ch in ast.iter_child_nodes(n):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if (isinstance(ch, ast.Assign) and len(ch.targets) == 1
                    and isinstance(ch.targets[0], ast.Name)
                    and isinstance(ch.value, ast.Call)):
                tgt = resolve(mod, ch.value, None, {})
                if tgt and tgt in _allclasses:
                    vm[ch.targets[0].id] = tgt
            rec(ch)
    rec(fn_node)
    return vm


def _build_fnvarmaps(mods, resolve):
    maps = {}
    for mod, info in mods.items():
        per = {}

        class V(ast.NodeVisitor):
            stack = []

            def _fn(self, node):
                q = _qual_stack_fn(self.stack, node.name)
                self.stack.append(q)
                per[q] = _scan_varmap(node, mod, resolve)
                self.generic_visit(node)
                self.stack.pop()

            visit_FunctionDef = _fn
            visit_AsyncFunctionDef = _fn

            def visit_ClassDef(self, node):
                self.stack.append(node.name)
                self.generic_visit(node)
                self.stack.pop()

        V().visit(info.tree)
        maps[mod] = per
    return maps


def _edges_and_badcalls(mod, mods, resolve, fnvarmaps, async_check=None):
    """Collect caller->callee edges (and, if async_check given, unawaited
    async calls) with proper scope and lambda exclusion."""
    results = []
    info = mods[mod]

    class V(ast.NodeVisitor):
        def __init__(self):
            self.stack = []
            self.lam = 0
            self.parent = None

        def _fn(self, node):
            q = _qual_stack_fn(self.stack, node.name)
            self.stack.append(q)
            self.generic_visit(node)
            self.stack.pop()

        visit_FunctionDef = _fn
        visit_AsyncFunctionDef = _fn

        def visit_ClassDef(self, node):
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Lambda(self, node):
            self.lam += 1
            self.generic_visit(node)
            self.lam -= 1

        def _visit(self, node):
            prev = self.parent
            self.parent = node
            for ch in ast.iter_child_nodes(node):
                self.visit(ch)
            self.parent = prev

        def visit_Call(self, node):
            if self.stack and not self.lam:
                caller = self.stack[-1]
                vm = fnvarmaps.get(mod, {}).get(caller, {})
                tgt = resolve(mod, node, caller, vm)
                if tgt:
                    if async_check is None:
                        results.append((caller, tgt))
                    elif tgt in async_check and not isinstance(self.parent, ast.Await):
                        results.append((mod, getattr(node, "lineno", 0), tgt))
            self._visit(node)

        def generic_visit(self, node):
            self._visit(node)

    V().visit(info.tree)
    return results


class _Xform(ast.NodeTransformer):
    def __init__(self, mod, resolve, async_full, fnvarmaps):
        self.mod = mod
        self.resolve = resolve
        self.async_full = async_full
        self.fnvarmaps = fnvarmaps
        self.stack = []
        self.lam = 0

    def _fn(self, node):
        q = _qual_stack_fn(self.stack, node.name)
        self.stack.append(q)
        self.generic_visit(node)
        self.stack.pop()
        if (self.mod + ":" + q) in self.async_full:
            node.__class__ = ast.AsyncFunctionDef
        return node

    def visit_FunctionDef(self, node):
        return self._fn(node)

    def visit_AsyncFunctionDef(self, node):
        return self._fn(node)

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()
        return node

    def visit_Lambda(self, node):
        self.lam += 1
        self.generic_visit(node)
        self.lam -= 1
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if not self.stack or self.lam:
            return node
        caller = self.stack[-1]
        vm = self.fnvarmaps.get(self.mod, {}).get(caller, {})
        tgt = self.resolve(self.mod, node, caller, vm)
        if tgt and tgt in self.async_full:
            return ast.copy_location(ast.Await(value=node), node)
        return node


_allclasses = set()


def webify_all(root):
    global _allclasses
    root = Path(root)
    files = json.loads((root / "web" / "files.json").read_text(encoding="utf-8"))
    mods = {}
    for rel in files:
        if not rel.endswith(".py"):
            continue
        mod = _modname(rel)
        src = (root / rel).read_text(encoding="utf-8")
        for old, new in TEXT_PATCHES.get(rel, []):
            if old not in src:
                sys.exit(f"webify: patch MISS in {rel}: {old[:60]!r}")
            src = src.replace(old, new)
        if rel == "src/core/webbridge.py":
            src += ASK_LINE
        if rel == "src/screens/hub.py":
            src += HUB_RUN_ACTION
        mods[mod] = _Info(rel, ast.parse(src))

    _collect(mods)
    allfuncs = {mod + ":" + q for mod, i in mods.items() for q in i.funcs}
    _allclasses = {mod + ":" + q for mod, i in mods.items() for q in i.classes}

    resolve = _make_resolver(mods, allfuncs, _allclasses, None)
    fnvarmaps = _build_fnvarmaps(mods, resolve)

    edge_map = {}
    for mod in mods:
        edge_map[mod] = _edges_and_badcalls(mod, mods, resolve, fnvarmaps)

    async_full = set(SEEDS)
    changed = True
    while changed:
        changed = False
        for mod in mods:
            for caller, callee in edge_map[mod]:
                if callee in async_full:
                    full = mod + ":" + caller
                    if full not in async_full:
                        async_full.add(full)
                        changed = True

    for mod, info in mods.items():
        xform = _Xform(mod, resolve, async_full, fnvarmaps)
        new_tree = xform.visit(info.tree)
        ast.fix_missing_locations(new_tree)
        info.tree = new_tree

    problems = []
    for mod in mods:
        for entry in _edges_and_badcalls(mod, mods, resolve, fnvarmaps,
                                         async_check=async_full):
            problems.append(entry)
    if problems:
        for mod, line, tgt in problems[:20]:
            print(f"webify: UNAWAITED async call {tgt} at {mod}:{line}",
                  file=sys.stderr)
        sys.exit(f"webify: {len(problems)} unawaited async call(s) - aborting")

    out = {}
    for mod, info in mods.items():
        text = ast.unparse(info.tree)
        out[info.rel] = (
            "# auto-webified build (async input bridge) - do not edit\n" + text + "\n"
        )
    seeded = sorted(f for f in async_full if f not in SEEDS)
    print(f"webify: {len(async_full)} async functions "
          f"({len(SEEDS)} seeds + {len(seeded)} propagated), verified")
    return out


if __name__ == "__main__":
    result = webify_all(Path("."))
    for rel in sorted(result):
        print(" ", rel)
