---
title: "The Tritium Problem: Fusion's Hidden Bottleneck"
author: "detroit.dev community"
date: 2026-03-31
tags: [fusion, tritium, fuel-cycle, breeding-blanket, lithium, safety]
---

# The Tritium Problem: Fusion's Hidden Bottleneck

D-T fusion is the easiest reaction to achieve, but tritium doesn't exist in nature in useful quantities. Every D-T fusion reactor must breed its own fuel — and the margins are razor-thin.

## Why D-T?

The deuterium-tritium reaction has the highest cross-section (probability of fusion) at the lowest temperature:

```
D + T → ⁴He (3.5 MeV) + n (14.1 MeV)
```

Alternatives exist but are vastly harder:

| Reaction | Temp needed | Notes |
|----------|------------|-------|
| D-T | ~15 keV (~170M °C) | Easiest. Neutron output. |
| D-D | ~50 keV | Two branches, lower power density |
| D-³He | ~60 keV | Aneutronic (mostly), but ³He is scarce |
| p-¹¹B | ~200 keV | Fully aneutronic, but extremely hard plasma physics |

D-T it is, for now. But T is radioactive (t₁/₂ = 12.3 years) and there's essentially no natural supply.

## Where tritium comes from today

Global tritium inventory: approximately 20-25 kg (as of ~2025).

Almost all comes from **CANDU heavy-water fission reactors** (Canada, South Korea, Romania):
- D₂O moderator captures neutrons → some deuterium transmutes to tritium
- Ontario Power Generation extracts ~1.5-2 kg/year from its CANDU fleet
- This is a byproduct, not a primary mission. CANDU reactors are aging and retiring.

**The supply cliff**: If no new CANDU-type reactors are built, global tritium production drops to near zero by the 2040s through radioactive decay alone. The half-life eats ~5.5% of inventory per year.

ITER alone needs ~12 kg of tritium over its lifetime. The startup inventory for a single D-T power reactor is estimated at 1-5 kg. If multiple fusion plants come online in the 2030s-2040s, the math doesn't close without self-breeding.

## Tritium self-sufficiency: breeding blankets

The plan: surround the reactor with lithium → neutrons from fusion reactions convert lithium to tritium:

```
⁶Li + n (slow) → T + ⁴He + 4.8 MeV    (exothermic)
⁷Li + n (fast) → T + ⁴He + n - 2.5 MeV  (endothermic, but regenerates a neutron)
```

Natural lithium is 92.5% ⁷Li, 7.5% ⁶Li. Enrichment in ⁶Li improves breeding.

### The Tritium Breeding Ratio (TBR)

**TBR** = tritium atoms produced per tritium atom consumed.

Must be > 1.0 for self-sufficiency. Accounting for:
- Radioactive decay during processing and storage
- Losses in extraction and purification
- Tritium trapped in materials
- Startup inventory for new reactors (if the fleet is growing)

**Target**: TBR ≥ 1.05-1.15 depending on assumptions.

**The problem**: Achieving TBR > 1.0 is not guaranteed. Every penetration in the blanket (heating ports, diagnostics, divertor) is a hole where neutrons escape without breeding. Monte Carlo neutronics simulations (OpenMC, MCNP) show TBR > 1.0 is *possible* but sensitive to design details.

No one has ever demonstrated tritium breeding in a real fusion environment. ITER's Test Blanket Module (TBM) program will be the first experimental data.

### Blanket concepts

| Concept | Breeder | Coolant | Multiplier | Notes |
|---------|---------|---------|------------|-------|
| HCPB (EU) | Li₄SiO₄ pebbles | Helium | Be pebbles | Solid breeder, reference EU DEMO concept |
| HCLL (EU) | PbLi liquid | Helium | Pb (in PbLi) | Liquid breeder, dual-coolant variant (DCLL) |
| WCLL (EU) | PbLi liquid | Water | Pb (in PbLi) | Water-cooled, lower technology risk |
| FLiBe (CFS/ARC) | ²LiF-BeF₂ molten salt | FLiBe itself | Be (in FLiBe) | Combined breeder/coolant/multiplier |

**Neutron multipliers** (beryllium or lead) are critical: each D-T fusion produces only one neutron, but you need ~1.1 tritium atoms per neutron (accounting for losses). Multiplier reactions like ⁹Be(n,2n) create extra neutrons.

## Tritium processing

Tritium must be extracted from the breeding blanket, purified, and recycled back into fueling systems — all while minimizing inventory in the loop (safety) and processing time (fuel availability).

**Typical processing loop**:
1. Tritium bred in blanket → extracted (permeation through membranes for liquid breeders, purge gas for solid breeders)
2. Mixed with hydrogen isotopes from plasma exhaust (vacuum pumping)
3. Isotope separation (cryogenic distillation — the most mature method)
4. Purification and storage (as uranium tritide for safe solid storage)
5. Fuel pellet injection back into the plasma

**Turnaround time matters**: if processing takes weeks, you need a larger T inventory (safety risk, cost). Target is hours to days.

### Fueling efficiency

Only ~1-2% of injected fuel actually fuses — the rest is exhausted and must be recycled. This means the processing plant handles vastly more tritium throughput than the burn rate suggests. A 1 GW fusion plant burns ~55 kg T/year but must process 5-10× that through the fuel cycle.

## Safety considerations

Tritium is a pure beta emitter (t₁/₂ = 12.3 years, E_max = 18.6 keV). The beta particles can't penetrate skin, but:
- **Inhalation/ingestion** of tritiated water (HTO) is the primary hazard
- HTO behaves like regular water in the body (biological half-life ~10 days)
- Regulatory limits on tritium release are strict

**On-site inventory targets**: Minimize total tritium on site to < 1-2 kg for licensing reasons. This drives aggressive processing speed requirements.

**Comparison to fission**: A fusion plant's worst-case accident releases tritium (hazardous but short-lived, disperses in atmosphere) — fundamentally different from fission accidents that release long-lived fission products (cesium-137, strontium-90) and actinides. There is no criticality excursion possible and no long-lived high-level waste.

## The lithium question

D-T fusion trades a tritium scarcity problem for a lithium demand, but lithium is abundant:
- ~600,000 tonnes of fusion fuel from seawater lithium (vs. ~90,000 tonnes in identified land reserves)
- A 1 GW fusion plant uses ~100 kg lithium/year — negligible compared to battery industry demand (~100,000+ tonnes/year)
- Even accounting for ⁶Li enrichment, lithium supply is not a constraint for fusion

## Open questions

- Can TBR > 1.0 be achieved in an integrated reactor design? (ITER TBM will provide first data, but only for small test modules)
- How quickly can tritium be extracted from solid breeding pebbles under irradiation? (Retention increases with radiation damage)
- Can the startup inventory problem be solved? (First-of-a-kind reactors need tritium from fission; fleet expansion requires surplus from operating fusion plants)
- Will FLiBe salt chemistry work under intense neutron irradiation? (Radiolysis produces fluorine gas — corrosion concern)

## Links

- [Abdou et al., "Physics and technology considerations for the D-T fuel cycle" Nuclear Fusion 2021](https://doi.org/10.1088/1741-4326/abbf35)
- [Pearson et al., "Tritium supply and use" Fusion Engineering and Design 2018](https://doi.org/10.1016/j.fusengdes.2018.04.090)
- [ITER TBM program](https://www.iter.org/mach/testblanketsystem)
- [Kovari et al., "Tritium resources available for D-T fusion" Nuclear Fusion 2018](https://doi.org/10.1088/1741-4326/aa9d25)
