// AAF Adaptive Core v0.4.0 - test suite (34 tests).
// Contract: every test must pass with zero failures. These tests also
// define the acceptance contract for a 1:1 Python port of the core.
import {
  deriveProfile,
  EXECUTORS,
  route,
  classifyError,
  nextRecoveryAction,
  evaluateGates,
  validateManifest,
} from "./adaptive_core";
import type { JobRequest, Manifest, MeshMetrics, QualityPolicy, RecoveryState } from "./adaptive_core";

const tests: Array<{ name: string; run: () => boolean }> = [];
function test(name: string, fn: () => boolean) { tests.push({ name, run: fn }); }
function assert(cond: boolean, msg: string): boolean {
  if (!cond) throw new Error(msg);
  return true;
}

// --- profiles ---
test("profile: nvidia 8GB -> gpu-local", () => {
  const p = deriveProfile({ os: "windows", nvidiaSmiOk: true, gpuName: "RTX 4070", gpuVramMb: 8192, ramGb: 32 });
  return assert(p.mode === "gpu-local" && p.cuda, "expected gpu-local");
});
test("profile: windows no nvidia 16GB -> cpu-local with honest note", () => {
  const p = deriveProfile({ os: "windows", nvidiaSmiOk: false, ramGb: 16 });
  return assert(p.mode === "cpu-local" && !p.cuda && p.notes.some((n) => n.includes("CPU")), "expected cpu-local");
});
test("profile: low RAM -> degraded", () => {
  const p = deriveProfile({ os: "windows", nvidiaSmiOk: false, ramGb: 6 });
  return assert(p.mode === "cpu-local-degraded", "expected degraded");
});
test("profile: tiny RAM -> offline only", () => {
  const p = deriveProfile({ os: "windows", nvidiaSmiOk: false, ramGb: 3 });
  return assert(p.mode === "offline", "expected offline");
});
test("profile: GPU under 6GB VRAM -> not gpu-local", () => {
  const p = deriveProfile({ os: "windows", nvidiaSmiOk: true, gpuName: "MX450", gpuVramMb: 2048, ramGb: 16 });
  return assert(p.mode === "cpu-local", "expected cpu fallback");
});

// --- router ---
const cpuProfile = deriveProfile({ os: "windows", nvidiaSmiOk: false, ramGb: 16 });
const offlineProfile = deriveProfile({ os: "windows", nvidiaSmiOk: false, ramGb: 3 });
const baseReq: JobRequest = {
  capability: "image-to-3d", inputPx: 512, consentGranted: true, territory: "UK",
  policy: { allowExperimentalRemoteGpu: false, spendCapUsd: 0 },
};

test("router: consent denied -> blocked", () => {
  const r = route({ ...baseReq, consentGranted: false }, cpuProfile);
  return assert(!r.eligible && r.blockedBy.includes("consent-not-granted"), "expected consent block");
});
test("router: hunyuan3d blocked for UK territory", () => {
  const r = route({ ...baseReq, requestedModel: "hunyuan3d-2.1" }, cpuProfile);
  return assert(!r.eligible && r.blockedBy.some((b) => b.startsWith("model-licence-territory-excluded")), "expected licence block");
});
test("router: hunyuan3d not blocked for OTHER territory", () => {
  const r = route({ ...baseReq, territory: "OTHER", requestedModel: "hunyuan3d-2.1" }, cpuProfile);
  return assert(r.eligible === true || (r.eligible === false && !r.blockedBy.some((b) => b.includes("territory"))), "no territory block expected");
});
test("router: local cpu executor preferred when available", () => {
  const r = route({ ...baseReq, policy: { allowExperimentalRemoteGpu: true, spendCapUsd: 0 } }, cpuProfile);
  return assert(r.eligible && r.executorId === "triposr-cpu-local", "expected local first");
});
test("router: remote experimental excluded when policy disallows", () => {
  const r = route(baseReq, cpuProfile);
  return assert(r.eligible && r.executorId === "triposr-cpu-local", "only local eligible");
});
test("router: offline profile blocks image-to-3d with clear reason", () => {
  const r = route(baseReq, offlineProfile);
  return assert(!r.eligible && r.blockedBy[0].includes("no-eligible-executor"), "expected executor block");
});
test("router: oversized input downscaled to executor cap", () => {
  const r = route({ ...baseReq, inputPx: 2048 }, cpuProfile);
  return assert(r.eligible && r.adjustedInputPx === 512, "expected downscale");
});
test("router: spend cap 0 never excludes zero-cost executors", () => {
  const r = route(baseReq, cpuProfile);
  return assert(r.eligible, "zero-cost executors must pass a 0 cap");
});
test("budget: every registered executor is zero-cost", () => {
  return assert(EXECUTORS.every((e) => e.costUsd === 0), "all executors must be zero-cost");
});

// --- recovery ---
const max3: RecoveryState = { attempts: 0, maxAttempts: 3 };
test("recovery: permanent error -> fail, never retry", () => {
  const a = nextRecoveryAction("permanent", max3);
  return assert(a.action === "fail", "expected fail");
});
test("recovery: timeout -> reconcile, never auto-resubmit", () => {
  const a = nextRecoveryAction("timeout-ambiguous", max3);
  return assert(a.action === "reconcile", "expected reconcile");
});
test("recovery: transient under budget -> retry", () => {
  const a = nextRecoveryAction("transient", { attempts: 1, maxAttempts: 3 });
  return assert(a.action === "retry", "expected retry");
});
test("recovery: transient at budget -> fail", () => {
  const a = nextRecoveryAction("transient", { attempts: 3, maxAttempts: 3 });
  return assert(a.action === "fail", "expected fail at cap");
});
test("classify: corrupt input is permanent", () => {
  return assert(classifyError({ type: "corrupt-output" }) === "permanent", "expected permanent");
});
test("classify: worker busy is transient", () => {
  return assert(classifyError({ type: "worker-busy" }) === "transient", "expected transient");
});
test("classify: submit timeout is ambiguous", () => {
  return assert(classifyError({ type: "submit-timeout" }) === "timeout-ambiguous", "expected ambiguous");
});

// --- validation ---
const qPolicy: QualityPolicy = { minFaces: 500, maxFaces: 500000, maxWarnings: 5 };
const goodMesh: MeshMetrics = { vertices: 25000, faces: 48000, finiteCoords: true, hasTexture: true };
test("gates: clean output passes", () => {
  return assert(evaluateGates({ errors: 0, warnings: 0 }, goodMesh, qPolicy).outcome === "pass", "expected pass");
});
test("gates: khronos errors fail regardless of mesh", () => {
  return assert(evaluateGates({ errors: 1, warnings: 0 }, goodMesh, qPolicy).outcome === "fail", "expected fail");
});
test("gates: non-finite coords fail", () => {
  return assert(evaluateGates({ errors: 0, warnings: 0 }, { ...goodMesh, finiteCoords: false }, qPolicy).outcome === "fail", "expected fail");
});
test("gates: empty mesh fails", () => {
  return assert(evaluateGates({ errors: 0, warnings: 0 }, { vertices: 0, faces: 0, finiteCoords: true, hasTexture: true }, qPolicy).outcome === "fail", "expected fail");
});
test("gates: face count over cap fails", () => {
  return assert(evaluateGates({ errors: 0, warnings: 0 }, { ...goodMesh, faces: 900000 }, qPolicy).outcome === "fail", "expected fail");
});
test("gates: excessive warnings -> human review, not pass", () => {
  return assert(evaluateGates({ errors: 0, warnings: 9 }, goodMesh, qPolicy).outcome === "review", "expected review");
});
test("gates: missing texture -> review", () => {
  return assert(evaluateGates({ errors: 0, warnings: 0 }, { ...goodMesh, hasTexture: false }, qPolicy).outcome === "review", "expected review");
});

// --- provenance ---
const gen = { model: "TripoSR", inputSha256: "a".repeat(64), outputSha256: "b".repeat(64), durationSeconds: 210 };
test("manifest: valid reconstruction manifest", () => {
  const m: Manifest = { schema: "aaf.asset-manifest.v1", stage: "reconstruction", costModel: "zero-marginal-cost", executionProfile: cpuProfile, generation: gen, validation: { khronosErrors: 0, khronosWarnings: 0 } };
  return assert(validateManifest(m).ok, "expected valid");
});
test("manifest: avatar stage without rigging evidence rejected", () => {
  const m: Manifest = { schema: "aaf.asset-manifest.v1", stage: "avatar", costModel: "zero-marginal-cost", executionProfile: cpuProfile, generation: gen, validation: { khronosErrors: 0, khronosWarnings: 0 } };
  return assert(!validateManifest(m).ok, "expected rejection");
});
test("manifest: avatar stage with rigging + deformation pass accepted", () => {
  const m: Manifest = { schema: "aaf.asset-manifest.v1", stage: "avatar", costModel: "zero-marginal-cost", executionProfile: cpuProfile, generation: gen, validation: { khronosErrors: 0, khronosWarnings: 0 }, rigging: { bones: 32, deformationTest: "pass" } };
  return assert(validateManifest(m).ok, "expected valid");
});
test("manifest: costModel 'free' explicitly rejected", () => {
  const m: Manifest = { schema: "aaf.asset-manifest.v1", stage: "reconstruction", costModel: "free", executionProfile: cpuProfile, generation: gen, validation: { khronosErrors: 0, khronosWarnings: 0 } };
  const v = validateManifest(m);
  return assert(!v.ok && v.problems.includes("costModel-must-not-be-free"), "expected wording rejection");
});
test("manifest: missing output hash rejected", () => {
  const m: Manifest = { schema: "aaf.asset-manifest.v1", stage: "reconstruction", costModel: "zero-marginal-cost", executionProfile: cpuProfile, generation: { ...gen, outputSha256: "" }, validation: { khronosErrors: 0, khronosWarnings: 0 } };
  return assert(!validateManifest(m).ok, "expected rejection");
});
test("manifest: khronos errors in manifest rejected", () => {
  const m: Manifest = { schema: "aaf.asset-manifest.v1", stage: "reconstruction", costModel: "zero-marginal-cost", executionProfile: cpuProfile, generation: gen, validation: { khronosErrors: 2, khronosWarnings: 0 } };
  return assert(!validateManifest(m).ok, "expected rejection");
});

// ---------- runner ----------
export function runAllTests(): { total: number; passed: number; failures: string[] } {
  const failures: string[] = [];
  for (const t of tests) {
    try { t.run(); } catch (e) { failures.push(t.name + ": " + String(e)); }
  }
  return { total: tests.length, passed: tests.length - failures.length, failures };
}

if (require.main === module) {
  const r = runAllTests();
  console.log("AAF Adaptive Core tests: " + r.passed + "/" + r.total + " passed");
  if (r.failures.length > 0) {
    for (const f of r.failures) console.error("FAILED " + f);
    process.exit(1);
  }
  process.exit(0);
}
