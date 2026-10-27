"""Tests for the PQBlocks MCP server and catalog."""

import ast
import json
import subprocess
import sys

import pytest

from pqblocks_mcp import catalog
from pqblocks_mcp.server import check_config, get_snippet, list_packages, recommend_package


def test_catalog_is_complete_and_every_quickstart_ran():
    pkgs = catalog.packages()
    assert len(pkgs) >= 26
    for p in pkgs:
        assert p["package"].startswith("pqblocks-") and p["url"].startswith("https://github.com/PQBlocks/")
        assert p["area"], p["package"]
        assert p["verified"] is True, (p["package"], p["verify_output"])
        ast.parse(p["quickstart"])
        # the install line must be one that works today
        assert p["install"] == ("pip install %s" % p["package"] if p["on_pypi"] else
                                "pip install git+%s" % p["url"])


@pytest.mark.parametrize("task,expected", [
    ("encrypt a JWT post-quantum with ML-KEM", "pqblocks-jose"),
    ("sign JSON web tokens with ML-DSA", "pqblocks-jose"),
    ("TLS 1.3 hybrid key exchange X25519MLKEM768", "pqblocks-tls-interop"),
    ("hybrid X25519 + ML-KEM key exchange in python", "pqblocks-core"),
    ("encrypt files post-quantum", "pqblocks-files"),
    ("find RSA usage in my repo", "pqblocks-scan"),
    ("check if my app still uses RSA/ECC only", "pqblocks-scan"),
    ("enrich CycloneDX CBOM readiness score", "pqblocks-cbom"),
    ("policy as code gate in CI for crypto", "pqblocks-policy"),
    ("lint python crypto code", "pqblocks-lint"),
    ("CNSA 2.0 compliance evidence", "pqblocks-cnsa-evidence"),
    ("audit JWE algorithms in gateway", "pqblocks-jwe-audit"),
    ("ML-KEM CSR proof of possession", "pqblocks-csr-pop"),
    ("validate malformed ML-KEM ciphertext length", "pqblocks-fips-check"),
    ("serialize ML-DSA signatures binary container", "pqblocks-wire"),
    ("run NIST ACVP vectors against my ML-KEM", "pqblocks-acvp"),
    ("kyber dilithium basics", "pqblocks-primitives"),
    ("crypto agility score", "pqblocks-agility"),
    ("solve QUBO with simulated bifurcation", "pqblocks-bifurcation"),
    ("convert ising to qubo matrix", "pqblocks-qubo"),
    ("benchmark qubo solvers time to solution", "pqblocks-qubo-bench"),
    ("use pqblocks-wire", "pqblocks-wire"),
])
def test_recommend(task, expected):
    res = recommend_package(task)
    assert res["recommended_package"] == expected, res
    assert res["install"] and res["quickstart"]


def test_recommend_honours_what_a_package_says_it_does_not_do():
    # pqblocks-jwe's README: "It does not encrypt anything."
    assert recommend_package("encrypt a JWE token")["recommended_package"] != "pqblocks-jwe"


def test_recommend_no_match():
    res = recommend_package("bake a cake")
    assert res["recommended_package"] is None and res["alternatives"] == []


def test_get_snippet_is_the_verified_quickstart():
    res = get_snippet("pqblocks-jwe")
    assert res["verified"] is True and "from pqblocks_jwe import" in res["code"]
    assert get_snippet("jwe")["package"] == "pqblocks-jwe"          # short names work
    assert "note" in get_snippet("pqblocks-jwe", "fastapi")       # no invented framework code
    assert "error" in get_snippet("unknown-pkg")


def test_check_config_flags_quantum_vulnerable_and_weak():
    code = ('key = rsa.generate_private_key(key_size=2048)\nalg = "ES256"\n'
            'curve = ec.SECP256R1()\nh = hashlib.md5(x)\nkx = "x25519"\n')
    found = {(f["line"], f["algorithm"]) for f in check_config(code)["findings"]}
    assert {(1, "RSA"), (2, "ECDSA"), (3, "ECDH / NIST curve"), (4, "MD5"), (5, "X25519 (alone)")} <= found


def test_check_config_no_false_positives():
    clean = 'group = "X25519MLKEM768"\nUNIVERSAL_TRANSACTIONS = 1\nkem = "ML-KEM-768"\nsig = "ML-DSA-65"\n'
    res = check_config(clean)
    assert res["compliant"], res["findings"]


def test_list_packages_filter():
    every = list_packages()
    assert {p["package"] for p in every} >= {"pqblocks-jwe", "pqblocks-bifurcation", "pqblocks-scan"}
    q = list_packages(category="Quantum-inspired")
    assert q and all(p["area"] == "Quantum-inspired" and p["kind"] == "optimizer" for p in q)


def test_stdio_protocol():
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "recommend_package", "arguments": {"task_description": "sign JWTs with ML-DSA"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "nope", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 5, "method": "ping"},
    ]
    out = subprocess.run([sys.executable, "-m", "pqblocks_mcp.server", "--stdio-fallback"],
                         input="\n".join(json.dumps(m) for m in msgs) + "\n",
                         capture_output=True, text=True, timeout=60).stdout.splitlines()
    replies = {r["id"]: r for r in map(json.loads, out)}
    assert sorted(replies) == [1, 2, 3, 4, 5]                       # the notification got no reply
    assert replies[1]["result"]["protocolVersion"] == "2025-06-18"
    assert {t["name"] for t in replies[2]["result"]["tools"]} == {
        "recommend_package", "get_snippet", "check_config", "list_packages"}
    body = json.loads(replies[3]["result"]["content"][0]["text"])
    assert body["recommended_package"] == "pqblocks-jose" and replies[3]["result"]["isError"] is False
    assert replies[4]["result"]["isError"] is True
    assert replies[5]["result"] == {}
