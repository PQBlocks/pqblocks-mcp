"""PQBlocks catalog: package facts, recommendations and a classical-crypto checker.

All package facts come from catalog.json, which scripts/build_catalog.py generates from the
released package sources (pyproject.toml, README.md, examples/) and verifies by running every
README quickstart. Nothing here describes an API by hand.
"""

import json
import re
from functools import lru_cache
from importlib import resources
from typing import Any, Dict, List, Optional

_WORD = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# words that say nothing about which package fits
_STOP = {"a", "an", "and", "the", "to", "for", "of", "in", "on", "with", "my", "our", "how", "i",
         "do", "is", "it", "use", "using", "want", "need", "add", "make", "python", "pqc",
         "post-quantum", "quantum", "post", "pqblocks", "library", "package", "code", "app"}
# a few spellings people type that the package metadata writes differently
_ALIAS = {"kyber": "ml-kem", "dilithium": "ml-dsa", "sphincs": "slh-dsa", "jwt": "jws",
          "token": "jwt", "tokens": "jwt", "encrypt": "encryption", "encrypting": "encryption",
          "sign": "signature", "signing": "signature", "signatures": "signature",
          "certificate": "csr", "inventory": "crypto-inventory", "sbom": "cbom",
          "optimise": "optimization", "optimize": "optimization", "anneal": "annealing",
          "maxcut": "max-cut", "files": "file-encryption", "file": "file-encryption"}


@lru_cache(maxsize=1)
def _catalog() -> Dict[str, Any]:
    return json.loads(resources.files(__package__).joinpath("catalog.json").read_text("utf-8"))


def packages() -> List[Dict[str, Any]]:
    return _catalog()["packages"]


def _find(name: str) -> Optional[Dict[str, Any]]:
    key = name.strip().lower().replace("_", "-")
    if not key.startswith("pqblocks-"):
        key = "pqblocks-" + key
    return next((p for p in packages() if p["package"] == key or p["repo"].lower().endswith("/" + key[9:])), None)


def _terms(text: str) -> List[str]:
    out = []
    for w in _WORD.findall(text.lower()):
        if w in _STOP:
            continue
        out.append(w)
        if w in _ALIAS:
            out.append(_ALIAS[w])
        out.extend(p for p in w.split("-") if len(p) > 2 and p not in _STOP)
    return out


# phrasings that metadata alone ranks badly; each points at the package whose README covers it
_INTENTS = [
    (r"\b(find|detect|where|inventory|discover|uses?|still use|scan)\b.*\b(rsa|ecc|ecdsa|crypto|cryptography|algorithms?)\b"
     r"|\b(rsa|ecc)\b.*\b(only|left|where|usage|in (?:my|the|our) (?:repo|code|app|project))", "pqblocks-scan"),
    (r"\b(sign|signing|verify)\b.*\b(jwts?|jws|json web tokens?|tokens?)\b|\bjws\b", "pqblocks-jose"),
    (r"\b(encrypt|decrypt)\w*\b.*\b(jwts?|jwes?|tokens?)\b", "pqblocks-jose"),
    (r"\b(enrich|enrichment)\b.*\b(cbom|sbom|cyclonedx)\b", "pqblocks-cbom"),
    (r"\bpolicy[- ]as[- ]code\b|\bcrypto(?:graphic)? polic", "pqblocks-policy"),
    (r"\b(lint|linter|static analysis|data[- ]flow)\b.*\bpython\b|\bpython\b.*\b(lint|linter)\b", "pqblocks-lint"),
    (r"\b(malformed|truncated|boundary|length|size)\b.*\b(key|ciphertext|signature|buffer)", "pqblocks-fips-check"),
    (r"\b(ml-kem|ml-dsa|slh-dsa|kyber|dilithium|sphincs)\b.*\b(keygen|key pair|keypair|basics|primitives?|encapsulat\w*|sign)\b"
     r"|\b(basics|primitives?)\b", "pqblocks-primitives"),
    (r"^(?!.*\btls\b).*\bhybrid\b.*\b(kem|key exchange|key encapsulation)\b", "pqblocks-core"),
    (r"\b(convert|conversion|bqm)\b.*\b(qubo|ising)\b|\bising to qubo\b|\bqubo to ising\b", "pqblocks-qubo"),
    (r"\bagility\b|\bcars\b", "pqblocks-agility"),
    (r"\b(benchmark|time[- ]to[- ]solution|tts)\b", "pqblocks-qubo-bench"),
    (r"\baudit\w*\b.*\b(jwe|jose|tokens?)\b|\b(jwe|jose)\b.*\baudit", "pqblocks-jwe-audit"),
]


def _intent_bonus(task: str, pkg: Dict[str, Any]) -> float:
    low = task.lower()
    bonus = sum(10.0 for rx, name in _INTENTS if name == pkg["package"] and re.search(rx, low))
    # the package's own name typed in the task ("pqblocks-lint")
    if pkg["package"] in low:
        bonus += 20
    return bonus


def _score(task_terms: List[str], pkg: Dict[str, Any]) -> float:
    tags = {t.lower() for t in pkg["keywords"] + pkg["topics"]}
    tag_parts = {p for t in tags for p in t.split("-") if len(p) > 2}
    summary = set(_terms(pkg["summary"]))
    # the package's own README says what it does NOT do; honour it
    denied = set()
    for line in pkg["intro"]:
        for m in re.finditer(r"(?i)\bdoes not ([a-z ,]+)", line):
            denied.update(_terms(m.group(1)))
    score = 0.0
    for t in set(task_terms):
        if t in tags:
            score += 3
        elif t in tag_parts:
            score += 1.5
        if t in summary:
            score += 1
        if t in denied:
            score -= 4
    return score


def recommend(task_description: str, limit: int = 3) -> Dict[str, Any]:
    """Rank packages for a task by their own metadata; return the best one and the runners-up."""
    terms = _terms(task_description)
    ranked = sorted(((_score(terms, p) + _intent_bonus(task_description, p), p) for p in packages()),
                    key=lambda x: -x[0])
    ranked = [(s, p) for s, p in ranked if s > 0][:limit]
    if not ranked:
        return {"recommended_package": None,
                "why": "No PQBlocks package matches this task. Call list_packages to see the full catalog.",
                "alternatives": []}
    _, best = ranked[0]
    return {
        "recommended_package": best["package"],
        "why": best["summary"],
        "use_when": next((l for l in best["intro"] if l.lower().startswith(("use it", "when to use"))), ""),
        "area": best["area"],
        "kind": best["kind"],
        "install": best["install"],
        "import": best["import"],
        "quickstart": best["quickstart"],
        "docs": best["docs"].get("README.md", best["url"]),
        "alternatives": [{"package": p["package"], "summary": p["summary"]} for _, p in ranked[1:]],
    }


def snippet(package_name: str, framework: Optional[str] = None) -> Dict[str, Any]:
    """The package's README quickstart (verified to run), its install line and its examples."""
    pkg = _find(package_name)
    if pkg is None:
        return {"error": "Unknown package %r. Known packages: %s" % (
            package_name, ", ".join(p["package"] for p in packages()))}
    fw = (framework or "python").lower()
    seeded = bool(re.search(r"(?:keypair|keygen)\([^)]*\bseed\s*=", pkg["quickstart"]))
    out = {
        "package": pkg["package"],
        "install": pkg["install"],
        "import": pkg["import"],
        "code": pkg["quickstart"],
        "verified": pkg.get("verified"),
        "needs_liboqs": pkg["needs_liboqs"],
        "examples": ["%s/blob/main/examples/%s" % (pkg["url"], e) for e in pkg["examples"]],
        "docs": pkg["docs"],
    }
    if seeded:
        out["warning"] = ("This quickstart passes seed= for reproducible output. Remove it in production code: "
                          "keys must come from the operating system random source.")
    if fw != "python":
        out["note"] = ("No %s-specific snippet is published for %s; this is the plain Python quickstart. "
                       "It is framework-independent and can be called from a %s handler." % (fw, pkg["package"], fw))
    return out


# classical public-key algorithms a cryptographically relevant quantum computer breaks (Shor),
# each mapped to what replaces it and the PQBlocks packages that help
_CLASSICAL = [
    (r"\bRSA(?:[-_ ]?(?:OAEP|PSS|PKCS1))?(?:[-_ ]?\d{3,4})?\b", "RSA",
     "ML-KEM (FIPS 203) for key establishment, ML-DSA (FIPS 204) for signatures, ideally in hybrid mode",
     ["pqblocks-primitives", "pqblocks-core", "pqblocks-jose"]),
    (r"\bE(?:C)?DSA\b|\bES(?:256|384|512)\b", "ECDSA",
     "ML-DSA (FIPS 204), or a composite ML-DSA + Ed25519 signature during transition",
     ["pqblocks-core", "pqblocks-jose"]),
    (r"\bECDH(?:E)?(?:-ES)?\b|\bsecp\d{3}[rk]1\b|\bP-(?:256|384|521)\b|\bprime256v1\b", "ECDH / NIST curve",
     "hybrid X25519 + ML-KEM-768 key establishment (X25519MLKEM768 in TLS 1.3)",
     ["pqblocks-core", "pqblocks-tls-interop"]),
    (r"\bDiffie[- ]Hellman\b|\bDHE\b|\bffdhe\d+\b", "Diffie-Hellman",
     "ML-KEM (FIPS 203) in a hybrid KEM", ["pqblocks-core", "pqblocks-primitives"]),
    (r"(?<![A-Z-])DSA\b", "DSA", "ML-DSA (FIPS 204)", ["pqblocks-primitives"]),
    (r"\bX25519\b(?![-_ ]?ML[-_]?KEM)", "X25519 (alone)",
     "pair it with ML-KEM-768 (X25519MLKEM768) so the session survives a quantum attacker",
     ["pqblocks-core", "pqblocks-tls-interop"]),
    (r"\bEd(?:25519|448)\b", "Ed25519 / Ed448 (alone)",
     "a composite with ML-DSA-65 during transition", ["pqblocks-core"]),
]
_WEAK = [
    (r"\bMD5\b", "MD5", "broken classically; use SHA-256 or SHA-3"),
    (r"\bSHA-?1\b", "SHA-1", "broken classically; use SHA-256 or SHA-3"),
    (r"\b(?:3DES|DES-EDE3?|TripleDES)\b", "3DES", "deprecated; use AES-256-GCM"),
    (r"\bAES-?128\b", "AES-128", "Grover halves effective strength; CNSA 2.0 requires AES-256"),
]


def check_configuration(code_or_config: str) -> Dict[str, Any]:
    """Flag quantum-vulnerable and weak algorithms named in code or config, line by line."""
    findings = []
    for n, line in enumerate(code_or_config.splitlines(), 1):
        for rx, label, fix, pkgs in _CLASSICAL:
            for m in re.finditer(rx, line, re.I):
                findings.append({"line": n, "match": m.group(0), "algorithm": label, "severity": "high",
                                 "why": "broken by a cryptographically relevant quantum computer (Shor)",
                                 "replace_with": fix, "packages": pkgs})
        for rx, label, fix in _WEAK:
            for m in re.finditer(rx, line, re.I):
                findings.append({"line": n, "match": m.group(0), "algorithm": label, "severity": "medium",
                                 "why": fix, "replace_with": fix, "packages": []})
    return {
        "compliant": not findings,
        "findings_count": len(findings),
        "findings": findings,
        "next_step": ("For a whole repository, run pqblocks-scan (CBOM + SARIF) or pqblocks-lint "
                      "(Python data-flow) instead of pasting snippets." if findings else ""),
        "limits": "Pattern match on algorithm names only; it cannot see algorithms chosen at runtime "
                  "or hidden behind library defaults.",
    }


def list_catalog(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Every package with its area, status and install line; optional area filter."""
    want = (category or "").strip().lower()
    return [{"package": p["package"], "area": p["area"], "kind": p["kind"], "summary": p["summary"],
             "version": p["version"], "status": p["status"], "on_pypi": bool(p["on_pypi"]),
             "install": p["install"], "repo": p["url"]}
            for p in packages() if not want or want in (p["area"] or "").lower()]
