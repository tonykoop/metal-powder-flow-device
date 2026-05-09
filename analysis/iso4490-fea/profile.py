"""Parametric ISO 4490 / ASTM B964 funnel-cone geometry + materials.

Single source of truth for the geometry (Hall + Carney variants) and
the material property records used by the thermal and structural FEA.
All units SI internally (meters, kelvin, watts, pascals); see
geometry.md for the standards-derived values in the "natural" units
the standards use.

Pure numpy. No SciPy, FEniCS, or external mesh tooling.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FunnelGeometry:
    """ISO 4490 / ASTM B964 cone parameterized by orifice diameter."""

    label: str
    standard: str
    cone_half_angle_deg: float
    r_orifice_m: float
    r_top_m: float
    wall_thickness_m: float
    sample_mass_kg: float

    @property
    def cone_half_angle_rad(self) -> float:
        return math.radians(self.cone_half_angle_deg)

    @property
    def slant_length_m(self) -> float:
        return (self.r_top_m - self.r_orifice_m) / math.sin(self.cone_half_angle_rad)

    @property
    def cone_height_m(self) -> float:
        return (self.r_top_m - self.r_orifice_m) / math.tan(self.cone_half_angle_rad)

    def radius_at(self, s_m: float) -> float:
        """Inner radius at slant position s (meters)."""
        return self.r_orifice_m + s_m * math.sin(self.cone_half_angle_rad)

    def vertical_height_above_orifice(self, s_m: float) -> float:
        return s_m * math.cos(self.cone_half_angle_rad)

    def sample(self, n_nodes: int) -> tuple[np.ndarray, np.ndarray]:
        """Return (s, r) arrays sampled uniformly on [0, L_slant]."""
        s = np.linspace(0.0, self.slant_length_m, n_nodes)
        r = np.array([self.radius_at(si) for si in s])
        return s, r


HALL = FunnelGeometry(
    label="Hall (ISO 4490)",
    standard="ISO 4490:2018",
    cone_half_angle_deg=30.0,
    r_orifice_m=1.25e-3,    # 2.5 mm orifice diameter
    r_top_m=19.0e-3,        # 38 mm cup ID
    wall_thickness_m=1.5e-3,
    sample_mass_kg=0.050,
)

CARNEY = FunnelGeometry(
    label="Carney (ASTM B964)",
    standard="ASTM B964",
    cone_half_angle_deg=30.0,
    r_orifice_m=2.50e-3,    # 5.0 mm orifice diameter
    r_top_m=19.0e-3,
    wall_thickness_m=1.5e-3,
    sample_mass_kg=0.150,
)

FUNNELS: dict[str, FunnelGeometry] = {"hall": HALL, "carney": CARNEY}


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Material:
    """Linear-elastic + linear-thermal material record. SI units.

    Values pulled from public datasheets and ASM Handbook volumes; see
    references.md for citations.
    """

    label: str
    E_pa: float                 # Young's modulus, Pa
    alpha_per_k: float          # Coefficient of thermal expansion, /K
    rho_kg_per_m3: float        # Density, kg/m^3
    k_w_per_mk: float           # Thermal conductivity, W/m·K
    c_p_j_per_kgk: float        # Specific heat, J/kg·K
    yield_pa: float             # Yield strength, Pa
    citation: str               # Where the value came from


ALSI10MG = Material(
    label="AlSi10Mg (LPBF, as-built)",
    E_pa=70e9,
    alpha_per_k=21e-6,
    rho_kg_per_m3=2670.0,
    k_w_per_mk=130.0,
    c_p_j_per_kgk=910.0,
    yield_pa=230e6,
    citation="EOS AlSi10Mg datasheet; MatWeb cast AlSi10Mg summary",
)

SS316 = Material(
    label="316 stainless steel (annealed)",
    E_pa=193e9,
    alpha_per_k=16e-6,
    rho_kg_per_m3=8000.0,
    k_w_per_mk=16.2,
    c_p_j_per_kgk=500.0,
    yield_pa=205e6,
    citation="ASM Handbook Vol 1; AK Steel 316/316L datasheet",
)

MATERIALS: dict[str, Material] = {"alsi10mg": ALSI10MG, "316ss": SS316}


# Apparent (loose) powder densities for the gravity-load model.
POWDER_APPARENT_DENSITY: dict[str, float] = {
    "316ss_powder": 4500.0,
    "alsi10mg_powder": 1300.0,
}


# Convection coefficients used as point estimates in the thermal FEA.
H_INSIDE_W_PER_M2K = 200.0      # powder-on-metal contact (loose contact)
H_OUTSIDE_W_PER_M2K = 8.0       # ambient natural convection on inclined wall


if __name__ == "__main__":
    print("Funnel geometries (SI):")
    for name, f in FUNNELS.items():
        print(f"  {name:8} L_slant = {f.slant_length_m*1e3:6.3f} mm   "
              f"h_cone = {f.cone_height_m*1e3:6.3f} mm   "
              f"r_orifice = {f.r_orifice_m*1e3:5.3f} mm")
    print()
    print("Materials:")
    for name, m in MATERIALS.items():
        print(f"  {name:9} E = {m.E_pa/1e9:5.1f} GPa   "
              f"alpha = {m.alpha_per_k*1e6:5.1f} e-6/K   "
              f"k = {m.k_w_per_mk:6.1f} W/m·K   "
              f"({m.label})")
