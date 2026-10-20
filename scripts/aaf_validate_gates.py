# aaf_validate_gates.py - AAF dual validation gates (DRAFT)
# Mirrors evaluateGates() in aaf/adaptive-core/adaptive_core.ts - keep in sync.
# Usage: python aaf_validate_gates.py <output.glb>
# Gate 1: official Khronos glTF Validator (npm package gltf-validator).
# Gate 2: mesh metrics via Trimesh.
# Exit codes: 0 = pass | 2 = review | 1 = fail
import json, subprocess, sys, tempfile, pathlib

GLB = pathlib.Path(sys.argv[1])
MAX_WARNINGS = 5
MIN_FACES, MAX_FACES = 500, 500_000

def gate1_khronos(glb_path: pathlib.Path) -> dict:
    node_js = """
    const validator = require('gltf-validator');
    const fs = require('fs');
    const data = fs.readFileSync(process.argv[1]);
    validator.validateBytes(new Uint8Array(data)).then(r =>
      console.log(JSON.stringify({errors: r.issues.numErrors, warnings: r.issues.numWarnings}))
    ).catch(e => { console.error(e.message); process.exit(1); });
    """
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(node_js); script = f.name
    out = subprocess.run(["node", script, str(glb_path)], capture_output=True, text=True, timeout=120)
    pathlib.Path(script).unlink(missing_ok=True)
    if out.returncode != 0:
        return {"errors": 1, "warnings": 0, "_note": "validator-invocation-failed: " + out.stderr[:200]}
    return json.loads(out.stdout)

def gate2_mesh(glb_path: pathlib.Path) -> dict:
    import trimesh
    scene = trimesh.load(glb_path, force="scene")
    meshes = list(scene.geometry.values()) if hasattr(scene, "geometry") else [scene]
    total_v = sum(m.vertices.shape[0] for m in meshes)
    total_f = sum(m.faces.shape[0] for m in meshes)
    finite = all(bool(m.verticesFinite) if hasattr(m, "verticesFinite")
                 else bool((m.vertices == m.vertices).all()) for m in meshes)
    has_texture = any(getattr(m.visual, "texture", None) is not None for m in meshes)
    return {"vertices": total_v, "faces": total_f, "finiteCoords": finite, "hasTexture": has_texture}

if __name__ == "__main__":
    kh = gate1_khronos(GLB)
    mesh = gate2_mesh(GLB)
    reasons, review = [], []
    if kh["errors"] > 0: reasons.append("khronos-errors:" + str(kh["errors"]))
    if not mesh["finiteCoords"]: reasons.append("non-finite-coordinates")
    if mesh["vertices"] == 0 or mesh["faces"] == 0: reasons.append("empty-mesh")
    if mesh["faces"] > MAX_FACES: reasons.append("face-count-over-cap:" + str(mesh["faces"]))
    if mesh["faces"] < MIN_FACES: reasons.append("face-count-under-floor:" + str(mesh["faces"]))
    if kh["warnings"] > MAX_WARNINGS: review.append("khronos-warnings:" + str(kh["warnings"]))
    if not mesh["hasTexture"]: review.append("texture-missing")
    verdict = "fail" if reasons else ("review" if review else "pass")
    print(json.dumps({"outcome": verdict, "reasons": reasons or review, "khronos": kh, "mesh": mesh}, indent=2))
    sys.exit({"pass": 0, "review": 2, "fail": 1}[verdict])
