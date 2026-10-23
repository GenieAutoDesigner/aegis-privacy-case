"""Genera presentacion/AEGIS_Presentacion_Aportantes.pdf (A4 apaisado).
Uso: python3 build_pdf.py [DIRECCION_WALLET]
"""
import sys, os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMG = os.path.join(ROOT, "assets", "img")
OUT = os.path.join(HERE, "AEGIS_Presentacion_Aportantes.pdf")
WALLET = sys.argv[1] if len(sys.argv) > 1 else "0x7584FD9cAf0c2F5D2c9BFEEA06A750010ce3A7A1"
REPO = "github.com/GenieAutoDesigner/aegis-privacy-case"
if len(sys.argv) > 2:
    REPO = sys.argv[2]

pdfmetrics.registerFont(TTFont("S", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("SB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("SL", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
pdfmetrics.registerFont(TTFont("M", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))

W, H = landscape(A4)
BG = HexColor("#0E1012"); PANEL = HexColor("#171A1E"); LINE = HexColor("#2A2F36")
TXT = HexColor("#E8EAED"); MUTED = HexColor("#9AA3AD"); GREEN = HexColor("#3DDC84")
RED = HexColor("#FF5A4F"); AMBER = HexColor("#F2B84B")
M = 42  # margen

def para(text, size=11, color=TXT, font="S", lead=None):
    return ParagraphStyle("p", fontName=font, fontSize=size, leading=lead or size * 1.42,
                          textColor=color)

def P(c, text, x, y_top, w, size=11, color=TXT, font="S", lead=None):
    p = Paragraph(text, para(text, size, color, font, lead))
    _, h = p.wrap(w, 1000)
    p.drawOn(c, x, y_top - h)
    return y_top - h

def frame(c, n, total, kicker):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(GREEN); c.rect(0, H - 4, W * n / total, 4, fill=1, stroke=0)
    c.setFont("M", 8.5); c.setFillColor(MUTED)
    c.drawString(M, H - 28, kicker.upper())
    c.drawRightString(W - M, H - 28, f"AEGIS  ·  {n:02d}/{total:02d}")
    c.setStrokeColor(LINE); c.line(M, 30, W - M, 30)
    c.setFont("S", 7.5)
    c.drawString(M, 18, "Proyecto personal independiente · Documento público para aportantes · Octubre 2026")
    c.drawRightString(W - M, 18, REPO)

def title(c, t, y=H - 70, size=28):
    c.setFont("SB", size); c.setFillColor(TXT); c.drawString(M, y, t)
    return y

def box(c, x, y, w, h, color=PANEL, border=LINE):
    c.setFillColor(color); c.setStrokeColor(border); c.roundRect(x, y, w, h, 8, fill=1, stroke=1)

def img(c, name, x, y, w, h):
    ir = ImageReader(os.path.join(IMG, name)); iw, ih = ir.getSize()
    s = min(w / iw, h / ih); dw, dh = iw * s, ih * s
    c.drawImage(ir, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh)
    return dw, dh

def tag(c, x, y, text, color):
    c.setFont("SB", 8); tw = c.stringWidth(text, "SB", 8) + 14
    c.setFillColor(color); c.roundRect(x, y, tw, 15, 7, fill=1, stroke=0)
    c.setFillColor(BG); c.drawString(x + 7, y + 4.3, text)
    return tw

TOTAL = 10
c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("AEGIS — Privacidad física para tu teléfono")
c.setAuthor("AEGIS"); c.setCreator("AEGIS")
c.setSubject("Presentación del proyecto AEGIS para aportantes")

# 1 PORTADA ----------------------------------------------------------------
frame(c, 1, TOTAL, "Campaña de crowdfunding")
c.setFont("SB", 64); c.setFillColor(TXT); c.drawString(M, H - 140, "AEGIS")
P(c, "Privacidad física para tu teléfono.<br/>Un deslizador. Sin software. Sin confiar en nadie.",
  M, H - 160, 380, 19, TXT, "S", 27)
P(c, "Una funda para iPhone 15 Pro que, con un único movimiento lateral, tapa las cámaras, "
     "cierra micrófonos y altavoces y busca atenuar las señales inalámbricas. "
     "Hoy es un concepto con CAD propio y un estudio técnico externo pagado. "
     "Con <b>6.000 €</b> se financia la fase de prototipo funcional.",
  M, H - 245, 370, 11.5, MUTED)
box(c, M, 70, 370, 80)
c.setFont("M", 9); c.setFillColor(GREEN); c.drawString(M + 16, 128, "OBJETIVO DE ESTA FASE")
c.setFont("SB", 30); c.setFillColor(TXT); c.drawString(M + 16, 88, "6.000 €")
P(c, "600 personas × 10 € ya lo consiguen.", M + 160, 116, 200, 11, MUTED)
img(c, "concepto_online_offline.jpg", 430, 60, W - 430 - M, H - 120)
c.setFont("S", 7.5); c.setFillColor(MUTED)
c.drawRightString(W - M, 50, "Imagen conceptual generada con IA para comunicar la idea. No es el producto final.")
c.showPage()

# 2 PROBLEMA ---------------------------------------------------------------
frame(c, 2, TOTAL, "El problema")
title(c, "Tu teléfono te ve, te oye y te localiza.")
P(c, "Los interruptores de privacidad actuales son de software: confías en que el sistema operativo, "
     "las apps y el fabricante hagan lo que dicen. Las alternativas físicas existen, pero se usan poco "
     "porque son incómodas: pegatinas, bolsas Faraday en las que el teléfono deja de ser utilizable, "
     "o accesorios sueltos que se pierden.", M, H - 90, W - 2 * M, 12.5, MUTED)
cards = [("Cámaras", "Trasera y frontal. Un fallo o un malware puede activarlas sin aviso.", RED),
         ("Micrófonos", "Siempre abiertos físicamente. El «LED» de uso es software.", RED),
         ("Radio", "Móvil, WiFi, Bluetooth, UWB: el teléfono se localiza aunque no lo uses.", RED),
         ("Lo que falta", "Algo que lleves siempre puesto y que corte todo con un gesto comprobable a simple vista.", GREEN)]
cw = (W - 2 * M - 3 * 14) / 4
for i, (t, d, col) in enumerate(cards):
    x = M + i * (cw + 14)
    box(c, x, 70, cw, 250)
    c.setFillColor(col); c.rect(x + 16, 290, 26, 4, fill=1, stroke=0)
    c.setFont("SB", 16); c.setFillColor(TXT); c.drawString(x + 16, 262, t)
    P(c, d, x + 16, 246, cw - 32, 11.5, MUTED)
c.showPage()

# 3 LA IDEA ----------------------------------------------------------------
frame(c, 3, TOTAL, "La idea")
title(c, "Un único deslizador lateral. Dos estados.")
y = P(c, "Desplazas el deslizador y la funda pasa de ONLINE a OFFLINE. Todo es mecánico: no hay batería, "
         "ni electrónica, ni app. Lo que ves es lo que hay.", M, H - 90, 330, 12, MUTED)
rows = [("ONLINE", GREEN, ["Cámaras y micrófonos libres", "Altavoces, botones y USB-C accesibles", "Aspecto de funda normal"]),
        ("OFFLINE", RED, ["Cubrecámaras trasero y frontal cerrados", "Entradas de micrófono y salidas de altavoz cerradas",
                          "Envolvente conductora para atenuar radio (objetivo a validar por ensayo)"])]
yy = y - 26
for name, col, items in rows:
    tag(c, M, yy, name, col); yy -= 10
    for it in items:
        yy = P(c, "• " + it, M + 6, yy - 4, 320, 11, TXT)
    yy -= 22
for k,(nm,lab,col) in enumerate([("cad_v3_online_iso_trasera_sup.jpg","ONLINE",GREEN),("cad_v3_offline_iso_trasera_sup.jpg","OFFLINE",RED)]):
    x0 = 395 + k * 210
    box(c, x0, 62, 200, H - 150)
    img(c, nm, x0 + 6, 90, 188, H - 186)
    c.setFont("SB", 10); c.setFillColor(col); c.drawCentredString(x0 + 100, 72, lab)
c.setFont("S", 7.5); c.setFillColor(MUTED)
c.drawRightString(W - M, 40, "Renders del CAD conceptual V3 del autor (vista exterior).")
c.showPage()

# 4 ESTADO REAL ------------------------------------------------------------
frame(c, 4, TOTAL, "Dónde está el proyecto hoy")
title(c, "Estado real, sin maquillaje.")
P(c, "Prefiero que aportes sabiendo exactamente qué hay y qué falta.", M, H - 90, W - 2 * M, 12, MUTED)
colw = (W - 2 * M - 28) / 3
blocks = [
    ("HECHO", GREEN, [
        "Definición completa del producto y de los dos modos de uso.",
        "CAD conceptual propio en Fusion 360 (varias iteraciones) con barrido de interferencias.",
        "Acuerdo de confidencialidad firmado con un estudio de ingeniería de fabricación aditiva.",
        "Estudio técnico inicial encargado y pagado por mí.",
        "Todo el diseño publicado como hardware abierto (CERN-OHL-S-2.0): CAD, planos y documentación."]),
    ("LO QUE DIJO EL ESTUDIO", AMBER, [
        "El concepto merece una fase de desarrollo.",
        "El CAD actual sirve para comunicar la idea, pero no es fabricable tal cual: la arquitectura mecánica debe rediseñarse desde cero.",
        "El bloqueo de radio es una hipótesis: necesita material conductor, continuidad eléctrica y ensayos.",
        "Accionarlo todo con un solo deslizador es un objetivo a validar, no una garantía."]),
    ("LO QUE FALTA", RED, [
        "Nueva arquitectura mecánica y prototipos físicos (Hito 1).",
        "Integración del modo OFFLINE y MVP demostrable (Hito 2).",
        "Ensayos de atenuación de radio y acústica.",
        "Industrialización (fase posterior, fuera de este objetivo)."])]
for i, (t, col, items) in enumerate(blocks):
    x = M + i * (colw + 14)
    box(c, x, 50, colw, H - 160)
    tag(c, x + 14, H - 140, t, col)
    yy = H - 152
    for it in items:
        yy = P(c, "• " + it, x + 14, yy - 6, colw - 28, 10.5, TXT) - 4
c.showPage()

# 5 PLAN -------------------------------------------------------------------
frame(c, 5, TOTAL, "Plan de desarrollo")
title(c, "Por hitos, con decisión en cada paso.")
P(c, "El estudio externo propone avanzar por hitos. Cada uno termina con una revisión: si el resultado "
     "no es suficiente, se ajusta o se para antes de gastar más.", M, H - 90, W - 2 * M, 12, MUTED)
steps = [("HITO 1", "Núcleo mecánico", "Nueva arquitectura, CAD de validación y hasta 5 prototipos impresos para probar apertura, cierre, guiado y fuerza.", "Demostrador mecánico"),
         ("HITO 2", "Modo OFFLINE + MVP", "Integración en el volumen de la funda, ajustes de material y montaje, hasta 5 prototipos más.", "MVP demostrable"),
         ("ENSAYOS", "Radio y acústica", "Materiales conductores, juntas y medidas básicas de atenuación. No incluido en la propuesta del estudio.", "Datos medidos"),
         ("DESPUÉS", "Industrialización", "Solo si el MVP funciona y hay interés real. Se presupuestará aparte.", "Fuera de este objetivo")]
sw = (W - 2 * M - 3 * 14) / 4
for i, (k, t, d, out) in enumerate(steps):
    x = M + i * (sw + 14)
    box(c, x, 70, sw, 290)
    c.setFont("M", 9); c.setFillColor(GREEN if i < 3 else MUTED); c.drawString(x + 16, 334, k)
    c.setFont("SB", 12.5); c.setFillColor(TXT); c.drawString(x + 16, 310, t)
    P(c, d, x + 16, 294, sw - 32, 10.5, MUTED)
    c.setStrokeColor(LINE); c.line(x + 16, 112, x + sw - 16, 112)
    c.setFont("S", 8); c.setFillColor(MUTED); c.drawString(x + 16, 96, "RESULTADO")
    c.setFont("SB", 10.5); c.setFillColor(TXT); c.drawString(x + 16, 80, out)
c.showPage()

# 6 PRESUPUESTO ------------------------------------------------------------
frame(c, 6, TOTAL, "En qué se usa el dinero")
title(c, "Presupuesto: 6.000 €")
P(c, "Cifras de la propuesta técnica y comercial recibida (oct. 2026), con IVA (21 %) añadido para que "
     "sea el coste real. Las cifras de la reserva son estimaciones mías.", M, H - 90, 420, 11, MUTED)
data = [["Concepto", "Base", "Con IVA"],
        ["Estudio técnico inicial  (ya pagado por mí)", "100,00 €", "121,00 €"],
        ["Hito 1 · diseño 30 h + prototipado", "1.450,00 €", "1.754,50 €"],
        ["Hito 2 · diseño 50 h + prototipado", "2.200,00 €", "2.662,00 €"],
        ["Subtotal desarrollo financiado (Hitos 1 y 2)", "3.650,00 €", "4.416,50 €"],
        ["Reserva: materiales conductores, juntas, ensayo básico de radio,\ncomisiones de cambio cripto→€ e imprevistos (estimación)", "—", "1.583,50 €"],
        ["OBJETIVO", "", "6.000,00 €"]]
t = Table(data, colWidths=[310, 80, 85])
t.setStyle(TableStyle([
    ("FONT", (0, 0), (-1, -1), "S", 9.5), ("FONT", (0, 0), (-1, 0), "SB", 9),
    ("FONT", (0, -1), (-1, -1), "SB", 11), ("FONT", (0, 4), (-1, 4), "SB", 9.5),
    ("TEXTCOLOR", (0, 0), (-1, -1), TXT), ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
    ("TEXTCOLOR", (0, 1), (-1, 1), MUTED), ("TEXTCOLOR", (0, -1), (-1, -1), GREEN),
    ("ALIGN", (1, 0), (-1, -1), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LINEBELOW", (0, 0), (-1, -2), 0.5, LINE), ("LINEABOVE", (0, -1), (-1, -1), 1, GREEN),
    ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
tw, th = t.wrap(0, 0); t.drawOn(c, M, H - 145 - th)
bx = M + 500
box(c, bx, 60, W - M - bx, H - 170)
c.setFont("M", 9); c.setFillColor(GREEN); c.drawString(bx + 16, H - 140, "REGLAS DEL DINERO")
yy = H - 152
for it in ["Todo lo aportado se destina íntegramente al desarrollo de AEGIS.",
           "Iré publicando en el repositorio los pagos hechos y los resultados de cada hito.",
           "Si se supera el objetivo, el exceso va a ensayos de radio/acústica y a adaptar el diseño a otros modelos.",
           "El estudio inicial (121 €) lo he pagado yo y no cuenta como gasto a cubrir."]:
    yy = P(c, "• " + it, bx + 16, yy - 6, W - M - bx - 32, 10.5, TXT) - 4
c.showPage()

# 7 COMO APORTAR -----------------------------------------------------------
frame(c, 7, TOTAL, "Crowdfunding · cómo aportar")
title(c, "10 € y compartirlo ya es mucho.")
P(c, "Con 600 personas aportando 10 € se cubre la fase entera. Si aportas y lo compartes con dos personas "
     "a las que les importe la privacidad, entre muy pocos lo conseguimos.", M, H - 90, 420, 12.5, MUTED)
OFF7 = 60
box(c, M, 70 + OFF7, 430, 230)
c.setFont("M", 9); c.setFillColor(GREEN); c.drawString(M + 16, 278 + OFF7, "APORTACIÓN EN CRIPTOMONEDAS (MetaMask)")
c.setFont("S", 9.5); c.setFillColor(MUTED); c.drawString(M + 16, 256 + OFF7, "Dirección (redes EVM):")
c.setFont("M", 9.6 if len(WALLET) <= 44 else 8); c.setFillColor(TXT); c.drawString(M + 16, 236 + OFF7, WALLET)
yy = P(c, "• Recomendado: <b>USDC</b> o <b>USDT</b> en Polygon, Base o Arbitrum (comisiones de céntimos). "
          "En la red principal de Ethereum la comisión puede comerse una aportación de 10 €.<br/>"
          "• Solo redes compatibles con Ethereum (EVM). Enviar desde otra red (Bitcoin, Tron, Solana…) "
          "a esta dirección hace que los fondos se pierdan.<br/>"
          "• Comprueba los primeros y últimos caracteres de la dirección antes de enviar.",
       M + 16, 222 + OFF7, 398, 9.5, TXT)
bx = M + 450
box(c, bx, 70 + OFF7, W - M - bx, 230)
c.setFont("M", 9); c.setFillColor(GREEN); c.drawString(bx + 16, 278 + OFF7, "SI NO PUEDES APORTAR")
P(c, "• Comparte el repositorio o este PDF.<br/>"
     "• Dale una estrella en GitHub: ayuda a que lo vea más gente.<br/>"
     "• Si sabes de mecanismos, materiales conductores o ensayos de radio, abre un issue con tu idea.",
  bx + 16, 266 + OFF7, W - M - bx - 32, 10.5, TXT)
c.setFont("S", 9); c.setFillColor(MUTED)
c.drawString(M, 100, "¿Quieres aportar o colaborar? Contacta conmigo abriendo un issue en el repositorio de GitHub y te respondo con los detalles.")
c.showPage()

# 8 COMPROMISOS ------------------------------------------------------------
frame(c, 8, TOTAL, "Compromisos y contacto")
title(c, "Lo que prometo y lo que no.")
colw = (W - 2 * M - 14) / 2
box(c, M, 60, colw, H - 160)
tag(c, M + 16, H - 128, "ME COMPROMETO A", GREEN)
yy = H - 140
for it in ["Invertir todo el dinero recibido en el desarrollo de AEGIS.",
           "Leer los comentarios y mensajes que dejéis en GitHub (issues y discusiones del repositorio).",
           "Publicar avances, gastos y resultados de cada hito, también los negativos.",
           "Contar con honestidad lo que funcione y lo que no."]:
    yy = P(c, "• " + it, M + 16, yy - 6, colw - 32, 11, TXT) - 4
bx = M + colw + 14
box(c, bx, 60, colw, H - 160)
tag(c, bx + 16, H - 128, "NO PUEDO PROMETER", AMBER)
yy = H - 140
for it in ["Un plazo concreto de respuesta a los comentarios: es un proyecto personal y respondo cuando puedo.",
           "Que el prototipo funcione a la primera, ni el nivel de bloqueo de radio antes de medirlo.",
           "Fechas de entrega cerradas.",
           "Ninguna rentabilidad: esto es una aportación voluntaria, no una inversión con retorno, "
           "ni una preventa, ni da derechos sobre el proyecto."]:
    yy = P(c, "• " + it, bx + 16, yy - 6, colw - 32, 11, TXT) - 4
c.showPage()

# 9 FUTURO -----------------------------------------------------------------
frame(c, 9, TOTAL, "Más allá del iPhone 15 Pro")
title(c, "Un modelo primero. Después, todos los posibles.")
P(c, "Está claro que esta fase es solo para un modelo de teléfono: el iPhone 15 Pro. Es la forma "
     "realista de llegar a algo que funcione de verdad.<br/><br/>"
     "Si funciona, y se vende o lo usa gente que lo quiere y lo apoya, el diseño se trasladará a todos los "
     "modelos nuevos que sea posible. La arquitectura se está pensando para que el núcleo mecánico "
     "pueda adaptarse a otras carcasas.<br/><br/>Y como el diseño es abierto, cualquiera puede adaptarlo, auditarlo o mejorarlo.", M, H - 95, 430, 13, MUTED, "S", 20)
img(c, "cad_v3_offline_iso_frontal.jpg", 500, 50, W - 500 - M, H - 150)
c.showPage()

# 10 AVISO + ENGLISH ---------------------------------------------------------
frame(c, 10, TOTAL, "Aviso / English summary")
title(c, "Aviso", size=20, y=H - 66)
P(c, "AEGIS es un proyecto personal en fase de desarrollo. Las imágenes son conceptuales o del CAD conceptual "
     "y no representan el producto final. Ninguna prestación (bloqueo de cámaras, sellado acústico, atenuación de "
     "radio) está validada todavía mediante ensayo. Este documento no reproduce documentación de terceros: las "
     "cifras proceden de una propuesta recibida y se resumen sin datos de la empresa ni datos personales. "
     "Las aportaciones son voluntarias y sin contraprestación. "
     "Licencias: hardware CERN-OHL-S-2.0; documentación e imágenes CC BY-SA 4.0.", M, H - 80, W - 2 * M, 10, MUTED)
title(c, "English summary", size=20, y=H - 200)
P(c, "AEGIS is a 3D-printed iPhone 15 Pro case where a single side slider physically covers the rear and front "
     "cameras, closes the microphone and speaker ports and aims to attenuate radio signals through a conductive "
     "enclosure — no battery, no software. Today it is a concept with its own CAD and a paid external engineering "
     "review, which concluded the concept deserves development. The full design (CAD, drawings, reports) is open hardware under CERN-OHL-S-2.0. The review also found that the mechanism must be redesigned from scratch "
     "and RF blocking must be proven by testing. The goal is <b>€6,000</b> to fund two prototyping milestones "
     "(€4,416.50 incl. VAT) plus materials and basic RF testing. Donations in crypto to the EVM address on page 7 "
     "(USDC/USDT on Polygon, Base or Arbitrum recommended). Every euro goes to the project; I read GitHub issues "
     "and discussions but cannot promise response times. Donations are voluntary, with no financial return. "
     "If it works, it will be ported to as many new phone models as possible.",
  M, H - 214, W - 2 * M, 10.5, TXT)
c.showPage()
c.save()
print(OUT)
