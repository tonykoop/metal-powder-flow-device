# Design Notes — Granular-Flow Bridging Model

Status: L1 concept packet
Sources: published physics only; no proprietary device data

---

## 1. The Beverloo Equation

The Beverloo equation (Beverloo, Leniger & Van de Velde, 1961) is the standard
empirical relation for mass flow rate of granular material through a circular orifice
under gravity:

```
W = C * ρ_b * √g * (D - k*d)^(5/2)
```

### Parameters

| Symbol | Description | Units | Typical value |
|--------|-------------|-------|---------------|
| W | Mass flow rate | kg/s | — |
| C | Empirical discharge coefficient | dimensionless | ~0.58 (spheres) |
| ρ_b | Bulk density of powder | kg/m³ | ~4500 for 316L SS |
| g | Gravitational acceleration | m/s² | 9.81 |
| D | Orifice diameter | m | 0.0025–0.010 (ISO 4490) |
| d | Mean particle diameter | m | 15–45 × 10⁻⁶ (LPBF) |
| k | Dead-zone correction constant | dimensionless | ~1.5 |

### Physical meaning

The term `(D - k*d)` is the effective orifice diameter after subtracting the
"dead zone" — the annular region near the orifice edge where particles cannot
flow because of geometric packing constraints. The constant k ≈ 1.5 accounts for
this effect. The 5/2 exponent arises from the dimensional analysis of a free-fall
model through the orifice.

C ≈ 0.58 is well-established for near-spherical particles (Brown & Richards 1970,
Nedderman 1992). For irregular or highly cohesive particles, C can be lower.

### Applicability

The Beverloo equation applies when:
- Flow is gravity-driven (no external vibration or pressure)
- The orifice is circular
- D >> d (orifice much larger than particle)
- Particle shape is approximately spherical

For LPBF powders (near-spherical, 15–45 μm), the equation is applicable in the
non-arching regime.

---

## 2. ISO 4490 Orifice Geometry

ISO 4490:2018 specifies the Hall flowmeter geometry for measuring powder flow rate:

- **Funnel cone angle:** 60° (included angle)
- **Standard orifice diameters:** 2.5 mm (fine powders), 5 mm, 10 mm (coarse powders)
- **Test procedure:** measure time for 50 g of powder to flow through; report in s/50g

The 2.5 mm orifice is standard for fine metal powders used in LPBF and other
powder metallurgy applications.

No device-specific or proprietary geometry is used in this model. Only the
publicly specified ISO 4490 values above are referenced.

---

## 3. Arch-Blocking Threshold

Arching (bridging) occurs when particles form a stable mechanical arch across
the orifice, stopping flow. The critical condition is governed by the ratio D/d:

```
Arching occurs approximately when D/d < 5–7  (spherical particles)
```

This threshold is well-documented in granular physics literature (Nedderman 1992,
Zuriguel et al. 2005). A simple approximate criterion for the critical diameter:

```
D_crit ≈ k*d + 5*d  ==>  D/d_crit ≈ 6  (using k=1.5, critical ratio = 6.5)
```

For angular or irregular particles, the critical ratio is typically higher
(flow stops at larger D/d) because irregular shapes interlock more effectively.

### Application to LPBF powders

For d = 30 μm (typical mean for 15–45 μm LPBF powder):

```
D_crit ≈ 6.5 × 30 μm = 195 μm ≈ 0.2 mm
```

The ISO 4490 2.5 mm orifice gives D/d ≈ 83. This is far above the arching
threshold for ideal spheres, meaning free-flowing powder should not arch under
standard conditions.

However, the effective D/d can be reduced by:
- Particle agglomeration (satellites, moisture)
- Electrostatic bridging
- Powder bed compaction above the orifice

---

## 4. Intermittency Regime

Near the arching threshold, flow transitions from steady to intermittent. In
this regime, arches form, become unstable, and collapse, producing bursts of
flow separated by momentary blockages.

Published characterization (Zuriguel et al., Phys. Rev. Letters, 2005; Janda et al. 2008):

```
Intermittent regime:  approximately 5 < D/d < 10–15
Steady flow:          D/d > 10–15
Persistent arch:      D/d < 5
```

The boundaries are not sharp and shift with:
- Particle shape irregularity (shifts threshold higher)
- Cohesion (electrostatic, capillary) — expands intermittent zone toward larger D/d
- Vibration — can break arches and restore steady flow

### Why this matters for powder characterization

The FEA work (analysis/iso4490-fea/) confirmed the cone structure is mechanically
robust. The granular-flow question is distinct: even with a perfectly rigid cone,
the powder stream itself can be intermittent if the powder is cohesive.

For ISO 4490 measurements, intermittency appears as high variance in measured
flow time (s/50g). Contaminated or aged powders can shift from steady flow to
intermittent flow without changing the orifice geometry at all.

---

## 5. Key Variables for LPBF Powder

### Typical LPBF powder parameters (316L stainless steel, published ranges)

| Parameter | Typical range | Notes |
|-----------|---------------|-------|
| d (mean) | 15–45 μm | Laser diffraction; D50 often ~30 μm |
| d₁₀ | ~15 μm | Fine fraction, most susceptible to cohesion |
| d₉₀ | ~45 μm | Coarse fraction |
| ρ_b (bulk density) | 4000–5000 kg/m³ | Depends on tap/fill state; ~4500 loose |
| ρ_true (316L) | ~8000 kg/m³ | Literature |
| Particle shape | Near-spherical | Gas atomized; satellites possible |
| Flowability (Hall) | 15–25 s/50g | Powder-grade dependent |

### ISO 4490 standard conditions applied to this powder

| Orifice | D (mm) | D/d (d=30 μm) | Regime |
|---------|--------|----------------|--------|
| Fine | 2.5 | 83 | Well above arching threshold |
| Medium | 5.0 | 167 | Well above arching threshold |
| Coarse | 10.0 | 333 | Well above arching threshold |

At standard conditions with fresh, uncontaminated powder, arching is not expected.
Intermittency risk increases when powder is:
- Recycled (satellites, oxidation, moisture uptake)
- Stored improperly (humidity, compaction)
- Fine-fraction enriched (d₁₀ component accumulates over reuse cycles)

### Estimated Beverloo flow rate (2.5 mm orifice, d=30 μm, ρ_b=4500 kg/m³)

```
D_eff = D - k*d = 0.0025 - 1.5 × 30×10⁻⁶ = 0.0025 - 0.000045 = 0.002455 m
W = 0.58 × 4500 × √9.81 × (0.002455)^(5/2)
  = 0.58 × 4500 × 3.132 × 2.979×10⁻⁴
  ≈ 0.58 × 4500 × 3.132 × 2.979×10⁻⁴
  ≈ 2.44 × 10⁻³ kg/s  ≈  2.44 g/s
```

At 2.44 g/s, a 50 g Hall test would take approximately **20 s** — consistent with
the published Hall flow range of 15–25 s/50g for good-quality LPBF 316L powder.

This rough agreement supports the applicability of the Beverloo model in this regime.
The Wolfram file `metal-powder-flow-device-analysis-granular-flow-bridging-starter.wl` computes this across the full range of ISO
4490 orifice diameters with plots.

---

## References

- Beverloo, W.A., Leniger, H.A., Van de Velde, J. (1961). Chemical Engineering
  Science, 15(3–4), 260–269.
- Brown, R.L., Richards, J.C. (1970). *Principles of Powder Mechanics*. Pergamon.
- Nedderman, R.M. (1992). *Statics and Kinematics of Granular Materials*. Cambridge.
- Zuriguel, I., Garcimartín, A., Maza, D., Pugnaloni, L.A., Pastor, J.M. (2005).
  Physical Review E, 71, 051303.
- Janda, A., Zuriguel, I., Garcimartín, A., Pugnaloni, L.A., Maza, D. (2008).
  Europhysics Letters, 84(4), 44002.
- ISO 4490:2018. *Metallic powders — Determination of flow rate by means of a
  calibrated funnel (Hall flowmeter)*. ISO.
