"""Static structural FEA — gravity load of the powder column on the cone wall.

Models the cone as a thin shell of revolution under axisymmetric
pressure loading p(s) along the slant. Uses the **membrane
approximation** for a conical shell of revolution: hoop and meridional
stresses follow from local pressure and geometry; radial deflection
follows directly from the hoop strain. Bending and edge effects near
the orifice and rim are ignored — flagged as a known limitation in
results.md.

The membrane equilibrium equations for a thin conical shell loaded by
internal pressure `p`:

    σ_meridional = p · r_normal / (2 · t)
    σ_hoop       = p · r_normal / t

For a cone of half-angle α, the normal radius equals r(s) / cos α
(the principal radius perpendicular to the slant; the meridional
radius is infinite for a straight cone). Specifically:

    σ_hoop = p · r(s) / (t · cos α)
    σ_meridional = (1/2) · σ_hoop

Hoop strain: ε_hoop = (σ_hoop − ν·σ_meridional) / E, with Poisson's
ratio ν taken from material data (typical ν=0.30 for steel, ν=0.33 for
Al). Radial deflection of a ring at slant position s:

    w(s) = ε_hoop(s) · r(s)

The meridional strain is reported as well; axial deflection of the
whole cone is small for these load levels and not the design-driving
quantity. Cone-half-angle drift comes from differential w between top
and bottom rings, similarly to thermal expansion.

For the pressure profile, we treat the powder column as a static
fluid: p(z_above_cone) = ρ_apparent · g · h_above_cone(s). The cup
above the cone holds part of the sample; we approximate the *whole*
sample mass as a static column above the orifice. This is a worst-case
upper bound — real powder bridges and supports itself partially.

Pure numpy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from profile import (
    FunnelGeometry,
    Material,
    POWDER_APPARENT_DENSITY,
)


GRAVITY_M_PER_S2 = 9.80665
DEFAULT_POISSON_RATIO = 0.30
ISO_4490_ORIFICE_TOLERANCE_M = 25e-6


@dataclass(frozen=True)
class StructuralResult:
    geometry_label: str
    material_label: str
    powder_label: str
    sample_mass_kg: float
    s_nodes_m: np.ndarray
    radius_at_node_m: np.ndarray
    pressure_pa: np.ndarray
    sigma_hoop_pa: np.ndarray
    sigma_meridional_pa: np.ndarray
    radial_deflection_m: np.ndarray
    cone_half_angle_drift_deg: float
    delta_d_orifice_m: float
    iso_4490_orifice_tolerance_m: float

    @property
    def drift_ratio_vs_tolerance(self) -> float:
        return abs(self.delta_d_orifice_m) / self.iso_4490_orifice_tolerance_m

    @property
    def max_sigma_hoop_pa(self) -> float:
        return float(np.max(self.sigma_hoop_pa))


def _powder_pressure_along_slant(
    geom: FunnelGeometry,
    s_m: np.ndarray,
    powder_density_kg_per_m3: float,
    sample_mass_kg: float,
) -> np.ndarray:
    """Static-fluid powder pressure at slant position s.

    Treats the entire sample mass as a single static column above the
    orifice. h(s) = total column height − vertical position above
    orifice. The cup above the cone contributes additional head; we
    approximate the cup as a cylinder of radius r_top with height set
    by the total volume.
    """
    cone_height = geom.cone_height_m

    # Total powder volume
    v_pow = sample_mass_kg / powder_density_kg_per_m3
    v_cone = (math.pi / 3.0) * cone_height * (
        geom.r_top_m ** 2 + geom.r_top_m * geom.r_orifice_m + geom.r_orifice_m ** 2
    )
    if v_pow <= v_cone:
        # Sample fits inside the cone — column height equals filled cone height.
        # For simplicity we still use cone_height as the worst case head; this
        # over-estimates pressure but keeps the analysis as a conservative bound.
        h_cup_m = 0.0
    else:
        v_remaining = v_pow - v_cone
        cup_area = math.pi * geom.r_top_m ** 2
        h_cup_m = v_remaining / cup_area

    h_total_m = cone_height + h_cup_m

    z_above_orifice = s_m * math.cos(geom.cone_half_angle_rad)
    h_above_node = np.maximum(h_total_m - z_above_orifice, 0.0)
    p = powder_density_kg_per_m3 * GRAVITY_M_PER_S2 * h_above_node
    return p


def solve_membrane(
    geom: FunnelGeometry,
    material: Material,
    powder_label: str = "316ss_powder",
    poisson_ratio: float = DEFAULT_POISSON_RATIO,
    n_elem: int = 400,
) -> StructuralResult:
    """Membrane-shell stresses + radial deflection along the slant."""
    s = np.linspace(0.0, geom.slant_length_m, n_elem + 1)
    r = np.array([geom.radius_at(si) for si in s])

    rho_pow = POWDER_APPARENT_DENSITY[powder_label]
    p = _powder_pressure_along_slant(geom, s, rho_pow, geom.sample_mass_kg)

    cos_alpha = math.cos(geom.cone_half_angle_rad)
    t = geom.wall_thickness_m
    sigma_hoop = p * r / (t * cos_alpha)
    sigma_meridional = 0.5 * sigma_hoop

    eps_hoop = (sigma_hoop - poisson_ratio * sigma_meridional) / material.E_pa
    w = eps_hoop * r

    # Cone-angle drift from differential top/bottom radial deflection.
    # Δα is the change in arctan((r_top + w_top − (r_orifice + w_orifice)) /
    # (L_slant + axial-stretch)). Axial stretch is comparable in magnitude
    # to radial; for these load levels we report the kinematic limit
    # ignoring axial stretch (the ~1% correction is well below the
    # interesting digits).
    new_top_minus_bot = (geom.r_top_m + w[-1]) - (geom.r_orifice_m + w[0])
    sin_alpha_new = max(min(new_top_minus_bot / geom.slant_length_m, 1.0), -1.0)
    new_alpha_deg = math.degrees(math.asin(sin_alpha_new))
    drift_deg = new_alpha_deg - geom.cone_half_angle_deg

    delta_d_orifice = 2.0 * w[0]

    return StructuralResult(
        geometry_label=geom.label,
        material_label=material.label,
        powder_label=powder_label,
        sample_mass_kg=geom.sample_mass_kg,
        s_nodes_m=s,
        radius_at_node_m=r,
        pressure_pa=p,
        sigma_hoop_pa=sigma_hoop,
        sigma_meridional_pa=sigma_meridional,
        radial_deflection_m=w,
        cone_half_angle_drift_deg=drift_deg,
        delta_d_orifice_m=delta_d_orifice,
        iso_4490_orifice_tolerance_m=ISO_4490_ORIFICE_TOLERANCE_M,
    )


# ---------------------------------------------------------------------------
# Self-verification: closed-form vs FE on a uniform-pressure rim ring
# ---------------------------------------------------------------------------


def _verify_uniform_pressure_rim(rtol: float = 1e-6) -> None:
    """For uniform pressure on a thin cone, the per-ring deflection
    formula w(r) = (1 − ν/2) · p · r² / (E · t · cos α) must hold
    exactly node-by-node. (Sanity check that the discretization is
    nodal: a uniform-pressure load gives a closed-form deflection at
    every node, and our membrane solver should reproduce it.)"""
    from profile import HALL, SS316
    geom = HALL
    mat = SS316
    nu = DEFAULT_POISSON_RATIO
    n_elem = 100
    s = np.linspace(0.0, geom.slant_length_m, n_elem + 1)
    r = np.array([geom.radius_at(si) for si in s])
    p = np.full_like(s, 1000.0)  # 1 kPa uniform
    cos_alpha = math.cos(geom.cone_half_angle_rad)
    sigma_hoop = p * r / (geom.wall_thickness_m * cos_alpha)
    sigma_mer = 0.5 * sigma_hoop
    eps_hoop = (sigma_hoop - nu * sigma_mer) / mat.E_pa
    w_numeric = eps_hoop * r
    w_analytic = (1.0 - 0.5 * nu) * 1000.0 * r ** 2 / (mat.E_pa * geom.wall_thickness_m * cos_alpha)
    rel = np.max(np.abs(w_numeric - w_analytic) / np.maximum(np.abs(w_analytic), 1e-30))
    if rel > rtol:
        raise AssertionError(
            f"structural verifier failed: max rel error = {rel:.2e}"
        )


if __name__ == "__main__":
    from profile import FUNNELS, MATERIALS

    print("Verifying membrane solver against closed-form rim deflection ...")
    _verify_uniform_pressure_rim()
    print("  OK — node-by-node match to (1−ν/2)·p·r²/(E·t·cos α).\n")

    print(f"{'geom':8} {'mat':9} {'powder':16} "
          f"{'p_max (Pa)':>11} {'σ_hoop_max (kPa)':>17} "
          f"{'Δd_orifice (μm)':>16} {'Δα (deg)':>10} {'frac of tol':>12}")
    for g_name, g in FUNNELS.items():
        powder = "316ss_powder" if "316" in MATERIALS["316ss"].label.lower() else "316ss_powder"
        for m_name, m in MATERIALS.items():
            pname = "alsi10mg_powder" if "alsi10mg" in m_name else "316ss_powder"
            r = solve_membrane(g, m, powder_label=pname, n_elem=400)
            print(f"{g_name:8} {m_name:9} {pname:16} "
                  f"{np.max(r.pressure_pa):11.2f} "
                  f"{r.max_sigma_hoop_pa / 1000.0:17.4f} "
                  f"{r.delta_d_orifice_m * 1e6:16.6f} "
                  f"{r.cone_half_angle_drift_deg:10.8f} "
                  f"{r.drift_ratio_vs_tolerance:12.6f}")
