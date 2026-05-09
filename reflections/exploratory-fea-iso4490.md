# Exploratory FEA on a Public-Geometry Hall Flowmeter Cone

> Portfolio reflection accompanying the
> [`analysis/iso4490-fea/`](../analysis/iso4490-fea/) folder.
> **Public geometry. Public material properties. No Uniformity Labs IP.**
> Closes [`tonykoop/metal-powder-flow-device#1`](https://github.com/tonykoop/metal-powder-flow-device/issues/1).

## Scope

This is an *exploratory FEA portfolio piece* — not a continuation of
the original Uniformity instrument's design history, and not a study
of any Uniformity geometry. I no longer have access to the Uniformity
resources that designed and built the original device. The substrate
for the analysis is the **public ISO 4490:2018 / ASTM B964 funnel
geometry** (60° cone, 2.5 mm orifice for Hall, 5.0 mm for Carney) and
the **published material properties** for AlSi10Mg and 316 SS from
public datasheet and handbook sources.

The frame is "this is what FEA brings to a measurement-instrument
design problem" rather than documentation of any specific instrument.
A hiring manager or any Uniformity reader can verify the inputs
against the public standards and re-run the solvers themselves.

The IP boundary is restated explicitly in
[`../NOTICE.md`](../NOTICE.md) and in the
[`analysis/iso4490-fea/`](../analysis/iso4490-fea/) folder's `README.md`
and `geometry.md`.

## What this PR is *not*

The interesting question about a Hall flowmeter is not "can the cone
withstand the powder weight." That answer is trivially yes — a
40-cubic-millimeter steel cone holding 50 g of metal powder is
laughably over-designed; you can show that with hoop-stress on the
back of an envelope and the structural FEM in this PR confirms it
(orifice deflection well under 1 µm, yield safety factor north of
10⁴). If the question were that, the part would not be standardized.

The Hall flowmeter exists as a standardized test because **we don't
have a closed-form predictor for whether a given metal powder will
flow through a given orifice** — and that's a granular-flow problem,
not a continuum-statics problem. Three things make it hard:

1. **Bridging and arching.** Particles can self-support over the
   orifice via a friction-locked stress arch — flow stops, pressure
   redistributes around the arch, and the powder column above it sits
   stably for some time. Fine cuts of LPBF feedstock bridge constantly;
   it's why ASTM B964 (Carney, 5 mm orifice) exists as the parallel
   standard for powders that won't go through the 2.5 mm Hall.
2. **Intermittent collapse.** Bridges have finite lifetimes. They
   build, support a column, then fail catastrophically — a chunk of
   the bed lets go, drops through the orifice, the next bridge forms,
   the cycle repeats. The free surface of the bed during this looks
   exactly like riverbank erosion or a slow landslide: angle of repose
   exceeded locally, grains slide, the bank reshapes, then it
   stabilizes until the next collapse. That's the visual signature of
   the Hall test under a fines-laden powder.
3. **Stress redistribution that the lumped model misses.** The static
   pressure column model used in the structural FEA below assumes
   `p(z) = ρ·g·h`. Real granular beds redistribute load to the walls
   via friction (Janssen 1895); deep beds reach a saturated wall
   pressure independent of fill height. That alone is a well-known
   continuum-granular correction. But Janssen still assumes flow —
   it cannot say *whether* flow happens.

**The static FEA in this PR cannot answer the bridging/collapse
question.** Neither can ISO 4490, beyond reporting an aggregate flow
time as a quality-control metric. Engaging with the actual flow
physics needs a different class of tool — see "What's actually needed
next" below and the follow-on issue tracking it.

## What this PR *does* do

The static-FEA work in `analysis/iso4490-fea/` establishes the
parametric geometry, material data, and pure-numpy 1D linear-FE
infrastructure that a granular-flow follow-on will sit on top of.
Treat it as the warmup, not the headline:

- **Pure-numpy 1D linear-FE solvers** along the cone slant, both
  with built-in self-verification:
  - **Thermal** — variable-property fin equation along the slant,
    surface convection on inside (powder-side) and outside
    (ambient-side) faces, insulated boundaries at orifice and cup
    rim. Verifier: FE mean wall temperature equals lumped h-balance
    closed form to machine precision.
  - **Structural** — membrane-shell approximation for a thin
    conical shell under axisymmetric pressure load from the powder
    column. Verifier: `w(r) = (1 − ν/2)·p·r²/(E·t·cos α)` matched
    node-by-node on a uniform-pressure load.
- **A standards-cited geometry + material framework**
  (`geometry.md`, `references.md`, `profile.py`) that any granular-
  flow follow-on can pull from without re-deriving the cone profile.
- **A confirmation that the cone itself is not the limiting
  factor.** Both perturbations (thermal expansion, gravity load) sit
  comfortably inside the ISO 4490 ±25 µm orifice tolerance.

| Mechanism | Δd_orifice | Fraction of ISO 4490 ±25 µm tolerance |
|---|---|---|
| Thermal expansion (60 °C powder, 20 °C ambient) | 1.5–4.0 µm | 6–16% |
| Gravity load (50 g Hall / 150 g Carney column) | < 0.2 µm | < 0.001% |

Read this table the right way: thermal drift consumes a meaningful
fraction of the orifice tolerance and would be worth modeling on a
funnel that lives in a shop with thermal cycles. Gravity-load drift is
several orders of magnitude smaller, which is exactly the "the cone
isn't the interesting failure mode" finding.

## What's actually needed next

The granular-flow problem needs one of:

- **DEM (Discrete Element Method).** Track every particle; pairwise
  Hertzian contact + Coulomb friction; integrate Newton's equations.
  Open-source workhorses are LIGGGHTS, Yade, MercuryDPM. A pared-down
  2D-disk version is doable in pure-numpy / numpy+numba for a few
  thousand particles and is enough to *visualize* bridge formation
  and collapse — which is the value here, since the qualitative
  intermittent-flow behavior is the point.
- **MPM (Material Point Method).** Continuum-on-particles. Handles
  the large-deformation bridge→collapse transition gracefully.
  Higher implementation cost than DEM at this scale; the right tool
  if the goal is quantitative flow-rate prediction.
- **Mohr-Coulomb continuum FEM.** A friction-angle yield surface in
  a continuum FEM captures the *static* arch (the stress field that
  *would* support the bridge) but not the dynamic intermittency.
  Useful intermediate step between Janssen and DEM.
- **Janssen-Walker silo equations.** 1D analytic. Gets the
  saturated-pressure-with-depth phenomenon right but assumes flow.
  Cheap to add to this same numpy infrastructure as a "next layer up
  from static-column pressure" closed-form.

The follow-on issue
[`tonykoop/metal-powder-flow-device#3`](https://github.com/tonykoop/metal-powder-flow-device/issues/3)
(filed alongside this PR) tracks a 2D-disk DEM demo on the same
ISO 4490 cone, with frames captured to visualize the bridge → arrest
→ collapse cycle. The riverbank-erosion analogy on the free surface
is the visual deliverable; aggregate flow time and the histogram of
inter-collapse intervals are the quantitative deliverables. That
issue is where the "what's actually interesting about FEA on this
funnel" question lives.

## Figures (in this PR)

Generated by `analysis/iso4490-fea/run_analysis.py`:

- [`analysis/iso4490-fea/figures/thermal-wall-temperature.png`](../analysis/iso4490-fea/figures/thermal-wall-temperature.png)
  — Steady-state T(s) along the slant for all four geometry × material
  cases.
- [`analysis/iso4490-fea/figures/thermal-orifice-drift.png`](../analysis/iso4490-fea/figures/thermal-orifice-drift.png)
  — Bar chart of Δd_orifice per case against the ±25 µm tolerance line.
- [`analysis/iso4490-fea/figures/structural-pressure.png`](../analysis/iso4490-fea/figures/structural-pressure.png)
  — Powder-column pressure p(s) per case (static-fluid upper bound; a
  Janssen-corrected version is the natural next plot in the follow-on
  issue).
- [`analysis/iso4490-fea/figures/structural-orifice-drift.png`](../analysis/iso4490-fea/figures/structural-orifice-drift.png)
  — Log-scale bar chart vs the same tolerance line.

## What FEA actually buys here

For the static questions answered in this PR: not much that the
back-of-the-envelope calculation didn't already say. Both problems
have the same parametric closed form; the FE solver just lays the
groundwork.

For the *real* question — granular flow — the value of the
computational approach is exactly that the closed form *doesn't
exist*. Bridge formation, arch collapse, intermittent flow, and the
sensitivity of all of those to particle size distribution, friction
coefficient, and fill rate are emergent properties that you have to
*simulate* to see. That is the FEA-adjacent skill worth demonstrating
here — and the static analysis below is the geometry and material
scaffolding to make that simulation reproducible.

## Limitations of the static work

- **Membrane shell, no bending.** Bending modes near the orifice and
  ring stiffeners near the cup rim are smeared by the membrane
  assumption. For a 1.5 mm wall and 4–17 kPa hoop stress those
  bending corrections are well below the accuracy interesting at
  ISO-tolerance levels.
- **Static powder column.** Treated as a static fluid: this is an
  upper bound on wall pressure, not a measured value. Janssen-Walker
  would reduce it; DEM would replace it. The static column was the
  honest first pass, called out as such throughout the writeup.
- **Constant convection coefficients.** h_inside and h_outside are
  point estimates from textbook tables. Real h varies along the
  slant; for the verifier-matching case (insulated ends, uniform h)
  the wall is isothermal so the variation does not bite.
- **Through-thickness isothermal.** Biot number << 1 for both
  materials at the chosen wall thickness; well-justified for a 1.5 mm
  steel or aluminum wall at these h coefficients.
- **No ambient radiation, no powder radiation.** Both are < 5 W/m²·K
  at the modeled temperatures; including them would shift the wall
  temperature by < 1 K.
- **Empirical validation deferred.** No instrumented physical funnel
  was tested. Thermocouple-array on a 3D-printed cone with controlled
  powder temperature is one L4 follow-on; the granular-flow DEM in
  the follow-on issue is the higher-priority one.

## Reproduce

```bash
cd analysis/iso4490-fea
python3 profile.py          # geometry + material summary
python3 thermal_fea.py      # verifier + thermal matrix summary
python3 structural_fea.py   # verifier + structural matrix summary
python3 run_analysis.py     # writes results.{csv,md} + figures/
```

Pure Python with numpy + matplotlib only. The full static analysis
(both physics, four cases each, all figures and CSVs) runs in under
three seconds on a laptop.

## Cross-references

- Issue (this PR closes): [`tonykoop/metal-powder-flow-device#1`](https://github.com/tonykoop/metal-powder-flow-device/issues/1)
- Follow-on issue (granular flow / DEM): [`tonykoop/metal-powder-flow-device#3`](https://github.com/tonykoop/metal-powder-flow-device/issues/3) — the "what's actually interesting about FEA on a flowmeter" work (bridging, arching, intermittent collapse, riverbank-erosion analogy on the free surface).
- IP boundary: [`../NOTICE.md`](../NOTICE.md)
- Public-standard geometry: [`../analysis/iso4490-fea/geometry.md`](../analysis/iso4490-fea/geometry.md)
- Material data citations: [`../analysis/iso4490-fea/references.md`](../analysis/iso4490-fea/references.md)
- Repo `README.md` "Conformance to standard — ISO 4490" — narrative.
