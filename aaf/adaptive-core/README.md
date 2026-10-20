# AAF Adaptive Core (v0.4.0)

Pure-logic TypeScript layer for AAF Phase 1. It encodes the locked project configuration: Windows PC without NVIDIA GPU (CPU-first execution), $0.00 cloud spend ("zero-marginal-cost", never "free"), and interactive AI avatar end-use with strict stage labelling - Phase 1 output is a "3D Reconstruction" and never an "Avatar" until rigging plus deformation-test evidence exists.

## Modules

| Module | Behaviour | Key rule enforced |
|---|---|---|
| Execution profiler | Parses hardware detection into gpu-local / cpu-local / cpu-local-degraded / offline | CPU mode gets honest "minutes per image" notes; GPUs under 6 GB VRAM never pass as inference-capable |
| Adaptive router | Hard gates (consent, UK/EU licence exclusion for Hunyuan3D 2.x, $0 spend cap), then ranks eligible executors | Local-first: the source image never leaves the machine; experimental remote GPU only when policy explicitly allows |
| Self-healing recovery | Classifies errors transient / permanent / timeout-ambiguous with bounded retries | Permanent errors never retry; ambiguous timeouts force reconciliation before any resubmit |
| Dual validation gates | Khronos structural errors plus mesh metrics produce pass / review / fail | Missing texture or excess warnings means human review, never a silent pass |
| Provenance passport | Builds and validates the asset manifest with stage enforcement | The avatar stage requires bones and a passed deformation test; costModel may never be the word "free" |

## Running the tests

Requires Node.js 20 or newer.

    npm install
    npm test

The test command compiles with strict TypeScript and runs the suite (34 tests). Evidence: 34/34 passed on 2026-10-19 in a sandboxed run.

## Integration

This package is deterministic logic only - no provider calls, no I/O, no persistence. Integrate it behind the aaf_api control plane, or port it 1:1 to Python; the test suite defines the contract either way.

## Honest status

- Implemented and verified: the pure logic and its 34-test suite (local sandbox, 2026-10-19).
- Not claimed: live inference, deployment, cloud account connection, or that any Windows helper script has been executed. The companion scripts under scripts/ are drafts pending their first run on the target Windows machine.
- The 240 s CPU planning estimate in the router is deliberately conservative and must be replaced with the measured median once 10 or more real smoke-test durations exist.
