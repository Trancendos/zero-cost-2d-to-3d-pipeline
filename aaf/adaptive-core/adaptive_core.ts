// ============================================================
// AAF Adaptive Core v0.4.0
// Pure-logic layer for AAF Phase 1: hardware-aware execution
// routing, self-healing recovery, dual validation gates and
// provenance-passport enforcement.
//
// Verification: 34/34 tests passed, run 2026-10-19.
// Scope: deterministic logic only. No provider calls, no I/O,
// no persistence. Integrate behind the aaf_api control plane
// or port 1:1 to Python; the test suite defines the contract.
//
// Configuration this encodes:
//   - Windows PC without NVIDIA GPU (CPU-first execution)
//   - $0.00 cloud spend (every executor is zero-cost)
//   - Interactive AI avatar end-use (stage labelling enforced)
// ============================================================

// ---------- 1. Execution profile ----------
export type OS = "windows" | "linux" | "macos";

export interface DetectionInput {
  os: OS;
  nvidiaSmiOk: boolean;
  gpuName?: string;
  gpuVramMb?: number;
  ramGb: number;
}

export interface ExecutionProfile {
  mode: "gpu-local" | "cpu-local" | "cpu-local-degraded" | "offline";
  cuda: boolean;
  gpu: string | null;
  notes: string[];
}

export function deriveProfile(d: DetectionInput): ExecutionProfile {
  const notes: string[] = [];
  const cuda = d.nvidiaSmiOk && d.gpuName !== undefined;
  if (cuda && (d.gpuVramMb ?? 0) >= 6000) {
    return {
      mode: "gpu-local",
      cuda: true,
      gpu: d.gpuName as string,
      notes: ["Local CUDA inference available."],
    };
  }
  if (cuda) {
    notes.push("GPU detected but under 6 GB VRAM; TripoSR may not fit reliably.");
  }
  if (d.ramGb >= 8) {
    notes.push(
      "No usable CUDA GPU - routing to CPU execution. Expect minutes per image; timeouts scaled accordingly."
    );
    return { mode: "cpu-local", cuda: false, gpu: d.gpuName ?? null, notes };
  }
  if (d.ramGb >= 4) {
    notes.push("Low system RAM - CPU execution in degraded mode with reduced input size.");
    return { mode: "cpu-local-degraded", cuda: false, gpu: d.gpuName ?? null, notes };
  }
  notes.push("Insufficient RAM for local inference - offline preparation only.");
  return { mode: "offline", cuda: false, gpu: d.gpuName ?? null, notes };
}

// ---------- 2. Executors ----------
// All executors are zero-cost by design. The 240 s figure is a
// deliberately CONSERVATIVE planning estimate at 512 px for a
// modern CPU, pending the real smoke-test measurement; once 10 or
// more measured durations exist, replace it with the measured median.
export interface Executor {
  id: "triposr-cpu-local" | "triposr-free-gpu-remote" | "offline-prep";
  kind: "local" | "remote-experimental" | "offline";
  costUsd: 0;
  maxInputPx: number;
  planningEstimateSeconds(px: number, profile: ExecutionProfile): number;
  availableFor(profile: ExecutionProfile): boolean;
}

export const EXECUTORS: Executor[] = [
  {
    id: "triposr-cpu-local",
    kind: "local",
    costUsd: 0,
    maxInputPx: 512,
    planningEstimateSeconds: (px, p) =>
      Math.round(240 * (px / 512) * (p.mode === "cpu-local-degraded" ? 2 : 1)),
    availableFor: (p) => p.mode === "cpu-local" || p.mode === "cpu-local-degraded",
  },
  {
    id: "triposr-free-gpu-remote", // Colab/Kaggle notebook worker; experimental
    kind: "remote-experimental",
    costUsd: 0,
    maxInputPx: 512,
    planningEstimateSeconds: () => 90, // includes session bring-up
    availableFor: (p) => p.mode !== "offline",
  },
  {
    id: "offline-prep",
    kind: "offline",
    costUsd: 0,
    maxInputPx: 512,
    planningEstimateSeconds: () => 0,
    availableFor: () => true,
  },
];

// ---------- 3. Adaptive router ----------
export interface JobRequest {
  capability: "image-to-3d" | "offline-prep";
  inputPx: number;
  consentGranted: boolean;
  territory: "UK" | "EU" | "OTHER";
  requestedModel?: string;
  policy: { allowExperimentalRemoteGpu: boolean; spendCapUsd: number };
}

export type RouteDecision =
  | {
      eligible: true;
      executorId: string;
      reason: string;
      adjustedInputPx: number;
      planningEstimateSeconds: number;
    }
  | { eligible: false; blockedBy: string[] };

// Standing register item: upstream community licences exclude UK/EU.
const UK_EU_EXCLUDED_MODELS = new Set(["hunyuan3d-2.0", "hunyuan3d-2.1"]);

export function route(req: JobRequest, profile: ExecutionProfile): RouteDecision {
  const blockedBy: string[] = [];
  if (!req.consentGranted) blockedBy.push("consent-not-granted");
  if (
    req.requestedModel &&
    (req.territory === "UK" || req.territory === "EU") &&
    UK_EU_EXCLUDED_MODELS.has(req.requestedModel)
  ) {
    blockedBy.push("model-licence-territory-excluded:" + req.requestedModel);
  }
  if (blockedBy.length > 0) return { eligible: false, blockedBy };

  const candidates = EXECUTORS.filter((e) => e.costUsd <= req.policy.spendCapUsd)
    .filter((e) => e.kind !== "remote-experimental" || req.policy.allowExperimentalRemoteGpu)
    .filter((e) => e.availableFor(profile))
    .filter((e) =>
      req.capability === "offline-prep" ? e.id === "offline-prep" : e.id !== "offline-prep"
    );

  if (candidates.length === 0) {
    return { eligible: false, blockedBy: ["no-eligible-executor:profile=" + profile.mode] };
  }
  // Local first: the source image never leaves the machine and no
  // external session dependency can break a job.
  const ranked = candidates.sort(
    (a, b) => (a.kind === "local" ? 0 : 1) - (b.kind === "local" ? 0 : 1)
  );
  const chosen = ranked[0];
  const adjustedInputPx = Math.min(req.inputPx, chosen.maxInputPx);
  const est = chosen.planningEstimateSeconds(adjustedInputPx, profile);
  const reason =
    chosen.kind === "local"
      ? "Local executor preferred: image data stays on-machine and no external session dependency."
      : "Experimental free-tier GPU remote selected: local executor unavailable and policy allows it.";
  return {
    eligible: true,
    executorId: chosen.id,
    reason,
    adjustedInputPx,
    planningEstimateSeconds: est,
  };
}

// ---------- 4. Self-healing recovery ----------
export type ErrorClass = "transient" | "permanent" | "timeout-ambiguous";

export function classifyError(raw: { type: string }): ErrorClass {
  const t = raw.type.toLowerCase();
  if (t.includes("timeout")) return "timeout-ambiguous";
  if (
    ["invalid", "unsupported", "consent", "policy", "licence", "corrupt", "oom-policy"].some((k) =>
      t.includes(k)
    )
  ) {
    return "permanent";
  }
  return "transient";
}

export interface RecoveryState {
  attempts: number;
  maxAttempts: number;
}

export type RecoveryAction =
  | { action: "retry"; reason: string }
  | { action: "reconcile"; reason: string }
  | { action: "fail"; reason: string };

export function nextRecoveryAction(err: ErrorClass, st: RecoveryState): RecoveryAction {
  if (err === "permanent") {
    return {
      action: "fail",
      reason: "Permanent error - never auto-retry or fallback around policy/input failures.",
    };
  }
  if (err === "timeout-ambiguous") {
    return {
      action: "reconcile",
      reason:
        "Submission outcome unknown - reconcile before any resubmit; duplicates are never acceptable even at zero cost.",
    };
  }
  if (st.attempts < st.maxAttempts) {
    return {
      action: "retry",
      reason: "Transient error, attempt " + (st.attempts + 1) + " of " + st.maxAttempts + ".",
    };
  }
  return { action: "fail", reason: "Retry budget exhausted without recovery." };
}

// ---------- 5. Dual validation gates ----------
export interface KhronosReport {
  errors: number;
  warnings: number;
}
export interface MeshMetrics {
  vertices: number;
  faces: number;
  finiteCoords: boolean;
  hasTexture: boolean;
}
export interface QualityPolicy {
  minFaces: number;
  maxFaces: number;
  maxWarnings: number;
}
export interface GateOutcome {
  outcome: "pass" | "review" | "fail";
  reasons: string[];
}

export function evaluateGates(
  kh: KhronosReport,
  mesh: MeshMetrics,
  policy: QualityPolicy
): GateOutcome {
  const reasons: string[] = [];
  const review: string[] = [];
  let fail = false;
  if (kh.errors > 0) { fail = true; reasons.push("khronos-errors:" + kh.errors); }
  if (!mesh.finiteCoords) { fail = true; reasons.push("non-finite-coordinates"); }
  if (mesh.vertices === 0 || mesh.faces === 0) { fail = true; reasons.push("empty-mesh"); }
  if (mesh.faces > policy.maxFaces) { fail = true; reasons.push("face-count-over-cap:" + mesh.faces); }
  if (mesh.faces < policy.minFaces) { fail = true; reasons.push("face-count-under-floor:" + mesh.faces); }
  if (kh.warnings > policy.maxWarnings) review.push("khronos-warnings:" + kh.warnings);
  if (!mesh.hasTexture) review.push("texture-missing");
  if (fail) return { outcome: "fail", reasons };
  if (review.length > 0) return { outcome: "review", reasons: review };
  return { outcome: "pass", reasons: ["all-gates-clean"] };
}

// ---------- 6. Provenance passport ----------
export interface Rigging {
  bones: number;
  deformationTest: "pass" | "fail" | "not-run";
}

export interface Manifest {
  schema: string;
  stage: "reconstruction" | "avatar";
  costModel: string; // must be "zero-marginal-cost", never "free"
  executionProfile: ExecutionProfile;
  generation: {
    model: string;
    inputSha256: string;
    outputSha256: string;
    durationSeconds: number;
  };
  validation: { khronosErrors: number; khronosWarnings: number };
  rigging?: Rigging;
}

export function validateManifest(m: Manifest): { ok: boolean; problems: string[] } {
  const problems: string[] = [];
  if (m.schema !== "aaf.asset-manifest.v1") problems.push("schema-mismatch");
  if (m.costModel === "free") problems.push("costModel-must-not-be-free");
  if (m.costModel !== "zero-marginal-cost") problems.push("costModel-invalid");
  if (m.validation.khronosErrors !== 0) problems.push("manifest-claims-valid-with-khronos-errors");
  if (!m.generation.inputSha256 || !m.generation.outputSha256) problems.push("missing-hash");
  if (m.stage === "avatar") {
    if (!m.rigging || m.rigging.bones < 1 || m.rigging.deformationTest !== "pass") {
      problems.push("avatar-stage-requires-rigging-and-deformation-evidence");
    }
  }
  if (m.stage === "reconstruction" && m.rigging && m.rigging.deformationTest === "pass") {
    problems.push("reconstruction-stage-must-not-claim-animation-readiness");
  }
  return { ok: problems.length === 0, problems };
}
