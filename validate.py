#!/usr/bin/env python3
"""Check SKILL.md: frontmatter (name + a description with a 'Use when' trigger) and that every referenced file exists."""
import os, re, sys
here = os.path.dirname(os.path.abspath(__file__)); t = open(os.path.join(here, "SKILL.md"), encoding="utf-8").read()
m = re.match(r"^---\nname:\s*(\S+)\ndescription:\s*(.+)\n---\n", t); bad = []
if not m: bad.append("frontmatter must be exactly name + description")
elif not re.search(r"\bUse (when|before|after|whenever|if)\b", m.group(2)): bad.append("description lacks a 'Use when ...' trigger")
for ref in set(re.findall(r"`((?:references|scripts|examples)/[A-Za-z0-9_./-]+)`", t)):
    if not os.path.exists(os.path.join(here, ref)): bad.append("references missing path " + ref)
print("\n".join(bad) if bad else "SKILL.md is valid"); sys.exit(1 if bad else 0)
