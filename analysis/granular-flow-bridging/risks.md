# Risks — Granular-Flow Bridging Model

Status: L1 concept packet

---

## Proprietary Boundary

All device CAD, measurement methodology, and laboratory data are the proprietary
property of Uniformity Labs. `NOTICE.md` in the repository root governs.

**This model contains ZERO proprietary content.**

The analysis uses only:
- Published equations (Beverloo 1961)
- ISO 4490 publicly specified geometry values
- Published empirical constants from open literature
- Typical LPBF powder parameters from published ranges

No device drawings, no measured flow data, no internal process parameters.

---

## Source-Only Wolfram

The file `wolfram-starter.wl` has not been executed. No plot outputs, no
computed result tables, and no numeric claims from this file have been verified
by execution.

Execution in Wolfram Desktop, Wolfram Cloud, or `wolframscript` is required
before any quantitative prediction from this model is treated as L3 evidence.
Gate W001 in `validation.csv` is open until this step is completed.

---

## Public-Physics Approximations

The Beverloo constants C ≈ 0.58 and k ≈ 1.5 are empirical fits to experimental
data for near-spherical particles. Their values:
- Vary by material (shape, surface roughness, cohesion)
- Were determined in experiments with orifice geometry that may differ from
  the ISO 4490 Hall flowmeter funnel
- Are not guaranteed to apply to LPBF powders without experimental validation

This model is a **conceptual framework**, not a calibrated predictor for
specific powder grades or production conditions.

---

## Cohesion Effects Not Modeled

The Beverloo equation does not capture:
- **Electrostatic cohesion**: LPBF powders are electrostatically active, especially
  after sieving or blending operations
- **Moisture / capillary bridging**: humid storage or handling shifts the effective
  cohesion significantly
- **Satellite-induced interlocking**: satellites (small particles fused to larger ones
  during atomization or reuse) change both shape and flow resistance
- **Compaction above the orifice**: powder column weight creates additional arch
  stability; Beverloo assumes a loosely packed feed

These effects can shift the arch-blocking threshold upward and expand the
intermittent regime to larger D/d ratios than the idealized model predicts.

---

## D/d Ratio Sensitivity

The model shows that, at nominal conditions (d=30 μm, D=2.5 mm), D/d ≈ 83 —
well above the arching threshold. However:
- If effective d increases due to agglomeration, D/d drops toward the critical zone
- At D/d ≈ 10–15, intermittency onset can occur without full arching
- The Beverloo equation itself becomes unreliable as D/d approaches 5–7

Any quantitative claim about intermittency onset requires experimental data
that is not contained in this L1 packet.

---

## ISO 4490 Standard Version

This model references ISO 4490:2018. If the applicable version in use differs,
orifice diameter specifications or test-procedure details may vary. Gate W003
requires verification against the current applicable standard.
