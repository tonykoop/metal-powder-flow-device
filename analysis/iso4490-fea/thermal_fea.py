"""Steady-state thermal FEA on the ISO 4490 / ASTM B964 cone wall.

Models the cone wall as a 1D thin-shell fin along the slant coordinate
`s` ∈ [0, L_slant]. Through-thickness gradients are neglected (Biot
number << 1 — see references.md). Surface heat-transfer coefficients
are applied on the inside (powder contact) and outside (ambient air)
faces.

Governing equation (linear-elliptic 1D fin with two distinct convective
faces):

    d   ⎡          dT ⎤
   ─── ⎢ k · t · ─── ⎥ − h_in (T − T_pow) − h_out (T − T_amb) = 0
    ds  ⎣          ds ⎦

Discretization: linear (P1) Galerkin finite elements on a uniform mesh.
Boundary conditions: insulated at both s=0 (orifice) and s=L (cup rim)
— the conservative case where there is no axial heat sink at either
end. Both ends being insulated means axial conduction only redistributes
heat; the mean wall temperature is set entirely by the surface
convection balance, which matches the lumped check used as a verifier.

Sign convention: heat *into* the wall is positive. The element
contributions are:

    K_axial[i,j] = ∫ k·t·φ_i'·φ_j' ds          (axial conduction)
    K_conv [i,j] = ∫ (h_in + h_out)·φ_i·φ_j ds (convection coupling)
    F_load [i]   = ∫ (h_in·T_pow + h_out·T_amb)·φ_i ds

K_total = K_axial + K_conv,   K_total · T = F_load.

This is a deterministic linear solve, not an eigenvalue problem.

Pure numpy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from profile import (
    FunnelGeometry,
    Material,
    H_INSIDE_W_PER_M2K,
    H_OUTSIDE_W_PER_M2K,
)


@dataclass(frozen=True)
class ThermalResult:
    geometry_label: str
    material_label: str
    s_nodes_m: np.ndarray              # (n_elem+1,)
    temperature_k: np.ndarray          # (n_elem+1,)
    t_pow_k: float
    t_amb_k: float
    h_in_w_per_m2k: float
    h_out_w_per_m2k: float

    @property
    def temperature_c(self) -> np.ndarray:
        return self.temperature_k - 273.15

    @property
    def mean_wall_temperature_k(self) -> float:
        return float(np.trapezoid(self.temperature_k, self.s_nodes_m)
                     / (self.s_nodes_m[-1] - self.s_nodes_m[0]))

    @property
    def lumped_balance_temperature_k(self) -> float:
        """h-balance steady-state wall temperature (no axial conduction)."""
        h_in = self.h_in_w_per_m2k
        h_out = self.h_out_w_per_m2k
        return (h_in * self.t_pow_k + h_out * self.t_amb_k) / (h_in + h_out)


def _assemble_thermal(
    s: np.ndarray,
    k_t: float,
    h_total: float,
    f_source: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Assemble K (= K_axial + K_conv) and F for the 1D fin equation.

    Parameters carried as constants because k, t, h_in, h_out, T_pow,
    T_amb are uniform along the cone in the model. (The element
    routines below are written so a varying-property version is a
    one-line change.)
    """
    n_nodes = len(s)
    n_elem = n_nodes - 1
    K = np.zeros((n_nodes, n_nodes))
    F = np.zeros(n_nodes)

    for e in range(n_elem):
        h_e = s[e + 1] - s[e]
        # Axial conduction element matrix: (k·t / h) [[1,-1],[-1,1]]
        Ke_ax = (k_t / h_e) * np.array([[1.0, -1.0], [-1.0, 1.0]])
        # Convection element matrix: h_total · h_e · [[1/3, 1/6],[1/6, 1/3]]
        Ke_cv = h_total * h_e * np.array([[1.0 / 3.0, 1.0 / 6.0],
                                          [1.0 / 6.0, 1.0 / 3.0]])
        # Source vector: f_source · h_e · [1/2, 1/2]
        Fe = f_source * h_e * np.array([0.5, 0.5])
        idx = [e, e + 1]
        for li, gi in enumerate(idx):
            for lj, gj in enumerate(idx):
                K[gi, gj] += Ke_ax[li, lj] + Ke_cv[li, lj]
            F[gi] += Fe[li]

    return K, F


def solve_steady_state(
    geom: FunnelGeometry,
    material: Material,
    t_pow_c: float = 60.0,
    t_amb_c: float = 20.0,
    h_in: float = H_INSIDE_W_PER_M2K,
    h_out: float = H_OUTSIDE_W_PER_M2K,
    n_elem: int = 200,
) -> ThermalResult:
    """Solve K·T = F for the wall temperature distribution.

    Returns a ThermalResult with T(s) in kelvin. Both ends insulated
    (Neumann), so the matrix is fully populated by the convection term
    and the linear system is well-conditioned.
    """
    s = np.linspace(0.0, geom.slant_length_m, n_elem + 1)
    t_pow_k = t_pow_c + 273.15
    t_amb_k = t_amb_c + 273.15
    k_t = material.k_w_per_mk * geom.wall_thickness_m
    h_total = h_in + h_out
    f_source = h_in * t_pow_k + h_out * t_amb_k

    K, F = _assemble_thermal(s, k_t, h_total, f_source)
    temperature_k = np.linalg.solve(K, F)

    return ThermalResult(
        geometry_label=geom.label,
        material_label=material.label,
        s_nodes_m=s,
        temperature_k=temperature_k,
        t_pow_k=t_pow_k,
        t_amb_k=t_amb_k,
        h_in_w_per_m2k=h_in,
        h_out_w_per_m2k=h_out,
    )


# ---------------------------------------------------------------------------
# Thermal-expansion-induced cone-angle drift
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ThermalExpansionResult:
    geometry_label: str
    material_label: str
    delta_t_avg_k: float                # mean wall ΔT vs reference (K)
    delta_r_orifice_m: float            # radial expansion of orifice
    delta_r_top_m: float                # radial expansion of cup rim
    cone_half_angle_drift_deg: float    # change in cone half-angle (degrees)
    iso_4490_orifice_tolerance_m: float
    drift_ratio_vs_tolerance: float     # |Δd_orifice| / tolerance


ISO_4490_ORIFICE_TOLERANCE_M = 25e-6  # ±0.025 mm on Hall orifice


def thermal_expansion(
    geom: FunnelGeometry,
    material: Material,
    result: ThermalResult,
    t_ref_c: float = 20.0,
) -> ThermalExpansionResult:
    """Compute thermal-expansion radial drift + cone-angle drift.

    Each ring at slant position s expands radially by:
        Δr(s) = α_CTE · (T(s) − T_ref) · r(s)

    The slant length similarly stretches by α_CTE · ΔT_avg · L_slant.
    The new cone half-angle is recomputed from the deformed corner
    radii; small-angle drift is reported in degrees.
    """
    t_ref_k = t_ref_c + 273.15
    delta_t = result.temperature_k - t_ref_k
    delta_t_avg = float(np.trapezoid(delta_t, result.s_nodes_m)
                        / (result.s_nodes_m[-1] - result.s_nodes_m[0]))

    alpha = material.alpha_per_k
    r0 = geom.r_orifice_m
    rt = geom.r_top_m

    delta_r_orifice = alpha * delta_t[0] * r0
    delta_r_top = alpha * delta_t[-1] * rt

    l_slant_new = geom.slant_length_m * (1.0 + alpha * delta_t_avg)
    sin_alpha_new = ((rt + delta_r_top) - (r0 + delta_r_orifice)) / l_slant_new
    sin_alpha_new = max(min(sin_alpha_new, 1.0), -1.0)
    new_alpha_deg = math.degrees(math.asin(sin_alpha_new))
    drift_deg = new_alpha_deg - geom.cone_half_angle_deg

    drift_ratio = abs(2.0 * delta_r_orifice) / ISO_4490_ORIFICE_TOLERANCE_M

    return ThermalExpansionResult(
        geometry_label=geom.label,
        material_label=material.label,
        delta_t_avg_k=delta_t_avg,
        delta_r_orifice_m=delta_r_orifice,
        delta_r_top_m=delta_r_top,
        cone_half_angle_drift_deg=drift_deg,
        iso_4490_orifice_tolerance_m=ISO_4490_ORIFICE_TOLERANCE_M,
        drift_ratio_vs_tolerance=drift_ratio,
    )


# ---------------------------------------------------------------------------
# Self-verification: lumped h-balance vs FE mean wall temperature
# ---------------------------------------------------------------------------


def _verify_lumped_match(rtol: float = 1e-6) -> None:
    """The mean FE wall temperature must equal the lumped h-balance
    temperature to many digits, because both ends are insulated and the
    boundary conditions are uniform along s. Any drift indicates a
    sign error or assembly bug."""
    from profile import HALL, SS316
    result = solve_steady_state(HALL, SS316, n_elem=200)
    t_lumped = result.lumped_balance_temperature_k
    t_mean = result.mean_wall_temperature_k
    rel = abs(t_mean - t_lumped) / t_lumped
    if rel > rtol:
        raise AssertionError(
            f"thermal verifier failed: mean FE T = {t_mean:.6f} K, "
            f"lumped balance = {t_lumped:.6f} K, rel = {rel:.2e}"
        )


if __name__ == "__main__":
    from profile import FUNNELS, MATERIALS

    print("Verifying thermal solver against lumped h-balance ...")
    _verify_lumped_match()
    print("  OK — mean FE wall temperature matches lumped h-balance.\n")

    print(f"{'geom':8} {'mat':9} {'T_wall_mean (°C)':>18} "
          f"{'T_lumped (°C)':>14} {'ΔT_avg (K)':>12} "
          f"{'Δd_orifice (μm)':>16} {'Δα (deg)':>10} {'frac of tol':>12}")
    for g_name, g in FUNNELS.items():
        for m_name, m in MATERIALS.items():
            r = solve_steady_state(g, m, n_elem=200)
            te = thermal_expansion(g, m, r)
            print(f"{g_name:8} {m_name:9} "
                  f"{r.mean_wall_temperature_k - 273.15:18.4f} "
                  f"{r.lumped_balance_temperature_k - 273.15:14.4f} "
                  f"{te.delta_t_avg_k:12.4f} "
                  f"{2 * te.delta_r_orifice_m * 1e6:16.4f} "
                  f"{te.cone_half_angle_drift_deg:10.6f} "
                  f"{te.drift_ratio_vs_tolerance:12.4f}")
