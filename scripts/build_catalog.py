#!/usr/bin/env python3
"""Build src/pqblocks_mcp/catalog.json from the released package sources.

Every field comes from a file in the package (pyproject.toml, README.md, examples/),
from GitHub (repository topics) or from PyPI (is the name live). Nothing is written by hand,
so the catalog can never describe an API the package does not have.

    python3 scripts/build_catalog.py <packages-dir> [--verify]

--verify runs each README quickstart against the package source (PYTHONPATH=src) and records
the result; a snippet that does not run is still listed, marked "verified": false.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
import urllib.request

ORG = "PQBlocks"
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "pqblocks_mcp", "catalog.json")
AREAS = {"pq-crypto": "PQ cryptography", "pq-migration": "Migration & readiness",
         "pq-interop": "Interoperability", "pq-conformance": "Conformance",
         "quantum-inspired": "Quantum-inspired"}
DOCS = ("README.md", "AGENTS.md", "SECURITY_NOTES.md", "TESTING.md", "BENCHMARKS.md",
        "EVIDENCE.md", "VERIFICATION_REPORT.md", "USE_CASES.md", "CHANGELOG.md")
NOISE = re.compile(r"^(\s*$|\[!\[|<|---|>\s*\[!|\s*!\[)")


def repo_of(pyproject):
    url = pyproject["project"].get("urls", {}).get("Homepage", "")
    m = re.search(r"github\.com/%s/([^/#]+)" % ORG, url)
    return m.group(1) if m else None


def on_pypi(dist):
    try:
        with urllib.request.urlopen("https://pypi.org/pypi/%s/json" % dist, timeout=15) as r:
            return json.load(r)["info"]["version"]
    except Exception:
        return None


def topics():
    out = subprocess.run(["gh", "repo", "list", ORG, "--limit", "200", "--json", "name,repositoryTopics"],
                         capture_output=True, text=True, check=True).stdout
    return {r["name"]: [t["name"] for t in (r.get("repositoryTopics") or [])] for r in json.loads(out)}


def readme_parts(text):
    lines = text.splitlines()
    intro = []
    for line in lines[1:]:
        if line.startswith("```") or line.startswith("## "):
            break
        if NOISE.match(line):
            continue
        intro.append(line.lstrip("> ").strip())
    quick = re.search(r"```python\n(.*?)```", text, re.S)
    heads = [h.strip() for h in re.findall(r"^## (.+)$", text, re.M)]
    return [l for l in intro if l][:4], quick.group(1) if quick else "", heads


def verify(pkg_dir, code):
    """Run a snippet against the package source; True/False plus the last output line."""
    if not code.strip():
        return False, "no python quickstart in README"
    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ, PYTHONPATH=os.path.abspath(os.path.join(pkg_dir, "src")))
        try:
            r = subprocess.run([sys.executable, "-c", code], cwd=d, env=env, capture_output=True,
                               text=True, timeout=120)
        except subprocess.TimeoutExpired:
            return False, "timed out"
        tail = (r.stdout.strip() or r.stderr.strip()).splitlines()[-1:] or [""]
        return r.returncode == 0, tail[0][:200]


def build(pkg_root, run_verify):
    tops = topics()
    out = []
    for name in sorted(os.listdir(pkg_root)):
        d = os.path.join(pkg_root, name)
        if not os.path.isfile(os.path.join(d, "pyproject.toml")):
            continue
        py = tomllib.load(open(os.path.join(d, "pyproject.toml"), "rb"))
        proj = py["project"]
        dist, repo = proj["name"], repo_of(py)
        readme = open(os.path.join(d, "README.md"), encoding="utf-8").read()
        intro, quick, heads = readme_parts(readme)
        live = on_pypi(dist)
        area = next((AREAS[t] for t in tops.get(repo, []) if t in AREAS), None)
        mods = [m for m in os.listdir(os.path.join(d, "src")) if m.startswith("pqblocks_") and
                os.path.isdir(os.path.join(d, "src", m))]
        ex = os.path.join(d, "examples")
        entry = {
            "package": dist,
            "import": mods[0] if mods else dist.replace("-", "_"),
            "version": proj.get("version"),
            "repo": "%s/%s" % (ORG, repo),
            "url": "https://github.com/%s/%s" % (ORG, repo),
            "area": area,
            "kind": "optimizer" if area == "Quantum-inspired" else "pq",
            "summary": proj.get("description", "").strip(),
            "intro": intro,
            "keywords": proj.get("keywords", []),
            "topics": tops.get(repo, []),
            "python": proj.get("requires-python"),
            "cli": sorted(proj.get("scripts", {})),
            "status": next((c.split(" - ")[-1] for c in proj.get("classifiers", [])
                            if c.startswith("Development Status")), None),
            "on_pypi": live,
            "install": "pip install %s" % dist if live else "pip install git+https://github.com/%s/%s" % (ORG, repo),
            "needs_liboqs": "liboqs" in readme,
            "quickstart": quick,
            "examples": sorted(f for f in os.listdir(ex) if f.endswith(".py")) if os.path.isdir(ex) else [],
            "docs": {f: "https://github.com/%s/%s/blob/main/%s" % (ORG, repo, f)
                     for f in DOCS if os.path.isfile(os.path.join(d, f))},
            "sections": heads,
        }
        if run_verify:
            entry["verified"], entry["verify_output"] = verify(d, quick)
        out.append(entry)
    return out


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    cat = build(argv[0], "--verify" in argv)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"org": ORG, "site": "https://pqblocks.github.io", "packages": cat}, fh, indent=1,
                  ensure_ascii=False)
        fh.write("\n")
    bad = [p["package"] for p in cat if p.get("verified") is False]
    print("%d packages -> %s; on PyPI: %d; quickstart failed: %s" % (
        len(cat), os.path.normpath(OUT), sum(1 for p in cat if p["on_pypi"]), bad or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
