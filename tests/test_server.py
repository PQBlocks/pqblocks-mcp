"""Tests for PQBlocks MCP server & catalog."""

import ast
import json
import io
import sys
from pqblocks_mcp.server import (
    recommend_package,
    get_snippet,
    check_config,
    list_packages
)


def test_recommend_jwt_task():
    res = recommend_package("How to encrypt a JWT post-quantum with ML-KEM?")
    assert res["recommended_package"] == "pqblocks-jwe"
    assert "RFC 7516" in res["standards"]
    assert res["install_command"] == "pip install pqblocks-jwe"
    assert "pqblocks_jwe" in res["quick_snippet"]


def test_recommend_signing_task():
    res = recommend_package("Sign JSON web tokens using ML-DSA digital signatures")
    assert res["recommended_package"] == "pqblocks-jose"
    assert "FIPS 204" in str(res["standards"])


def test_recommend_tls_task():
    res = recommend_package("Setup TLS 1.3 hybrid key exchange with X25519MLKEM768")
    assert res["recommended_package"] == "pqblocks-tls-interop"


def test_recommend_qubo_optimization():
    res = recommend_package("Solve large-scale QUBO and Ising combinatorial optimization with simulated bifurcation")
    assert res["recommended_package"] == "pqblocks-bifurcation"
    assert res["kind"] == "optimizer"


def test_recommend_cbom_enricher():
    res = recommend_package("Enrich CycloneDX CBOM and calculate quantum readiness score")
    assert res["recommended_package"] == "pqblocks-cbom"


def test_get_snippet_valid():
    res = get_snippet("pqblocks-jwe", "python")
    assert res["package"] == "pqblocks-jwe"
    assert "from pqblocks_jwe import" in res["code"]
    # Check syntax of snippet
    ast.parse(res["code"])


def test_get_snippet_fastapi():
    res = get_snippet("pqblocks-jwe", "fastapi")
    assert "from fastapi import" in res["code"]
    ast.parse(res["code"])


def test_get_snippet_unknown():
    res = get_snippet("unknown-pkg")
    assert "error" in res


def test_check_config_vulnerable():
    code = """
    key = generate_key(algorithm="RSA-2048")
    cert = sign_cert(algorithm="ECDSA")
    """
    res = check_config(code)
    assert not res["compliant"]
    assert res["findings_count"] >= 2
    detected = [f["detected"] for f in res["findings"]]
    assert "RSA" in detected or "RSA-2048" in detected
    assert "ECDSA" in detected


def test_check_config_pure_mlkem_warning():
    code = "kem = load_primitive('ML-KEM-768')"
    res = check_config(code)
    assert any("hybrid" in f["vulnerability"].lower() for f in res["findings"])


def test_check_config_clean():
    code = "from pqblocks_core import HybridKEM; kem = HybridKEM.standard_768()"
    res = check_config(code)
    # No classical algorithms mentioned
    assert res["compliant"]
    assert res["findings_count"] == 0


def test_list_packages_all():
    packages = list_packages()
    assert len(packages) >= 10
    names = [p["package"] for p in packages]
    assert "pqblocks-jwe" in names
    assert "pqblocks-bifurcation" in names


def test_list_packages_filtered():
    pq_crypto = list_packages(category="Interoperability")
    for p in pq_crypto:
        assert p["category"] == "Interoperability"
