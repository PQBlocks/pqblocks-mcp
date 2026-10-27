"""PQBlocks Catalog & Migration Engine for AI Coding Assistants.

Authoritative package metadata, keywords, snippets, and crypto rule checkers.
Part of PQBlocks — a QubitRock project.
"""

from typing import Dict, List, Optional, Any

PACKAGES: Dict[str, Dict[str, Any]] = {
    "pqblocks-jwe": {
        "repo": "hybrid-jwe",
        "category": "Interoperability",
        "kind": "pq",
        "summary": "Compact five-part wire format for post-quantum hybrid JSON Web Encryption (JWE) using ML-KEM-768 + X25519.",
        "standards": ["RFC 7516", "FIPS 203 (ML-KEM-768)", "RFC 7748 (X25519)"],
        "keywords": ["jwe", "json web encryption", "jwt", "token encryption", "hybrid encryption", "encrypt jwt", "payload encryption"],
        "pip": "pip install pqblocks-jwe",
        "import_name": "pqblocks_jwe",
        "snippets": {
            "python": """from pqblocks_jwe import encrypt_jwe, decrypt_jwe, generate_hybrid_keypair

# 1. Generate post-quantum hybrid keypair (ML-KEM-768 + X25519)
recipient_priv, recipient_pub = generate_hybrid_keypair()

# 2. Encrypt plaintext payload into compact 5-part JWE token
payload = b"Top secret post-quantum payload"
token = encrypt_jwe(payload, recipient_pub)

# 3. Decrypt token using recipient private key
decrypted = decrypt_jwe(token, recipient_priv)
assert decrypted == payload
print("Decrypted successfully:", decrypted.decode("utf-8"))
""",
            "fastapi": """from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pqblocks_jwe import decrypt_jwe, generate_hybrid_keypair

app = FastAPI(title="PQC JWE Auth Service")
security = HTTPBearer()

# Server private key loaded from secure config
SERVER_PRIV, SERVER_PUB = generate_hybrid_keypair()

def get_current_payload(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        data = decrypt_jwe(token, SERVER_PRIV)
        return data
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid post-quantum JWE token")

@app.get("/api/v1/protected")
def protected_endpoint(payload: bytes = Depends(get_current_payload)):
    return {"status": "ok", "bytes_received": len(payload)}
"""
        }
    },
    "pqblocks-jose": {
        "repo": "hybrid-jose",
        "category": "Interoperability",
        "kind": "pq",
        "summary": "Post-quantum hybrid JOSE: JWS signing with ML-DSA-65 / Ed25519 and JWE encryption with ML-KEM-768.",
        "standards": ["RFC 7515 (JWS)", "RFC 7516 (JWE)", "FIPS 203", "FIPS 204"],
        "keywords": ["jose", "jws", "jwt signing", "jwt verify", "ml-dsa jwt", "hybrid signature", "token sign"],
        "pip": "pip install pqblocks-jose",
        "import_name": "pqblocks_jose",
        "snippets": {
            "python": """from pqblocks_jose import sign_jws, verify_jws, generate_signing_keypair

# 1. Generate ML-DSA + Ed25519 hybrid keypair
signing_key, verify_key = generate_signing_keypair()

# 2. Sign a JWT header + claims
claims = {"sub": "user_123", "role": "admin", "aud": "pqblocks.org"}
compact_jws = sign_jws(claims, signing_key)

# 3. Verify signature and extract claims
verified_claims = verify_jws(compact_jws, verify_key)
print("Verified claims:", verified_claims)
"""
        }
    },
    "pqblocks-core": {
        "repo": "hybrid-sdk",
        "category": "PQ cryptography",
        "kind": "pq",
        "summary": "Core post-quantum hybrid cryptographic primitives (ML-KEM-768/1024, ML-DSA-65/87, X25519, Ed25519).",
        "standards": ["FIPS 203 (ML-KEM)", "FIPS 204 (ML-DSA)", "RFC 7748", "RFC 8032"],
        "keywords": ["hybrid-sdk", "core crypto", "ml-kem", "ml-dsa", "kem keypair", "encap", "decap", "dilithium", "kyber"],
        "pip": "pip install pqblocks-core",
        "import_name": "pqblocks_core",
        "snippets": {
            "python": """from pqblocks_core import HybridKEM

# Combined ML-KEM-768 + X25519 key encapsulation
kem = HybridKEM.standard_768()
pubkey, privkey = kem.keygen()

# Sender encapsulates a shared secret
ciphertext, shared_secret_sender = kem.encapsulate(pubkey)

# Receiver decapsulates using private key
shared_secret_receiver = kem.decapsulate(ciphertext, privkey)
assert shared_secret_sender == shared_secret_receiver
print("Shared secret negotiated:", shared_secret_sender.hex()[:32], "...")
"""
        }
    },
    "pqblocks-wire": {
        "repo": "pqc-wireformat",
        "category": "Interoperability",
        "kind": "pq",
        "summary": "Length-prefixed binary container and serialization format for post-quantum keys, ciphertexts and signatures.",
        "standards": ["NIST PQC Framing Draft", "CBOR / Length-prefix"],
        "keywords": ["wireformat", "binary format", "container", "length-prefixed", "serialization", "pqc wire", "packet encoding"],
        "pip": "pip install pqblocks-wire",
        "import_name": "pqblocks_wire",
        "snippets": {
            "python": """from pqblocks_wire import pack_message, unpack_message, ALGO_MLKEM_768_X25519

# Package hybrid public key + metadata into structured wire packet
packed = pack_message(algo_id=ALGO_MLKEM_768_X25519, key_bytes=b"raw_key_material", payload=b"hello wire")
msg = unpack_message(packed)
print(f"Algorithm: {msg.algo_id}, Payload size: {len(msg.payload)}")
"""
        }
    },
    "pqblocks-tls-interop": {
        "repo": "tls-hybrid-interop",
        "category": "Interoperability",
        "kind": "pq",
        "summary": "TLS 1.3 hybrid key exchange interoperability test suite and client/server handshake validators (X25519MLKEM768).",
        "standards": ["RFC 8446 (TLS 1.3)", "draft-ietf-tls-hybrid-design-09", "X25519MLKEM768"],
        "keywords": ["tls", "tls 1.3", "x25519mlkem768", "handshake", "tls client", "tls server", "post-quantum tls"],
        "pip": "pip install pqblocks-tls-interop",
        "import_name": "pqblocks_tls_interop",
        "snippets": {
            "python": """from pqblocks_tls_interop import validate_tls_client_hello, test_hybrid_handshake

# Validate that a ClientHello offers the standardized X25519MLKEM768 group (0x11ec)
result = validate_tls_client_hello(raw_client_hello_bytes)
print(f"PQC Offered: {result.pqc_enabled}, Named Group: {result.group_name}")
"""
        }
    },
    "pqblocks-csr-pop": {
        "repo": "mlkem-csr-pop",
        "category": "Interoperability",
        "kind": "pq",
        "summary": "ML-KEM (FIPS 203) PKCS#10 Certificate Signing Request (CSR) Proof-of-Possession challenge/response engine.",
        "standards": ["RFC 2986 (PKCS#10)", "RFC 4210 (CMP)", "IETF draft-ietf-lamps-kyber-certificates"],
        "keywords": ["csr", "pkcs10", "proof of possession", "csr pop", "ca", "x509 csr", "certificate request"],
        "pip": "pip install pqblocks-csr-pop",
        "import_name": "pqblocks_csr_pop",
        "snippets": {
            "python": """from pqblocks_csr_pop import create_kem_csr, verify_csr_pop_challenge

# Generate CSR for an ML-KEM key with interactive POP challenge
csr = create_kem_csr(kem_pubkey, subject_dn="CN=quantum-safe.example.com")
print("Generated CSR size:", len(csr))
"""
        }
    },
    "pqblocks-scan": {
        "repo": "cbom-scanner",
        "category": "Migration & readiness",
        "kind": "pq",
        "summary": "Static analysis cryptography inventory scanner detecting classical and quantum-safe algorithms across source trees.",
        "standards": ["CycloneDX 1.5 CBOM", "NIST SP 800-131A"],
        "keywords": ["scan", "cbom", "crypto inventory", "static analysis", "detect classical", "find crypto", "audit algorithms"],
        "pip": "pip install pqblocks-scan",
        "import_name": "pqblocks_scan",
        "snippets": {
            "python": """from pqblocks_scan import scan_directory

# Scan project directory for cryptographic algorithm references
inventory = scan_directory("./src")
for item in inventory.findings:
    print(f"[{item.severity}] {item.file}:{item.line} -> {item.algorithm} ({item.recommendation})")
"""
        }
    },
    "pqblocks-cbom": {
        "repo": "cbom-enricher",
        "category": "Migration & readiness",
        "kind": "pq",
        "summary": "CycloneDX 1.5 Cryptography Bill of Materials (CBOM) enricher and compliance scorer against NIST/CNSA 2.0 standards.",
        "standards": ["CycloneDX 1.5 CBOM", "CNSA 2.0", "NIST IR 8547"],
        "keywords": ["cbom", "cyclonedx", "sbom", "bom", "crypto bill of materials", "cnsa score", "readiness score"],
        "pip": "pip install pqblocks-cbom",
        "import_name": "pqblocks_cbom",
        "snippets": {
            "python": """from pqblocks_cbom import enrich_cbom, score_readiness

# Enrich raw CBOM file with NIST/CNSA security levels and timeline deadlines
cbom = enrich_cbom("cyclonedx-cbom.json")
score = score_readiness(cbom)
print(f"Quantum Readiness Score: {score.percentage}% (CNSA 2.0 compliance: {score.cnsa_compliant})")
"""
        }
    },
    "pqblocks-policy": {
        "repo": "crypto-policy-engine",
        "category": "Migration & readiness",
        "kind": "pq",
        "summary": "Policy-as-code evaluation engine enforcing quantum-safe algorithm requirements in CI/CD and runtime systems.",
        "standards": ["CNSA 2.0", "ANSSI PQC Guidelines", "BSI TR-02102"],
        "keywords": ["policy", "crypto policy", "policy as code", "ci gate", "algorithm rules", "forbid rsa", "require hybrid"],
        "pip": "pip install pqblocks-policy",
        "import_name": "pqblocks_policy",
        "snippets": {
            "python": """from pqblocks_policy import PolicyEngine, PolicyPreset

# Enforce CNSA 2.0 policy in CI/CD
engine = PolicyEngine(preset=PolicyPreset.CNSA_2_0)
verdict = engine.evaluate_configuration({"kem": "ML-KEM-768", "sig": "RSA-2048"})
print(f"Compliant: {verdict.is_allowed}")
for error in verdict.violations:
    print(f"Violation: {error}")
"""
        }
    },
    "pqblocks-cnsa-evidence": {
        "repo": "cnsa-evidence-pack",
        "category": "Migration & readiness",
        "kind": "pq",
        "summary": "NSA CNSA 2.0 migration evidence generation, gap-matrix compilation and auditor verification artifacts.",
        "standards": ["NSA CNSA 2.0 Mandate"],
        "keywords": ["cnsa", "cnsa 2.0", "evidence pack", "nsa compliance", "gap matrix", "audit report", "compliance proof"],
        "pip": "pip install pqblocks-cnsa-evidence",
        "import_name": "pqblocks_cnsa_evidence",
        "snippets": {
            "python": """from pqblocks_cnsa_evidence import generate_evidence_pack

# Generate complete CNSA 2.0 compliance dossier
pack = generate_evidence_pack(system_profile="profile.json", target_timeline="2030")
pack.export_markdown("CNSA_EVIDENCE_REPORT.md")
print("Evidence pack written to CNSA_EVIDENCE_REPORT.md")
"""
        }
    },
    "pqblocks-lint": {
        "repo": "pqc-lint",
        "category": "Migration & readiness",
        "kind": "pq",
        "summary": "AST-based static linter flagging deprecated classical cryptography APIs (pyca/cryptography, hashlib, ssl) in Python.",
        "standards": ["Python AST", "NIST SP 800-131A"],
        "keywords": ["lint", "pqc-lint", "linter", "ast lint", "check python crypto", "flake8 plugin", "pre-commit crypto"],
        "pip": "pip install pqblocks-lint",
        "import_name": "pqblocks_lint",
        "snippets": {
            "python": """from pqblocks_lint import lint_source

code = \"\"\"
from cryptography.hazmat.primitives.asymmetric import rsa
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
\"\"\"
issues = lint_source(code)
for issue in issues:
    print(f"Line {issue.lineno}: {issue.message} -> {issue.recommendation}")
"""
        }
    },
    "pqblocks-fips-check": {
        "repo": "fips-boundary-validator",
        "category": "Conformance",
        "kind": "pq",
        "summary": "Strict input/output boundary validator rejecting malformed, truncated or out-of-spec FIPS 203/204/205 wire buffers.",
        "standards": ["FIPS 203", "FIPS 204", "FIPS 205"],
        "keywords": ["boundary", "fips check", "buffer validation", "malformed key", "wire check", "fips boundary", "length check"],
        "pip": "pip install pqblocks-fips-check",
        "import_name": "pqblocks_fips_check",
        "snippets": {
            "python": """from pqblocks_fips_check import validate_mlkem768_ciphertext, ValidationError

try:
    validate_mlkem768_ciphertext(raw_ciphertext_bytes)
    print("Ciphertext format conforms to FIPS 203 exactly (1088 bytes)")
except ValidationError as e:
    print("Rejected malformed input:", e)
"""
        }
    },
    "pqblocks-acvp": {
        "repo": "acvp-conformance",
        "category": "Conformance",
        "kind": "pq",
        "summary": "Automated NIST Automated Cryptographic Validation Protocol (ACVP) vector harness runner for ML-KEM and ML-DSA.",
        "standards": ["NIST ACVP", "FIPS 203 Vectors", "FIPS 204 Vectors"],
        "keywords": ["acvp", "conformance", "kat", "nist vectors", "test vectors", "cavp", "validation runner"],
        "pip": "pip install pqblocks-acvp",
        "import_name": "pqblocks_acvp",
        "snippets": {
            "python": """from pqblocks_acvp import run_acvp_vector_set

results = run_acvp_vector_set("tests/vectors/ML-KEM-keyGen-FIPS203.json")
print(f"Tests executed: {results.total}, Passed: {results.passed}, Failed: {results.failed}")
"""
        }
    },
    "pqblocks-bifurcation": {
        "repo": "simulated-bifurcation",
        "category": "Quantum-inspired",
        "kind": "optimizer",
        "summary": "Ballistic (bSB) and Discrete (dSB) Simulated Bifurcation algorithm for large-scale Ising and QUBO combinatorial optimization.",
        "standards": ["Goto et al. (Science Advances 2019 / Nature Communications 2021)"],
        "keywords": ["bifurcation", "simulated bifurcation", "qubo", "ising", "max-cut", "combinatorial optimization", "quantum-inspired"],
        "pip": "pip install pqblocks-bifurcation",
        "import_name": "pqblocks_bifurcation",
        "snippets": {
            "python": """import numpy as np
from pqblocks_bifurcation import SimulatedBifurcationSampler

# Formulate Ising coupling matrix J and external field h
J = np.array([
    [0.0, 1.0, 0.0, 1.0],
    [1.0, 0.0, 1.0, 0.0],
    [0.0, 1.0, 0.0, 1.0],
    [1.0, 0.0, 1.0, 0.0]
])
h = np.zeros(4)

sampler = SimulatedBifurcationSampler(mode="bSB", steps=1000, seed=42)
spins, energy = sampler.sample_ising(J, h)
print(f"Ground state configuration: {spins}, Energy: {energy}")
"""
        }
    },
    "pqblocks-qubo": {
        "repo": "qubo-core",
        "category": "Quantum-inspired",
        "kind": "optimizer",
        "summary": "Unified mathematical representations, matrix conversions and validation for QUBO and Ising models.",
        "standards": ["Ising Hamiltonian Formulism"],
        "keywords": ["qubo", "ising", "hamiltonian", "qubo-core", "quadratic unconstrained binary optimization", "matrix conversion"],
        "pip": "pip install pqblocks-qubo",
        "import_name": "pqblocks_qubo",
        "snippets": {
            "python": """from pqblocks_qubo import QUBOMatrix, ising_to_qubo

# Convert Ising instance (J, h) into upper-triangular QUBO matrix Q
Q = ising_to_qubo(J, h)
print("QUBO Matrix shape:", Q.shape)
"""
        }
    }
}

CLASSICAL_ALGORITHMS = {
    "RSA": {"replace_with": "ML-KEM-768 / X25519 hybrid (encryption) or ML-DSA-65 (signatures)", "package": "pqblocks-jwe or pqblocks-jose"},
    "RSA-2048": {"replace_with": "ML-KEM-768 hybrid (RFC 9180/FIPS 203)", "package": "pqblocks-core"},
    "RSA-4096": {"replace_with": "ML-KEM-1024 hybrid (FIPS 203)", "package": "pqblocks-core"},
    "ECDSA": {"replace_with": "ML-DSA-65 / Ed25519 hybrid (FIPS 204)", "package": "pqblocks-jose"},
    "SECP256R1": {"replace_with": "ML-DSA-65 or ML-KEM-768 hybrid", "package": "pqblocks-core"},
    "P-256": {"replace_with": "ML-KEM-768 hybrid (X25519MLKEM768)", "package": "pqblocks-tls-interop"},
    "DIFFIE-HELLMAN": {"replace_with": "ML-KEM-768 hybrid KEM", "package": "pqblocks-core"},
    "ECDH": {"replace_with": "Hybrid X25519 + ML-KEM-768", "package": "pqblocks-core"}
}


def recommend(task_description: str) -> Dict[str, Any]:
    """Find the best matching PQBlocks package for a developer task."""
    desc = task_description.lower()
    best_pkg = "pqblocks-core"
    best_score = 0
    matched_reason = "General post-quantum hybrid cryptographic library"

    for name, data in PACKAGES.items():
        score = 0
        for kw in data["keywords"]:
            if kw in desc:
                score += 3
        for std in data["standards"]:
            if std.lower() in desc:
                score += 4
        if score > best_score:
            best_score = score
            best_pkg = name
            matched_reason = f"Matches requirements for {data['summary']}"

    # Default fallbacks if no direct match
    if "jwt" in desc or "jwe" in desc or "encrypt token" in desc:
        best_pkg = "pqblocks-jwe"
        matched_reason = "Compact post-quantum hybrid JWE token encryption"
    elif "sign" in desc or "signature" in desc or "jws" in desc:
        best_pkg = "pqblocks-jose"
        matched_reason = "Post-quantum hybrid JWS signing (ML-DSA + Ed25519)"
    elif "tls" in desc or "handshake" in desc:
        best_pkg = "pqblocks-tls-interop"
        matched_reason = "TLS 1.3 X25519MLKEM768 hybrid group validation"
    elif "scan" in desc or "inventory" in desc or "find" in desc:
        best_pkg = "pqblocks-scan"
        matched_reason = "Static cryptography inventory scanner and CBOM generation"
    elif "cbom" in desc or "cyclonedx" in desc:
        best_pkg = "pqblocks-cbom"
        matched_reason = "CycloneDX 1.5 CBOM compliance enricher and readiness scorer"
    elif "policy" in desc or "gate" in desc or "cnsa" in desc:
        best_pkg = "pqblocks-policy"
        matched_reason = "Policy-as-code gate enforcing quantum-safe standards"
    elif "bifurcation" in desc or "qubo" in desc or "ising" in desc or "optimize" in desc:
        best_pkg = "pqblocks-bifurcation"
        matched_reason = "Simulated Bifurcation heuristic solver for QUBO/Ising optimization"

    pkg_info = PACKAGES[best_pkg]
    return {
        "recommended_package": best_pkg,
        "repo": f"PQBlocks/{pkg_info['repo']}",
        "category": pkg_info["category"],
        "kind": pkg_info["kind"],
        "why": matched_reason,
        "install_command": pkg_info["pip"],
        "standards": pkg_info["standards"],
        "quick_snippet": pkg_info["snippets"].get("python", "")
    }


def snippet(package_name: str, framework: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve runnable code snippet and setup instructions for a package."""
    pkg = package_name.lower().replace("_", "-")
    if pkg not in PACKAGES:
        return {
            "error": f"Package '{package_name}' not found. Available packages: {list(PACKAGES.keys())}"
        }
    
    data = PACKAGES[pkg]
    fw = (framework or "python").lower()
    code = data["snippets"].get(fw) or data["snippets"].get("python", "")
    
    return {
        "package": pkg,
        "install": data["pip"],
        "framework": fw if fw in data["snippets"] else "python",
        "code": code,
        "standards": data["standards"],
        "summary": data["summary"]
    }


def check_configuration(code_or_config: str) -> Dict[str, Any]:
    """Analyze code or configuration for classical-only crypto and missing post-quantum protections."""
    text = code_or_config.upper()
    findings = []
    
    for algo, info in CLASSICAL_ALGORITHMS.items():
        if algo in text:
            findings.append({
                "vulnerability": "Classical algorithm vulnerable to quantum decryption (CRQC)",
                "detected": algo,
                "replacement": info["replace_with"],
                "recommended_package": info["package"],
                "severity": "HIGH"
            })
            
    # Check for missing hybrid posture
    if "ML-KEM" in text and "X25519" not in text:
        findings.append({
            "vulnerability": "Standalone post-quantum KEM without classical hybrid pairing",
            "detected": "Pure ML-KEM",
            "replacement": "Hybrid ML-KEM + X25519",
            "recommended_package": "pqblocks-core or pqblocks-jwe",
            "severity": "MEDIUM",
            "note": "Defense-in-depth: combine PQC with classical algorithms to maintain security if either has an implementation defect."
        })
        
    return {
        "findings_count": len(findings),
        "compliant": len(findings) == 0,
        "findings": findings
    }


def list_catalog(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all available packages with metadata and category filter."""
    result = []
    for name, data in PACKAGES.items():
        if category and category.lower() != data["category"].lower():
            continue
        result.append({
            "package": name,
            "repo": f"PQBlocks/{data['repo']}",
            "category": data["category"],
            "kind": data["kind"],
            "summary": data["summary"],
            "standards": data["standards"],
            "install": data["pip"]
        })
    return result
