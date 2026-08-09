#!/usr/bin/env python3
"""
Parche local de Nacho sobre n8n-skills (upstream czlonkowski/n8n-skills).

Agrega `domain: ops` + `mcp-bundled: true` al frontmatter de cada SKILL.md del
bundle. Nace de reemplazar el commit local 61a6b81, que chocaba en cada pull
porque este repo es un fork de una sola linea que no se puede pushear.

Es IDEMPOTENTE: se corre despues de cada `git pull` sin duplicar lineas.

Uso:
    python3 aplicar-frontmatter-local.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent / "skills"
SKIP = {"n8n-llm-agent-design"}  # skill custom propia, no viene del bundle MCP

cambiados = 0
for f in sorted(ROOT.glob("*/SKILL.md")):
    if f.parent.name in SKIP:
        print(f"  skip     {f.parent.name}")
        continue

    lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        print(f"  SIN FRONTMATTER  {f}", file=sys.stderr)
        continue

    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    if end is None:
        print(f"  FRONTMATTER SIN CIERRE  {f}", file=sys.stderr)
        continue

    fm = "".join(lines[1:end])
    add = []
    if "domain:" not in fm:
        add.append("domain: ops\n")
    if "mcp-bundled:" not in fm:
        add.append("mcp-bundled: true\n")

    if add:
        lines[end:end] = add
        f.write_text("".join(lines), encoding="utf-8")
        cambiados += 1
        print(f"  parchado {f.parent.name}: {[a.strip() for a in add]}")
    else:
        print(f"  ya ok    {f.parent.name}")

print(f"\n{cambiados} skills parchadas")
