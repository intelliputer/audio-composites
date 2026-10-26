#!/usr/bin/env python3
"""Generate the placed, unrouted Rev. A Intellivision audio-line-driver PCB."""

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
CUSTOM = ROOT / "intellivision.pretty"
KICAD_FP = Path("/app/extensions/Library/Footprints/footprints")
OUT = ROOT / "intv-audio-line-driver.kicad_pcb"
ROUTE = True


def mm(value):
    return pcbnew.FromMM(value)


def point(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


board = pcbnew.BOARD()
board.SetCopperLayerCount(2)

nets = {}
for name in ("GND", "+5V", "AUD_IN", "Q1_BASE", "Q1_COL", "Q1_EM",
             "Q2_BASE", "Q2_COL", "Q2_EM", "AUDIO_BUS", "AUD_OUT"):
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

footprint(CUSTOM, wire_pad, "J1", "RAW AUD IN", 50, 76, {1: "AUD_IN"})
footprint(CUSTOM, wire_pad, "J2", "BUF AUD OUT", 131, 80, {1: "AUD_OUT"})
footprint(CUSTOM, wire_pad, "J3", "+5V FROM VID", 50, 94, {1: "+5V"})
footprint(CUSTOM, wire_pad, "J4", "GND FROM VID", 50, 104, {1: "GND"})

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
footprint(resistor, rname, "R9", "1k", 116, 80, {1: "AUDIO_BUS", 2: "AUD_OUT"})

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
text("REV A — ROUTED PROTOTYPE — DO NOT FAB", 88, 118, 1.1)
text("Q1 GAIN", 78, 88, 0.9)
text("Q2 BUFFER", 96, 88, 0.9)
text("RAW AUDIO IN", 52, 88, 0.9)
text("+5V FROM VIDEO", 54, 91, 0.9)
text("GND FROM VIDEO", 54, 108, 0.9)
text("BUFFERED AUDIO OUT", 124, 75, 0.9)


def route(net_name, layer, points, width=0.5):
    """Add a same-layer, Manhattan-style trace through each supplied point."""
    if not ROUTE:
        return
    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(point(*start))
        track.SetEnd(point(*end))
        track.SetWidth(mm(width))
        track.SetLayer(layer)
        track.SetNet(nets[net_name])
        board.Add(track)


def via(net_name, x, y):
    item = pcbnew.PCB_VIA(board)
    item.SetPosition(point(x, y))
    item.SetWidth(mm(1.0))
    item.SetDrill(mm(0.5))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    item.SetNet(nets[net_name])
    board.Add(item)


# Power and ground returns use B.Cu to keep them separate from the audio paths.
route("+5V", pcbnew.B_Cu, [(50, 94), (55, 94), (55, 70), (108, 70)])
route("+5V", pcbnew.B_Cu, [(58, 65), (58, 70)])
route("+5V", pcbnew.B_Cu, [(58, 73), (58, 70)])
route("+5V", pcbnew.B_Cu, [(68, 72), (68, 70)])
route("+5V", pcbnew.B_Cu, [(80, 72), (80, 70)])
route("+5V", pcbnew.B_Cu, [(94, 72), (94, 70)])
route("+5V", pcbnew.B_Cu, [(108, 72), (108, 70)])

route("GND", pcbnew.B_Cu, [(50, 104), (50, 110), (110, 110)])
route("GND", pcbnew.F_Cu, [(60.5, 65), (64, 65), (64, 76)])
route("GND", pcbnew.F_Cu, [(60.5, 73), (64, 73)])
via("GND", 64, 76)
route("GND", pcbnew.B_Cu, [(64, 76), (64, 110)])
route("GND", pcbnew.B_Cu, [(68, 93.84), (70, 93.84), (70, 110)])
route("GND", pcbnew.B_Cu, [(80, 93.84), (82, 93.84), (82, 110)])
route("GND", pcbnew.B_Cu, [(94, 93.84), (96, 93.84), (96, 110)])
route("GND", pcbnew.B_Cu, [(108, 93.84), (110, 93.84), (110, 110)])

# Audio signal path on F.Cu. Each branch is deliberately short and direct.
route("AUD_IN", pcbnew.F_Cu, [(50, 76), (56, 76), (56, 82), (60, 82)])
route("Q1_BASE", pcbnew.F_Cu, [(62.5, 82), (62.5, 78), (79.27, 78), (79.27, 82)])
route("Q1_BASE", pcbnew.F_Cu, [(68, 78), (72, 78), (72, 59), (68, 59), (68, 61.84)])
route("Q1_BASE", pcbnew.F_Cu, [(72, 78), (72, 104), (68, 104)])
route("Q1_COL", pcbnew.F_Cu, [(80.54, 82), (87, 82)])
route("Q1_COL", pcbnew.F_Cu, [(84, 82), (84, 60), (80, 60), (80, 61.84)])
route("Q1_EM", pcbnew.F_Cu, [(78, 82), (76, 84), (76, 106), (80, 106), (80, 104)])
route("Q2_BASE", pcbnew.F_Cu, [(89.5, 82), (89.5, 78), (97.27, 78), (97.27, 82)])
route("Q2_BASE", pcbnew.F_Cu, [(92, 78), (90, 78), (90, 59), (94, 59), (94, 61.84)])
route("Q2_BASE", pcbnew.F_Cu, [(92, 78), (92, 104), (94, 104)])
route("Q2_COL", pcbnew.F_Cu, [(98.54, 82), (100, 82), (100, 60), (108, 60), (108, 61.84)])
route("Q2_EM", pcbnew.F_Cu, [(96, 82), (96, 86), (104, 86), (104, 82)])
route("Q2_EM", pcbnew.F_Cu, [(102, 86), (102, 106), (108, 106), (108, 104)])
route("AUDIO_BUS", pcbnew.F_Cu, [(106.5, 82), (116, 82), (116, 80)])
route("AUD_OUT", pcbnew.F_Cu, [(126.16, 80), (131, 80)])

pcbnew.SaveBoard(str(OUT), board)
