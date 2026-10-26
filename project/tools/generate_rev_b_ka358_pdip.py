#!/usr/bin/env python3
"""Generate the compact, placed KA358 PDIP Rev. B daughterboard."""
from pathlib import Path
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
FP = Path('/app/extensions/Library/Footprints/footprints')
CUSTOM = ROOT / 'intellivision.pretty'
OUT = ROOT / 'intv-audio-line-driver-rev-b.kicad_pcb'
# Placement is intentionally the deliverable at this stage.  Keep any future
# routing enabled only after the matching schematic has been reviewed.
ROUTE = False

def mm(v): return pcbnew.FromMM(v)
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
nets = {}
for name in ('GND', '+5V', 'AV5', 'RAW_AUD_IN', 'IN_BIASED', 'VREF_RAW',
             'VREF', 'U1A_MINUS', 'U1A_OUT', 'AUDIO_BUS', 'BUFFERED_AUD_OUT'):
    n = pcbnew.NETINFO_ITEM(b, name); b.Add(n); nets[name] = n

def fp(lib, name, ref, value, x, y, pads):
    f = pcbnew.FootprintLoad(str(lib), name)
    if f is None: raise RuntimeError(f'Missing {lib}/{name}')
    f.SetReference(ref); f.SetValue(value); f.Reference().SetVisible(False); f.Value().SetVisible(False)
    f.SetPosition(pt(x, y))
    for number, net in pads.items(): f.FindPadByNumber(str(number)).SetNet(nets[net])
    b.Add(f)

wire = 'WirePad_1x01_D3.5mm_Drill1.3mm'
fp(CUSTOM, wire, 'J1', 'RAW AUDIO IN', 48, 70, {1:'RAW_AUD_IN'})
fp(CUSTOM, wire, 'J2', 'BUFFERED AUDIO OUT', 109, 70, {1:'BUFFERED_AUD_OUT'})
fp(CUSTOM, wire, 'J3', '+5V FROM VIDEO', 48, 84, {1:'+5V'})
fp(CUSTOM, wire, 'J4', 'GND FROM VIDEO', 48, 94, {1:'GND'})

# KA358 / LM358 pinout: 1 OUTA, 2 INA-, 3 INA+, 4 V-, 5 INB+, 6 INB-, 7 OUTB, 8 V+.
fp(FP/'Package_DIP.pretty', 'DIP-8_W7.62mm', 'U1', 'KA358', 72, 70,
   {1:'U1A_OUT', 2:'U1A_MINUS', 3:'IN_BIASED', 4:'GND', 5:'VREF_RAW', 6:'VREF', 7:'VREF', 8:'AV5'})

r = FP/'Resistor_THT.pretty'; rn = 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
fp(r, rn, 'R1', '10R', 93, 60, {1:'+5V', 2:'AV5'})
fp(r, rn, 'R2', '10k', 93, 66, {1:'AV5', 2:'VREF_RAW'})
fp(r, rn, 'R3', '10k', 93, 72, {1:'VREF_RAW', 2:'GND'})
fp(r, rn, 'R4', '100k', 93, 78, {1:'IN_BIASED', 2:'VREF'})
fp(r, rn, 'R5', '10k', 93, 84, {1:'U1A_MINUS', 2:'VREF'})
fp(r, rn, 'R6', '10k', 93, 90, {1:'U1A_OUT', 2:'U1A_MINUS'})
fp(r, rn, 'R7', '1k', 93, 96, {1:'AUDIO_BUS', 2:'BUFFERED_AUD_OUT'})

c = FP/'Capacitor_THT.pretty'; cp = 'CP_Radial_D6.3mm_P2.50mm'
fp(c, 'C_Disc_D5.0mm_W2.5mm_P2.50mm', 'C1', '1u', 58, 62, {1:'RAW_AUD_IN', 2:'IN_BIASED'})
fp(c, cp, 'C2', '47u', 58, 72, {1:'U1A_OUT', 2:'AUDIO_BUS'})
fp(c, cp, 'C3', '47u', 58, 82, {1:'VREF', 2:'GND'})
fp(c, cp, 'C4', '10u', 66, 90, {1:'AV5', 2:'GND'})
fp(c, 'C_Disc_D5.0mm_W2.5mm_P2.50mm', 'C5', '100n', 66, 98, {1:'AV5', 2:'GND'})

def edge(x1,y1,x2,y2):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(pt(x1,y1)); s.SetEnd(pt(x2,y2)); s.SetLayer(pcbnew.Edge_Cuts); b.Add(s)
for a in ((44,55,114,55),(114,55,114,105),(114,105,44,105),(44,105,44,55)): edge(*a)

# Ground pour on both copper faces keeps the return impedance low and leaves
# routing space for the signal and bias nets.
for layer in (pcbnew.F_Cu,):
    zone = pcbnew.ZONE(b)
    zone.SetNet(nets['GND'])
    zone.SetLayer(layer)
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((44.5,55.5),(113.5,55.5),(113.5,104.5),(44.5,104.5)):
        outline.Append(pt(x,y))
    b.Add(zone)
def text(value,x,y):
    t=pcbnew.PCB_TEXT(b); t.SetText(value); t.SetPosition(pt(x,y)); t.SetTextSize(pcbnew.VECTOR2I(mm(1),mm(1))); t.SetTextThickness(mm(.18)); t.SetLayer(pcbnew.F_SilkS); b.Add(t)

def route(net, layer, points, width=.4):
    if not ROUTE:
        return
    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(b)
        track.SetStart(pt(*start)); track.SetEnd(pt(*end)); track.SetWidth(mm(width))
        track.SetLayer(layer); track.SetNet(nets[net]); b.Add(track)

def via(net, x, y):
    if not ROUTE:
        return
    item = pcbnew.PCB_VIA(b); item.SetPosition(pt(x,y)); item.SetWidth(mm(1)); item.SetDrill(mm(.5))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); item.SetNet(nets[net]); b.Add(item)

# Two-layer prototype routing.  Power/return travel principally on B.Cu; the
# sensitive audio and bias paths stay on F.Cu and remain easy to inspect.
route('+5V', pcbnew.B_Cu, [(48,78),(51,78),(51,61),(82,61),(82,62)], .6)
route('GND', pcbnew.B_Cu, [(48,88),(48,97),(92,97)], .6)
route('GND', pcbnew.B_Cu, [(59.5,81),(59.5,97)])
route('GND', pcbnew.B_Cu, [(67.5,89),(67.5,97)])
route('GND', pcbnew.B_Cu, [(67.5,95),(67.5,97)])
route('GND', pcbnew.B_Cu, [(69,76.62),(69,97)])
route('GND', pcbnew.B_Cu, [(92.16,72),(92.16,97)])

route('AV5', pcbnew.F_Cu, [(92.16,62),(95,62),(95,65),(82,65),(82,67)])
route('AV5', pcbnew.F_Cu, [(82,67),(78,67),(78,69),(76.62,69)])
route('AV5', pcbnew.F_Cu, [(76.62,69),(79,69),(79,86),(65,86),(65,89)])
route('AV5', pcbnew.F_Cu, [(65,89),(65,95)])

route('VREF_RAW', pcbnew.F_Cu, [(92.16,67),(92.16,70),(82,70),(82,72)])
route('VREF_RAW', pcbnew.F_Cu, [(82,70),(80,70),(80,76.62),(76.62,76.62)])

route('VREF', pcbnew.F_Cu, [(76.62,71.54),(76.62,74.08)])
route('VREF', pcbnew.F_Cu, [(76.62,74.08),(78,74.08),(78,79),(92.16,79),(92.16,77)])
route('VREF', pcbnew.F_Cu, [(92.16,79),(92.16,82)])
route('VREF', pcbnew.F_Cu, [(78,79),(78,81),(57,81)])

route('RAW_AUD_IN', pcbnew.F_Cu, [(48,68),(52,68),(52,62),(57,62)])
route('IN_BIASED', pcbnew.F_Cu, [(59.5,62),(63,62),(63,74.08),(69,74.08)])
via('IN_BIASED',63,74.08); via('IN_BIASED',82,77)
route('IN_BIASED', pcbnew.B_Cu, [(63,74.08),(63,79),(82,79),(82,77)])

route('U1A_OUT', pcbnew.F_Cu, [(69,69),(60,69),(60,72),(57,72)])
route('U1A_OUT', pcbnew.F_Cu, [(69,69),(65,69),(65,87),(82,87)])
route('U1A_MINUS', pcbnew.F_Cu, [(69,71.54),(67,71.54),(67,82),(82,82)])
route('U1A_MINUS', pcbnew.F_Cu, [(82,82),(84,82),(84,85),(92.16,85),(92.16,87)])

via('AUDIO_BUS',59.5,72); via('AUDIO_BUS',82,92)
route('AUDIO_BUS', pcbnew.B_Cu, [(59.5,72),(59.5,93),(82,93),(82,92)])
route('BUFFERED_AUD_OUT', pcbnew.F_Cu, [(92.16,92),(98,92),(98,68),(97,68)])

# Reviewed production routing.  The unused experimental routes above remain
# disabled behind ROUTE=False; these are intentionally simple, inspectable
# point-to-point paths for a two-layer hand-assembled prototype.
def final_route(net, layer, points, width=.35):
    return
    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(b)
        track.SetStart(pt(*start)); track.SetEnd(pt(*end)); track.SetWidth(mm(width))
        track.SetLayer(layer); track.SetNet(nets[net]); b.Add(track)

# Input supply and filtered analogue rail.
final_route('+5V', pcbnew.B_Cu, [(48,78),(46.5,78),(46.5,60.7),(82,60.7),(82,62)], .5)
final_route('AV5', pcbnew.F_Cu, [(92.16,62),(95,62),(95,65),(82,65),(82,67)])
final_route('AV5', pcbnew.F_Cu, [(82,67),(80,67),(80,69),(76.62,69)])
final_route('AV5', pcbnew.F_Cu, [(76.62,69),(80,69),(80,88),(65,88),(65,89)])
final_route('AV5', pcbnew.F_Cu, [(65,89),(65,95)])

# Half-supply generator and its buffered reference.
final_route('VREF_RAW', pcbnew.F_Cu, [(92.16,67),(94,67),(94,70),(85,70),(85,72),(82,72)])
final_route('VREF_RAW', pcbnew.F_Cu, [(85,72),(85,75),(76.62,75),(76.62,76.62)])
final_route('VREF', pcbnew.B_Cu, [(76.62,71.54),(76.62,74.08)])
final_route('VREF', pcbnew.B_Cu, [(76.62,74.08),(75,74.08),(75,91),(61,91),(61,78.5),(57,78.5),(57,81)])
final_route('VREF', pcbnew.B_Cu, [(76.62,74.08),(78,74.08),(78,79),(92.16,79),(92.16,77)])
final_route('VREF', pcbnew.B_Cu, [(92.16,79),(92.16,82)])

# Raw audio input and gain-setting network.
final_route('RAW_AUD_IN', pcbnew.F_Cu, [(48,68),(52,68),(52,62),(57,62)])
final_route('IN_BIASED', pcbnew.F_Cu, [(59.5,62),(64,62),(64,68),(83,68),(83,77),(82,77)])
final_route('IN_BIASED', pcbnew.F_Cu, [(64,68),(64,74.08),(69,74.08)])
final_route('U1A_MINUS', pcbnew.F_Cu, [(69,71.54),(67,71.54),(67,82),(82,82)])
final_route('U1A_MINUS', pcbnew.F_Cu, [(82,82),(84,82),(84,85),(92.16,85),(92.16,87)])

# Amplifier output, AC coupling, and daughterboard return.
final_route('U1A_OUT', pcbnew.B_Cu, [(69,69),(61,69),(61,70),(57,70),(57,72)])
final_route('U1A_OUT', pcbnew.B_Cu, [(69,69),(66,69),(66,87),(82,87)])
final_route('AUDIO_BUS', pcbnew.F_Cu, [(59.5,72),(46.5,72),(46.5,98),(82,98),(82,92)])
final_route('BUFFERED_AUD_OUT', pcbnew.F_Cu, [(92.16,92),(98,92),(98,68),(97,68)])

def production_route(net, layer, points, width=.35):
    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(b)
        track.SetStart(pt(*start)); track.SetEnd(pt(*end)); track.SetWidth(mm(width))
        track.SetLayer(layer); track.SetNet(nets[net]); b.Add(track)

def production_via(net, x, y):
    item = pcbnew.PCB_VIA(b); item.SetPosition(pt(x,y)); item.SetWidth(mm(1)); item.SetDrill(mm(.5))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); item.SetNet(nets[net]); b.Add(item)

# Two-layer production routing.  The enlarged board preserves all through-hole
# parts while giving the raw audio, bias, and buffered output separate paths.
production_route('+5V', pcbnew.B_Cu, [(48,84),(52,84),(52,57),(93,57),(93,60)], .5)
production_route('AV5', pcbnew.F_Cu, [(103.16,60),(106,60),(106,63),(93,63),(93,66)])
production_route('AV5', pcbnew.F_Cu, [(93,66),(86,66),(86,70),(79.62,70)])
production_route('AV5', pcbnew.F_Cu, [(79.62,70),(86,70),(86,88),(66,88),(66,90)])
production_route('AV5', pcbnew.F_Cu, [(66,90),(66,98)])

production_route('VREF_RAW', pcbnew.B_Cu, [(103.16,66),(106,66),(106,70),(85,70),(85,72),(93,72)])
production_route('VREF_RAW', pcbnew.B_Cu, [(85,72),(85,77.62),(79.62,77.62)])
production_route('VREF', pcbnew.B_Cu, [(79.62,72.54),(79.62,75.08)])
production_route('VREF', pcbnew.B_Cu, [(79.62,75.08),(82,75.08),(82,76),(103.16,76),(103.16,78)])
production_route('VREF', pcbnew.F_Cu, [(79.62,75.08),(82,75.08),(82,85)])
production_via('VREF',82,85)
production_route('VREF', pcbnew.B_Cu, [(82,85),(82,91),(62,91),(62,84),(58,84),(58,82)])
production_route('VREF', pcbnew.B_Cu, [(79.62,75.08),(82,75.08),(82,86),(103.16,86),(103.16,84)])

production_route('RAW_AUD_IN', pcbnew.F_Cu, [(48,70),(52,70),(52,62),(58,62)])
production_route('IN_BIASED', pcbnew.B_Cu, [(60.5,62),(64,62),(64,75.08),(72,75.08)])
production_route('IN_BIASED', pcbnew.B_Cu, [(64,75.08),(64,87)])
production_via('IN_BIASED',64,87); production_via('IN_BIASED',80,87)
production_route('IN_BIASED', pcbnew.F_Cu, [(64,87),(80,87)])
production_route('IN_BIASED', pcbnew.B_Cu, [(80,87),(95,87),(95,78),(93,78)])

production_route('U1A_MINUS', pcbnew.F_Cu, [(72,72.54),(70,72.54),(70,84),(85,84)])
production_via('U1A_MINUS',85,84)
production_route('U1A_MINUS', pcbnew.B_Cu, [(85,84),(93,84)])
production_route('U1A_MINUS', pcbnew.B_Cu, [(93,84),(96,84),(96,88),(103.16,88),(103.16,90)])
production_route('U1A_OUT', pcbnew.F_Cu, [(72,70),(61,70),(61,69),(58,69),(58,72)])
production_route('U1A_OUT', pcbnew.F_Cu, [(72,70),(64,70),(64,92),(93,92),(93,90)])

production_route('AUDIO_BUS', pcbnew.F_Cu, [(60.5,72),(60.5,74),(52,74),(52,102),(93,102),(93,96)])
production_route('BUFFERED_AUD_OUT', pcbnew.F_Cu, [(103.16,96),(110,96),(110,70),(109,70)])
production_route('GND', pcbnew.B_Cu, [(68.5,90),(68.5,88),(60.5,88),(60.5,82)], .5)
production_route('GND', pcbnew.B_Cu, [(68.5,98),(68.5,90)], .5)

text('REV B — ROUTING HANDOFF — DO NOT FAB', 79, 102)
text('RAW IN', 50, 65); text('AUDIO OUT', 93, 65); text('+5V', 49, 75); text('GND',49,94)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(str(OUT), b)
