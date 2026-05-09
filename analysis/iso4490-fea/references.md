# References — Standards and Material Properties

## Standards

| Citation | Used for |
|---|---|
| ISO 4490:2018 — *Metallic powders — Determination of flow rate by means of a calibrated funnel (Hall flowmeter)*. ISO catalog: https://www.iso.org/standard/65824.html | Hall funnel cone half-angle (30°), orifice diameter (2.50 mm), orifice tolerance (±0.025 mm), 50 g sample mass. |
| ASTM B964 — *Standard Test Methods for Flow Rate of Metal Powders Using the Carney Funnel*. ASTM catalog: https://www.astm.org/b0964-22.html | Carney funnel orifice diameter (5.00 mm), 150 g sample mass. |
| ASTM B213 — *Standard Test Methods for Flow Rate of Metal Powders Using the Hall Flowmeter Funnel*. ASTM equivalent of ISO 4490. | Cross-reference. |

The cone half-angle, orifice diameter, and overall cup geometry used
in [`geometry.md`](geometry.md) come from these public standards only.

## Material properties

Material properties below are pulled from publicly available datasheets
and handbook values. Each is cited with a publicly accessible source so
a reader can re-verify without an Uniformity Labs login.

### AlSi10Mg (LPBF as-built)

| Property | Symbol | Value | Source |
|---|---|---|---|
| Young's modulus | E | 70 GPa | EOS AlSi10Mg material datasheet (publicly available); MatWeb summary for cast AlSi10Mg |
| Coefficient of thermal expansion | α_CTE | 21 × 10⁻⁶ /K | EOS AlSi10Mg datasheet; ASM Handbook Vol 2 |
| Density | ρ | 2670 kg/m³ | EOS AlSi10Mg datasheet |
| Thermal conductivity | k | 130 W/m·K | EOS AlSi10Mg datasheet (LPBF as-built; cast is higher) |
| Specific heat | c_p | 910 J/kg·K | ASM Handbook (AlSi alloy generic) |
| Yield strength (as-built) | σ_y | 230 MPa | EOS AlSi10Mg datasheet (representative) |

### 316 stainless steel

| Property | Symbol | Value | Source |
|---|---|---|---|
| Young's modulus | E | 193 GPa | ASM Handbook Vol 1; AK Steel 316/316L datasheet |
| Coefficient of thermal expansion | α_CTE | 16 × 10⁻⁶ /K | ASM Handbook Vol 1 (20–100 °C range) |
| Density | ρ | 8000 kg/m³ | ASM Handbook |
| Thermal conductivity | k | 16.2 W/m·K | ASM Handbook (annealed) |
| Specific heat | c_p | 500 J/kg·K | ASM Handbook |
| Yield strength | σ_y | 205 MPa | ASM Handbook (annealed) |

### Powder column (loose / apparent density)

| Property | Symbol | Value | Source |
|---|---|---|---|
| Apparent density (steel powder, loose) | ρ_app | 4500 kg/m³ | Typical for gas-atomized 316L LPBF feedstock per manufacturer datasheets (~50–55% of solid density) |
| Apparent density (Al powder, loose) | ρ_app | 1300 kg/m³ | Typical for gas-atomized AlSi10Mg LPBF feedstock (~50% of solid density) |

These are *loose* (poured) apparent densities used for the gravity-load
calculation, not tap densities. Real values vary by particle size
distribution, morphology, and fill method; the 50% rule of thumb is the
public-handbook starting point.

## Convection coefficients

Order-of-magnitude convection coefficients for the thermal FEA, taken
from standard heat-transfer texts (Incropera & DeWitt, *Fundamentals of
Heat and Mass Transfer*).

| Coefficient | Value | Notes |
|---|---|---|
| h_inside (powder-on-metal contact) | 100–300 W/m²·K | Strong contact heat transfer from a settled powder bed; literature range for packed-bed-on-wall conduction |
| h_outside (air natural convection) | 5–10 W/m²·K | Vertical / inclined plate at low ΔT in still room air |
| h_radiation (room temp) | < 5 W/m²·K | ε ≈ 0.3–0.5 for as-printed metal; small at ΔT = 40 K |

The thermal FEA uses h_inside = 200, h_outside = 8 as point estimates,
with the lumped-balance check showing wall temperature is dominated by
h ratio rather than absolute values.

## Notes on reproduction

A reader who wants to reproduce this analysis can substitute alternate
material values from any of:

- MatWeb (https://www.matweb.com) — public materials database.
- ASM Handbooks (volumes 1, 2, 3) — engineering reference.
- Manufacturer datasheets (EOS, Renishaw, Carpenter, Sandvik) — public
  PDFs.

The numbers above are point estimates appropriate for an exploratory
demo. A production-grade analysis would tighten them with measured
property data on the actual feedstock and printed material.
