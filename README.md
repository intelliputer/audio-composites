## audio-composites

Since just seeing isn't believing.

## Intellivision mono audio line driver

This repository now contains a standalone audio-output prototype for the NTSC
Intellivision I, Intellivision II, and Sears 497.75022. It taps the console's
pre-RF mono audio, buffers it with a two-transistor gain/line-driver stage,
and provides isolated left/right line outputs carrying the same mono program.
It does not create stereo or alter the console's sound generation.

The project is intentionally separate from the composite-video board so audio
level, hum, loading, and video interaction can be tested independently.

### Current status: placed, unrouted prototype

[`project/intv-audio-line-driver.kicad_pcb`](project/intv-audio-line-driver.kicad_pcb)
is a real KiCad Rev. A placement with no physical DRC violations. It is
explicitly marked **DO NOT FAB**: 29 electrical connections still need routing,
and the inherited KiCad schematic has not yet been rewritten to match the new
audio netlist.

The circuit, component values, and first-article checks are defined in
[`project/REV-A-CIRCUIT.md`](project/REV-A-CIRCUIT.md). The placement can be
recreated through KiCad Flatpak with
[`project/tools/generate_rev_a_pcb.py`](project/tools/generate_rev_a_pcb.py).

Before any fabrication release:

1. Redraw the KiCad schematic from the Rev. A circuit contract.
2. Update the PCB from that schematic and route every net.
3. Resolve ERC/DRC findings and test a first article under a line-level load.
