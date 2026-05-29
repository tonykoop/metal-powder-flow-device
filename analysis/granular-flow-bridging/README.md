Status: L1 concept packet

# Granular-Flow Bridging Model — ISO 4490 Orifice

Analytical model for powder-flow intermittency and arch-blocking through a Hall
flowmeter orifice, using published Beverloo equation and ISO 4490 geometry only.

## Problem Statement

Powder flow through an orifice is not always steady. Near certain orifice-to-particle
diameter ratios, granular materials exhibit intermittent flow: bursts of discharge
separated by arch (bridge) formation and collapse events. For Laser Powder Bed
Fusion (LPBF) metal powders, this regime matters because:

- Powder is fine (15–45 μm), cohesive, and sensitive to moisture and satellite content
- The ISO 4490 Hall flowmeter orifice provides a standardized geometry for measuring
  flow rate, but the standard does not characterize intermittency directly
- The preceding FEA work (PR #2) confirmed the cone geometry is mechanically
  over-designed; the open question is whether the powder flows at all, and if so,
  whether it flows steadily or in stop-start bursts

This packet addresses that question analytically using published granular-flow physics.

## Scope

This model contains **only published physics**. Specifically:

- Beverloo equation (Beverloo, Leniger & Van de Velde, 1961)
- ISO 4490 standard orifice geometry (publicly specified)
- Published granular-flow literature (Brown & Richards 1970, Nedderman 1992)
- Typical LPBF powder parameters from open literature

**No proprietary data is included.** Device CAD, measurement methodology, and
laboratory data from Uniformity Labs are proprietary property. See `NOTICE.md`
in the repository root. This analysis does not reference, infer, or depend on
any such proprietary information.

## Wolfram Source Status

The file `wolfram-starter.wl` in this directory contains Wolfram Language source
code that implements the Beverloo model and produces flow-rate plots. This source
has **not been executed** in this context.

Status: **source-only (L2 evidence)**

Execution in Wolfram Desktop, Wolfram Cloud, or `wolframscript` is required
before any quantitative claims from this model can be treated as validated output.
See `validation.csv` gate W001.

## Governing Standard

ISO 4490: *Metallic powders — Determination of flow rate by means of a calibrated
funnel (Hall flowmeter)*

The ISO 4490 standard defines the funnel geometry (60° cone angle), orifice
diameters (2.5 mm for fine powders through 10 mm for coarse), and the
test procedure for measuring mass flow rate. This packet uses only the
publicly specified geometry values from that standard.

## File Inventory

| File | Description |
|------|-------------|
| `README.md` | This file — scope, status, problem statement |
| `design.md` | Analytical model: Beverloo equation, arch-blocking threshold, intermittency regime |
| `wolfram-starter.wl` | Wolfram Language source for Beverloo plots (source-only, not executed) |
| `validation.csv` | Open validation gates before this packet can advance to L2 |
| `risks.md` | Proprietary boundary, model limitations, open risks |

## References

- Beverloo, W.A., Leniger, H.A., Van de Velde, J. (1961). "The flow of granular
  solids through orifices." *Chemical Engineering Science*, 15(3–4), 260–269.
- Brown, R.L., Richards, J.C. (1970). *Principles of Powder Mechanics*. Pergamon Press.
- Nedderman, R.M. (1992). *Statics and Kinematics of Granular Materials*. Cambridge
  University Press.
- ISO 4490:2018. *Metallic powders — Determination of flow rate by means of a
  calibrated funnel (Hall flowmeter)*. International Organization for Standardization.
