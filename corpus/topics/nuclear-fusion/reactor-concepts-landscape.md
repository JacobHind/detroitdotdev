---
title: "Fusion Reactor Concepts: From ITER to Private Startups"
author: "detroit.dev community"
date: 2026-03-31
tags: [fusion, reactor-design, iter, sparc, hts-magnets, compact-fusion, stellarator]
---

# Fusion Reactor Concepts: From ITER to Private Startups

A survey of active fusion reactor designs, from the international ITER mega-project to the wave of private companies betting on compact, high-field approaches.

## The conventional path: ITER → DEMO → commercial

The mainstream roadmap has been:
1. **ITER** — Prove Q=10 burning plasma physics
2. **DEMO** — First electricity-producing fusion plant (~2050s)
3. **Commercial** — Nth-of-a-kind power plants

This timeline is increasingly being challenged by private companies claiming they can skip steps.

## ITER (International)

The world's largest science experiment. 35 nations, ~$25B+ (original estimate $5B).

| Parameter | Value |
|-----------|-------|
| Plasma volume | 840 m³ |
| Major radius | 6.2 m |
| Magnetic field | 5.3 T (Nb₃Sn superconducting) |
| Fusion power | 500 MW (thermal) |
| Q (gain) | 10 (target), 5 (baseline) |
| Pulse length | 400 s (inductive), 3000 s (advanced) |

**What ITER will prove**: Sustained burning plasma (alpha-particle self-heating dominates), tritium breeding blanket modules (test blanket program), long-pulse operation, integrated plasma-facing component performance.

**What ITER won't do**: Generate electricity, breed its own tritium at full scale, demonstrate commercial viability.

## SPARC / ARC (Commonwealth Fusion Systems)

The high-field compact approach. CFS is the MIT spinout that bet everything on high-temperature superconducting (HTS) magnets.

**Key insight**: Fusion power density scales as B⁴. If you can double the magnetic field, you get 16× the power density, enabling a device ~1/40th ITER's volume to produce similar fusion power.

**SPARC** (the experiment):
- 20 T HTS magnets (REBCO tape) — demonstrated a record 20 T large-bore magnet in Sept 2021
- R₀ = 1.85 m, a = 0.57 m — fits in a large gym
- Target Q > 2, fusion power ~140 MW
- First plasma targeting 2026-2027

**ARC** (the power plant concept):
- Demountable HTS magnets — the tokamak opens like a clamshell for maintenance
- Molten salt FLiBe blanket (tritium breeding + neutron shielding + heat extraction)
- Compact enough to be factory-manufactured
- Target: ~500 MWe, LCOE competitive with natural gas

The demountable magnet concept is transformative: conventional tokamak maintenance requires cutting through the vacuum vessel. ARC's magnets unbolt, the vessel opens, components swap out.

## Wendelstein 7-X / Stellarators

W7-X in Greifswald, Germany is proving the stellarator concept can achieve tokamak-level confinement.

**Why stellarators matter for reactors**:
- Inherently steady-state (no plasma current to sustain)
- No disruptions (no current to quench)
- Might enable simpler, more reliable power plants

**The catch**: Manufacturing precision. W7-X's 50 non-planar superconducting coils were machined to sub-millimeter tolerance. Each is unique. This makes stellarators expensive to build but potentially cheaper to operate.

**HELIAS** — the proposed stellarator power plant study. Would produce ~3 GW thermal. Still conceptual.

**Type One Energy** (startup) — designing a stellarator using simplified HTS coils and additive manufacturing. Claims this solves the "every coil is unique" manufacturing problem.

## TAE Technologies (FRC)

Formerly Tri Alpha Energy. Uses Field-Reversed Configuration — a compact, high-β plasmoid sustained by neutral beam injection.

- **Norman** reactor (2017) achieved stable FRC plasmas at >50 million °C
- **Copernicus** (next device) aims to demonstrate net energy conditions
- D-³He fuel cycle is the long-term target — produces protons instead of neutrons (aneutronic), meaning dramatically less radioactive waste and no need for tritium breeding
- **Challenge**: D-³He requires ~10× higher temperatures than D-T, and ³He is extremely scarce on Earth

## Tokamak Energy (Spherical Tokamak)

UK company betting on spherical tokamaks (very low aspect ratio, A ~ 1.5-1.8).

- **ST40** achieved 100 million °C ion temperature in 2022
- Using HTS magnets
- Compact geometry: higher β means more fusion power per unit magnetic field
- **Challenge**: The center column is extremely space-constrained; fitting neutron shielding and structural material around it is an unsolved engineering problem

## Helion Energy (FRC + Direct Energy Conversion)

Unique approach: collide two FRC plasmoids at high speed, compress magnetically, capture energy via direct electromagnetic conversion (changing flux induces current — no steam turbine needed).

- Targeting D-³He fuel
- Claims 95% efficient electrical conversion (vs. ~33% for thermal cycle)
- Signed a PPA (power purchase agreement) with Microsoft for 2028 delivery
- **Polaris** (7th prototype) under construction
- Extremely aggressive timeline — most physicists are skeptical but watching

## General Fusion (Magnetized Target Fusion)

Canadian company. Hybrid approach: compress a magnetized plasma target using a liquid metal liner driven by pistons.

- Doesn't need sustained confinement — just crush it fast enough
- Liquid metal (lithium-lead) acts as both compressor and tritium breeding blanket
- Building a demonstration plant at Culham, UK

## Zap Energy (Sheared-Flow Z-Pinch)

Uses a Z-pinch plasma (current flowing through the plasma creates its own confining magnetic field) stabilized by sheared axial flow.

- No external magnets at all — dramatically simpler and cheaper
- Z-pinches were historically unstable (sausage and kink instabilities), but sheared flow suppresses these
- Very compact device
- Still at early experimental stage

## The HTS magnet revolution

The thread connecting most private fusion companies: **REBCO (Rare Earth Barium Copper Oxide) high-temperature superconducting tape**.

Why it changes everything:
- Operates at 20 K (vs. 4 K for Nb₃Sn/NbTi) — cheaper, simpler cryogenics
- Carries much higher current density at high field
- Enables 20+ T magnets in compact geometries
- Can be wound as flat tape → demountable joints become possible (CFS's key innovation)
- ITER's magnets use Nb₃Sn which was state-of-art when designed in the 2000s. New devices use REBCO.

**The bottleneck**: REBCO tape production. Currently ~2,000+ km/year globally, but prices are falling and multiple manufacturers are scaling (SuperPower, Fujikura, SuNam, THEVA).

## Comparison matrix

| Company | Concept | Fuel | Target Q/gain | First power | Magnets |
|---------|---------|------|---------------|-------------|---------|
| ITER | Tokamak | D-T | Q=10 | ~2040s (no electricity) | Nb₃Sn |
| CFS (SPARC→ARC) | Compact tokamak | D-T | Q>2 (SPARC) | ~2030s | HTS REBCO |
| TAE | FRC | D-³He (long-term) | — | 2030s | Conventional |
| Tokamak Energy | Spherical tokamak | D-T | — | 2030s | HTS |
| Helion | FRC collision | D-³He | — | 2028 (claimed) | Pulsed |
| General Fusion | MTF | D-T | — | 2030s | None (liquid metal) |
| Zap Energy | Z-pinch | D-T | — | 2030s | None |
| Type One Energy | Stellarator | D-T | — | 2030s | HTS |

## Links

- [CFS / SPARC overview](https://cfs.energy/)
- [TAE Technologies](https://tae.com/)
- [Helion Energy](https://www.helionenergy.com/)
- [ITER progress](https://www.iter.org/newsline)
- [Fusion Industry Association members](https://www.fusionindustryassociation.org/members)
