## audio-composites

Since just seeing isn't believing.

## Intellivision mono audio line driver

This repository now contains a standalone audio-output prototype for the NTSC
Intellivision I, Intellivision II, and Sears 497.75022. It taps the console's
pre-RF mono audio, buffers it with a two-transistor gain/line-driver stage,
and returns a buffered mono line to the video-composite board's audio-output
connection.
It does not create stereo or alter the console's sound generation.

The project is intentionally separate from the composite-video board so audio
level, hum, loading, and video interaction can be tested independently. It is
intended to mount as a daughterboard beside that board, using four short wires:
raw audio, buffered audio return, +5 V, and ground. The video board's original
straight-through audio capacitor is bypassed.

### Current status: routed prototype, not yet fabrication-ready

[`project/intv-audio-line-driver.kicad_pcb`](project/intv-audio-line-driver.kicad_pcb)
is a fully routed KiCad Rev. A board. Its routing report has zero DRC
violations and zero unconnected pads. It remains explicitly marked **DO NOT
FAB** because the inherited KiCad schematic has not yet been rewritten to
match the new audio netlist, and the circuit still requires bench validation.

The circuit, component values, and first-article checks are defined in
[`project/REV-A-CIRCUIT.md`](project/REV-A-CIRCUIT.md). The placement can be
recreated through KiCad Flatpak with
[`project/tools/generate_rev_a_pcb.py`](project/tools/generate_rev_a_pcb.py).

The next compact, hand-assembled revision is specified in
[`project/REV-B-KA358-PDIP.md`](project/REV-B-KA358-PDIP.md). It replaces the
discrete stage with a KA358-compatible PDIP-8 dual op amp. Its enlarged
two-layer through-hole routing handoff is in
[`project/intv-audio-line-driver-rev-b.kicad_pcb`](project/intv-audio-line-driver-rev-b.kicad_pcb);
it is deliberately marked **DO NOT FAB** pending a reviewed schematic and
manual routing/DRC cleanup.

Before any fabrication release:

1. Redraw the KiCad schematic from the Rev. A circuit contract.
2. Update the PCB from that schematic and rerun ERC/DRC.
3. Test a first article under a line-level load.
