# Rev. B — KA358 PDIP daughterboard

Rev. B replaces the discrete-transistor prototype with a hand-solderable
`KA358` / LM358-compatible dual op-amp in a PDIP-8 package. It remains a
four-wire daughterboard installed next to the composite-video board:
`RAW_AUD_IN`, `BUFFERED_AUD_OUT`, `+5V`, and `GND`.

The original composite board's raw-audio straight-through capacitor is omitted
or bypassed; `BUFFERED_AUD_OUT` goes directly to its external audio-jack wire.

## Circuit

```text
+5V -- 10R/Ferrite -- AV5 -- U1 pin 8
GND ------------------------ U1 pin 4

AV5 -- 10k --+-- 10k -- GND
              |
             VREF_RAW -- U1B non-inverting input (pin 5)
                            U1B output (pin 7) tied to inverting input (pin 6)
                            => VREF

RAW_AUD_IN -- C1 1uF --+-- U1A non-inverting input (pin 3)
                         |
                        100k
                         |
                        VREF

U1A pin 2 -- 10k -- VREF
U1A pin 1 -- 10k -- U1A pin 2     (non-inverting gain = 2)
U1A pin 1 -- C2 47uF -- 1k -- BUFFERED_AUD_OUT

VREF -- 47uF || 100nF -- GND
AV5  -- 10uF  || 100nF -- GND
```

`C2` positive faces U1A's output. `C1` may be film or a bipolar electrolytic.
Gain is deliberately conservative; fit a 0-ohm link in place of the feedback
10 kOhm resistor for unity gain if the raw console audio proves large.

## Layout target

Use `Package_DIP:DIP-8_W7.62mm` for U1 and through-hole axial/disc/radial
parts. The compact 55 x 40 mm target was enlarged to **70 x 50 mm** to make a
two-layer, through-hole route practical. `RAW_AUD_IN`, `+5V`, and `GND` exit
on the left edge; the buffered audio return exits on the right, separating the
input and output wires.

`intv-audio-line-driver-rev-b.kicad_pcb` is a routing handoff, not a
fabrication file. It has complete electrical connectivity but still requires
manual DRC cleanup and a matching reviewed schematic before ordering.

## Validation hold

This is a design contract, not a fabrication release. Before ordering: redraw
the schematic using the LM358-compatible pinout with value `KA358`, route the
compact PCB from that schematic, and test gain/headroom/noise on a real
console.
