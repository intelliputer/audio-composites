#!/usr/bin/env python3
"""Generate the placed, unrouted Rev. A Intellivision audio-line-driver PCB."""

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
CUSTOM = ROOT / "intellivision.pretty"
KICAD_FP = Path("/app/extensions/Library/Footprints/footprints")
OUT = ROOT / "intv-audio-line-driver.kicad_pcb"


def mm(value):
    return pcbnew.FromMM(value)


def point(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


board = pcbnew.BOARD()
board.SetCopperLayerCount(2)

nets = {}
for name in ("GND", "+5V", "AUD_IN", "Q1_BASE", "Q1_COL", "Q1_EM",
             "Q2_BASE", "Q2_COL", "Q2_EM", "AUDIO_BUS", "LEFT_OUT", "RIGHT_OUT"):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    nets[name] = net


def footprint(lib_dir, name, reference, value, x, y, nets_by_pad, rotation=0):
    fp = pcbnew.FootprintLoad(str(lib_dir), name)
    if fp is None:
        raise RuntimeError(f"Unable to load footprint {lib_dir}/{name}")
    fp.SetReference(reference)
    fp.SetValue(value)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    fp.SetPosition(point(x, y))
    fp.SetOrientationDegrees(rotation)
    for pad_number, net_name in nets_by_pad.items():
        pad = fp.FindPadByNumber(str(pad_number))
        if pad is None:
            raise RuntimeError(f"{reference}: no pad {pad_number}")
        pad.SetNet(nets[net_name])
    board.Add(fp)
    return fp


resistor = KICAD_FP / "Resistor_THT.pretty"
capacitor = KICAD_FP / "Capacitor_THT.pretty"
wire_pad = "WirePad_1x01_D3.5mm_Drill1.3mm"

footprint(CUSTOM, wire_pad, "J1", "AUD IN", 50, 80, {1: "AUD_IN"})
footprint(CUSTOM, wire_pad, "J2", "LEFT OUT", 131, 74, {1: "LEFT_OUT"})
footprint(CUSTOM, wire_pad, "J3", "RIGHT OUT", 131, 86, {1: "RIGHT_OUT"})
footprint(CUSTOM, wire_pad, "J4", "+5V IN", 50, 98, {1: "+5V"})
footprint(CUSTOM, wire_pad, "J5", "GND", 50, 106, {1: "GND"})

transistor = "TO-92_Inline_OAR175"
footprint(CUSTOM, transistor, "Q1", "2N3904", 78, 82,
          {1: "Q1_EM", 2: "Q1_BASE", 3: "Q1_COL"})
footprint(CUSTOM, transistor, "Q2", "2N3904", 96, 82,
          {1: "Q2_EM", 2: "Q2_BASE", 3: "Q2_COL"})

rname = "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
footprint(resistor, rname, "R1", "68k", 68, 72, {1: "+5V", 2: "Q1_BASE"}, 90)
footprint(resistor, rname, "R2", "22k", 68, 104, {1: "Q1_BASE", 2: "GND"}, 90)
footprint(resistor, rname, "R3", "4.7k", 80, 72, {1: "+5V", 2: "Q1_COL"}, 90)
footprint(resistor, rname, "R4", "1k", 80, 104, {1: "Q1_EM", 2: "GND"}, 90)
footprint(resistor, rname, "R5", "33k", 94, 72, {1: "+5V", 2: "Q2_BASE"}, 90)
footprint(resistor, rname, "R6", "33k", 94, 104, {1: "Q2_BASE", 2: "GND"}, 90)
footprint(resistor, rname, "R7", "0R", 108, 72, {1: "+5V", 2: "Q2_COL"}, 90)
footprint(resistor, rname, "R8", "1k", 108, 104, {1: "Q2_EM", 2: "GND"}, 90)
footprint(resistor, rname, "R9", "1k", 116, 74, {1: "AUDIO_BUS", 2: "LEFT_OUT"})
footprint(resistor, rname, "R10", "1k", 116, 86, {1: "AUDIO_BUS", 2: "RIGHT_OUT"})

cp = "CP_Radial_D6.3mm_P2.50mm"
footprint(capacitor, cp, "C1", "10u", 60, 82, {1: "AUD_IN", 2: "Q1_BASE"})
footprint(capacitor, cp, "C2", "10u", 87, 82, {1: "Q1_COL", 2: "Q2_BASE"})
footprint(capacitor, cp, "C3", "100u", 104, 82, {1: "Q2_EM", 2: "AUDIO_BUS"})
footprint(capacitor, cp, "C4", "100u", 58, 65, {1: "+5V", 2: "GND"})
footprint(capacitor, "C_Disc_D5.0mm_W2.5mm_P2.50mm", "C5", "100n", 58, 73,
          {1: "+5V", 2: "GND"})


def edge(x1, y1, x2, y2):
    segment = pcbnew.PCB_SHAPE(board)
    segment.SetShape(pcbnew.SHAPE_T_SEGMENT)
    segment.SetStart(point(x1, y1))
    segment.SetEnd(point(x2, y2))
    segment.SetLayer(pcbnew.Edge_Cuts)
    board.Add(segment)


edge(44, 55, 138, 55)
edge(138, 55, 138, 122)
edge(138, 122, 44, 122)
edge(44, 122, 44, 55)


def text(value, x, y, size=1.2):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(value)
    item.SetPosition(point(x, y))
    item.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    item.SetTextThickness(mm(0.2))
    item.SetLayer(pcbnew.F_SilkS)
    board.Add(item)


text("INTELLIVISION MONO AUDIO LINE DRIVER", 88, 57.5, 1.4)
text("REV A — PLACEMENT ONLY — DO NOT FAB", 88, 118, 1.1)
text("Q1 GAIN", 78, 88, 0.9)
text("Q2 BUFFER", 96, 88, 0.9)
text("AUD IN", 50, 75, 0.9)
text("+5V", 50, 94, 0.9)
text("GND", 50, 110, 0.9)
text("LEFT OUT", 126, 69, 0.9)
text("RIGHT OUT", 126, 91, 0.9)

pcbnew.SaveBoard(str(OUT), board)
