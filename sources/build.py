# -*- coding: utf-8 -*-
"""Police « Rosmaryn Esoteric » : signes, planètes, points, aspects, trigrammes, hexagrammes.

Tracés maison des signes, planètes et points : ~/_commons-lot1/glyphes.json (traits sur une grille de 16,
extrémités rondes). Aspects, monogrammes, digrammes, trigrammes, hexagrammes : dessinés ici.
Hexagrammes : trigramme du bas et du haut lus dans ~/corpus/yi-king/noms.json (ordre de King Wen = ordre Unicode).
Traits convertis en contours par skia-pathops, puis police TrueType par fontTools.

Usage : PYTHONPATH=<pyfont> /opt/alt/python311/bin/python3 construire.py <sortie> [epaisseur=1.5] [style=Regular]
"""
import sys, os, json, math
ICI = os.path.dirname(os.path.abspath(__file__))
import pathops
from fontTools.svgLib.path import parse_path
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.fontBuilder import FontBuilder
from picosvg.svg_types import SVGPath

OUT = sys.argv[1] if len(sys.argv) > 1 else 'sortie'
EP = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
STYLE = sys.argv[3] if len(sys.argv) > 3 else 'Regular'
os.makedirs(OUT, exist_ok=True)
FAMILLE = 'Rosmaryn Esoteric'
VERSION = '0.100'
U = 50                      # unités de police par unité de grille (16 -> 800)
UPM, ASC, DESC = 1000, 800, -200
AVANCE = 900
XFORM = (U, 0, 0, -U, 50, 14 * U)   # x' = 50 + 50x ; y' = 700 - 50y (y = 14 sur la ligne de base)

G = json.load(open(os.path.join(ICI, 'glyphes.json'), encoding='utf-8'))
TR = {x[0]: x[-1] for k in G for x in G[k]}

# ---------- éléments de dessin ----------
def trait(d, ep=None, cap='round'):
    return ('trait', d, EP if ep is None else ep, cap)

def plein(d):
    return ('plein', d)

def cercle(cx, cy, r):
    return f'M{cx - r} {cy}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0Z'

def barre(x1, x2, y, h):
    return f'M{x1} {y - h / 2}H{x2}V{y + h / 2}H{x1}Z'

# ---------- répertoire : (nom de glyphe, [codes], [éléments]) ----------
GLY = []
SIGNES = ['Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge', 'Balance', 'Scorpion',
          'Sagittaire', 'Capricorne', 'Verseau', 'Poissons']
NOMS_SIGNES = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpius',
               'sagittarius', 'capricorn', 'aquarius', 'pisces']
for i, s in enumerate(SIGNES):
    GLY.append((NOMS_SIGNES[i], [0x2648 + i], [trait(TR[s])]))

GLY += [
    ('sun', [0x2609], [trait(TR['☉']), plein(cercle(8, 8, 1.3))]),
    ('moon', [0x263D], [plein('M10.5 2C7.5 2 5 4.5 5 8s2.5 6 5.5 6c-1.2-1.3-2-3.5-2-6s.8-4.7 2-6z')]),
    ('mercury', [0x263F], [trait(TR['☿'])]),
    ('venus', [0x2640], [trait(TR['♀'])]),
    ('earth', [0x1F728], [trait(TR['⊕'])]),
    ('mars', [0x2642], [trait(TR['♂'])]),
    ('jupiter', [0x2643], [trait(TR['♃'])]),
    ('saturn', [0x2644], [trait(TR['♄'])]),
    ('uranus', [0x2645], [trait(TR['♅'])]),
    ('neptune', [0x2646], [trait(TR['♆'])]),
    ('pluto', [0x2647, 0x2BD3], [trait(TR['♇'])]),
    ('ascendingnode', [0x260A], [trait(TR['☊'])]),
    ('descendingnode', [0x260B], [trait(TR['☋'])]),
    ('chiron', [0x26B7], [trait(TR['Chiron'])]),
    ('ceres', [0x26B3], [trait(TR['Ceres'])]),
    ('pallas', [0x26B4], [trait(TR['Pallas'])]),
    ('juno', [0x26B5], [trait(TR['Junon'])]),
    ('vesta', [0x26B6], [trait(TR['Vesta'])]),
    ('blackmoonlilith', [0x26B8], [trait(TR['LuneNoire'])]),
    ('lotoffortune', [0x1F774], [trait(TR['PartFortune'])]),
    ('vertex', [0xE000], [trait(TR['Vertex'])]),          # aucun code Unicode : zone à usage privé
]

# aspects (grille de 16)
GLY += [
    ('conjunction', [0x260C], [trait(cercle(6.4, 9.6, 3.2)), trait('M8.7 7.3L13 3')]),
    ('opposition', [0x260D], [trait(cercle(4.6, 11.4, 2.4)), trait(cercle(11.4, 4.6, 2.4)), trait('M6.3 9.7L9.7 6.3')]),
    ('square', [0x25A1], [trait('M3.2 3.2H12.8V12.8H3.2Z')]),
    ('trine', [0x25B3], [trait('M8 2.6L13.6 12.8H2.4Z')]),
    ('sextile', [0x26B9], [trait('M8 2.2V13.8'), trait('M2.98 5.1L13.02 10.9'), trait('M2.98 10.9L13.02 5.1')]),
    ('semisextile', [0x26BA], [trait('M3.5 3L8 11L12.5 3'), trait('M3 13.4H13')]),
    ('quincunx', [0x26BB], [trait('M3 2.6H13'), trait('M3.5 13L8 5L12.5 13')]),
    ('semisquare', [0x2220], [trait('M12.8 3.4L3.2 12.8H12.8')]),
    ('sesquiquadrate', [0x26BC], [trait('M2.8 6.2H9.8V13.2H2.8Z'), trait('M9.8 6.2L13.4 2.6')]),
]

# Yi King : traits pleins et brisés (épaisseur proportionnelle au réglage)
def lignes(bits, y0, y1, h, x1=2.2, x2=13.8, ecart=2.0):
    """bits du bas vers le haut ; renvoie des éléments pleins."""
    n = len(bits)
    el = []
    for i, b in enumerate(bits):
        y = y1 - i * (y1 - y0) / (n - 1) if n > 1 else (y0 + y1) / 2
        if b:
            el.append(plein(barre(x1, x2, y, h)))
        else:
            m = (x1 + x2) / 2
            el.append(plein(barre(x1, m - ecart / 2, y, h)))
            el.append(plein(barre(m + ecart / 2, x2, y, h)))
    return el

H6 = max(1.0, 1.05 * EP / 1.5)   # barres des hexagrammes : jamais plus fines que 1 (la Light les perdait à l'écran)
TRIG = {'Ciel': [1, 1, 1], 'Lac': [1, 1, 0], 'Feu': [1, 0, 1], 'Tonnerre': [1, 0, 0],
        'Vent': [0, 1, 1], 'Eau': [0, 1, 0], 'Montagne': [0, 0, 1], 'Terre': [0, 0, 0]}
ORDRE_TRIG = ['Ciel', 'Lac', 'Feu', 'Tonnerre', 'Vent', 'Eau', 'Montagne', 'Terre']   # 2630..2637
NOMS_TRIG = ['heaven', 'lake', 'fire', 'thunder', 'wind', 'water', 'mountain', 'earth']
GLY.append(('yang', [0x268A], lignes([1], 8, 8, 1.6 * EP / 1.5)))
GLY.append(('yin', [0x268B], lignes([0], 8, 8, 1.6 * EP / 1.5)))
for i, bits in enumerate([[1, 1], [0, 1], [1, 0], [0, 0]]):   # 268C grand yang, 268D petit yin, 268E petit yang, 268F grand yin
    pass
# digrammes Unicode, traits du bas vers le haut : grand yang ⚌ (1,1), petit yin ⚍ (yang en bas, yin en haut), petit yang ⚎ (yin en bas, yang en haut), grand yin ⚏ (0,0)
for code, nom, bits in [(0x268C, 'greateryang', [1, 1]), (0x268D, 'lesseryin', [1, 0]),
                        (0x268E, 'lesseryang', [0, 1]), (0x268F, 'greateryin', [0, 0])]:
    GLY.append((nom, [code], lignes(bits, 5.6, 10.4, 1.5 * EP / 1.5)))
for i, t in enumerate(ORDRE_TRIG):
    GLY.append(('trigram' + NOMS_TRIG[i], [0x2630 + i], lignes(TRIG[t], 3.8, 12.2, 1.45 * EP / 1.5)))
NOMS64 = json.load(open(os.path.join(ICI, 'hexagrammes.json'), encoding='utf-8'))
for n in range(1, 65):
    h = NOMS64[str(n)]
    bits = TRIG[h['bas']] + TRIG[h['haut']]
    GLY.append(('hexagram%02d' % n, [0x4DC0 + n - 1], lignes(bits, 2.0, 14.0, H6)))

# ---------- conversion en contours ----------
CAP = {'round': pathops.LineCap.ROUND_CAP, 'butt': pathops.LineCap.BUTT_CAP}

def contours(elements):
    total = pathops.Path()
    for el in elements:
        p = pathops.Path()
        d = SVGPath(d=el[1]).absolute().arcs_to_cubics().d
        parse_path(d, TransformPen(p.getPen(), XFORM))
        if el[0] == 'trait':
            p.stroke(el[2] * U, CAP[el[3]], pathops.LineJoin.ROUND_JOIN, 4)
            p.convertConicsToQuads()
        total = pathops.op(total, p, pathops.PathOp.UNION)
    total.simplify(fix_winding=True)
    return total

def glyphe_tt(path):
    tt = TTGlyphPen(None)
    ap = AreaPen(); path.draw(ap)
    pen = Cu2QuPen(tt, max_err=1.0, reverse_direction=False)
    if ap.value > 0:              # contour extérieur dans le sens antihoraire : TrueType veut l'horaire
        path.draw(ReverseContourPen(pen))
    else:
        path.draw(pen)
    return tt.glyph()

ordre = ['.notdef', 'space']
glyphs, cmap, metrics = {}, {0x20: 'space'}, {}
nd = TTGlyphPen(None)
for c in [[(100, 0), (100, 700), (600, 700), (600, 0)], [(150, 50), (550, 50), (550, 650), (150, 650)]]:
    nd.moveTo(c[0]); [nd.lineTo(q) for q in c[1:]]; nd.closePath()
glyphs['.notdef'] = nd.glyph(); metrics['.notdef'] = (700, 100)
glyphs['space'] = TTGlyphPen(None).glyph(); metrics['space'] = (AVANCE // 2, 0)
for nom, codes, el in GLY:
    p = contours(el)
    g = glyphe_tt(p)
    glyphs[nom] = g
    ordre.append(nom)
    for c in codes:
        cmap[c] = nom
    xmin = int(p.bounds[0]) if p.bounds else 0
    metrics[nom] = (AVANCE, xmin)

fb = FontBuilder(UPM, isTTF=True)
fb.setupGlyphOrder(ordre)
fb.setupCharacterMap(cmap)
fb.setupGlyf(glyphs)
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=ASC, descent=DESC)
fb.setupNameTable({
    'familyName': FAMILLE, 'styleName': STYLE,
    'uniqueFontIdentifier': f'{FAMILLE.replace(" ", "")}-{STYLE};{VERSION}',
    'fullName': f'{FAMILLE} {STYLE}', 'psName': f'{FAMILLE.replace(" ", "")}-{STYLE}',
    'version': f'Version {VERSION}',
    'copyright': 'Copyright 2026 Rosmaryn (https://rosmaryn.app/)',
    'manufacturer': 'Rosmaryn', 'designer': 'Rosmaryn',
    'vendorURL': 'https://rosmaryn.app/', 'designerURL': 'https://library.rosmaryn.app/',
    'licenseDescription': 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org',
    'licenseInfoURL': 'https://openfontlicense.org',
})
fb.setupOS2(sTypoAscender=ASC, sTypoDescender=DESC, sTypoLineGap=200, usWinAscent=900, usWinDescent=250,
            achVendID='RSMR', fsType=0, usWeightClass={'Light': 300, 'Regular': 400, 'Bold': 700}.get(STYLE, 400))
fb.setupPost()
from fontTools.misc.timeTools import timestampNow
fb.setupHead(unitsPerEm=UPM, created=timestampNow(), modified=timestampNow(), fontRevision=float(VERSION))
chemin = os.path.join(OUT, f'{FAMILLE.replace(" ", "")}-{STYLE}.ttf')
fb.save(chemin)
json.dump([{'nom': n, 'codes': ['%04X' % c for c in cs]} for n, cs, _ in GLY],
          open(os.path.join(OUT, 'repertoire.json'), 'w'), ensure_ascii=False, indent=0)
print('police', chemin, len(GLY), 'glyphes,', len(cmap) - 1, 'codes')
