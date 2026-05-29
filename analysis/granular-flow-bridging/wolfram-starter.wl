(* ============================================================
   Granular-Flow Bridging Model — ISO 4490 Orifice
   Beverloo Equation: Mass Flow Rate vs. Orifice Diameter

   Status: source-only (L2 evidence)
   This file has NOT been executed. Execution in Wolfram Desktop,
   Wolfram Cloud, or wolframscript is required before any
   quantitative claims can be treated as validated output.

   Public-physics model only. No proprietary device data.
   See NOTICE.md in the repository root.

   References:
     Beverloo et al. (1961) Chem. Eng. Sci. 15, 260-269
     Brown & Richards (1970) Principles of Powder Mechanics
     Nedderman (1992) Statics and Kinematics of Granular Materials
     ISO 4490:2018 Hall flowmeter standard
   ============================================================ *)

(* --- Parameters (LPBF 316L stainless steel, published ranges) --- *)

d = 30*^-6;           (* mean particle diameter [m], 30 um typical for 15-45 um LPBF powder *)
rhoB = 4500;          (* bulk density [kg/m^3], approximate for 316L loose powder *)
g = 9.81;             (* gravitational acceleration [m/s^2] *)
C = 0.58;             (* Beverloo discharge coefficient, ~0.58 for near-spherical particles *)
k = 1.5;              (* dead-zone correction constant, ~1.5 standard value *)

(* --- Beverloo equation as a function of orifice diameter D [m] --- *)
(* W = C * rhoB * Sqrt[g] * (D - k*d)^(5/2)                        *)
(* Valid only when D > k*d (effective orifice positive)              *)

beverloo[D_] := C * rhoB * Sqrt[g] * (D - k*d)^(5/2)

(* --- Arch-blocking threshold --- *)
(* Flow ceases approximately when D/d < 5-7 (spheres)               *)
(* Simple criterion: D_crit = (k + 5) * d  =>  D/d_crit ~ 6.5      *)

dCrit = (k + 5) * d;    (* critical orifice diameter [m] for arching *)
Print["Arch-blocking threshold D_crit = ", dCrit * 1000, " mm  (D/d = ", dCrit/d, ")"]

(* --- Intermittent-flow regime bounds --- *)
(* Intermittent regime: approximately 5 < D/d < 10                  *)

dLow  = 5  * d;    (* lower bound of intermittent regime [m] *)
dHigh = 10 * d;    (* upper bound of intermittent regime [m] *)
Print["Intermittent regime: ", dLow*1000, " mm to ", dHigh*1000, " mm"]

(* --- ISO 4490 standard orifice diameters [m] --- *)

isoOrifices = {0.0025, 0.005, 0.010};   (* 2.5 mm, 5 mm, 10 mm *)
isoLabels   = {"ISO 2.5 mm", "ISO 5 mm", "ISO 10 mm"};

(* Print D/d ratio for each ISO orifice *)
Print["D/d ratios at ISO 4490 orifices (d = 30 um):"]
MapThread[
  Print["  ", #2, ": D/d = ", #1 / d],
  {isoOrifices, isoLabels}
]

(* --- Flow rate at ISO 4490 orifices --- *)
Print["Beverloo flow rate at ISO 4490 orifices:"]
MapThread[
  Print["  ", #2, ": W = ",
        NumberForm[beverloo[#1] * 1000, {4, 2}], " g/s  =>  50g test ~ ",
        NumberForm[50 / (beverloo[#1] * 1000), {4, 1}], " s"],
  {isoOrifices, isoLabels}
]

(* ============================================================
   PLOT: Mass flow rate vs. orifice diameter
   Range: D = 2 mm to 12 mm (covers all ISO 4490 orifices)
   ============================================================ *)

(* Plot range in meters *)
dMin = 0.002;
dMax = 0.012;

(* Main Beverloo curve — only valid where D > k*d *)
beverlooCurve = Plot[
  beverloo[D] * 1000,   (* convert to g/s for readability *)
  {D, dMin, dMax},
  PlotStyle  -> {Thick, Blue},
  PlotRange  -> {0, Automatic},
  AxesLabel  -> {"Orifice diameter D [m]", "Mass flow rate W [g/s]"},
  PlotLabel  -> Style[
    "Beverloo Equation — ISO 4490 Orifice\n(Public-physics model; no proprietary data)",
    14, Bold
  ],
  Frame      -> True,
  FrameLabel -> {
    "Orifice diameter D [m]",
    "Mass flow rate W [g/s]"
  },
  GridLines -> Automatic,
  ImageSize -> Large
]

(* Shaded intermittent-flow regime band *)
(* 5 < D/d < 10  =>  dLow < D < dHigh *)
intermittentBand = Graphics[{
  Opacity[0.15], Yellow,
  Rectangle[{dLow, 0}, {dHigh, 100}]
}]

(* ISO 4490 orifice markers — vertical dashed lines *)
isoLines = Graphics[
  Table[{
    Dashed, Thick, Red,
    Line[{{isoOrifices[[i]], 0}, {isoOrifices[[i]], beverloo[isoOrifices[[i]]] * 1000 * 1.15}}],
    Text[
      Style[isoLabels[[i]], 10, Red],
      {isoOrifices[[i]], beverloo[isoOrifices[[i]]] * 1000 * 1.2},
      {0, -1}
    ]
  }, {i, 1, Length[isoOrifices]}]
]

(* Arch-blocking threshold line *)
archLine = Graphics[{
  Dashed, Thick, Orange,
  Line[{{dCrit, 0}, {dCrit, 5}}],
  Text[
    Style["Arch threshold\nD/d \[TildeEqual] 6.5", 9, Orange],
    {dCrit + 0.0002, 4},
    {-1, 0}
  ]
}]

(* Intermittent regime label *)
intermittentLabel = Graphics[{
  Text[
    Style["Intermittent\nregime\n5 < D/d < 10", 9, Darker[Yellow, 0.4]],
    {(dLow + dHigh)/2, 1.5},
    {0, 0}
  ]
}]

(* Source-only watermark *)
watermark = Graphics[{
  Gray,
  Text[
    Style["SOURCE-ONLY — not executed — no validated output", 8, Italic, Gray],
    {dMin + (dMax - dMin)/2, -3},
    {0, 0}
  ]
}]

(* --- Combined figure --- *)
finalPlot = Show[
  intermittentBand,
  beverlooCurve,
  isoLines,
  archLine,
  intermittentLabel,
  PlotRange -> {{dMin, dMax}, {0, Automatic}}
]

Print["Plot generated. Export with Export[\"beverloo-plot.png\", finalPlot]"]
Print["NOTE: This file is source-only. Execute before treating output as L3 evidence."]

(* ============================================================
   SUMMARY TABLE: Key computed values
   ============================================================ *)

Print["\n=== Summary ==="]
Print["Model parameters: d = ", d*1e6, " um, rhoB = ", rhoB, " kg/m^3, C = ", C, ", k = ", k]
Print["Arch-blocking threshold: D_crit = ", dCrit*1000, " mm"]
Print["Intermittent regime: ", dLow*1000, " - ", dHigh*1000, " mm"]
Print["ISO 4490 2.5 mm orifice: D/d = ", 0.0025/d, " (well above arch threshold)"]
