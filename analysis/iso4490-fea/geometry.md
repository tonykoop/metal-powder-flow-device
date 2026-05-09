# ISO 4490 / ASTM B964 Funnel-Cone Geometry

## Scope

Public-geometry model of the **Hall flowmeter funnel** specified in
ISO 4490:2018 and the equivalent **Carney funnel** specified in
ASTM B964. Built from the published standard dimensions only — no
proprietary CAD, no Uniformity-internal geometry, no employer IP. See
[`../../NOTICE.md`](../../NOTICE.md) and the scope note in the
[issue body](https://github.com/tonykoop/metal-powder-flow-device/issues/1).

## Cone parameters

The Hall and Carney funnels share the same cone half-angle and the same
overall cup geometry; they differ only in orifice diameter.

| Parameter | Symbol | Hall (ISO 4490) | Carney (ASTM B964) |
|---|---|---|---|
| Cone half-angle | α | 30.0° (60° included angle) | 30.0° |
| Orifice diameter | d_orifice | 2.50 mm | 5.00 mm |
| Orifice radius | r_orifice | 1.25 mm | 2.50 mm |
| Cup top inner diameter | d_top | 38.0 mm (nominal) | 38.0 mm |
| Cup top inner radius | r_top | 19.0 mm | 19.0 mm |
| Cone slant length | L_slant | (r_top − r_orifice) / sin α = 35.50 mm | 33.00 mm |
| Cone vertical height | h_cone | (r_top − r_orifice) / tan α = 30.74 mm | 28.58 mm |
| Wall thickness (representative) | t_wall | 1.5 mm | 1.5 mm |
| Sample mass (per standard) | m_sample | 50 g | 150 g |

The cup that sits on top of the cone is a flat-bottom cylinder; this
analysis treats the cone alone and applies a static-pressure boundary
at its top corresponding to the powder column above.

The standard tolerance on the orifice is ±0.025 mm on the 2.5 mm Hall
diameter (per ISO 4490:2018), which is the geometric tolerance the
analysis benchmarks dimensional drift against.

## Parametric model

Both funnels are modeled as a single class `Funnel` parameterized by
orifice diameter (the only delta between Hall and Carney). The cone
profile is straight-line:

```
r(s) = r_orifice + s · sin(α),   s ∈ [0, L_slant]
```

where `s` is arc-length along the slant from the orifice (s = 0) to
the cup rim (s = L_slant). The wall is modeled as a thin shell of
constant thickness `t_wall`. Through-thickness temperature gradients
are neglected (Biot number << 1 for both AlSi10Mg and 316 SS — see
[`references.md`](references.md)).

## Why a cone is a 1D problem here

A circular-cone funnel under axisymmetric loading and axisymmetric
thermal boundary conditions reduces to a 1D problem along the slant
coordinate `s`:

- **Thermal:** solve a fin equation along `s` with surface convection
  on the powder side (inside) and the ambient side (outside).
- **Structural:** treat the cone as a shell of revolution and use the
  membrane approximation — hoop stress and radial deflection per ring
  follow from local pressure and hoop stiffness.

This makes a pure-numpy 1D linear-FE solver an honest tool for the
problem; we are not avoiding 3D for convenience, the geometry is 1D.
The trade-off is that bending modes near the orifice and ring-stiffened
rim regions are smeared; this analysis flags the membrane approximation
explicitly in the structural-FEA writeup.

## Cross-references

- ISO 4490:2018 — *Metallic powders — Determination of flow rate by
  means of a calibrated funnel (Hall flowmeter)*. ISO catalog:
  https://www.iso.org/standard/65824.html. Public-standard dimensions
  for the Hall geometry.
- ASTM B964 — *Standard Test Methods for Flow Rate of Metal Powders
  Using the Carney Funnel*. Public-standard dimensions for the Carney
  geometry.
- Repo top-level `README.md` "Conformance to standard — ISO 4490"
  section — narrative provenance for the standards used here.
