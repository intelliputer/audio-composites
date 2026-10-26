# Rev. A circuit contract — Intellivision mono line driver

## Status

The files named `intv-audio-line-driver.*` are the working KiCad project.
They were copied from the historical composite-video board as a mechanical
starting point. The PCB has since been regenerated and routed as the Rev. A
audio board from this circuit contract. The inherited schematic still
describes the former video circuit and is not yet the authoritative source for
the PCB.

This document is the electrical target for the first audio conversion. It is
intentionally all through-hole so the existing board style, wire pads, and
serviceability can be retained for the first hardware evaluation. The
reproducible placement generator is
[`tools/generate_rev_a_pcb.py`](tools/generate_rev_a_pcb.py); it requires the
KiCad Flatpak Python environment.

The routing report (`rev-a-routing-drc.rpt`) records **zero DRC violations,
zero unconnected pads, and zero footprint errors**. A schematic rewrite, ERC,
and first-article validation are still mandatory before fabrication.

## Functional circuit

```text
AUD_IN -- C1 --+-- Q1 base
               |
              R1
               |
              +5V
               |
              R2
               |
              GND

Q1 collector -- C2 -- Q2 base
Q1 emitter ---- R4 -------- GND
Q1 collector -- R3 -------- +5V

Q2 collector -- R7 (0 ohm link) -- +5V
Q2 emitter ---- R8 -------- GND
Q2 emitter ---- C3 ---- AUDIO_BUS

AUDIO_BUS -- R9 -- BUFFERED_AUD_OUT
```

`Q1` is a low-current common-emitter voltage stage. `Q2` is a common-collector
(emitter-follower) stage, providing a substantially lower output impedance than
the raw console audio node. `R9` supplies the buffered mono signal back to the
video-composite board's audio-output connection.

## Daughterboard interface

Install this board beside the video-composite board with four short wires:

| Daughterboard pad | Connect at the video/composite installation |
| --- | --- |
| `RAW AUD IN` | The console's original pre-RF audio tap. |
| `BUFFERED AUD OUT` | The video board's former `AUD_OUT` / external-audio-jack connection. |
| `+5V FROM VIDEO` | The regulated +5 V point used by the video board. |
| `GND FROM VIDEO` | The video board signal-ground point. |

Do **not** route the raw audio through the video board's original `C4`
straight-through path. Leave that path disconnected (or omit C4) and route the
new buffered-output wire to the external audio connector instead.

## Initial values

| Ref. | Value | Reason |
| --- | --- | --- |
| Q1, Q2 | 2N3904 | Existing board footprint; adequate for this low-level prototype. |
| C1 | 10 uF, >=10 V | Input DC blocking; positive terminal toward Q1 base. |
| R1 | 68 kOhm | Q1 base-bias upper leg. |
| R2 | 22 kOhm | Q1 base-bias lower leg; nominal base bias about 1.22 V. |
| R3 | 4.7 kOhm | Q1 collector load. |
| R4 | 1 kOhm | Q1 emitter degeneration and bias stability. |
| C2 | 10 uF, >=10 V | Q1/Q2 AC coupling; positive terminal toward Q2 base. |
| R5 | 33 kOhm | Q2 base-bias upper leg; nominal base bias about 2.5 V. |
| R6 | 33 kOhm | Q2 base-bias lower leg. |
| R7 | 0 Ohm link | Connects Q2 collector directly to +5 V. |
| R8 | 1 kOhm | Q2 emitter bias; nominal quiescent output about 1.8 V. |
| C3 | 47–100 uF, >=10 V | Output DC blocking; positive terminal toward Q2 emitter. |
| R9 | 1 kOhm | Output isolation between `AUDIO_BUS` and `BUFFERED AUD OUT`. |
| C4 | 100 nF ceramic | New supply-decoupling footprint directly between +5 V and GND. |
| C5 | 47–100 uF, >=10 V | New local supply bulk capacitor. |

The output resistor and decoupling capacitors are additions; therefore
this is not a drop-in value change to the inherited PCB.

## Required KiCad conversion work

1. Rename connector functions to `RAW_AUD_IN`, `BUFFERED_AUD_OUT`, `+5V`, and
   `GND`; remove video-only labels.
2. Rewire C3 to the **Q2 emitter**, not the inherited Q2 collector node.
3. Change Q2 from common-emitter to emitter-follower use by connecting its
   collector directly to +5 V through R7.
4. Add R9/R10 at the output and C4/C5 next to the transistor supply pins.
5. Redraw the PCB from the audio schematic; do not reuse inherited copper as
   if it matched these nets.
6. Run ERC in KiCad, then validate under a >=10 kOhm line load before
   a fabrication release.

## First-article acceptance

- No measurable DC at each audio output after C3.
- No audible 50/60 Hz hum with a short shielded input lead.
- No oscillation at either transistor when viewed with an oscilloscope.
- No clipping through representative games at both left/right outputs.
- No visible interference in the separately installed composite-video output.
