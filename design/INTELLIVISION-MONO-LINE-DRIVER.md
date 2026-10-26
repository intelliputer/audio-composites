# Intellivision mono line-driver board — Rev. A concept

## Purpose

This is a separate, experimental audio board for the NTSC Intellivision I,
Intellivision II, and Sears 497.75022. It takes the console's pre-RF mono
audio node and produces a buffered, adjustable line-level output. It is not a
stereo or sound-synthesis modification: it preserves the console's original
mono programme material.

Keeping this circuit separate from the composite-video board makes its noise,
gain, and loading characteristics independently measurable and avoids changing
the proven video PCB during audio development.

**Status:** circuit-definition stage; do not manufacture until a schematic,
PCB review, and bench validation are complete.

## Proposed signal path

```text
INTV_AUD_IN
  -> C1 input DC block
  -> U1A non-inverting high-impedance buffer / gain stage
  -> C4 output DC block -> R4 output isolation -> MONO_LINE_OUT

5 V -> FB1 -> AV5
AV5 -> U1 supply decoupling
AV5 -> R1/R2/C2/C3 reference network -> VREF (2.5 V)
```

`VREF` is the audio signal reference, not an external ground. The output
connector shield and the console's audio return connect to board ground.

## Rev. A component budget

| Ref. | Proposed value / function | Qty. |
| --- | --- | ---: |
| U1 | TLV9062 dual, RRIO, 5 V op amp; U1A is the audio stage and U1B buffers `VREF` | 1 |
| C1 | 1 uF film input coupling capacitor | 1 |
| C2 | 47 uF VREF bulk capacitor | 1 |
| C3, C6 | 100 nF ceramic, VREF and supply HF decoupling | 2 |
| C4 | 47 uF, >= 10 V output coupling electrolytic | 1 |
| C5 | 10 uF, >= 10 V supply bulk capacitor | 1 |
| R1, R2 | 10 kOhm 1% VREF divider | 2 |
| R3 | 100 kOhm input bias to `VREF` | 1 |
| R4 | 1 kOhm output isolation | 1 |
| R5 | 10 kOhm gain-setting resistor from U1A inverting input to `VREF` | 1 |
| R6 | 10 kOhm feedback resistor, giving a nominal gain of 2 | 1 |
| JP1 | 2-pin header; fit a shunt across R6 for unity gain | 1 |
| FB1 | Ferrite bead or 10 Ohm resistor to isolate `AV5` | 1 |

**Total: 15 placed components**, or **14** for fixed gain 2 with `JP1`
omitted. A fixed unity-gain buffer can omit `R5`, `R6`, and `JP1`, reducing
the board to **12 components**. The existing video board remains unmodified.

At gain 2, the board should be evaluated first with a normal high-impedance
line input (10 kOhm or greater). Use the unity-gain option if clipping is
observed or if the console's native level already suits the destination.

## Connections

| Board connection | Console / destination |
| --- | --- |
| `+5V_IN` | regulated console +5 V |
| `GND` | console signal ground |
| `INTV_AUD_IN` | raw mono audio going to the RF modulator |
| `MONO_LINE_OUT` | audio RCA centre pin, or two 1 kOhm branches to TRS tip and ring |
| `GND` | RCA shell / TRS sleeve |

Use a short twisted pair or shielded lead for `INTV_AUD_IN` and its ground
return. Keep it away from the video amplifier's high-current output wiring and
from the console's mains-side power-supply area.

## Bench acceptance criteria

1. With no console audio connected, confirm `VREF` is approximately half of
   `AV5` and that no DC appears at `MONO_LINE_OUT` after C4 settles.
2. Verify no oscillation at U1A/U1B with a scope before connecting the console.
3. Compare the raw audio tap and output at unity gain and gain 2 using a
   >=10 kOhm load. Record level, audible hum, and clipping.
4. Test with at least one capture device and powered speakers/headphones via a
   line-input amplifier; this board is not intended to drive passive speakers
   or headphones directly.
5. Confirm that installing/removing the audio board does not affect composite
   video amplitude or introduce visible interference.

## Next implementation step

Turn this definition into a KiCad schematic with explicit net labels, then
place the board so that the input area, analog supply filter, and output
connector form separate zones. Do not reuse the video board's layout merely
to save space: audio return routing and connector placement need their own
review.
