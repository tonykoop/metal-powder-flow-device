# Exploratory FEA — ISO 4490 / ASTM B964 Funnel Cone

L3-frontier portfolio analysis demonstrating thermal and structural
finite-element methodology on a **public-geometry** Hall (ISO 4490) /
Carney (ASTM B964) flowmeter funnel. **No proprietary geometry. No
Uniformity Labs IP.** See [`../../NOTICE.md`](../../NOTICE.md) and the
issue scope note: this folder uses only the published standard
dimensions and publicly-cited material properties.

## Readiness

| Gate | Status |
|---|---|
| Physics gate | ✅ Governing equations derived (thin-shell fin equation; membrane shell of revolution); assumptions and limitations called out in `geometry.md` and `references.md`. |
| Artifact gate | ✅ Two design-table-style CSVs (thermal + structural matrices), four figures, capstone-style writeup at `reflections/exploratory-fea-iso4490.md`. |
| Solver-verification gate | ✅ Thermal solver matches lumped h-balance to machine precision; structural solver matches closed-form ring-deflection node-by-node. Both verifiers raise on failure and run in `__main__` of their respective modules. |
| Manufacturing / safety gates | 🚫 N/A — analysis-only PR. |
| Empirical gate | ⏸ **Explicitly deferred.** No physical funnel was instrumented. |

## Files

| File | Role |
|---|---|
| [`geometry.md`](geometry.md) | Public ISO 4490 / ASTM B964 cone parameters; cup, cone, orifice, wall thickness. |
| [`references.md`](references.md) | Standards citations + AlSi10Mg / 316SS material data with public-source attribution. |
| [`profile.py`](profile.py) | Parametric `FunnelGeometry` + `Material` records. SI units. Single source of truth. |
| [`thermal_fea.py`](thermal_fea.py) | 1D linear-FE fin-equation solver along the cone slant; surface convection on both faces; insulated ends. Self-verifies against lumped h-balance. |
| [`structural_fea.py`](structural_fea.py) | Membrane-shell solver for the cone under powder-column pressure; hoop + meridional stress + radial deflection; cone-angle drift. Self-verifies against closed-form ring deflection. |
| [`run_analysis.py`](run_analysis.py) | End-to-end driver: matrix sweep across (Hall × Carney) × (AlSi10Mg × 316SS), figures, CSVs, results.md. |
| [`results-thermal.csv`](results-thermal.csv) | Machine-readable thermal matrix (4 rows). |
| [`results-structural.csv`](results-structural.csv) | Machine-readable structural matrix (4 rows). |
| [`results.md`](results.md) | Human-readable writeup combining both physics. |
| [`figures/`](figures/) | `thermal-wall-temperature.png`, `thermal-orifice-drift.png`, `structural-pressure.png`, `structural-orifice-drift.png`. |

## Reproduce

```bash
cd analysis/iso4490-fea
python3 profile.py          # geometry + material summary
python3 thermal_fea.py      # verifier + thermal matrix summary
python3 structural_fea.py   # verifier + structural matrix summary
python3 run_analysis.py     # writes results.{csv,md} + figures/
```

Pure numpy + matplotlib. No SciPy, FEniCS, gmsh, CalculiX, COMSOL, or
SimScale required. The 1D meshes (200 elements thermal, 400 structural)
solve in under a second on a laptop.

## Headline result

The funnel geometry stays well inside the ISO 4490 ±25 µm orifice
tolerance under modeled powder-handling conditions:

| Mechanism | Δd_orifice | Fraction of ISO tolerance |
|---|---|---|
| Thermal expansion (60 °C powder, 20 °C ambient) | 1.5–4.0 µm | 6–16% |
| Gravity load (50 g Hall / 150 g Carney column) | < 0.2 µm | < 0.001% |

Thermal expansion dominates; gravity load is essentially negligible.
The full discussion lives in [`results.md`](results.md) and the
portfolio writeup at
[`../../reflections/exploratory-fea-iso4490.md`](../../reflections/exploratory-fea-iso4490.md).

## Cross-references

- Issue: [`tonykoop/metal-powder-flow-device#1`](https://github.com/tonykoop/metal-powder-flow-device/issues/1)
- IP boundary: [`../../NOTICE.md`](../../NOTICE.md)
- Repo top-level `README.md` "Conformance to standard — ISO 4490" — the
  conformance narrative this analysis exercises.
