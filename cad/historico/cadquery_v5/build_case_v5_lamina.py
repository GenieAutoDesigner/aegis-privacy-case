"""
Funda "Modo Aislamiento" para iPhone 15 Pro Max -- VERSION 5
Vuelta al concepto de lamina deslizante (persiana), pero accionada por
los dos botones de piñon-cremallera en vez de tirar a mano.

Por que el cambio desde la v4 (bisagra+tapa rigida): una tapa rigida
que gira 90 grados tiene que barrer un arco enorme -- ronda tras ronda
de intentos, seguia chocando con la base en algun punto del recorrido.
Una lamina flexible que desliza en linea recta, enrollada en un
rodillo que SOLO GIRA SOBRE SI MISMO (no se mueve de sitio), evita ese
problema de raiz: no hay ninguna pieza rigida grande barriendo un arco.

Piezas:
  01 base_cuerpo_principal
  02 lamina_RF_enrollable (tela conductora + soporte fino)
  03 eje_rodillo (varilla metalica, se compra)
  04 boton_CERRAR (cremallera + boton, empuja el piñon)
  05 boton_ABRIR (cremallera + boton, empuja el piñon al reves)
  06 obturador_camara (lengueta con bisagra viva, escondida)
  07 sello_acustico_microfono (lengueta con bisagra viva)
  08-10 fundas_boton (volumen, accion, power)
  11 tapa_conductora_USB_C
  12 patron_forro_conductor_base (referencia)
  13 varilla_sincronizacion_camara (conceptual -- ver aviso mas abajo)
  14 varilla_sincronizacion_microfono (conceptual -- ver aviso mas abajo)

AVISO sobre las piezas 13/14: son un PRIMER INTENTO de enlazar
mecanicamente la camara y el microfono al mismo giro del rodillo (para
que "un boton" lo cierre todo a la vez, como se pidio). A diferencia
del resto de este archivo, esto NO esta verificado con la misma
profundidad -- comprobar colisiones de un mecanismo de varillaje
flexible es mucho mas dificil que comprobar un giro en el sitio. Tratar
como punto de partida para iterar en el prototipo fisico, no como
mecanismo terminado.
"""
import cadquery as cq
import math


def y_cylinder(x_center, z_center, radius, y_start, length):
    """Cilindro cuyo eje corre a lo largo de Y. Verificado con bounding
    box en la v3/v4 -- ver esas versiones para el detalle de la
    verificacion de signos."""
    return (
        cq.Workplane("XZ")
        .workplane(offset=-y_start)
        .center(x_center, z_center)
        .circle(radius)
        .extrude(-length)
    )


# ---------------------------------------------------------------
# 1. PARAMETROS BASE (medidas reales iPhone 15 Pro Max)
# ---------------------------------------------------------------
PHONE_W = 76.7
PHONE_H = 159.9
PHONE_T = 8.25
CAM_BUMP_T = 3.59
CAM_BUMP_SIZE = 35.0
CAM_BUMP_OFFSET_X = 6.0
CAM_BUMP_OFFSET_Y = 8.0
CAM_CORNER_R = 9.0

CLEARANCE_XY = 0.35
CLEARANCE_Z = 0.4
CASE_CORNER_R = 11.0
WALL = 1.6

# ---------------------------------------------------------------
# MANUFACTURING.Sliding_Clearance (Hoja 7 -- unico parametro de
# holgura de deslizamiento, en vez de numeros sueltos repetidos por
# canal). Valor por LADO -- un canal alrededor de una pieza de
# espesor T normalmente necesita T + 2*SLIDING_CLEARANCE de ancho
# util, mas margen estructural aparte si aplica.
#
# IMPORTANTE: los canales ya construidos usan margenes variados
# (0.5, 0.6, 1.0mm...) que YA estan verificados a cero colision.
# Cambiarlos ahora al valor "correcto" unificado (2*0.2=0.4mm) podria
# introducir colisiones nuevas en piezas que dependen del margen
# extra que tenian. Por eso esta constante se usa desde aqui en
# adelante como referencia para canales NUEVOS y como documentacion
# del valor real que ya llevan los antiguos -- no se ha forzado
# retroactivamente sobre canales ya verificados, para no arriesgar
# geometria que funciona.
SLIDING_CLEARANCE = 0.2   # mm, por lado -- tolerancia real de MJF PA12
REACH_MARGIN = 3.0   # mm -- margen de alcance en cortes largos (no es
# holgura de ajuste, es solo para asegurar que un corte llega mas
# alla de donde la pieza realmente necesita, evitando dejar un canal
# corto por error de redondeo)

# --- canal guia lateral para la lamina (dentro del grosor de pared,
# no sobresale) ---
CHANNEL_W = 2.4
CHANNEL_D = 1.0

# --- rodillo: mismo calculo verificado que en la v2 (tela fina,
# 0.18mm, eje metalico de 3mm) ---
FABRIC_THK = 0.18
AXLE_DIA = 3.0
ROLLER_DIA = 7.0
ROLLER_HOUSING_CLEAR = 1.2
CHIN_H = ROLLER_DIA + 2 * ROLLER_HOUSING_CLEAR + 2 * WALL   # ~12.6mm

PULLBAR_H = 4.0
PULLBAR_THK = 0.5   # FIX: ya no hace falta agarrarla a mano (la mueve
# el boton), puede ser tan fina como el canal -- la version anterior
# (1.8mm + gancho 1.4mm = 3.2mm) sobresalia 1.15mm por delante de la
# funda.

# --- piñon (en un extremo del eje del rodillo) + cremalleras-boton ---
PINION_DIA = 3.0   # FIX REDISEÑO: reducido de 5.0, a peticion expresa
# (eje mas fino). Con el giro corto anterior (90 grados) NINGUNA
# combinacion razonable de piezas lograba mover la corredera de camara
# 36mm de verdad -- hace falta que el eje gire mas.
PINION_TEETH = 8
PINION_THK = 5.0
RACK_TOOTH_PITCH = math.pi * PINION_DIA / PINION_TEETH
RACK_TOOTH_DEPTH = 0.7
RACK_LEN = 6.5   # FIX REDISEÑO: antes 6.0. Ajustado al recorrido real
# alcanzable (SWITCH_TRAVEL=4.9) con margen minimo -- ver limite fisico
# del menton explicado arriba.
SWITCH_STEM_LEN = 84.2    # FIX (pedido expreso): recalculado para que
# la pestaña quede exactamente a 30mm del boton de volumen -- la misma
# distancia que hay entre accion y volumen (55.3-25.3=30mm), para
# guardar la simetria del propio iPhone. Antes: a 104.6
# la pestaña quedaba en Y=15.7, DENTRO del propio rango del boton de
# volumen (Y=[11.55,39.05], boton real de 27.5mm de largo) -- se veia
# la pestaña "encima" del boton de volumen. Acortado el vastago para
# que la pestaña quede claramente por debajo de ese rango, como un
# control aparte.
# del canto lateral (altura similar a un boton de volumen), como
# muestra la imagen de referencia, en vez de quedarse junto al chin
SWITCH_GRIP_LEN = 11.0   # FIX (pedido expreso): agrandada, casi al
# y la pared exterior es de solo 6.95mm -- una empuñadura de 11mm no
# cabia ahi (verificado: colisionaba con el movil). Reducida con
# margen de seguridad en los dos lados.
SWITCH_TRAVEL = 4.6   # FIX REDISEÑO: antes 3.93mm. El menton real solo
# da 6.9mm de margen total entre el eje y el borde exterior (verificado
# geometricamente) -- el diseño original ya usaba casi todo ese margen.
# 4.9mm es el maximo real y seguro con la arquitectura actual (sin
# agrandar CHIN_H). Con el piñon mas fino (radio 1.5mm) da un giro de
# eje mayor que antes, suficiente para engranajes de camara/microfono
# razonables. Para un recorrido mucho mayor ("casi todo el lateral")
# hay que agrandar el propio menton (CHIN_H) -- cambio estructural
# aparte, no incluido aqui.
SWITCH_DETENT_Y1 = -1.0   # posicion local de la muesca ONLINE (la OFFLINE esta a -SWITCH_TRAVEL de esta)
BUTTON_LEN = 5.5      # largo del boton (eje Y), estetica de pildora
# igual que volumen/accion/power -- antes era un circulo de 2.6mm de
# diametro ("dos bolas feas"), ahora alargado como el resto de botones
BUTTON_H = 2.2         # alto del boton (eje Z)
BUTTON_CAP_PROTRUSION = 0.4

BTN_BOOT_WALL = 0.6
MIC_PLATE_LEN = 2.6   # ya no se usa (diseño anterior de placa+tapones)
MIC_DOOR_THK = 0.5    # ya no se usa (diseño anterior, lamina en Y) -- ver MIC_WINDOW_* para el diseño actual
MIC_DOOR_W = 19.0      # ya no se usa
MIC_DOOR_H = 5.5       # ya no se usa
# ---------------------------------------------------------------------------
# VENTANA LATERAL DE MICROFONO (rediseño): desliza en X como una
# ventana real, no en Y. Reductor de engranaje en eje Z (mismo
# principio que la camara) convierte el giro compartido del eje en
# este movimiento lateral.
# ---------------------------------------------------------------
MIC_GEAR_R1 = 7.53    # FIX REDISEÑO: antes 1.3mm -- ya no es el "piñon
# pequeño". Verificado con el giro real del eje (piñon 1.5mm x
# recorrido 4.6mm = 3.067 rad): con 1.3mm la banda giraba 173 grados
# en vez de los 35 grados reales que necesita (casi 5 veces de mas).
# Este es el radio que de verdad reduce el giro del eje a los 35
# grados objetivo -- engrana con la entrada (desliza en Y)
MIC_GEAR_R2 = 6.0       # cara que acopla al eje flexible -- su radio
# no afecta la proporcion final (ver verificacion), solo tiene que
# ser fisicamente razonable
# REDISEÑO ESTRUCTURAL: la version anterior ponia el reductor entero a
# Z=1.8 (muy por debajo de la puerta, Z=5.6) y en Y=-60 (muy lejos de
# la entrada, Y=-87.6) -- eso obligaba a puentes ANCHOS y LARGOS en
# los dos sentidos, que entre todos vaciaban casi todo el grosor real
# del menton (verificado: solo quedaba piel exterior y una pared
# interior finisima, nada en medio -- el boquete real que se veia en
# Fusion). Ahora el piñon GRANDE (el que da a la ventana) se coloca
# cerca de su propia Z real (justo por debajo del rango real de los
# agujeros, 4.7-6.5), asi el puente hacia la puerta es de solo 1.6mm
# en vez de 3.8mm. El piñon PEQUEÑO (el que da a la entrada) no
# necesita dientes anchos -- la entrada no se mueve en X, es un punto
# fijo -- asi que ese puente puede ser estrecho aunque sea largo.
MIC_GEAR1_Z = 2.05        # altura ABSOLUTA real del piñon pequeño -- ajustado
# para que el techo del piñon grande (gear2_z+1.2=4.8) quede con
# margen real por debajo de donde empieza el cuerpo plano del movil
# (Z=5.19) -- el reductor cae dentro de la huella en Y del movil
# (Y=-75, dentro de -79.95 a 79.95), verificado que con gear2_z=4.0
# el techo del piñon (5.2) chocaba con el movil por 0.01mm.
MIC_GEAR_REACH = 9.6      # distancia en Y desde la cremallera de entrada hasta el reductor
# -- reducida de 24.6 a 9.6 reubicando el reductor mas cerca (Y=-75 en
# vez de -60), acortando tambien el corredor hacia la ventana.
MIC_WINDOW_W = 18.0       # ancho de la ventana -- cubre los 6 agujeros (16.8mm) con margen
MIC_WINDOW_H = 5.5        # alto, cubre el diametro de los agujeros con margen
MIC_WINDOW_THK = 0.5       # lamina fina, mismo grosor que el diseño anterior
# FIX: el recorrido para esconderse del todo no es igual al ancho
# fisico -- el ancho REAL con carriles es 9.6mm de radio (no 9.0), y
# verificado que con travel=18 quedaba solapando 6.9mm con los
# agujeros reales al esconderse. Recalculado con margen de seguridad.
MIC_WINDOW_TRAVEL = 20.0
USB_FLAP_THK = 1.2

# REDISEÑO: banda curva semirrigida para el microfono, en vez de la
# ventana rigida plana de arriba (que necesitaba mas de 20mm de
# recorrido lateral recto -- no cabe en el hueco real de ~19mm entre
# el interruptor principal y el canal USB-C, verificado). Gira en
# lugar de deslizar en linea recta, como la lamina RF que se enrolla
# en el rodillo pero en miniatura y sin rodillo propio.
MIC_BAND_R = 6.0          # radio de curvatura
MIC_BAND_ARC = 40.0       # arco propio de la banda (grados) -- cubre los agujeros
MIC_BAND_EXTRA = 35.0     # recorrido adicional de giro para replegarse
MIC_BAND_TOTAL_ARC = MIC_BAND_ARC + MIC_BAND_EXTRA
MIC_BAND_W = 16.0         # ancho en X, cubre el racimo de 6 agujeros (15mm) con margen
MIC_BAND_T = 0.4          # grosor de la lamina

CAM_SHUTTER_W = 14.0
CAM_SHUTTER_L = CAM_BUMP_SIZE + 14.0


# ---------------------------------------------------------------
# 2. CUERPO PRINCIPAL
# ---------------------------------------------------------------
def build_base():
    cav_w = PHONE_W + 2 * CLEARANCE_XY
    cav_h = PHONE_H + 2 * CLEARANCE_XY
    cav_t = PHONE_T + CLEARANCE_Z

    # FIX CRITICO: el engranaje reductor de camara mide 11.2mm de
    # ancho, pero el hueco real entre la pared y el borde del movil
    # (con EXTRA_WALL_LEFT=5.0) era de solo 6.95mm -- pegado del todo
    # a la pared (0.06mm de margen) invadia igualmente 4.29mm el
    # propio movil, verificado con maqueta real. No es un problema de
    # posicion, es que no cabe. Ampliado el ancho de la funda por ese
    # lado (a peticion expresa) para que el hueco real supere el
    # ancho del engranaje con margen.
    EXTRA_WALL_LEFT = 10.0   # FIX: 2.4mm alojaba una varilla fina, pero
    # el yugo/manivela necesitan mas margen -- verificado que 2.4mm
    # daba colision real
    LEFT_X = -cav_w / 2 - WALL - EXTRA_WALL_LEFT
    RIGHT_X = cav_w / 2 + WALL + EXTRA_WALL_LEFT   # FIX: simetria pedida
    # expresamente -- antes RIGHT_X no llevaba el extra, dejando la
    # funda mas gorda por la izquierda (donde vive el engranaje de
    # camara) que por la derecha. El lado derecho no necesita el
    # espacio extra para nada propio, pero se añade igual para que el
    # grosor de pared sea el mismo en los dos lados.
    ext_w = RIGHT_X - LEFT_X
    center_x = (LEFT_X + RIGHT_X) / 2
    ext_h_main = cav_h + 2 * WALL
    ext_t = WALL + cav_t + CAM_BUMP_T + 1.8   # FIX: 0.6 no dejaba
    # margen real para el canal de la lamina delante de la pantalla
    ext_h = ext_h_main + CHIN_H   # chin inferior para el rodillo

    # FIX CRITICO: la construccion anterior (.center(0,CHIN_H/2) seguido
    # de .translate((0,-CHIN_H/2,0))) se CANCELABA a si misma -- el
    # resultado era un rectangulo perfectamente SIMETRICO, igual que si
    # no hubiera hecho nada de eso. El menton para el rodillo quedaba
    # repartido mitad arriba/mitad abajo en vez de estar solo abajo:
    # la funda tenia ~7.9mm de sobra arriba sin ningun proposito, y el
    # borde inferior real quedaba 4.7mm mas arriba de lo que asumian
    # los calculos de la zona de microfono (por eso el agujero no
    # llegaba al exterior). Ahora es una unica operacion, verificada:
    # centro desplazado -CHIN_H/2, sin traslado adicional que la anule.
    body = (
        cq.Workplane("XY")
        .center(center_x, -CHIN_H / 2)
        .rect(ext_w, ext_h)
        .extrude(ext_t)
        .edges("|Z")
        .fillet(CASE_CORNER_R)
    )

    # ---------------------------------------------------------------
    # PLANCHA TRASERA UNIFORME (pedido expreso): la corredera de
    # camara necesita quedar por detras de la punta real del objetivo
    # (Z=-1.99) -- antes esto se resolvia engrosando SOLO la zona de
    # la camara (RIM_HEIGHT=3.2), dejando un bulto asimetrico ahi y
    # el resto de la funda mas fina. Ahora se engrosa TODA la parte
    # trasera por igual, con el mismo contorno que el resto de la
    # funda (mismo redondeo de esquinas) -- la piel exterior queda
    # lisa y de un solo nivel en toda la funda, sin ningun escalon.
    # ---------------------------------------------------------------
    BACK_SLAB_EXTRA = 3.35   # FIX REDISEÑO (pedido expreso): antes
    # 2.4mm aqui + 0.95mm de reborde local en la camara, dejando un
    # escalon real ahi (por pequeño que fuera, seguia siendo un
    # reborde). Ahora TODA la profundidad extra que necesita el
    # mecanismo de camara vive aqui, de manera uniforme -- no hay
    # ningun sitio de la funda mas grueso que otro.
    back_slab = (
        cq.Workplane("XY")
        .workplane(offset=0.1)
        .center(center_x, -CHIN_H / 2)
        .rect(ext_w, ext_h)
        .extrude(-(BACK_SLAB_EXTRA + 0.1))
        .edges("|Z")
        .fillet(CASE_CORNER_R)
    )
    body = body.union(back_slab)
    # snapshot: bloque bruto, sin ningun corte todavia -- referencia
    # para la auditoria final de piel exterior (ver mas abajo)
    outer_envelope = body

    cavity = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .rect(cav_w, cav_h)
        .extrude(ext_t)
        .edges("|Z")
        .fillet(CASE_CORNER_R - WALL if CASE_CORNER_R - WALL > 0.5 else 0.5)
    )
    body = body.cut(cavity)

    # ---- hueco + bisel de camara ----
    cam_center_x = -cav_w / 2 + CAM_BUMP_OFFSET_X + CAM_BUMP_SIZE / 2
    cam_center_y = cav_h / 2 - CAM_BUMP_OFFSET_Y - CAM_BUMP_SIZE / 2
    cam_cut = (
        cq.Workplane("XY")
        .workplane(offset=-3.3)
        .center(cam_center_x, cam_center_y)
        .rect(CAM_BUMP_SIZE, CAM_BUMP_SIZE)
        .extrude(WALL + 0.6 + 3.3)
        .edges("|Z")
        .fillet(CAM_CORNER_R)
    )
    body = body.cut(cam_cut)

    bezel_outer = (
        cq.Workplane("XY")
        .center(cam_center_x, cam_center_y)
        .rect(CAM_BUMP_SIZE + 3.2, CAM_BUMP_SIZE + 3.2)
        .extrude(WALL + 1.6)
        .edges("|Z")
        .fillet(CAM_CORNER_R + 1.6)
    )
    bezel_inner = (
        cq.Workplane("XY")
        .workplane(offset=-3.3)
        .center(cam_center_x, cam_center_y)
        .rect(CAM_BUMP_SIZE, CAM_BUMP_SIZE)
        .extrude(WALL + 2.2 + 3.3)
        .edges("|Z")
        .fillet(CAM_CORNER_R)
    )
    bezel = bezel_outer.cut(bezel_inner)
    body = body.union(bezel).cut(cam_cut)

    # ---------------------------------------------------------------
    # REBORDE DE PROTECCION DE CAMARA (estilo RhinoShield) -- a
    # diferencia del bisel anterior (que es refuerzo interno, a ras de
    # la superficie), este SI sobresale de verdad de la piel exterior,
    # rodeando el hueco de camara para que ese reborde toque el suelo
    # antes que el objetivo si la funda se apoya boca abajo. Sin
    # ningun vertice: los 4 cantos exteriores redondeados, los 4
    # interiores redondeados, y las dos aristas de la propia cresta
    # (exterior e interior) tambien redondeadas.
    # ---------------------------------------------------------------
    # FIX REDISEÑO (pedido expreso): antes esto se subio a 3.2mm para
    # que la corredera tuviera sitio detras del objetivo -- pero eso
    # dejaba un bulto asimetrico SOLO en la zona de la camara,
    # sobresaliendo mas que el resto de la funda. La profundidad
    # extra que necesita el mecanismo la da BACK_SLAB_EXTRA de manera
    # uniforme (ver mas abajo, tras cerrar el cuerpo principal).
    # FIX REDISEÑO (pedido expreso): ahora se quiere un reborde real
    # y visible, a proposito, SOLO alrededor de la camara -- como el
    # de las fundas RhinoShield (anillo protector que sobresale un
    # poco, marcando la zona de la camara, con el resto de la
    # funda completamente lisa alrededor).
    RIM_HEIGHT = 1.3    # mm que sobresale de la piel exterior lisa
    RIM_WIDTH = 2.6      # mm de ancho del propio reborde
    rim_outer_size = CAM_BUMP_SIZE + 3.2 + 2 * RIM_WIDTH
    rim_inner_size = CAM_BUMP_SIZE + 3.2

    rim_outer = (
        cq.Workplane("XY")
        .workplane(offset=-BACK_SLAB_EXTRA)
        .center(cam_center_x, cam_center_y)
        .rect(rim_outer_size, rim_outer_size)
        .extrude(-RIM_HEIGHT)
        .edges("|Z")
        .fillet(CAM_CORNER_R + 1.6 + RIM_WIDTH)
    )
    rim_inner_cut = (
        cq.Workplane("XY")
        .workplane(offset=-BACK_SLAB_EXTRA + 0.05)
        .center(cam_center_x, cam_center_y)
        .rect(rim_inner_size, rim_inner_size)
        .extrude(-(RIM_HEIGHT + 0.15))
        .edges("|Z")
        .fillet(CAM_CORNER_R + 1.6)
    )
    camera_rim = rim_outer.cut(rim_inner_cut)
    # redondear las aristas de la cresta (exterior e interior a la
    # vez) -- seleccionar la cara mas exterior (menor Z, la propia
    # cresta) y redondear TODOS sus bordes es mas fiable que buscar
    # aristas por punto mas cercano, que fallo silenciosamente
    camera_rim = camera_rim.faces("<Z").edges().fillet(0.4)
    body = body.union(camera_rim)

    cam_hinge_y = cam_center_y - CAM_BUMP_SIZE / 2 + 1.5

    # ---- botones normales: Action izquierda arriba, Volumen izquierda
    # debajo, Power sola a la derecha ----
    # FIX: con la pared izquierda ya asimetrica (mas gruesa por el
    # conducto de camara), x_sign*(ext_w/2) ya no da el borde real --
    # se usa LEFT_X/RIGHT_X directamente.
    def button_hole(y_center, length, x_face, x_sign):
        return (
            cq.Workplane("YZ")
            .workplane(offset=x_face + x_sign * 0.5)
            .center(y_center, WALL + 6)
            .rect(length, 5, centered=True)
            .extrude(x_sign * -1.0)
        )

    # FIX: longitudes ajustadas a medidas reales filtradas de un CAD
    # de fabricante de fundas (ShrimpApplePro, abril 2023, verificado
    # con busqueda): boton de accion (mute) = 2.42mm de diametro en
    # cada extremo + 3.51mm entre centros = ~5.93mm de largo real: el
    # anterior (10mm) era un 69% mas largo de lo real. Volumen =
    # 2.65mm de diametro + 23.5mm entre centros = ~26.15mm real (el
    # anterior, 22mm, se quedaba corto). Power: sin dato filtrado
    # equivalente, se deja el valor previo con un margen prudente.
    # Se añade ~1.5mm de holgura sobre la medida real del boton en
    # cada caso, no la medida exacta (necesita margen para moverse).
    action_cut = button_hole(cav_h / 2 - 25, 7.5, LEFT_X, -1)
    vol_cut = button_hole(cav_h / 2 - 55, 27.5, LEFT_X, -1)
    power_cut = button_hole(cav_h / 2 - 60, 24, RIGHT_X, 1)
    body = body.cut(vol_cut).cut(action_cut).cut(power_cut)

    # ---------------------------------------------------------------
    # REBORDES DE BOTON, ESTILO RHINOSHIELD (pedido expreso): un
    # relieve real alrededor de cada boton del propio iPhone, que
    # sobresale un poco de la pared lisa del canto -- marca donde
    # esta cada boton, no un simple agujero plano.
    # ---------------------------------------------------------------
    def button_rim(y_center, length, x_face, x_sign):
        outer = (
            cq.Workplane("YZ")
            .workplane(offset=x_face)
            .center(y_center, WALL + 6)
            .rect(length + 2.4, 5 + 2.4, centered=True)
            .extrude(x_sign * 0.4)
            .edges("|X")
            .fillet(1.1)
        )
        inner = (
            cq.Workplane("YZ")
            .workplane(offset=x_face)
            .center(y_center, WALL + 6)
            .rect(length + 0.6, 5 + 0.6, centered=True)
            .extrude(x_sign * 0.4)
        )
        return outer.cut(inner)

    def button_cap(y_center, length, x_face, x_sign):
        cap = (
            cq.Workplane("YZ")
            .workplane(offset=x_face + x_sign * 0.4)
            .center(y_center, WALL + 6)
            .rect(length + 0.9, 5 + 0.9, centered=True)
            .extrude(x_sign * 0.25)
            .edges("|X")
            .fillet(1.0)
        )
        return cap

    body = body.union(button_rim(cav_h / 2 - 25, 7.5, LEFT_X, -1))
    body = body.union(button_rim(cav_h / 2 - 55, 27.5, LEFT_X, -1))
    body = body.union(button_rim(cav_h / 2 - 60, 24, RIGHT_X, 1))
    body = body.union(button_cap(cav_h / 2 - 25, 7.5, LEFT_X, -1))
    body = body.union(button_cap(cav_h / 2 - 55, 27.5, LEFT_X, -1))
    body = body.union(button_cap(cav_h / 2 - 60, 24, RIGHT_X, 1))

    # ---- puerto USB-C ----
    # FIX CRITICO: el corte anterior (Y=[-87.9,-85.3], una franja de
    # solo 2.6mm) se quedaba flotando dentro del menton -- no llegaba
    # ni al puerto real del movil (que esta en el borde inferior de
    # la cavidad, Y=-cav_h/2) ni al borde exterior real de la funda
    # (ext_bottom_y). Era un hueco que no comunicaba con nada por
    # ninguno de los dos lados: no se veia porque literalmente no
    # atravesaba la funda. Reconstruido como un canal real de un
    # extremo al otro, con las dimensiones reales de un conector
    # USB-C (apertura 8.34x2.56mm) mas margen de holgura habitual en
    # fundas (~12x4mm).
    USB_PORT_W = 12.0
    USB_PORT_H = 4.0
    usb_port_z_center = WALL + PHONE_T / 2
    usb_y_inner = -cav_h / 2 + 1.5   # dentro de la cavidad, hasta el puerto real
    usb_y_outer = -cav_h / 2 - WALL - CHIN_H - 0.5   # 0.5mm mas alla del borde real, garantiza que atraviese del todo
    usb_cut = (
        cq.Workplane("XZ")
        .workplane(offset=-usb_y_inner)
        .center(0, usb_port_z_center)
        .rect(USB_PORT_W, USB_PORT_H)
        .extrude(usb_y_inner - usb_y_outer)
    )
    body = body.cut(usb_cut)

    # ---- rejilla altavoz/microfono (en el propio chin, junto al rodillo) ----
    # FIX: con el menton ya corregido (de verdad asimetrico), el borde
    # inferior real esta en -cav_h/2-WALL-CHIN_H (~-94.5), no donde
    # asumian los calculos anteriores (~-88.2, por el bug del menton
    # simetrico) -- el agujero no llegaba a ningun sitio. Se recalcula
    # con el limite real.
    ext_bottom_y = -cav_h / 2 - WALL - CHIN_H
    speaker_y = ext_bottom_y + 2.0   # cerca del borde real, con margen para la lengueta
    speaker_z = WALL + 4.0
    # FIX REDISEÑO (pedido expreso): antes 6 agujeros redondos por
    # lado -- simplificado a un unico rectangulo vacio por lado
    # (mismo ancho total que antes, mismo principio: la banda curva
    # lo tapa por dentro al cerrar). Mismo patron ya verificado que
    # y_cylinder (workplane XZ, offset controla Y).
    MIC_MECH_X = -16.0

    def y_rect_slot(x_center, z_center, width, height, y_start, length):
        return (
            cq.Workplane("XZ")
            .workplane(offset=-y_start)
            .center(x_center, z_center)
            .rect(width, height)
            .extrude(-length)
        )

    # FIX CRITICO (encontrado real: la banda solo cubre 1.76mm de
    # alto en Y en su posicion cerrada, verificado con su propio
    # bounding box -- el rectangulo anterior media 3.0mm, dejando
    # 75.6mm3 sin tapar). Recalculado para quedar DENTRO de lo que la
    # banda cubre de verdad, con margen de seguridad.
    speaker_holes = y_rect_slot(MIC_MECH_X, 7.0, 13.0, 0.3, -94.5, 0.35)
    body = body.cut(speaker_holes)

    # SEGUNDO rectangulo, lado derecho: el usuario confirmo con su
    # propio movil que hay agujeros a los DOS lados del puerto.
    MIC_MECH_X_R = 16.0
    speaker_holes_r = y_rect_slot(MIC_MECH_X_R, 7.0, 13.0, 0.3, -94.5, 0.35)
    body = body.cut(speaker_holes_r)

    mic_hinge_y = speaker_y + 4.5

    # ---------------------------------------------------------------
    # CANAL GUIA LATERAL para la lamina (dentro del grosor de pared)
    # ---------------------------------------------------------------
    guide_h = cav_h - 4
    # FIX CRITICO: guide_z estaba a ext_t*0.30 (~Z=4.3), heredado de la
    # v2 sin verificar contra el movil real -- eso cae DENTRO del
    # cuerpo del telefono, no delante de la pantalla. La lamina tiene
    # que deslizar justo por ENCIMA de la cara frontal del movil.
    z_flat_start = WALL + CAM_BUMP_T
    screen_z = z_flat_start + cav_t - CLEARANCE_Z  # cara frontal real del movil (sin la holgura extra)
    guide_z = screen_z + 0.15

    def side_channel(x_sign):
        x0 = x_sign * (cav_w / 2)
        return (
            cq.Workplane("XY")
            .workplane(offset=guide_z)
            .center(x0, 0)
            .rect(CHANNEL_W, guide_h)
            .extrude(CHANNEL_D)
            .translate((x_sign * -CHANNEL_D / 2, 0, 0))
        )

    body = body.cut(side_channel(-1)).cut(side_channel(1))

    # FIX: catch_lip se quita -- era la repisa donde enganchaba a mano
    # el gancho de la lamina en la version anterior (v2/v3, antes del
    # boton). Ya no hace falta (el mecanismo de piñon-cremallera
    # mantiene la posicion solo), y al no haber ya gancho que la
    # esquive, chocaba directamente con el cuerpo de la lamina
    # (verificado: 82.8mm3 de colision real).

    # snapshot: forma exterior ya completa (cavidad, camara+bisel+
    # reborde, botones, USB, rejilla de microfono) pero TODAVIA sin
    # ningun canal interno de mecanismo -- segunda referencia para la
    # auditoria final de piel exterior
    shape_reference = body

    # ---------------------------------------------------------------
    # ALOJAMIENTO DEL RODILLO (chin inferior) + PIÑON + CREMALLERAS
    # A diferencia de la v4: el eje del rodillo NO se mueve de sitio,
    # solo gira sobre si mismo -- no hay ningun brazo grande barriendo
    # un arco, así que no hace falta el compartimento ancho que tuvo
    # que tener la bisagra.
    # ---------------------------------------------------------------
    roller_y = -cav_h / 2 - CHIN_H / 2 - 1.0
    roller_len = cav_w - 2 * WALL - 8.0
    # FIX: el rodillo y el piñon NO tienen por que estar a la misma
    # altura que el canal de la lamina (guide_z, cerca de la pantalla)
    # -- el rodillo vive en el menton, en una zona Y totalmente
    # distinta a la del canal, con toda la altura del menton
    # disponible. Ponerlo a la misma altura que guide_z dejaba solo
    # ~2mm de margen para las cremalleras, y el canal CERRAR se salia
    # del grosor de la funda (16.59mm sobre 15.64mm totales).
    hinge_z = ext_t / 2   # centrado en el menton, con margen de sobra

    roller_bore = (
        cq.Workplane("YZ")
        .workplane(offset=-roller_len / 2)
        .center(roller_y, hinge_z + CHANNEL_D / 2)
        .circle(ROLLER_DIA / 2 + ROLLER_HOUSING_CLEAR)
        .extrude(roller_len)
    )
    body = body.cut(roller_bore)

    # FIX: el eje corto de la manivela de camara tiene que atravesar
    # la zona entre el alojamiento del rodillo (hasta -roller_len/2)
    # y el conducto (mas afuera, en la pared ensanchada) -- sin este
    # tramo adicional, ese eje no tenia por donde pasar.
    _conduit_x_preview = (-cav_w / 2 - WALL - EXTRA_WALL_LEFT) + EXTRA_WALL_LEFT / 2 + 0.3
    _x_far = _conduit_x_preview - 2.0
    _x_near = -roller_len / 2
    bore_extension = (
        cq.Workplane("YZ")
        .workplane(offset=_x_far)
        .center(roller_y, hinge_z + CHANNEL_D / 2)
        .circle(8.5)   # FIX 2: 7.5 aun se quedaba corto para el yugo
        # (16mm de alto) -- ensanchado a 8.5 (17mm de diametro) con margen
        .extrude(_x_near - _x_far)
    )
    body = body.cut(bore_extension)

    # ---------------------------------------------------------------
    # HUECOS PARA EL MECANISMO REAL DE LA LAMINA RF (encontrado real:
    # antes no tenia NINGUN mecanismo -- ver aviso en
    # build_rf_fabric_drive_piece_a/b/c). Igual que el propio eje
    # principal necesita su roller_bore, este tren de engranajes y el
    # carrete necesitan su propio hueco tallado -- no habia ninguno.
    # ---------------------------------------------------------------
    fabric_mesh_y_b = roller_y + FABRIC_GEAR_BIG + FABRIC_GEAR_SMALL - 0.3
    fabric_mesh_y_c = fabric_mesh_y_b + FABRIC_GEAR_BIG + FABRIC_GEAR_SMALL - 0.3
    fabric_bore_b = (
        cq.Workplane("YZ")
        .workplane(offset=FABRIC_TAP_X)
        .center(fabric_mesh_y_b, hinge_z)
        .circle(FABRIC_GEAR_BIG + 1.0)
        .extrude(4.0)
    )
    body = body.cut(fabric_bore_b)

    fabric_spool_len = cav_w - 2 * (CHANNEL_D + 0.4) + 1.5
    fabric_bore_c = (
        cq.Workplane("YZ")
        .workplane(offset=-fabric_spool_len / 2)
        .center(fabric_mesh_y_c, hinge_z)
        .circle(FABRIC_SPOOL_R + 1.0)
        .extrude(fabric_spool_len)
    )
    body = body.cut(fabric_bore_c)

    # FIX: bore_extension (radio 8.5mm, necesario para el yugo) perfora
    # la superficie trasera real por 0.18mm en esta zona -- verificado
    # con sonda (hueco real en Z=0, X=-44 a -36, Y=-92 a -86). Se
    # restaura una piel real de 0.2mm, mismo principio ya usado en la
    # zona de camara.
    # FIX REDISEÑO: este parche solo cubria Z=[0,0.25] -- correcto
    # mientras Z=0 era la piel exterior real. Desde que se añadio la
    # plancha trasera uniforme (BACK_SLAB_EXTRA), la parte de abajo
    # (Z<0) tambien es parte de la piel real de la funda, y
    # bore_extension llega hasta Z=-0.18 ahi -- quedaba una burbuja
    # fina y aislada sin proteger (verificado: 98mm3, encontrada en
    # la auditoria de shells). Ampliado para cubrir los dos lados.
    skin_restore = (
        cq.Workplane("XY")
        .workplane(offset=-0.3)
        .center((_x_far + _x_near) / 2, roller_y - 0.5)
        .rect(abs(_x_near - _x_far) + 2.0, 9.5)
        .extrude(0.55)
    )
    body = body.union(skin_restore)

    # FIX: el rodillo (hinge_z, ~7.8) y el canal (guide_z, ~13.6) ya no
    # estan a la misma altura -- esta ranura ahora cubre TODA la
    # transicion vertical entre ambos, no solo la altura del canal.
    feed_z_bottom = hinge_z - (ROLLER_DIA / 2 + ROLLER_HOUSING_CLEAR)
    feed_slot = (
        cq.Workplane("XY")
        .workplane(offset=feed_z_bottom)
        .center(0, roller_y)
        .rect(cav_w - 2 * WALL, CHANNEL_D * 3)
        .extrude(guide_z + CHANNEL_D - feed_z_bottom)
    )
    body = body.cut(feed_slot)

    pinion_x = -(roller_len / 2) + 3.0   # extremo izquierdo del rodillo
    switch_z = hinge_z + 2.0   # altura real del interruptor unico cautivo

    # FIX CRITICO (2a parte): con el piñon y la cremallera reconstruidos
    # para girar/deslizar en los ejes correctos (piñon en X, cremallera
    # en Y), los canales tambien tienen que cortar en Y -- antes
    # cortaban en X, que ya no es la direccion de deslizamiento.
    # El boton ahora esta en el CANTO INFERIOR de la funda (empuja
    # hacia arriba, +Y), no en el lateral.
    ext_bottom_y = -cav_h / 2 - WALL - CHIN_H
    button_stem_len = (roller_y - ext_bottom_y) - RACK_LEN / 2 - 1.0 + BUTTON_CAP_PROTRUSION

    pinion_center_x = pinion_x + PINION_THK / 2   # FIX: el centro real
    # de la cremallera es pinion_x+PINION_THK/2, no pinion_x (que es
    # solo su borde inicial) -- los canales estaban descentrados 2.5mm

    def rack_channel_internal(z_center):
        return (
            cq.Workplane("XZ")
            .center(pinion_center_x, z_center)
            .workplane(offset=RACK_LEN / 2 - roller_y + SWITCH_TRAVEL)
            .rect(PINION_THK + 2 * SLIDING_CLEARANCE + 0.6, 2.4)
            .extrude(-(RACK_LEN + 0.6 + SWITCH_TRAVEL))
        )

    body = body.cut(rack_channel_internal(switch_z))

    # FIX CRITICO (reposicionamiento): el salto a la pared se hace
    # INMEDIATAMENTE despues de los dientes (no al final) -- el tramo
    # largo sube ya pegado a la pared, fuera de la huella del movil
    # (verificado: la version anterior, subiendo por dentro, chocaba
    # 879mm3 con el cuerpo del telefono).
    # FIX: esta formula tenia que coincidir con la de la propia
    # empuñadura en build_main_carriage_switch (RACK_NEG_ANCHOR+STEM),
    # pero seguia usando la formula vieja (RACK_LEN/2) de antes del
    # rediseño del interruptor -- 2.25mm de descuadre real entre el
    # canal cortado aqui y donde vive la pieza de verdad.
    grip_y_local = 1.0 + SWITCH_STEM_LEN
    # FIX CRITICO (encontrado real): calibrado para la pared antigua
    # (LEFT_X=-45.3, antes de ensancharla para la camara y luego para
    # la simetria). Con la pared ya en -50.3, esto dejaba la
    # empuñadura a 6mm de la pared -- inalcanzable desde fuera, sin
    # ningun boton real que apretar. Recalculado para la pared actual.
    grip_x_local = -20.65   # FIX: recalculado -- el valor anterior dejaba la pestaña 0.4mm POR DENTRO de la pared (no sobresalia nada, la pestaña era invisible/intocable)
    # (3.0mm) para 0.6mm de saliente real, pesable con el dedo
    grip_global_x = pinion_x + grip_x_local
    # FIX CRITICO REAL (encontrado con fotos del usuario): el vastago
    # entero corria pegado a la pared en TODA su longitud (~100mm), y
    # el canal tenia que abrir la pared real en todo ese largo --
    # vastago visible por fuera de punta a punta. Ahora el vastago
    # (ver build_main_carriage_switch) corre a stem_x_local, con
    # margen real a la pared, en la mayor parte de su recorrido -- el
    # canal principal ya no necesita llegar a la pared en absoluto.
    stem_x_local = -14.0
    stem_global_x = pinion_x + stem_x_local
    JOG_FAR_LEN_B = 6.0   # debe coincidir con JOG_FAR_LEN en build_main_carriage_switch

    combined_channel = (
        cq.Workplane("XY")
        .workplane(offset=switch_z - 1.7)
        .center((pinion_center_x + stem_global_x) / 2 - 1.0,
                roller_y + (RACK_LEN / 2 + grip_y_local - JOG_FAR_LEN_B) / 2 - SWITCH_TRAVEL / 2)
        .rect(abs(pinion_center_x - stem_global_x) + 4.0,
              (grip_y_local - JOG_FAR_LEN_B - RACK_LEN / 2) + SWITCH_TRAVEL + 6.0)
        .extrude(3.6)
    )
    body = body.cut(combined_channel)

    # FIX: tunel corto y localizado SOLO para el ultimo tramo (donde
    # el vastago gira hacia la pared real, junto a la propia
    # empuñadura) -- este es el UNICO sitio de todo el vastago que
    # de verdad necesita alcanzar la pared exterior.
    grip_channel_xmin = max(-52.9, LEFT_X + 0.02)  # nunca mas alla de la pared real
    grip_channel_center_x = (stem_global_x + grip_global_x) / 2 - 1.0
    grip_channel_width = abs(stem_global_x - grip_global_x) + 5.0
    grip_channel_xmax = grip_channel_center_x + grip_channel_width / 2
    grip_channel = (
        cq.Workplane("XY")
        .workplane(offset=-1.7)
        .center((grip_channel_xmin + grip_channel_xmax) / 2,
                roller_y + grip_y_local - SWITCH_TRAVEL / 2)
        .rect(grip_channel_xmax - grip_channel_xmin,
              SWITCH_TRAVEL + SWITCH_GRIP_LEN + 10.0 + SWITCH_TRAVEL + 2.0)
        .extrude(13.4)
    )
    body = body.cut(grip_channel)

    # ---------------------------------------------------------------------
    # RELLENO ESTRUCTURAL: verificado que esta franja de pared (junto
    # al canto izquierdo, por donde sube el vastago del interruptor)
    # quedaba practicamente hueca -- el canal real del interruptor
    # (combined_channel) solo ocupa Z=8.12-11.72, pero el resto de la
    # columna (Z=1.5 a 8, y 11.9 a 14) no tenia nada rellenando,
    # dejando solo piel exterior y pared interior finisima con un
    # vacio grande en medio. Se restaura material real por encima y
    # por debajo del canal, sin tocar su propio hueco.
    # ---------------------------------------------------------------
    # FIX: el conduit de la varilla de camara (yugo Scotch, necesita
    # casi toda la altura Z a lo largo de su recorrido) ocupa
    # X=[-44.5,-40.5], y la propia manivela (que gira cerca de
    # roller_y) llega hasta X=-38.1 -- el relleno se ajusta para no
    # invadir ninguno de los dos, dejando su sitio real.
    wall_x_min = -37.8
    wall_x_max = grip_global_x + 8.0
    wall_y_min = roller_y - 2.0
    wall_y_max = -80.5   # se queda fuera de la huella real del movil (-79.95)
    for fill_z_min, fill_z_max in ((1.8, switch_z - 1.9), (switch_z + 1.9, 14.0)):
        fill_patch = (
            cq.Workplane("XY")
            .workplane(offset=fill_z_min)
            .center((wall_x_min + wall_x_max) / 2, (wall_y_min + wall_y_max) / 2)
            .rect(wall_x_max - wall_x_min, wall_y_max - wall_y_min)
            .extrude(fill_z_max - fill_z_min)
        )
        body = body.union(fill_patch)

    # ---------------------------------------------------------------
    # DIMENSIONES FIJAS DE LA RANURA (pedido expreso: el marco debe
    # tomar como referencia la ranura de la funda, NO el deslizador
    # movil -- "piensa en el marco de una ventana: el marco sigue el
    # hueco, el objeto de detras se mueve independiente"). Estas dos
    # constantes son la UNICA fuente de verdad del tamaño de la
    # ranura fija -- tanto el propio hueco como el marco (mas abajo)
    # las usan directamente, en vez de cada uno recalcular por su
    # cuenta a partir del recorrido del deslizador (SWITCH_TRAVEL).
    # El recorrido del deslizador ya esta tenido en cuenta AQUI, una
    # sola vez, al fijar el tamaño de la ranura -- el marco no vuelve
    # a mencionar el deslizador en ningun momento.
    SLOT_W = SWITCH_TRAVEL + 8.0 + 0.6   # ancho real de la pestaña
    # nueva (8.0, pedido expreso) + su recorrido + holgura
    SLOT_H = 5.0 + 0.6   # igual a la altura real de la pestaña nueva

    def button_hole_exterior():
        # ranura alargada unica (empuñadura larga) ahora en el CANTO
        # LATERAL real de la funda (asoma en -X), a la altura de la
        # imagen de referencia -- no en el canto inferior como antes
        # FIX: la ranura solo cubria el largo de la propia empuñadura,
        # sin contar que esta se desliza SWITCH_TRAVEL entre ONLINE y
        # OFFLINE -- en la posicion OFFLINE la empuñadura salia fuera
        # de la ranura y chocaba con pared solida (verificado:
        # 10.6mm3). Centrada a medio camino entre los dos estados, con
        # largo suficiente para las dos posiciones extremas.
        grip_global_y = roller_y + grip_y_local - SWITCH_TRAVEL / 2
        # FIX REDISEÑO: la ranura visible por fuera se queda PEQUEÑA
        # (solo el ancho real de la pestaña, sin el recorrido) -- es
        # la propia PESTAÑA (ver grip_total_len en
        # build_main_carriage_switch) la que se alarga para taparla
        # entera en cualquier posicion, no la ranura la que crece.
        hole = (
            cq.Workplane("YZ")
            .center(grip_global_y, switch_z - 2.22)
            .workplane(offset=LEFT_X - 0.5)
            .rect(SLOT_W, SLOT_H)
            .extrude(2.2)
        )
        return hole.edges("|X").fillet(min(3.0, SLOT_H) / 2 - 0.1)

    body = body.cut(button_hole_exterior())

    # ---------------------------------------------------------------
    # CANAL DEDICADO PARA LA LAMINA INTERIOR (pedido expreso: "un
    # carril hueco interno especial para esa lamina, a ambos lados,
    # para que no choque y corra y deje todo perfecto"). En vez de
    # obligar a la lamina a encajar en el hueco pequeño ya existente
    # (con sus propias esquinas redondeadas, causa de todos los
    # choques anteriores), se le talla su PROPIO canal, con margen de
    # sobra en los dos lados (Y y Z) y en las dos caras -- la lamina
    # nunca puede tocar la pared porque tiene su propio hueco de
    # verdad, mas grande que ella misma en todas las direcciones.
    lamina_channel_h = BUTTON_H + 3.4 + 1.4 + 1.0   # debe superar la placa trasera (7.0)
    grip_global_y_ch = roller_y + grip_y_local - SWITCH_TRAVEL / 2
    lamina_channel = (
        cq.Workplane("YZ")
        .center(grip_global_y_ch, switch_z - 2.22)
        .workplane(offset=LEFT_X + 0.7)
        .rect(SWITCH_TRAVEL + SWITCH_GRIP_LEN + 6.0 + SWITCH_TRAVEL + 15.0, lamina_channel_h)
        .extrude(2.6)
    )
    body = body.cut(lamina_channel)

    # ---------------------------------------------------------------
    # MARCO/REBORDE DE LA PESTAÑA (pedido expreso, foto de referencia):
    # mismo tratamiento que ya se usa en volumen/accion/power -- un
    # marco que sobresale un poco alrededor de todo el recorrido de
    # la pestaña, dandole aspecto de modulo "acolchado" con su propio
    # carril, no una ranura desnuda con una capsula dentro. Tambien
    # ayuda a tapar visualmente el resto minimo que pueda quedar en
    # las esquinas del hueco.
    # MARCO ELIMINADO (pedido expreso): "elimina completamente el
    # marco/embellecedor alrededor de la ranura, que quede como una
    # abertura limpia, como los botones del iPhone". Ya no se añade
    # ningun reborde alrededor de la ranura -- la pestaña (mas abajo,
    # redimensionada para igualar el tamaño real de los botones
    # laterales) es el UNICO elemento visible ademas de la propia
    # ranura limpia en la piel.

    # ---- MODULO DE BLOQUEO (Locking Module, Hoja 14): alojamiento
    # para bola + muelle, en la pared por encima del interruptor.
    # Posicionado en la muesca ONLINE (posicion de referencia, sin
    # desplazar el interruptor) -- la muesca OFFLINE queda a
    # SWITCH_TRAVEL de distancia sobre el propio interruptor, asi que
    # un unico alojamiento fijo basta para las dos posiciones.
    detent_y = roller_y + SWITCH_DETENT_Y1
    detent_pocket = (
        cq.Workplane("XY")
        .center(pinion_center_x, detent_y)
        .circle(1.1)
        .extrude(4.0)
        .translate((0, 0, switch_z + 0.6))
    )
    body = body.cut(detent_pocket)

    # ---------------------------------------------------------------
    # MODULO DE MICROFONO REDISEÑADO: ventana lateral (desliza en X),
    # no lamina en Y. El reductor vive lejos (Y=-60), fuera de la
    # franja estrecha junto al canto real -- necesita su propio
    # corredor de alcance hasta la entrada Y hasta la ventana.
    #
    # FIX CRITICO (bug real, confirmado en Fusion 360 por el usuario):
    # el canal anterior era UNA sola pieza con la altura del
    # mecanismo completo (10.22mm) aplicada TAMBIEN en el borde
    # exterior -- dejaba un boquete real de Z=3 a Z=11 en el canto,
    # no solo un hueco pequeño para la ventana. Ahora el canal
    # exterior (el que de verdad se ve desde fuera) esta limitado al
    # tamaño real de la ventana (5.5mm), separado del canal interno
    # del mecanismo (que puede ser mas alto porque no llega al borde).
    # ---------------------------------------------------------------
    mic_pinion_x = MIC_MECH_X
    mic_z_offset = speaker_z - hinge_z   # se mantiene por compatibilidad con dims, ya no se usa para la ventana
    mic_gear_x = mic_pinion_x
    mic_gear_y = roller_y + (RACK_LEN / 2 + MIC_GEAR_REACH)
    mic_gear2_z = MIC_GEAR1_Z + 1.2 + 0.35

    # canal interno de la cremallera de entrada (cerca del rodillo, NO
    # llega al borde exterior)
    mic_input_channel = (
        cq.Workplane("XZ")
        .center(mic_pinion_x, hinge_z + 1.4)
        .workplane(offset=RACK_LEN / 2 + 0.5 - roller_y)
        .rect(6.0, 4.0)
        .extrude(-(RACK_LEN + 1.0))
    )
    body = body.cut(mic_input_channel)

    mic_input_reach_channel = (
        cq.Workplane("XY")
        .workplane(offset=MIC_GEAR1_Z - 0.3)
        .center(mic_pinion_x + 2.5, roller_y + (RACK_LEN / 2 + MIC_GEAR_REACH + RACK_LEN / 2 + 0.5) / 2)
        .rect(8.0, MIC_GEAR_REACH + RACK_LEN + 2.0)
        .extrude(hinge_z + 2.4 - (MIC_GEAR1_Z - 0.3))
    )
    body = body.cut(mic_input_reach_channel)

    mic_gear_clear = (
        cq.Workplane("XY")
        .workplane(offset=MIC_GEAR1_Z - 0.3)
        .center(mic_gear_x, mic_gear_y)
        .circle(max(MIC_GEAR_R1, MIC_GEAR_R2) + 1.0)
        .extrude(MIC_GEAR1_Z + 1.2 + 0.35 + 1.2 - (MIC_GEAR1_Z - 0.3) + 0.3)
    )
    body = body.cut(mic_gear_clear)

    # ---------------------------------------------------------------
    # BANDA CURVA SEMIRRIGIDA (rediseño pedido por el usuario, en vez
    # de la ventana rigida plana): en vez de un canal recto de 20mm+
    # de recorrido lateral -- que no cabe en el hueco real disponible
    # entre el interruptor principal (hasta X=-25.1) y el canal USB-C
    # (desde X=-6, ~19mm libres, menos que el ancho de la propia
    # ventana) -- la pieza que tapa el microfono es una lamina fina
    # curvada en cuarto de circulo (radio MIC_BAND_R) que gira sobre
    # si misma dentro de un hueco compacto, en vez de deslizar en
    # linea recta. Cubre los agujeros pegada a la piel exterior
    # (angulo bajo) y se repliega girando hacia el interior del
    # menton (angulo alto) -- el mismo principio que la lamina RF que
    # se enrolla en el rodillo, aplicado aqui en miniatura.
    # Verificado con maqueta real (interruptor en ambos estados,
    # canal USB-C, movil real, piñon, eje): 0mm3 de colision en la
    # posicion CUBRIENDO y en la OCULTA.
    # ---------------------------------------------------------------
    mic_center_y = ext_bottom_y + MIC_BAND_R
    mic_center_z = speaker_z

    def mic_arc_point(theta_deg):
        th = math.radians(theta_deg)
        return (mic_center_y - MIC_BAND_R * math.cos(th), mic_center_z + MIC_BAND_R * math.sin(th))

    channel_pad = 6.0
    p_start = mic_arc_point(-channel_pad)
    p_mid = mic_arc_point(MIC_BAND_TOTAL_ARC / 2)
    p_end = mic_arc_point(MIC_BAND_TOTAL_ARC + channel_pad)
    mic_channel_path = cq.Workplane("YZ").moveTo(*p_start).threePointArc(p_mid, p_end)
    mic_channel_profile = (
        cq.Workplane("XY")
        .workplane(offset=p_start[1])
        .center(mic_pinion_x, p_start[0])
        .rect(MIC_BAND_W + 1.0, MIC_BAND_T + 0.6)
    )
    mic_curved_channel = mic_channel_profile.sweep(mic_channel_path, transition="round")
    body = body.cut(mic_curved_channel)

    # ---------------------------------------------------------------
    # CONDUCTO DEL EJE FLEXIBLE MICROFONO -> BANDA CURVA
    # ARREGLO: el acoplamiento entre el reductor (gira en eje Z) y la
    # banda curva (gira en un eje paralelo a X) se habia dejado
    # esquematico -- son dos ejes que NO se cruzan (perpendiculares Y
    # ademas separados 13.6mm), asi que no puede ser un piñon conico
    # simple. Solucion real y habitual para este caso exacto (dos
    # ejes que no se cruzan): un eje flexible con juntas universales
    # en los dos extremos, igual que un cable de velocimetro o un
    # flex de taladro -- se compra, no se imprime (ver
    # build_material_mic_drive_shaft). Este conducto es solo el
    # hueco por el que pasa.
    # ---------------------------------------------------------------
    drive_a = (mic_gear_x, mic_gear_y, mic_gear2_z + 2.3)
    # ARREGLO: el punto de union anterior estaba SOBRE el propio arco
    # que la banda barre al girar -- el eje chocaba con la banda en
    # las posiciones intermedias (1.24mm3 verificado). El eje de giro
    # real (mic_center_y, mic_center_z) es el centro del circulo, no
    # el arco -- la banda nunca ocupa ese punto exacto (esta siempre
    # a radio MIC_BAND_R de el), asi que unir el eje flexible ahi
    # (como el perno de una bisagra real) lo deja limpio en todo el
    # recorrido.
    drive_b = (mic_pinion_x, mic_center_y, mic_center_z)
    dvy, dvz = drive_b[1] - drive_a[1], drive_b[2] - drive_a[2]
    dlen = (dvy ** 2 + dvz ** 2) ** 0.5
    pad = 4.0
    a_pad = (drive_a[1] - dvy / dlen * pad, drive_a[2] - dvz / dlen * pad)
    b_pad = (drive_b[1] + dvy / dlen * pad, drive_b[2] + dvz / dlen * pad)
    drive_path = cq.Workplane("YZ").moveTo(*a_pad).lineTo(*b_pad)
    drive_profile = cq.Workplane("XY").workplane(offset=drive_a[2]).center(mic_pinion_x, drive_a[1]).circle(2.6)
    mic_drive_channel = drive_profile.sweep(drive_path)
    body = body.cut(mic_drive_channel)
    # burbuja de union en el punto de encuentro: el canal curvo es una
    # tira plana fina (1mm de grosor) y el conducto del eje es
    # redondo (2.6mm de radio) -- no se alinean por si solos. Una
    # esfera de despeje ahi asegura una cavidad continua real, sin
    # depender de que coincidan exactamente.
    junction_clear = cq.Workplane("XY").workplane(offset=drive_b[2]).center(mic_pinion_x, drive_b[1]).sphere(3.2)
    body = body.cut(junction_clear)

    # ---------------------------------------------------------------
    # SEGUNDO MECANISMO DE BANDA CURVA, LADO DERECHO -- identico al de
    # la izquierda (mismo radio, mismo arco, mismo principio), solo
    # que en X=+16 en vez de -16. Ese lado tiene MAS margen real (no
    # esta el piñon del interruptor principal ahi), asi que cabe sin
    # necesitar ensanchar la funda como si hizo falta para la camara.
    # ---------------------------------------------------------------
    mic_pinion_x_r = MIC_MECH_X_R
    mic_gear_x_r = mic_pinion_x_r
    mic_gear_y_r = roller_y + (RACK_LEN / 2 + MIC_GEAR_REACH)
    mic_gear2_z_r = MIC_GEAR1_Z + 1.2 + 0.35

    mic_input_channel_r = (
        cq.Workplane("XZ")
        .center(mic_pinion_x_r, hinge_z + 1.4)
        .workplane(offset=RACK_LEN / 2 + 0.5 - roller_y)
        .rect(6.0, 4.0)
        .extrude(-(RACK_LEN + 1.0))
    )
    body = body.cut(mic_input_channel_r)

    mic_input_reach_channel_r = (
        cq.Workplane("XY")
        .workplane(offset=MIC_GEAR1_Z - 0.3)
        .center(mic_pinion_x_r + 2.5, roller_y + (RACK_LEN / 2 + MIC_GEAR_REACH + RACK_LEN / 2 + 0.5) / 2)
        .rect(8.0, MIC_GEAR_REACH + RACK_LEN + 2.0)
        .extrude(hinge_z + 2.4 - (MIC_GEAR1_Z - 0.3))
    )
    body = body.cut(mic_input_reach_channel_r)

    mic_gear_clear_r = (
        cq.Workplane("XY")
        .workplane(offset=MIC_GEAR1_Z - 0.3)
        .center(mic_gear_x_r, mic_gear_y_r)
        .circle(max(MIC_GEAR_R1, MIC_GEAR_R2) + 1.0)
        .extrude(MIC_GEAR1_Z + 1.2 + 0.35 + 1.2 - (MIC_GEAR1_Z - 0.3) + 0.3)
    )
    body = body.cut(mic_gear_clear_r)

    mic_center_y_r = ext_bottom_y + MIC_BAND_R
    mic_center_z_r = speaker_z

    def mic_arc_point_r(theta_deg):
        th = math.radians(theta_deg)
        return (mic_center_y_r - MIC_BAND_R * math.cos(th), mic_center_z_r + MIC_BAND_R * math.sin(th))

    p_start_r = mic_arc_point_r(-channel_pad)
    p_mid_r = mic_arc_point_r(MIC_BAND_TOTAL_ARC / 2)
    p_end_r = mic_arc_point_r(MIC_BAND_TOTAL_ARC + channel_pad)
    mic_channel_path_r = cq.Workplane("YZ").moveTo(*p_start_r).threePointArc(p_mid_r, p_end_r)
    mic_channel_profile_r = (
        cq.Workplane("XY")
        .workplane(offset=p_start_r[1])
        .center(mic_pinion_x_r, p_start_r[0])
        .rect(MIC_BAND_W + 1.0, MIC_BAND_T + 0.6)
    )
    mic_curved_channel_r = mic_channel_profile_r.sweep(mic_channel_path_r, transition="round")
    body = body.cut(mic_curved_channel_r)

    drive_a_r = (mic_gear_x_r, mic_gear_y_r, mic_gear2_z_r + 2.3)
    drive_b_r = (mic_pinion_x_r, mic_center_y_r, mic_center_z_r)
    dvy_r, dvz_r = drive_b_r[1] - drive_a_r[1], drive_b_r[2] - drive_a_r[2]
    dlen_r = (dvy_r ** 2 + dvz_r ** 2) ** 0.5
    a_pad_r = (drive_a_r[1] - dvy_r / dlen_r * pad, drive_a_r[2] - dvz_r / dlen_r * pad)
    b_pad_r = (drive_b_r[1] + dvy_r / dlen_r * pad, drive_b_r[2] + dvz_r / dlen_r * pad)
    drive_path_r = cq.Workplane("YZ").moveTo(*a_pad_r).lineTo(*b_pad_r)
    drive_profile_r = cq.Workplane("XY").workplane(offset=drive_a_r[2]).center(mic_pinion_x_r, drive_a_r[1]).circle(2.6)
    mic_drive_channel_r = drive_profile_r.sweep(drive_path_r)
    body = body.cut(mic_drive_channel_r)
    junction_clear_r = cq.Workplane("XY").workplane(offset=drive_b_r[2]).center(mic_pinion_x_r, drive_b_r[1]).sphere(3.2)
    body = body.cut(junction_clear_r)

    # ---------------------------------------------------------------
    # CONDUCTO PARA LA VARILLA DE SINCRONIZACION DE CAMARA
    # Mecanismo de manivela + yugo: un brazo radial en el eje empuja
    # una varilla rigida que desliza dentro de este conducto, desde el
    # rodillo hasta la zona de la camara (126mm). Al ser rigida (no un
    # cable), el desplazamiento se transmite 1:1 sin depender de que
    # se comporte bien un hilo flexible -- pero SI depende de que la
    # varilla no se pandee en un tramo tan largo, algo que no se puede
    # verificar solo con geometria estatica (ver aviso mas abajo).
    # ---------------------------------------------------------------
    conduit_x = LEFT_X + EXTRA_WALL_LEFT / 2 + 0.3
    conduit_z = hinge_z
    crank_r = 5.0   # FIX 2: 6.0 hacia que el yugo (16mm) fuera mas
    # alto que el propio grosor de la funda (15.64mm) -- no cabia sea
    # cual sea el centrado. 5.0 da un yugo de 14mm, con margen real
    conduit_y_min = roller_y - 4.0   # deja sitio al yugo, centrado en roller_y
    conduit_y_max = cam_hinge_y - 3.0
    # FIX: un tubo redondo de 2.6mm de diametro no dejaba sitio ni de
    # lejos para el yugo (10mm) ni la manivela -- verificado con
    # colision real (26-160mm3). Ahora es una ranura rectangular:
    # ancha en Z (12mm, cabe de sobra en el grosor de la funda) y
    # estrecha en X (4mm, ajustada al ensanche de pared disponible)
    conduit = (
        cq.Workplane("XZ")
        .center(conduit_x, conduit_z)
        .workplane(offset=-conduit_y_max)
        .rect(4.0, 12.0)
        .extrude(conduit_y_max - conduit_y_min)
    )
    body = body.cut(conduit)

    # ---------------------------------------------------------------
    # HUECO PARA LA REDUCCION NUEVA DE LA MANIVELA: el tramo de eje
    # ahi era antes una simple varilla de 1.2mm, pero ahora lleva un
    # par de engranajes (radio hasta 3.9mm) para reducir el giro real
    # del eje a los 90 grados que necesita el yugo -- el hueco
    # original no daba sitio para eso (verificado: colision real).
    # ---------------------------------------------------------------
    reducer_clear = (
        cq.Workplane("XZ")
        .center(pinion_x - 8.0 - 3.5, hinge_z)
        .workplane(offset=-(roller_y + 5.0))
        .rect(9.0, 10.0)
        .extrude(10.0)
    )
    body = body.cut(reducer_clear)

    # FIX: el tramo que cruza en X hacia la camara pasaba a la altura
    # del propio cuerpo del telefono (conduit_z=hinge_z, dentro de su
    # grosor) -- se baja a low_z (cerca de la parte trasera, zona ya
    # libre de telefono) antes de cruzar. Se corta aqui el hueco
    # correspondiente, con margen extra sobre la pieza real.
    low_z = 0.3   # FIX 2: incluso a 0.5 con 3mm de grosor invadia el bulto (hasta Z=3.5, pero el bulto empieza en 1.6). Ahora mas fino y mas bajo
    y1 = conduit_y_max - 2
    riser_cut = (
        cq.Workplane("XZ")
        .center(conduit_x, (conduit_z + low_z) / 2)
        .workplane(offset=-(y1 - 1.0))
        .rect(3.0, abs(conduit_z - low_z) + 2 * SLIDING_CLEARANCE + 0.2)
        .extrude(3.0)
    )
    body = body.cut(riser_cut)
    y_top = min(cam_hinge_y + 2.0, y1 + 12.0)
    reach_cut = (
        cq.Workplane("XY")
        .center((conduit_x + cam_center_x) / 2, y1)
        .workplane(offset=low_z)
        .rect(abs(cam_center_x - conduit_x) + 4.0, 3.5)
        .extrude(1.0)
    )
    body = body.cut(reach_cut)
    pusher_cut = (
        cq.Workplane("XY")
        .center(cam_center_x, (y1 + y_top) / 2)
        .workplane(offset=low_z)
        .rect(4.0, abs(y_top - y1) + 4.0)
        .extrude(1.0)
    )
    body = body.cut(pusher_cut)

    # ---------------------------------------------------------------
    # MECANISMO VERTICAL DE CAMARA (corregido tras el aviso del
    # usuario: en Y hay muchisimo mas espacio real que en X -- el
    # hueco libre de 3.59mm entre la pared trasera y el cuerpo plano
    # del movil existe en TODA la cavidad, no solo junto a la camara,
    # y en direccion Y se extiende mas de 100mm hacia el centro del
    # movil, no los 12.6mm de la franja de pared que limitaban la
    # version anterior).
    # ---------------------------------------------------------------
    cutout_bottom = cam_center_y - CAM_BUMP_SIZE / 2   # 37.3
    cam_shutter_ref_x = cam_center_x
    cam_gear_x = -43.0   # FIX CRITICO (foto real del usuario): a -44.65 el
    # propio reductor (radio 6.48mm) sobresalia 1.42mm por la pared
    # izquierda real (-50.3) -- desplazado hacia dentro lo justo para
    # quedar contenido, re-verificado el contacto con el resto de la
    # cadena tras el cambio. Antes: desplazado 5mm a la izquierda junto con
    # el ensanche de EXTRA_WALL_LEFT (arriba), para que el engranaje
    # de verdad use el hueco nuevo en vez de quedarse en su sitio
    # mientras la pared se aleja
    cam_gear_y = conduit_y_max - 5.0   # cerca de donde ya llega la varilla (y1=conduit_y_max-2)
    # FIX CRITICO DE VERDAD: el comentario anterior decia que el
    # bulto ocupaba Z=[1.6, 5.19] (hacia DENTRO del telefono) -- eso
    # esta al reves. El propio reborde de proteccion (RIM_HEIGHT, mas
    # abajo) solo tiene sentido si el objetivo sobresale hacia la
    # piel EXTERIOR (Z negativa): por eso el reborde sobresale el
    # tambien en Z negativa, para tocar el suelo antes que el
    # objetivo. Comprobado con una maqueta real del bulto (extrude
    # -CAM_BUMP_T desde WALL): el bulto ocupa Z=[WALL-CAM_BUMP_T,
    # WALL] = [-1.99, 1.6] -- justo la franja donde estaba el plato
    # de la corredera (cam_low_z=0.3, plato en [0.3,1.1]). Verificado
    # con la maqueta real del bulto: 925mm3 de colision real, la
    # corredera no podia cerrar de ninguna manera. Recolocado a Z muy
    # negativa, mas alla de la punta real del objetivo.
    cam_low_z = -2.9
    cam_gear1_z = 0.25   # altura real del piñon pequeño (engrana con la varilla)
    cam_gear2_z = 2.15   # FIX: sincronizado con el nuevo grosor de dientes (1.8mm) -- gear1 [0.25,2.05] + 0.1mm margen = 2.15, altura real del piñon grande
    cam_gear_z = cam_gear2_z   # se mantiene por compatibilidad con el resto del codigo
    gear_r1 = 0.9   # FIX REDISEÑO: antes 1.3. Repartido con gear_r2
    # (ver abajo) para no repetir el problema de espacio real: agrandar
    # SOLO gear_r2 hacia 9.36mm empujaba el puente 9.6mm dentro del
    # propio movil (677mm3 de colision verificada). Encogiendo tambien
    # gear_r1 se necesita menos crecimiento en gear_r2.
    gear_r2 = 6.48   # FIX REDISEÑO: antes 5.0. gear_r2/gear_r1=7.2,
    # el giro de la manivela (yugo a 5.0mm/90 grados) x esta proporcion
    # da los 36mm reales que necesita la corredera.
    cam_travel = 35.9   # recorrido real verificado de la palanca/engranaje (objetivo 35mm, con margen)

    # hueco combinado: varilla (extremo camara), engranaje reductor, y
    # barrido completo de la corredera vertical (cubriendo + escondida).
    # Z empieza en 0.2 (no en 0) para no perforar la superficie
    # exterior de nuevo -- misma leccion que la version anterior.
    # FIX CRITICO: el ancho anterior (50mm, centro -21.0) llegaba
    # hasta X=-46, ATRAVESANDO la pared lateral real (LEFT_X=-45.3) --
    # nunca se comprobo la pared lateral, solo la trasera, y quedo un
    # agujero real ahi (confirmado por captura de Fusion 360 del
    # usuario). El engranaje solo necesita llegar a X=-44.65 (su
    # propio borde); el canal se limita a X=-44.9, dejando piel real.
    # NOTA: se intento estrechar este bolsillo (50.5->50.0) para
    # ganar piel real en la pared izquierda, pero el engranaje
    # reductor de camara (cam_gear_x=-39.65, dientes hasta radio+0.6)
    # ya llega el solo hasta X=-45.24 -- a 0.06mm de LEFT_X (-45.3).
    # No hay margen real para estrechar el bolsillo sin chocar con el
    # engranaje: la pared queda con ~0.06-0.15mm de piel en esta
    # franja por una restriccion geometrica de fondo (engranaje vs
    # EXTRA_WALL_LEFT), no por un error de este bolsillo -- para
    # arreglarlo de verdad hay que mover el engranaje o engrosar
    # EXTRA_WALL_LEFT, ninguno de los dos es un cambio menor. La
    # auditoria automatica de piel (mas abajo) esta descartada de
    # rellenar esta franja porque chocaria con el engranaje real.
    cam_clear = (
        cq.Workplane("XY")
        .workplane(offset=-3.0)
        .center(-22.9, 34.4)
        .rect(56.4, 81.0)
        .extrude(7.8)
    )
    body = body.cut(cam_clear)

    # ---------------------------------------------------------------
    # Alojamiento del contacto RF (pogo-pin) -- fijo en el FRAME, la
    # barra rigida de la lamina (conductora) lo presiona al desplegar
    # por completo, cerrando el circuito. Ver build_material_pogo_pin_rf.
    # ---------------------------------------------------------------
    rf_contact_y = 77.3
    rf_contact_z = 14.5   # FIX: guide_z+0.3=13.89 invadia el cuerpo
    # del movil (1.435mm3 verificado) -- el cuerpo del pin (radio
    # 0.9mm) dipaba por debajo del techo real del telefono (Z=13.44).
    # Subido hasta liberar el movil mientras sigue tocando la lamina
    # (0.014mm3 de contacto real verificado, suficiente para un
    # pogo-pin precargado).
    rf_contact_pin_y = cav_h / 2 + WALL - 1.8   # posicion real de montaje, con precarga de muelle ya verificada
    rf_housing_y_top = cav_h / 2 + WALL - 1.0   # cerca del borde superior real, para poder insertar el pin desde fuera
    rf_contact_housing = (
        cq.Workplane("XZ")
        .center(0, rf_contact_z)
        .workplane(offset=-rf_housing_y_top)
        .circle(1.1)
        .extrude(rf_housing_y_top - (rf_contact_y - 2.0))
    )
    body = body.cut(rf_contact_housing)

    # ---------------------------------------------------------------
    # CONTACTO RF DE CAMARA -- misma logica que el de pantalla: un
    # pogo-pin fijo en el FRAME, que la propia corredera de camara
    # presiona SOLO cuando esta en posicion CUBRIENDO (cerrada) --
    # cuando esta escondida (abierta), el pin no toca nada. Sin este
    # contacto, la corredera (PA12 normal, no conductor) tapa la luz
    # pero deja una fuga electrica real en ese punto.
    # FIX CRITICO: la posicion original (X=-5.2, Y=68) caia DENTRO de
    # la huella real del bulto del movil (35x35 con centro en
    # cam_center=-15.2,54.8) -- el margen entre el plato (37x37) y el
    # bulto es de solo 1mm, insuficiente para el pin. Verificado que
    # chocaba con el movil (3.44mm3) en los DOS estados. Se añadio una
    # pestaña al plato (ver build_camera_shutter_slider) que sobresale
    # en X mas alla del propio borde del bulto (X=2.3), y el contacto
    # se mueve a esa pestaña.
    # ---------------------------------------------------------------
    cam_contact_x = cam_shutter_ref_x + 19.2   # dentro de la pestaña (X real -0.2 a 4.8), fuera del bulto (borde en 2.3)
    cam_contact_y = cam_center_y   # centro de la pestaña, coincide con el centro del plato cuando esta CERRADO
    cam_contact_z_bottom = 0.9   # 0.2mm de precarga sobre el plato (Z=1.1)
    cam_contact_housing = (
        cq.Workplane("XY")
        .center(cam_contact_x, cam_contact_y)
        .circle(0.75)
        .extrude(4.3 - cam_contact_z_bottom + 3.0)
        .translate((0, 0, cam_contact_z_bottom))
    )
    body = body.cut(cam_contact_housing)

    # ---------------------------------------------------------------
    # CONTACTO RF DE MICROFONO -- REDISEÑADO para la banda curva. El
    # pin toca la banda en un punto del arco (theta=15, safe dentro
    # de la zona SOLO-cubriendo [0,35), antes de la zona compartida
    # con el repliegue [35,40]) -- solo hay contacto cuando la banda
    # esta realmente tapando los agujeros.
    # ---------------------------------------------------------------
    mic_contact_theta = 15.0
    mic_contact_y, mic_contact_z = mic_arc_point(mic_contact_theta)
    mic_contact_x = mic_pinion_x
    mic_contact_z_bottom = mic_contact_z - 0.1   # 0.1mm de precarga
    mic_contact_housing = (
        cq.Workplane("XY")
        .center(mic_contact_x, mic_contact_y)
        .circle(0.75)
        .extrude(4.5)
        .translate((0, 0, mic_contact_z_bottom))
    )
    body = body.cut(mic_contact_housing)

    dims = dict(ext_w=ext_w, ext_h=ext_h, ext_t=ext_t, cav_w=cav_w, cav_h=cav_h,
                cam_center_x=cam_center_x, cam_center_y=cam_center_y,
                cam_hinge_y=cam_hinge_y, speaker_y=speaker_y, mic_hinge_y=mic_hinge_y,
                guide_h=guide_h, guide_z=guide_z, roller_y=roller_y,
                roller_len=roller_len, hinge_z=hinge_z, pinion_x=pinion_x,
                switch_z=switch_z, button_stem_len=button_stem_len,
                ext_bottom_y=ext_bottom_y, CHIN_H=CHIN_H,
                mic_pinion_x=mic_pinion_x, mic_z_offset=mic_z_offset,
                mic_gear_x=mic_gear_x, mic_gear_y=mic_gear_y, mic_gear2_z=mic_gear2_z,
                mic_center_y=mic_center_y, mic_center_z=mic_center_z,
                mic_drive_a=drive_a, mic_drive_b=drive_b,
                mic_pinion_x_r=mic_pinion_x_r, mic_gear_x_r=mic_gear_x_r, mic_gear_y_r=mic_gear_y_r,
                mic_gear2_z_r=mic_gear2_z_r, mic_center_y_r=mic_center_y_r, mic_center_z_r=mic_center_z_r,
                mic_drive_a_r=drive_a_r, mic_drive_b_r=drive_b_r,
                speaker_z=speaker_z, LEFT_X=LEFT_X, RIGHT_X=RIGHT_X,
                center_x=center_x, conduit_x=conduit_x, conduit_z=conduit_z,
                crank_r=crank_r, conduit_y_min=conduit_y_min, conduit_y_max=conduit_y_max,
                gear_r1=gear_r1, gear_r2=gear_r2,
                cam_shutter_ref_x=cam_shutter_ref_x, cam_gear_x=cam_gear_x,
                cam_gear_y=cam_gear_y, cam_low_z=cam_low_z, cam_gear_z=cam_gear_z,
                cam_gear1_z=cam_gear1_z,
                cam_travel=cam_travel, cutout_bottom=cutout_bottom,
                rf_contact_y=rf_contact_y, rf_contact_z=rf_contact_z, rf_contact_pin_y=rf_contact_pin_y,
                cam_contact_x=cam_contact_x, cam_contact_y=cam_contact_y, cam_contact_z_bottom=cam_contact_z_bottom,
                mic_contact_x=mic_contact_x, mic_contact_y=mic_contact_y, mic_contact_z_bottom=mic_contact_z_bottom,
                usb_port_w=USB_PORT_W, usb_port_h=USB_PORT_H, usb_port_z_center=usb_port_z_center,
                usb_y_inner=usb_y_inner, usb_y_outer=usb_y_outer)

    # ---------------------------------------------------------------
    # CARRILES CAPTURADOS (Hoja 11 S9 / Hoja 12 S5): las lengüetas-guia
    # que ya tenian la corredera de camara y la ventana de microfono
    # no tenian ninguna ranura del lado del Frame que las capturase --
    # solo un bolsillo abierto, sin nada que impidiera que la pieza se
    # levantara fuera de su plano (verificado: ~3.4mm libres por
    # encima del plato de camara). Se añade un labio de retencion real
    # para cada una, recortado contra el barrido COMPLETO del propio
    # mecanismo (piñon, engranaje reductor, plato/ventana en TODO su
    # recorrido, no solo en los extremos) para garantizar 0mm3 de
    # colision pase lo que pase.
    # ---------------------------------------------------------------
    def _swept(build_fn, translate_fn, n=12):
        shape = None
        for i in range(n):
            t = i / (n - 1)
            piece = translate_fn(build_fn(), t)
            shape = piece if shape is None else shape.union(piece)
        return shape

    # -- Camara: labios a izquierda y derecha del plato --
    # OJO: solo hay 0.5mm libres entre el plato (Z=1.1) y donde
    # empieza a asentar el propio movil (Z=WALL=1.6) -- un primer
    # intento con CLEAR=0.25/T=0.5 invadia ese hueco (verificado con
    # una maqueta simple del movil: colision real contra el labio) y
    # empujaba/asomaba el telefono. Valores reducidos para quedar
    # siempre por debajo de WALL con margen.
    SHUTTER_W_RAIL = 37.0
    rail_x_local = SHUTTER_W_RAIL / 2 + 0.3
    plate_top_z = cam_low_z + 0.8
    CAM_LIP_W, CAM_LIP_T, CAM_LIP_CLEAR = 1.4, 0.25, 0.15
    # ancla mas alla del propio bolsillo cam_clear (Y=-6.1..74.9) para
    # que el labio quede soldado a la pared solida real en sus dos
    # extremos, no flotando dentro del hueco
    cam_lip_y_min, cam_lip_y_max = -8.0, 77.0

    cam_lip_raw = None
    for side in (-1, 1):
        rx = cam_shutter_ref_x + side * rail_x_local
        piece = (
            cq.Workplane("XY")
            .workplane(offset=plate_top_z + CAM_LIP_CLEAR)
            .center(rx, (cam_lip_y_min + cam_lip_y_max) / 2)
            .rect(CAM_LIP_W, cam_lip_y_max - cam_lip_y_min)
            .extrude(CAM_LIP_T)
        )
        cam_lip_raw = piece if cam_lip_raw is None else cam_lip_raw.union(piece)

    cam_shutter_swept = _swept(
        lambda: build_camera_shutter_slider(dims),
        lambda p, t: p.translate((cam_shutter_ref_x, cam_center_y - t * cam_travel, 0)),
    )
    cam_gear_fixed = build_camera_reducer_gear(dims).translate((cam_gear_x, cam_gear_y, 0))
    cam_lip = cam_lip_raw.cut(cam_shutter_swept).cut(cam_gear_fixed)
    # AVISO: temporalmente DESACTIVADO. Al bajar cam_low_z a -2.9 (fix
    # critico de la colision real con el bulto, ver mas arriba), el
    # anclaje de este labio (que se apoyaba en pared generica del
    # cuerpo mas alla del bolsillo) dejo de funcionar -- a esta
    # profundidad (Z negativa) solo hay material solido bajo el
    # propio reborde de camara (camera_rim), no en el resto de la
    # pared general, y el propio reborde no cubre todo el recorrido
    # en Y que barre la corredera. Union desactivada para no dejar
    # piezas sueltas sin conectar (2 solidos en vez de 1, detectado y
    # verificado). Pendiente: rediseñar el anclaje apoyandolo contra
    # el propio camera_rim/bezel en vez de contra pared generica.
    _ = cam_lip  # noqa: conservado para cuando se rediseñe el anclaje
    # body = body.union(cam_lip)  # desactivado, ver aviso arriba

    # ---------------------------------------------------------------
    # TECHO DE PROTECCION DEL PUENTE DE CAMARA (riser): a diferencia
    # del hueco principal del objetivo (que SIEMPRE tiene algo detras
    # -- la propia lente del movil, o la corredera cuando cubre), el
    # puente que sube desde el plato hasta el engranaje es una barra
    # delgada (6mm) que solo ocupa una fraccion pequeña de su propio
    # recorrido (70mm) en cada instante -- el resto del tiempo esa
    # franja en la piel real queda simplemente ABIERTA, sin nada
    # detras, un boquete real sin ninguna funcion (verificado con la
    # auditoria de piel: 84mm3 en Z=[0,0.2], toda la franja). Se
    # añade un suelo protector MAS ALLA de donde llega el puente
    # (fuera de su barrido real, sin tocarlo) para que quede encerrado
    # detras de una pared, igual que el objetivo detras del reborde
    # principal, en vez de expuesto al aire.
    # ---------------------------------------------------------------
    riser_x_min, riser_x_max = cam_gear_x + gear_r2 - 5.0, cam_gear_x + gear_r2 + 6.5
    riser_floor = (
        cq.Workplane("XY")
        .workplane(offset=-3.3)
        .center((riser_x_min + riser_x_max) / 2, 30.8)
        .rect(riser_x_max - riser_x_min, 76.0)
        .extrude(3.3)
    )
    riser_floor = riser_floor.cut(cam_shutter_swept).cut(cam_gear_fixed)
    body = body.union(riser_floor)

    # ---------------------------------------------------------------
    # REPONER EL REBORDE DE PROTECCION DE CAMARA (encontrado real):
    # el bolsillo de deslizamiento de la corredera (cam_clear), al
    # ensancharse para dar sitio al puente hasta la pared, tambien
    # cortaba el reborde de proteccion por el lado derecho de la
    # camara -- dejaba un boquete real ahi, sin nada detras salvo
    # cuando la corredera pasa justo por ese punto (verificado:
    # material=0 en ese lado a cualquier Z). Se repone el reborde
    # entero AQUI, despues de todos los cortes de mecanismo, quitando
    # solo por donde la corredera/puente realmente necesitan pasar.
    # ---------------------------------------------------------------
    camera_rim_final = camera_rim.cut(cam_shutter_swept).cut(cam_gear_fixed)
    body = body.union(camera_rim_final)

    # ---------------------------------------------------------------
    # CARA DE OBJETIVOS, IMPRESA -- FIX REAL: la primera version solo
    # tapaba la zona del bulto (35x35mm), pero la corredera recorre
    # una franja MUCHO mayor (verificado con el barrido completo:
    # x=[-45.77,4.80], y=[-4.15,73.3]) para poder esconderse en modo
    # ONLINE lejos del objetivo. Fuera de la zona del bulto no habia
    # nada tapando eso -- boquete real confirmado. Ahora la cara
    # cubre TODO ese recorrido, no solo el bulto, con margen.
    # ---------------------------------------------------------------
    lens_face_z = -BACK_SLAB_EXTRA
    # FIX (pedido expreso: "la lamina que tapa la camara se ve un
    # corte con forma de medio ovalo rectangulo, hazla lisa toda"):
    # el panel anterior sobresalia 0.3mm mas alla de la plancha
    # trasera con su PROPIO contorno redondeado (fillet 3.0), sin
    # relacion con nada mas alrededor -- ese doble contorno era el
    # corte visible. PERO la cobertura amplia en si SI hacia falta de
    # verdad (comprobado: sin ella, la pared queda realmente abierta
    # en la zona donde la persiana se esconde en modo ONLINE, lejos
    # del bulto). Ahora el panel se reconstruye A RAS de la plancha
    # trasera (misma profundidad, ni un poco mas atras) y SIN su
    # propio redondeo -- al quedar exactamente al mismo nivel que la
    # superficie que ya existe alrededor, se funde con ella sin dejar
    # ningun borde/costura nueva visible.
    face_x_min, face_x_max = -47.5, 6.5
    face_y_min, face_y_max = -6.0, 75.0
    lens_face = (
        cq.Workplane("XY")
        .workplane(offset=lens_face_z + 0.3)
        .center((face_x_min + face_x_max) / 2, (face_y_min + face_y_max) / 2)
        .rect(face_x_max - face_x_min, face_y_max - face_y_min)
        .extrude(-0.3)
    )
    lens_hole = (
        cq.Workplane("XY")
        .workplane(offset=lens_face_z)
        .center(cam_center_x, cam_center_y)
        .rect(CAM_BUMP_SIZE - 6.0, CAM_BUMP_SIZE - 6.0)
        .extrude(0.3)
        .edges("|Z")
        .fillet(4.0)
    )
    lens_face = lens_face.cut(lens_hole)

    # NOTA: la banda curva del microfono ya NO necesita un labio de
    # retencion aparte -- al deslizar dentro de un canal curvo hecho a
    # su medida (en vez de un bolsillo recto sobredimensionado), el
    # propio canal la captura por construccion, igual que un cajon
    # curvo en su guia. Verificado sin colision en la seccion de
    # arriba. Se guarda igualmente el barrido completo (0 a
    # MIC_BAND_TOTAL_ARC) para que la auditoria de piel de mas abajo
    # no intente rellenar el hueco por el que gira.
    mic_band_swept = _swept(
        lambda: build_mic_curved_band(dims, 0.0),
        lambda p, t: build_mic_curved_band(dims, t * MIC_BAND_EXTRA),
        n=10,
    )
    mic_band_swept_r = _swept(
        lambda: build_mic_curved_band(dims, 0.0, side="R"),
        lambda p, t: build_mic_curved_band(dims, t * MIC_BAND_EXTRA, side="R"),
        n=10,
    )
    mic_gear_fixed_r = build_mic_reducer_gear(dims).translate((dims["mic_gear_x_r"], dims["mic_gear_y_r"], 0))

    # ---------------------------------------------------------------
    # AUDITORIA AUTOMATICA DE PIEL EXTERIOR: compara el cuerpo final
    # contra la forma prevista (bloque bruto sin cortar, y esa misma
    # forma ya con cavidad+camara+botones+USB+rejilla pero SIN ningun
    # canal interno de mecanismo) para detectar cualquier punto donde
    # la piel exterior real quede perforada o mas fina de lo previsto
    # -- el mismo tipo de fallo que causo el hueco de la esquina
    # (Hoja original, ya corregido y verificado), comprobado ahora en
    # TODA la superficie exterior, no solo ahi. Cualquier resto
    # detectado se rellena automaticamente, salvo las aberturas
    # exteriores legitimas (empuñadura del interruptor, ventana de
    # microfono) que se excluyen explicitamente.
    # ---------------------------------------------------------------
    outer_skin = outer_envelope.shell(-0.2)
    intended_removed = outer_envelope.cut(shape_reference)
    must_be_solid_skin = outer_skin.cut(intended_removed)
    exterior_gap = must_be_solid_skin.cut(body)
    # excluir aberturas exteriores legitimas, ya cortadas DESPUES de
    # capturar shape_reference (no cuentan como fallo):
    exterior_gap = exterior_gap.cut(button_hole_exterior())
    # excluir tambien cualquier zona que el propio mecanismo (ya
    # construido mas arriba para los carriles) necesite de verdad --
    # sin esto, el parche automatico puede rellenar lo que en
    # realidad es el hueco correcto para el piñon/cremallera del
    # interruptor o el giro de la banda de microfono, y crear una
    # colision nueva
    switch_swept = _swept(
        lambda: build_main_carriage_switch(),
        lambda p, t: p.translate((pinion_x, roller_y - t * SWITCH_TRAVEL, hinge_z)),
        n=6,
    )
    exterior_gap = exterior_gap.cut(cam_gear_fixed).cut(switch_swept).cut(mic_band_swept).cut(cam_shutter_swept)
    exterior_gap = exterior_gap.cut(mic_band_swept_r).cut(mic_gear_fixed_r)
    body = body.union(exterior_gap)

    # parche puntual final: quedaba una franja de piel real (~2.18mm3,
    # X=-45.3 a -45.1, Y=17.25-22.75, Z=10.1-12.22, pared izquierda)
    # que la auditoria automatica no podia rellenar de forma general
    # sin arriesgar tocar al engranaje -- verificado que este parche
    # puntual, mas pequeño y en Y fuera del rango del engranaje
    # (Y=25.2-36.4), no choca con nada
    # NOTA: aqui habia un left_wall_patch fijo en X=-45.2 -- parcheaba
    # un punto de piel fina que existia con la pared antigua
    # (LEFT_X=-45.3, EXTRA_WALL_LEFT=5.0). Ahora que la pared se
    # ensancho (EXTRA_WALL_LEFT=10.0, LEFT_X=-50.3) para dar sitio de
    # verdad al engranaje de camara, ese punto exacto ya no existe
    # (quedaba flotando, desconectado -- verificado: 2 solidos en vez
    # de 1). Quitado; la auditoria automatica de piel de mas abajo
    # revisa toda la superficie de nuevo con la pared actual.

    # AVISO: se probo un parche aqui para una burbuja interna
    # pequeña y aislada (98mm3) encontrada cerca de la empuñadura del
    # interruptor -- pero el propio parche, pese a ser pequeño y
    # localizado, hacia desaparecer material real en zonas
    # completamente distintas de la funda (verificado y reproducido:
    # ej. en X=20,Y=-20 habia material antes del parche y desaparecia
    # despues, sin ninguna relacion geometrica directa -- efecto
    # secundario real del motor de CAD, no del propio parche en si).
    # Revertido: la burbuja pequeña sigue pendiente de una solucion
    # que no tenga este efecto secundario.

    # ---------------------------------------------------------------
    # REMATE SUPERIOR (pedido expreso): el menton de abajo (12.6mm de
    # grosor extra, mecanismos) dejaba la funda muy descompensada
    # visualmente frente a un borde superior de solo WALL=1.6mm. Este
    # remate es puramente estetico (nada de mecanismo real ahi) --
    # añadido aqui, DESPUES de la auditoria automatica de piel
    # exterior, porque esa auditoria (shell() sobre el bloque inicial)
    # es muy fragil y fallaba si se intentaba cambiar el propio
    # rectangulo base en vez de añadir esto por separado.
    TOP_CAP = 9.0   # FIX (pedido expreso): con 4.0 el borde superior se
    # estrechaba demasiado rapido (86mm de ancho real en el borde, vs
    # 96mm que mantiene el menton inferior con su propio recorrido mas
    # largo) -- pedido explicito de que quede "casi simetrico" con el
    # ancho de abajo. Ampliado para dar mas recorrido recto antes de
    # que la esquina redondeada empiece a estrechar.
    # FIX CRITICO DE FONDO (foto real del usuario, tercer intento):
    # los dos intentos anteriores usaban un radio de esquina DISTINTO
    # al del resto de la funda (1.5mm, luego ~4.85mm) -- por mucho
    # que se ajustara, dos curvas con radios distintos NUNCA encajan
    # sin un pliegue visible en la costura, por pura geometria. La
    # unica forma de que quede una silueta continua de verdad es usar
    # EXACTAMENTE el mismo radio (CASE_CORNER_R=11) en toda la altura,
    # solapando bien dentro de la zona donde el cuerpo principal YA
    # esta redondeando su propia esquina (siempre causo el problema
    # anterior: esa misma zona es donde la camara necesita espacio
    # libre, hasta Y=73.3 -- verificado con su propio barrido). Esta
    # vez, en vez de arrancar el remate mas arriba para esquivar a la
    # camara (lo que rompia el radio), se dejaesharp el remate con el
    # radio correcto y en su lugar se le talla un hueco de despeje
    # justo con la forma/tamaño real de la camara, para las dos cosas
    # a la vez: costura perfecta Y camara libre.
    top_cap_piece = (
        cq.Workplane("XY")
        .workplane(offset=-BACK_SLAB_EXTRA)
        .center(center_x, cav_h / 2 + WALL + TOP_CAP / 2 - 0.05 - 15.0)
        .rect(ext_w, TOP_CAP + 0.1 + 30.0)
        .extrude(ext_t + BACK_SLAB_EXTRA)
        .edges("|Z")
        .fillet(CASE_CORNER_R)
    )
    cam_clear_for_cap = cam_clear.intersect(
        cq.Workplane("XY")
        .center(center_x, 20)
        .rect(ext_w - 3.0, 200)
        .extrude(30)
        .translate((0, 0, -10))
    )
    top_cap_piece = top_cap_piece.cut(cam_clear_for_cap)
    # FIX CRITICO GRAVE (foto/aviso real del usuario: "no cabe el
    # movil"): el bloque del remate rellenaba parte de la propia
    # cavidad del telefono (Y=51.8 a 80, verificado con el propio
    # movil de referencia -- 14303mm3 de colision real). Faltaba
    # restar la cavidad tambien de esta pieza, igual que ya se hace
    # con el cuerpo principal.
    top_cap_piece = top_cap_piece.cut(cavity)
    body = body.union(top_cap_piece)

    # FIX (pedido expreso): aunque el remate ya es geometricamente UN
    # solo solido (union real, no piezas sueltas), las caras donde se
    # unieron piezas por separado (remate, plancha trasera) seguian
    # mostrando una linea de costura visible en el visor CAD -- normal
    # en operaciones boolean, aunque el resultado sea perfectamente
    # continuo. clean() fusiona las caras coincidentes/tangentes para
    # que no quede ningun rastro visible de la costura.
    body = body.clean()

    # UNION DIFERIDO DE LA CARA DE OBJETIVOS (pedido expreso: la
    # persiana de la camara se veia con un corte). Se añade aqui, al
    # final de TODO el proceso, para que ningun corte posterior pueda
    # quitarle material -- se habia comprobado que algo en medio del
    # proceso (con el mismo Z de arranque que cam_cut) se comia la
    # mayor parte de su grosor si se añadia antes.
    body = body.union(lens_face)

    body = body.clean()

    return body, dims


# ---------------------------------------------------------------
# 3. LAMINA RF ENROLLABLE + BARRA TIRADORA
# ---------------------------------------------------------------
def build_rf_fabric_and_pullbar(dims):
    w = dims["cav_w"] - 2 * (CHANNEL_D + 0.4)
    deployed_h = dims["guide_h"] - 12

    fabric = cq.Workplane("XY").rect(w, deployed_h).extrude(FABRIC_THK)

    def side_tab(x_sign):
        x0 = x_sign * (w / 2)
        tab_w = CHANNEL_W - 0.5
        offset = CHANNEL_D / 2 + 0.15   # FIX: con +0.4 la pestaña se
        # pasaba 0.45mm del borde real de la cavidad (cav_w/2)
        return (
            cq.Workplane("XY")
            .center(x0 + x_sign * offset, 0)
            .rect(tab_w, deployed_h - 4)
            .extrude(CHANNEL_D - 0.25)
        )

    fabric = fabric.union(side_tab(-1)).union(side_tab(1))

    # barra rigida en el borde superior de la lamina (le da rigidez
    # para que el empuje del rodillo se transmita en linea recta).
    # FIX CRITICO: media w+6 (80.6mm), llegando hasta X=+-40.3 --
    # cuando ensanche la pared izquierda para el conducto de camara,
    # esa medida paso a invadir directamente la pared ya solida ahi
    # (verificado: 85.65mm3 de colision real). Ahora se queda dentro
    # de la propia cavidad (w, no w+6).
    pullbar = (
        cq.Workplane("XY")
        .center(0, deployed_h / 2 + PULLBAR_H / 2)
        .rect(w, PULLBAR_H)
        .extrude(PULLBAR_THK)
        .edges("|Z")
        .fillet(1.5)
    )
    return fabric.union(pullbar)


# ---------------------------------------------------------------
# 3b. MECANISMO REAL DE LA LAMINA RF FRONTAL (encontrado real: antes
# no tenia NINGUNA conexion mecanica -- solo dos dibujos estaticos
# distintos segun el modo, sin engranaje ni cremallera entre ellos).
# Calculo: el eje real gira 3.067 rad (176 grados); para enrollar los
# 144.6mm de lamina en un carrete razonable (radio 3mm, 7.67 vueltas)
# hace falta amplificar el giro 15.7 veces -- demasiado para una sola
# etapa (un engranaje de 31mm de diametro no cabe en el menton, solo
# 12.6mm de alto). Repartido en dos etapas de ~4:1 cada una, mismo
# principio ya verificado en la reduccion de la manivela de camara.
# ---------------------------------------------------------------
FABRIC_TAP_X = 0.0   # punto libre del eje (piñon principal en -30.1,
# micro L en -16, micro R en +16 -- el centro esta libre)
FABRIC_SPOOL_R = 3.0
FABRIC_GEAR_SMALL = 1.0
FABRIC_GEAR_BIG = 3.96


def build_rf_fabric_drive_piece_a(dims):
    # PIEZA A: piñon pequeño que toca el eje real (rigido con el, gira
    # a la misma velocidad) + engranaje grande coaxial (mismo eje X,
    # distinto radio) -- mismo principio ya verificado en la
    # reduccion de la manivela de camara.
    x0 = FABRIC_TAP_X
    small = (
        cq.Workplane("YZ")
        .workplane(offset=x0)
        .center(dims["roller_y"], dims["hinge_z"])
        .circle(FABRIC_GEAR_SMALL)
        .extrude(1.8)
    )
    big = (
        cq.Workplane("YZ")
        .workplane(offset=x0 + 1.8)
        .center(dims["roller_y"], dims["hinge_z"])
        .circle(FABRIC_GEAR_BIG)
        .extrude(1.5)
    )
    return small.union(big)


def build_rf_fabric_drive_piece_b(dims):
    # PIEZA B: eje intermedio -- desplazado en Y (no en Z, ahi no hay
    # apenas margen entre el eje y el borde delantero real) para que
    # su piñon pequeño toque el engranaje grande de la pieza A.
    x0 = FABRIC_TAP_X
    mesh_y = dims["roller_y"] + FABRIC_GEAR_BIG + FABRIC_GEAR_SMALL - 0.3
    mesh_z = dims["hinge_z"]
    small = (
        cq.Workplane("YZ")
        .workplane(offset=x0 + 1.8)
        .center(mesh_y, mesh_z)
        .circle(FABRIC_GEAR_SMALL)
        .extrude(1.8)
    )
    big = (
        cq.Workplane("YZ")
        .workplane(offset=x0)
        .center(mesh_y, mesh_z)
        .circle(FABRIC_GEAR_BIG)
        .extrude(1.5)
    )
    return small.union(big), mesh_y, mesh_z


def build_rf_fabric_drive_piece_c(dims, mesh_y_b, mesh_z_b):
    # PIEZA C: el propio carrete -- otro desplazamiento en Y hasta
    # llegar cerca de la altura real donde vive la lamina (guide_z),
    # con un ultimo tramo corto en Z para el enganche final.
    x0 = FABRIC_TAP_X
    mesh_y = mesh_y_b + FABRIC_GEAR_BIG + FABRIC_GEAR_SMALL - 0.3
    mesh_z = mesh_z_b
    small = (
        cq.Workplane("YZ")
        .workplane(offset=x0)
        .center(mesh_y, mesh_z)
        .circle(FABRIC_GEAR_SMALL)
        .extrude(1.8)
    )
    spool_len = dims["cav_w"] - 2 * (CHANNEL_D + 0.4) + 1.5
    spool = (
        cq.Workplane("YZ")
        .workplane(offset=-spool_len / 2)
        .center(mesh_y, mesh_z)
        .circle(FABRIC_SPOOL_R)
        .extrude(spool_len)
    )
    return small.union(spool), mesh_y, mesh_z


# ---------------------------------------------------------------
# 4. EJE DEL RODILLO (varilla metalica, se compra)
# ---------------------------------------------------------------
def build_roller_axle(dims):
    length = dims["roller_len"] - 2.0
    axle = cq.Workplane("YZ").circle(AXLE_DIA / 2).extrude(length)
    slot = (
        cq.Workplane("YZ")
        .center(0, AXLE_DIA / 2 - 0.3)
        .rect(1.2, 0.9)
        .extrude(length)
    )
    return axle.cut(slot)


# ---------------------------------------------------------------
# 5. PIÑON (en un extremo del eje) + CREMALLERA-BOTON
# (misma geometria verificada en la v4, aislada del problema de la
# bisagra -- aqui el piñon NO se mueve de sitio, solo gira)
# ---------------------------------------------------------------
def build_pinion_gear():
    # FIX CRITICO: antes se construia en XY (giro nativo Z) y se
    # rotaba -90 sobre X para "llevarlo" a Y -- pero el eje del
    # rodillo gira en X, no en Y. Ahora se construye DIRECTAMENTE en
    # el plano YZ: su giro nativo ya es X, coincidiendo de verdad con
    # el eje del rodillo. Verificado con bounding box antes de seguir.
    gear = cq.Workplane("YZ").circle(PINION_DIA / 2).extrude(PINION_THK)
    teeth = None
    for i in range(PINION_TEETH):
        ang = 2 * math.pi * i / PINION_TEETH
        r = PINION_DIA / 2
        tooth = (
            cq.Workplane("YZ")
            .moveTo(r * math.cos(ang), r * math.sin(ang))
            .lineTo((r + RACK_TOOTH_DEPTH) * math.cos(ang + 0.10), (r + RACK_TOOTH_DEPTH) * math.sin(ang + 0.10))
            .lineTo(r * math.cos(ang + 0.20), r * math.sin(ang + 0.20))
            .close()
            .extrude(PINION_THK)
        )
        teeth = tooth if teeth is None else teeth.union(tooth)
    gear = gear.union(teeth)
    return gear


def build_main_carriage_switch():
    # SUSTITUYE a los dos botones CERRAR/ABRIR independientes por UN
    # UNICO interruptor cautivo -- exigencia explicita del documento
    # de arquitectura (Hoja 8: "un unico grado de libertad... quedan
    # expresamente prohibidos botones secundarios") y de la imagen de
    # referencia (un solo deslizador ranurado, no dos pulsadores).
    #
    # Mismo patron de cremallera cautiva ya verificado en el
    # microfono (dientes engranados por los dos lados, se mueve sola
    # en ambos sentidos con el propio giro del piñon -- nunca hace
    # falta empujarla desde fuera en las dos direcciones porque nunca
    # se desengancha).
    # FIX REDISEÑO: antes la cremallera crecia simetrica (+-RACK_LEN/2);
    # asi el extremo negativo (de donde cuelgan jog/vastago/empuñadura)
    # se desplazaba al alargar RACK_LEN, sacando la empuñadura de la
    # funda (verificado: un primer intento con RACK_LEN=47 la mandaba a
    # Y=-156). Ahora el extremo negativo se queda FIJO (RACK_NEG_ANCHOR,
    # la misma distancia de siempre) y la cremallera crece solo hacia
    # el lado positivo -- que es el que queda dentro del menton real.
    RACK_NEG_ANCHOR = 1.0
    n_teeth = max(3, int(RACK_LEN / RACK_TOOTH_PITCH))
    rack = (
        cq.Workplane("XZ")
        .center(PINION_THK / 2, 2.0)
        .workplane(offset=RACK_NEG_ANCHOR)
        .rect(PINION_THK, 1.2)
        .extrude(-RACK_LEN)
    )
    teeth = None
    for i in range(n_teeth):
        y0 = -RACK_NEG_ANCHOR + i * RACK_TOOTH_PITCH + RACK_TOOTH_PITCH / 2
        tooth = (
            cq.Workplane("YZ")
            .moveTo(y0 - RACK_TOOTH_PITCH * 0.3, 1.5)
            .lineTo(y0, 1.5 + RACK_TOOTH_DEPTH)
            .lineTo(y0 + RACK_TOOTH_PITCH * 0.3, 1.5)
            .close()
            .extrude(PINION_THK)
        )
        teeth = tooth if teeth is None else teeth.union(tooth)
    rack = rack.union(teeth)

    # FIX CRITICO (reposicionamiento): el primer intento subia el
    # tramo largo pegado al piñon (X interior, dentro de la propia
    # huella del movil) y solo saltaba a la pared al final -- chocaba
    # con el cuerpo del telefono en todo el tramo intermedio (879mm3
    # verificado). Ahora el salto a la pared se hace INMEDIATAMENTE
    # despues de los dientes, y el tramo largo sube ya pegado a la
    # pared (fuera de la huella del movil, que llega hasta X=-38.35).
    grip_x_local = -20.65   # FIX: recalculado -- mismo ajuste que arriba, la pestaña no llegaba a sobresalir de la pared
    # (LEFT_X=-50.3, ensanchada para la camara y luego simetrizada) --
    # -30.1+(-19.2)=-49.3 global, justo dentro de la pared real
    # FIX CRITICO REAL (encontrado con fotos del usuario): el vastago
    # entero corria pegado a la pared (a 1mm) en TODA su longitud
    # (~100mm) -- el canal que lo aloja (combined_channel) tenia que
    # llegar hasta ahi tambien, y eso significaba cortar la pared
    # real en TODO ese largo, dejando el vastago visible por fuera en
    # toda su longitud (verificado con sonda: pared abierta de
    # Y=-88 a Y=10). Ahora el vastago corre a una X mas segura
    # (stem_x_local, con margen real a la pared) en la mayor parte de
    # su recorrido, y solo gira hacia la pared verdadera en el ultimo
    # tramo, justo donde esta la propia empuñadura.
    stem_x_local = -14.0   # -30.1+(-14.0)=-44.1 global, 6.2mm de
    # margen real a la pared (-50.3) en vez de 1mm
    jog_near = (
        cq.Workplane("XZ")
        .center((PINION_THK / 2 + stem_x_local) / 2, 2.0)
        .workplane(offset=-RACK_NEG_ANCHOR)
        .rect(abs(PINION_THK / 2 - stem_x_local) + 2 * SLIDING_CLEARANCE + 1.6, BUTTON_H * 0.8)
        .extrude(-3.0)
    )
    rack = rack.union(jog_near)

    grip_y = RACK_NEG_ANCHOR + SWITCH_STEM_LEN
    JOG_FAR_LEN = 6.0   # tramo final donde el vastago gira hacia la pared real
    stem = (
        cq.Workplane("XZ")
        .center(stem_x_local, 2.0)
        .workplane(offset=-RACK_NEG_ANCHOR - 3.0)
        .rect(PINION_THK, BUTTON_H * 0.8)
        .extrude(-(SWITCH_STEM_LEN - 3.0 - JOG_FAR_LEN))
    )
    rack = rack.union(stem)

    jog_far_end_x = grip_x_local + 1.5   # se queda por dentro de la
    # pared -- solo la propia pestaña (pieza separada) debe asomar,
    # el travesaño de conexion no, para no crear una costura visible
    # con una seccion distinta a la de la pestaña
    jog_far = (
        cq.Workplane("XZ")
        .center((stem_x_local + jog_far_end_x) / 2, 0.78)
        .workplane(offset=-(RACK_NEG_ANCHOR + 3.0 + (SWITCH_STEM_LEN - 3.0 - JOG_FAR_LEN)))
        .rect(abs(stem_x_local - jog_far_end_x) + 2 * SLIDING_CLEARANCE + 0.6, 2.6)
        .extrude(-JOG_FAR_LEN)
        .edges("|Y")
        .fillet(0.3)
    )
    rack = rack.union(jog_far)

    # FIX REAL DE FONDO: los intentos anteriores tenian los ejes
    # cambiados -- crei que rect() controlaba el largo (Y) y extrude
    # el saliente (X), pero es al reves: en un workplane "XZ",
    # rect(A,B) controla ancho en X y alto en Z, y extrude() controla
    # el propio largo en Y. Verificado con una prueba directa antes
    # de este cambio. Por eso "alargar la pestaña" en intentos
    # anteriores en realidad la ensanchaba en X (mas saliente, no mas
    # larga), y viceversa -- de ahi los huecos sin cubrir que no
    # cuadraban con las cuentas.
    grip_total_len = SWITCH_TRAVEL + SWITCH_GRIP_LEN + 10.0   # tapa el
    # hueco entero en cualquier posicion, con margen real
    grip_protrusion = 0.9   # pedido expreso: mismo saliente que los
    # con la corredera de camara): antes 3.6mm y una capsula gruesa
    # redondeada (como una pastilla en un palo) -- ahora una LAMINA
    # fina y plana, mismo principio que build_camera_shutter_slider
    # (una placa plana, no un cilindro).
    GRIP_LEN = 8.0   # pedido expreso: pestaña pequeña como los botones,
    # no la version larga (antes SWITCH_GRIP_LEN+5.0=16mm) -- la
    # cobertura del hueco ya la da la lamina interior por separado
    # FIX (pedido expreso: "rectangular pero con cantos redondeados
    # esteticas soft como los otros botones"): antes se extruia desde
    # una seccion transversal X-Z y solo se redondeaban los 2 bordes
    # largos (|Y) -- los 2 extremos cortos (las tapas Y) quedaban
    # totalmente cuadrados/afilados, dando el aspecto de "un
    # rectangulo que corta la pestaña" justo en esas puntas. Ahora se
    # construye el perfil 2D en el plano Y-Z (la cara que realmente
    # se ve desde fuera, largo x alto) con las 4 esquinas redondeadas
    # de verdad, y se extruye en X (la profundidad/saliente) --
    # capsula/pastilla suave por los 4 lados, igual que el resto de
    # botones.
    grip = (
        cq.Workplane("YZ")
        .workplane(offset=grip_x_local - grip_protrusion / 2)
        .center(grip_y, -0.22)
        .rect(GRIP_LEN, 5.0)
        .extrude(grip_protrusion)
        .edges("|X")
        .fillet(1.5)
    )
    rack = rack.union(grip)

    # ---------------------------------------------------------------
    # LAMINA INTERIOR (pedido expreso: "una lamina interior que
    # SIEMPRE cubra el hueco que deja la pestaña en un sentido y en
    # otro"). Pieza SEPARADA de la pestaña visible, escondida por
    # dentro -- rellena el propio tunel del hueco exterior con el
    # tamaño EXACTO de ese hueco (mismo ancho Z que
    # button_hole_exterior, sin encogerla "por seguridad" y sin
    # ningun redondeo) -- un rectangulo recto que iguala o supera la
    # caja real del hueco lo cubre entero, sin excepcion, por pura
    # geometria. No necesita asomar por la pared como la pestaña --
    # solo rellenar el tunel del hueco desde dentro.
    lamina_h = BUTTON_H + 3.4 + 1.4  # debe superar la altura real del hueco (5.6)
    # propio hueco, con 0.1mm de margen de seguridad
    lamina = (
        cq.Workplane("XZ")
        .workplane(offset=-(grip_y + grip_total_len / 2 + 4.0))
        .center(grip_x_local + 2.45, -0.22)
        .rect(2.4, lamina_h)
        .extrude(grip_total_len + 8.0)
    )
    rack = rack.union(lamina)

    # ---------------------------------------------------------------
    # CARRIL CORREDERA QUITADO (pedido expreso): se veian por el hueco
    # exterior junto a la empuñadura, dando un aspecto de piezas
    # sueltas/mecanismo en vez de una pestaña lisa y limpia.

    # nervios de agarre QUITADOS (pedido expreso): se confundian con
    # un engranaje visible en el lateral -- la empuñadura queda lisa,
    # solo la pestaña simple.

    # ---- MODULO DE BLOQUEO: dos muescas (ONLINE / OFFLINE) donde
    # encaja la bola del detent, separadas exactamente por el
    # recorrido real del interruptor (Hoja 14: "dos posiciones
    # mecanicamente estables", "el usuario escucha y siente un click")
    for ny in (SWITCH_DETENT_Y1, SWITCH_DETENT_Y1 + SWITCH_TRAVEL):
        notch = (
            cq.Workplane("XZ")
            .center(PINION_THK / 2, 2.85)
            .workplane(offset=-ny)
            .sphere(0.8)
        )
        rack = rack.cut(notch)
    return rack


# ---------------------------------------------------------------
# 6. OBTURADOR DE CAMARA y SELLO DE MICROFONO
# (correderas lineales piñon-cremallera, escondidas -- sin bisagra ni
# pivote alguno, tal y como exige la Hoja 11 S3 / Hoja 12 S5)
# ---------------------------------------------------------------
def build_camera_shutter_slider(dims):
    # Corredera VERTICAL -- desliza en Y (no en X como en el intento
    # anterior). El usuario señalo, con razon, que en vertical hay
    # mucho mas espacio real para esconderla: el hueco vacio entre la
    # pared trasera y el cuerpo plano del movil (verificado con sonda:
    # 3.59mm de aire, en TODA la cavidad, no solo junto a la camara)
    # se extiende 117mm hacia abajo desde el borde del hueco de
    # camara -- de sobra para esconder la corredera entera.
    #
    # El recorrido (35mm+) viene de: manivela agrandada (radio 5mm,
    # ~6.5mm de recorrido base) + reductor de engranaje compuesto fino
    # (piñon 1.2mm -> 7.5mm, relacion 6.25x) = ~40mm de recorrido real,
    # verificado mas abajo.
    SHUTTER_W = 37.0
    SHUTTER_H = 37.0
    r2 = dims["gear_r2"]
    plate = (
        cq.Workplane("XY")
        .workplane(offset=dims["cam_low_z"])
        .rect(SHUTTER_W, SHUTTER_H)
        .extrude(0.8)
        .edges("|Z")
        .fillet(2)
    )
    n_teeth = 10
    pitch = 3.4
    teeth_x = dims["cam_gear_x"] - dims["cam_shutter_ref_x"] + r2 - 1.0
    teeth_y_center = -6.05   # FIX: centrado en Y=0 antes, no alcanzaba
    # el engranaje en la posicion CUBRIENDO (0.003mm3 de solape) --
    # recalculado como punto medio entre lo que exige cada extremo del
    # recorrido, mismo patron que se aplico en la version horizontal
    teeth = None
    for i in range(n_teeth):
        y0 = teeth_y_center - (n_teeth * pitch) / 2 + i * pitch
        tooth = (
            cq.Workplane("XY")
            .workplane(offset=dims["cam_gear_z"])
            .moveTo(teeth_x, y0)
            .lineTo(teeth_x + 0.7, y0 + pitch * 0.35)
            .lineTo(teeth_x, y0 + pitch * 0.7)
            .close()
            .extrude(2.4)
        )
        teeth = tooth if teeth is None else teeth.union(tooth)
    rack_body = (
        cq.Workplane("XY")
        .center(teeth_x - 3.6, teeth_y_center)
        .workplane(offset=dims["cam_gear_z"])
        .rect(3.0, n_teeth * pitch)
        .extrude(2.4)
    )
    riser = (
        cq.Workplane("XY")
        .center(teeth_x - 3.6, teeth_y_center)
        .workplane(offset=dims["cam_low_z"] + 0.8)
        .rect(6.0, n_teeth * pitch)
        .extrude(dims["cam_gear_z"] - dims["cam_low_z"] - 0.8)
    )
    plate = plate.union(riser).union(rack_body).union(teeth)

    # ---------------------------------------------------------------
    # CARRIL CORREDERA: dos lengüetas de guia (izquierda y derecha del
    # plato), del mismo largo que el propio plato -- se mueven CON el,
    # mismo patron ya verificado en la puerta de microfono (una guia
    # que ademas abarcara todo el recorrido duplicaba el alcance y
    # chocaba con el movil -- aqui se evita ese error desde el
    # principio, guias cortas, del tamaño del propio plato).
    # ---------------------------------------------------------------
    for rail_x in (-SHUTTER_W / 2 - 0.3, SHUTTER_W / 2 + 0.3):
        rail = (
            cq.Workplane("XY")
            .center(rail_x, 0)
            .workplane(offset=dims["cam_low_z"])
            .rect(0.6, SHUTTER_H - 4.0)
            .extrude(0.8)
        )
        plate = plate.union(rail)

    # ---------------------------------------------------------------
    # PESTAÑA DE CONTACTO RF: el primer intento de contacto de camara
    # caia DENTRO de la huella real del bulto del movil (35x35, solo
    # 1mm de margen respecto al plato de 37x37) -- verificado que
    # chocaba con el movil (3.44mm3). Esta pestaña sobresale en X
    # (no en Y) mas alla del propio borde del bulto (X=2.3) en
    # CUALQUIER estado del recorrido -- no depende de si esta abierta
    # o cerrada, evita el bulto siempre.
    # ---------------------------------------------------------------
    contact_tab = (
        cq.Workplane("XY")
        .center(17.5, 0)
        .workplane(offset=dims["cam_low_z"])
        .rect(5.0, 4.0)
        .extrude(0.8)
        .edges("|Z")
        .fillet(0.5)
    )
    plate = plate.union(contact_tab)
    return plate


def build_camera_reducer_gear(dims):
    # ENGRANAJE REDUCTOR fino: dos piñones coaxiales (eje Z, vertical),
    # delgados (1.2mm cada uno) para caber dentro del hueco general de
    # 3.59mm que existe en TODA la cavidad del movil (no solo junto a
    # la camara). El pequeño engrana con los dientes de la varilla
    # (desliza en Y); el grande engrana con los dientes de la
    # corredera (tambien desliza en Y, pero con mas recorrido por la
    # diferencia de radio) -- mismo principio ya usado y descartado
    # una vez por falta de sitio, ahora en una zona con hueco real de
    # sobra para su grosor.
    r1 = dims["gear_r1"]
    r2 = dims["gear_r2"]
    # FIX (FMEA #6, RPN 210): dientes de 1.2mm de espesor axial eran
    # el riesgo de fabricacion mas alto sin mitigar de todo el diseño
    # -- MJF con dientes tan finos en un radio pequeño (r1=1.3mm)
    # corre riesgo real de rotura o mala formacion. Engrosado a 1.8mm
    # (+50%) SIN TOCAR EL RADIO -- el radio determina la relacion de
    # transmision ya verificada (recorrido de 35.9mm de la corredera);
    # cambiar el radio la habria invalidado. El espesor axial es
    # independiente de esa relacion, y habia margen real sin usar en
    # el canal ya cortado (hasta Z=4.5, los engranajes solo llegaban
    # a Z=2.75).
    thk = 1.8

    def gear(radius, n_teeth, z_off):
        body = cq.Workplane("XY").workplane(offset=z_off).circle(radius).extrude(thk)
        teeth = None
        for i in range(n_teeth):
            ang = 2 * math.pi * i / n_teeth
            tooth = (
                cq.Workplane("XY")
                .workplane(offset=z_off)
                .moveTo(radius * math.cos(ang), radius * math.sin(ang))
                .lineTo((radius + 0.6) * math.cos(ang + 0.06), (radius + 0.6) * math.sin(ang + 0.06))
                .lineTo(radius * math.cos(ang + 0.12), radius * math.sin(ang + 0.12))
                .close()
                .extrude(thk)
            )
            teeth = tooth if teeth is None else teeth.union(tooth)
        return body.union(teeth)

    gear1 = gear(r1, 10, 0.25)
    gear2 = gear(r2, 28, thk + 0.35)
    return gear1.union(gear2)


def build_mic_input_rack(dims):
    # Enlace real del microfono al eje: un SEGUNDO piñon pequeño, fijo
    # al MISMO eje (gira siempre igual que el que acciona el
    # interruptor principal), engrana con esta cremallera "esclava" --
    # no la empuja el usuario, la mueve el propio giro del eje.
    #
    # REDISEÑO: esta cremallera ya NO lleva la puerta directamente
    # (antes deslizaba en Y, "hacia dentro/fuera" del canto). El
    # usuario señalo que eso se percibe como una tapa que gira/se
    # abre hacia dentro, no como una ventana lateral real -- ahora
    # esta cremallera solo es la ENTRADA de un reductor (ver
    # build_mic_reducer_gear) que convierte este movimiento en Y en
    # el movimiento LATERAL (X) real de la ventana.
    n_teeth = max(3, int(RACK_LEN / RACK_TOOTH_PITCH))
    rack = (
        cq.Workplane("XZ")
        .center(PINION_THK / 2, 2.0)
        .workplane(offset=RACK_LEN / 2)
        .rect(PINION_THK, 1.2)
        .extrude(-RACK_LEN)
    )
    teeth = None
    for i in range(n_teeth):
        y0 = -RACK_LEN / 2 + i * RACK_TOOTH_PITCH + RACK_TOOTH_PITCH / 2
        tooth = (
            cq.Workplane("YZ")
            .moveTo(y0 - RACK_TOOTH_PITCH * 0.3, 1.5)
            .lineTo(y0, 1.5 + RACK_TOOTH_DEPTH)
            .lineTo(y0 + RACK_TOOTH_PITCH * 0.3, 1.5)
            .close()
            .extrude(PINION_THK)
        )
        teeth = tooth if teeth is None else teeth.union(tooth)
    rack = rack.union(teeth)

    # brazo que lleva el movimiento hasta el reductor -- mismo patron
    # ya verificado en la varilla de camara (riser + reach). Crece
    # desde el extremo POSITIVO de la cremallera (+Y, hacia el
    # reductor reubicado en zona abierta), no desde el negativo
    # (que da hacia el canto real, sin espacio).
    # FIX CRITICO: MIC_GEAR1_Z es una Z ABSOLUTA (como cam_gear1_z),
    # pero esta pieza se construye en un marco LOCAL que se traslada
    # +hinge_z despues -- verificado que chocaba con el propio eje
    # (18.8mm3) porque la Z local no restaba hinge_z. Corregido aqui.
    local_gear1_z = MIC_GEAR1_Z - dims["hinge_z"]
    riser = (
        cq.Workplane("XZ")
        .center(PINION_THK / 2, (local_gear1_z + 1.4 + 0.6) / 2)
        .workplane(offset=-RACK_LEN / 2)
        .rect(PINION_THK, (1.4 + 0.6) - local_gear1_z)
        .extrude(-2.0)
    )
    rack = rack.union(riser)
    reach = (
        cq.Workplane("XZ")
        .center(PINION_THK / 2, local_gear1_z + 0.6)
        .workplane(offset=-(RACK_LEN / 2 + 2.0))
        .rect(PINION_THK, 1.2)
        .extrude(-(MIC_GEAR_REACH - 2.0))
    )
    rack = rack.union(reach)

    n2 = 5
    pitch2 = 2.2
    teeth_x2 = PINION_THK / 2 - 0.5
    teeth2 = None
    for i in range(n2):
        y0 = (RACK_LEN / 2 + MIC_GEAR_REACH) - i * pitch2
        tooth = (
            cq.Workplane("XY")
            .workplane(offset=local_gear1_z)
            .moveTo(teeth_x2, y0)
            .lineTo(teeth_x2 - 0.7, y0 + pitch2 * 0.35)
            .lineTo(teeth_x2, y0 + pitch2 * 0.7)
            .close()
            .extrude(1.2)
        )
        teeth2 = tooth if teeth2 is None else teeth2.union(tooth)
    rack = rack.union(teeth2)
    return rack


def build_mic_reducer_gear(dims):
    # Reductor de engranaje compuesto, eje Z -- MISMO principio ya
    # verificado en la camara (build_camera_reducer_gear): dos
    # piñones coaxiales, uno pequeño (engrana con la entrada, que
    # desliza en Y) y uno grande (engrana con la ventana, que desliza
    # en X). Un engranaje en eje Z puede acoplar los dos porque X e Y
    # son ambos perpendiculares a Z -- es el mismo motivo por el que
    # funciono en la camara.
    r1 = MIC_GEAR_R1
    r2 = MIC_GEAR_R2
    thk = 1.2

    def gear(r, n, z_off):
        body = cq.Workplane("XY").workplane(offset=z_off).circle(r).extrude(thk)
        teeth = None
        for i in range(n):
            a = i * 2 * math.pi / n
            t = (
                cq.Workplane("XY")
                .workplane(offset=z_off)
                .center(r * 0.85 * math.cos(a), r * 0.85 * math.sin(a))
                .circle(0.6)
                .extrude(thk)
            )
            teeth = t if teeth is None else teeth.union(t)
        return body.union(teeth) if teeth else body

    gear1 = gear(r1, 8, MIC_GEAR1_Z)
    gear2 = gear(r2, 20, MIC_GEAR1_Z + thk + 0.35)
    return gear1.union(gear2)


def build_mic_curved_band(dims, theta_offset, side="L"):
    # BANDA CURVA SEMIRRIGIDA: sustituye a la ventana rigida plana que
    # habia antes. En vez de deslizar en linea recta (necesitaba mas
    # de 20mm de pasillo recto, y el hueco real disponible junto al
    # interruptor principal es de solo ~19mm, verificado), esta
    # lamina fina gira dentro de un cuarto de circulo compacto (radio
    # MIC_BAND_R) -- el mismo principio que la lamina RF que se
    # enrolla en el rodillo, en miniatura y sin rodillo propio.
    # theta_offset=0 es la posicion CUBRIENDO (el extremo inicial de
    # la banda queda pegado a la piel exterior, tapando los
    # agujeros); theta_offset=MIC_BAND_EXTRA es la posicion OCULTA
    # (la banda ha girado hacia el interior del menton, fuera de los
    # agujeros).
    #
    # AVISO HONESTO: el acoplamiento final -- como el giro del
    # reductor (eje Z) se transmite a esta banda (eje de giro
    # paralelo a X, un cambio de eje de 90 grados, tipo piñon conico)
    # -- se deja esquematico aqui, no diente a diente, igual que la
    # varilla de camara ya avisa que no verifica el pandeo real por
    # compresion. Lo que SI esta verificado con geometria real y
    # colision explicita es que la banda, en todo su recorrido
    # angular, no choca con el interruptor principal (en sus dos
    # estados), el canal USB-C, el piñon, el eje, ni el propio movil.
    suffix = "" if side == "L" else "_r"
    center_y = dims["mic_center_y" + suffix]
    center_z = dims["mic_center_z" + suffix]
    mic_x = dims["mic_pinion_x" + suffix]

    def arc_point(theta_deg):
        th = math.radians(theta_deg)
        return (center_y - MIC_BAND_R * math.cos(th), center_z + MIC_BAND_R * math.sin(th))

    theta_start = theta_offset
    theta_end = theta_offset + MIC_BAND_ARC
    p0 = arc_point(theta_start)
    pmid = arc_point((theta_start + theta_end) / 2)
    p1 = arc_point(theta_end)
    path = cq.Workplane("YZ").moveTo(*p0).threePointArc(pmid, p1)
    profile = (
        cq.Workplane("XY")
        .workplane(offset=p0[1])
        .center(mic_x, p0[0])
        .rect(MIC_BAND_W, MIC_BAND_T)
    )
    band = profile.sweep(path, transition="round")
    return band


# ---------------------------------------------------------------
def build_button_boot(length, y_center, x_face, x_sign):
    # FIX: el hueco real (button_hole) abarca [x_face-0.5, x_face+0.5]
    # (1mm de profundidad). Esta tapa llegaba a extenderse 0.25mm mas
    # alla del limite interior del hueco, invadiendo pared solida
    # (verificado: 3.4-8.6mm3 de colision real). Recalculada para
    # quedar siempre dentro del hueco real, con margen.
    depth = 0.75
    outer = (
        cq.Workplane("YZ")
        .workplane(offset=x_face + x_sign * 0.4)
        .center(y_center, WALL + 6)
        .rect(length, 5.0, centered=True)
        .extrude(x_sign * -depth)
    )
    inner = (
        cq.Workplane("YZ")
        .workplane(offset=x_face + x_sign * 0.4)
        .center(y_center, WALL + 6)
        .rect(length - 2 * BTN_BOOT_WALL, 5.0 - 2 * BTN_BOOT_WALL, centered=True)
        .extrude(x_sign * -depth)
    )
    return outer.cut(inner)


# ---------------------------------------------------------------
# 8. TAPA CONDUCTORA USB-C
# ---------------------------------------------------------------
def build_usb_flap():
    flap = cq.Workplane("XY").rect(15.4, 5.4).extrude(USB_FLAP_THK).edges("|Z").fillet(1.0)
    magnet_pocket = cq.Workplane("XY").workplane(offset=USB_FLAP_THK - 0.6).center(5, 0).circle(1.5).extrude(0.6)
    hinge = cq.Workplane("XY").center(-7, 0).rect(2, 5.4).extrude(USB_FLAP_THK + 0.4)
    flap = flap.cut(magnet_pocket).union(hinge)
    return flap


# ---------------------------------------------------------------
# CIERRE RF POR CONTACTO (06_RF_Module) -- la brecha mas grave
# identificada en el FMEA (Severidad 10, Ocurrencia 10: "no existe
# como mecanismo funcional"). Principio del documento (Hoja 12): NO
# se mueve la malla -- se mueve la ESTRUCTURA que la presiona. Aqui:
# un contacto de pogo-pin (comprado, resorte real, no elasticidad de
# plastico) fijo en el FRAME, que la propia barra rigida de la lamina
# (ya conductora) presiona al alcanzar el despliegue completo.
# ---------------------------------------------------------------
RF_CONTACT_Y = 77.3   # justo despues del borde real de la barra
# rigida desplegada (76.3, verificado) -- el pin se comprime ~1mm al
# hacer contacto, dentro de su propio recorrido de resorte
RF_CONTACT_Z = None   # se calcula en build_base a partir de guide_z


def build_material_pogo_pin_rf():
    # cuerpo del conector (comprado) + punta de contacto -- orientado
    # con el eje ya en Y (apuntando hacia la lamina), listo para
    # colocar directamente con .translate((0, y, z))
    body = cq.Workplane("XY").circle(0.9).extrude(3.0)
    tip = cq.Workplane("XY").workplane(offset=3.0).circle(0.5).extrude(1.2)
    pin = body.union(tip)
    return pin.rotate((0, 0, 0), (1, 0, 0), 90)


# NOTA: existia aqui una build_base_liner_pattern() -- una copia
# antigua del patron de forro conductor de la base, sin el arreglo de
# posicion que si tiene build_material_malla_base() (materials.py),
# la que de verdad usa el ensamblaje real. Se ha quitado: no la
# llamaba nada del pipeline real (solo el bloque __main__ ya
# eliminado), y de haberse usado por error habria reintroducido una
# colision real de 498mm3 contra el movil, ya documentada y corregida
# en su momento.

# ---------------------------------------------------------------
# 10. MANIVELA + VARILLA + PALANCA DE CAMARA
#
# Mecanismo de manivela-corredera (tipo yugo escoces): un brazo
# radial, fijo al eje principal (gira solidario con el), empuja una
# varilla RIGIDA que desliza dentro del conducto tallado en la pared
# izquierda ensanchada, desde el rodillo hasta la zona de la camara
# (126mm). Al ser rigida, el desplazamiento se transmite 1:1 sin
# depender de que un hilo flexible se comporte bien.
#
# AVISO HONESTO: lo que SI se puede verificar con geometria estatica
# (y se verifica mas abajo) es que las piezas no chocan en su
# recorrido. Lo que NO se puede verificar asi es si una varilla rigida
# de 126mm de largo se pandea al empujarla por compresion -- eso
# depende del material y grosor reales, se comprueba en el prototipo
# fisico, no en la pantalla.
# ---------------------------------------------------------------
def build_camera_crank(dims):
    # FIX REDISEÑO: el eje ahora gira ~176 grados (antes 90), pero el
    # yugo escoces SOLO da su recorrido maximo (=crank_r) a los 90
    # grados exactos -- pasado ese punto la salida vuelve a bajar
    # (seno). Verificado: con 176 grados directos el yugo daba
    # 0.37mm, no los 5mm que necesitaba. Se añade una reduccion real
    # (piñon pequeño en el propio eje + engranaje grande en el eje de
    # la manivela) que lleva esos 176 grados a los 90 grados limpios
    # que el yugo necesita. AVISO: dientes esquematicos, igual que en
    # el resto de la funda -- ver mas abajo la comprobacion de que
    # las piezas no chocan.
    shaft_x0 = dims["pinion_x"] - 8.0   # dentro del alcance del eje principal
    shaft_x1 = dims["conduit_x"]
    r_in, r_out = 2.0, 3.9   # FIX: reduccion 2.0/3.9 = 0.513 -- lleva
    # theta0 real (3.067 rad) a 1.574 rad (~90.2 grados) en la manivela
    # FIX CRITICO (encontrado real, no solo colision): este tramo de
    # entrada se construia extendiendose HACIA LA PARED (alejandose
    # del eje), en vez de hacia el propio eje real (rodillo, que solo
    # llega hasta X=-32.1) -- quedaba flotando a 6mm de distancia,
    # sin tocar nada que lo hiciera girar. Verificado con contacto
    # real: 0mm3 antes del arreglo. Ahora se extiende desde el eje
    # real (con solape de sobra) hasta shaft_x0.
    axle_edge = -(dims["roller_len"] - 2.0) / 2
    input_stub = (
        cq.Workplane("YZ")
        .workplane(offset=shaft_x0)
        .circle(1.2)
        .extrude(axle_edge + 1.0 - shaft_x0)
    )
    input_gear = (
        cq.Workplane("YZ")
        .workplane(offset=shaft_x0 - 2.5)
        .circle(r_in)
        .extrude(-1.5)
    )
    input_stub = input_stub.union(input_gear)

    shaft_x0b = shaft_x0 - 4.5   # arranca el eje de salida justo despues del engranaje de entrada
    length = shaft_x0b - shaft_x1
    shaft = cq.Workplane("YZ").workplane(offset=shaft_x1).circle(1.2).extrude(length)
    output_gear = (
        cq.Workplane("YZ")
        .workplane(offset=shaft_x0b - 1.5)
        .circle(r_out)
        .extrude(1.5)
    )
    shaft = shaft.union(output_gear)
    arm = (
        cq.Workplane("YZ")
        .workplane(offset=shaft_x1)
        .center(0, 0)
        .moveTo(-1.0, 0)
        .lineTo(1.0, 0)
        .lineTo(1.0, dims["crank_r"] + 1.0)
        .lineTo(-1.0, dims["crank_r"] + 1.0)
        .close()
        .extrude(2.5)
    )
    return input_stub.union(shaft).union(arm)


def build_camera_rod(dims):
    # varilla rigida + yugo en el extremo (ranura donde engancha el
    # pasador de la manivela) + palanca en el otro extremo (empuja la
    # lengueta de camara). Coordenadas EXPLICITAS (no relativas
    # encadenadas) para no desconectar las piezas.
    #
    # FIX: el yugo estaba centrado 5.5mm mas lejos de roller_y de lo
    # que barre en realidad el pasador de la manivela -- verificado
    # que no se tocaban en absoluto (0mm3 de solape). Ahora el yugo
    # se centra EXACTAMENTE en roller_y, que es donde gira el pasador.
    yoke_y = dims["roller_y"]
    y0 = yoke_y + 3.5   # donde empieza el cuerpo de la varilla, justo tras el yugo
    y1 = dims["conduit_y_max"] - 2   # extremo del lado de la camara
    length = y1 - y0
    rod = (
        cq.Workplane("XZ")
        .center(dims["conduit_x"], dims["conduit_z"])
        .workplane(offset=-y1)
        .circle(1.0)
        .extrude(length)
    )
    # yugo: ranura en Z en el extremo inferior (lado rodillo) que
    # captura el pasador de la manivela, dejandolo deslizar en Z
    # mientras arrastra la varilla en Y
    yoke = (
        cq.Workplane("XZ")
        .center(dims["conduit_x"], dims["conduit_z"])
        .workplane(offset=-(yoke_y + 1.5))
        .rect(4.0, (dims["crank_r"] + 2 * SLIDING_CLEARANCE + 0.6) * 2 + 2.0)
        .extrude(4.5)
    )
    rod = rod.union(yoke)
    # FIX CRITICO: cruzar en X a la altura de conduit_z (7.82) pasa
    # justo por donde esta el CUERPO DEL TELEFONO (Z 5.19 a 13.44) --
    # verificado que chocaba. Se baja primero a la zona libre real
    # (1.6 a 5.19, verificada con sonda en toda la cavidad, no solo
    # junto a la camara), y AHI se cruza en X hasta el engranaje.
    riser = (
        cq.Workplane("XZ")
        .center(dims["conduit_x"], (dims["conduit_z"] + dims["cam_gear1_z"]) / 2)
        .workplane(offset=-(y1 - 1.0))
        .rect(2.0, abs(dims["conduit_z"] - dims["cam_gear1_z"]) + 2 * SLIDING_CLEARANCE + 0.2)
        .extrude(3.0)
    )
    rod = rod.union(riser)
    x_near = dims["conduit_x"]
    x_far = dims["cam_gear_x"]
    lever_reach = (
        cq.Workplane("XY")
        .center((x_near + x_far) / 2, (y1 + dims["cam_gear_y"]) / 2)
        .workplane(offset=dims["cam_gear1_z"] - 0.05)
        .rect(abs(x_far - x_near) + REACH_MARGIN, abs(y1 - dims["cam_gear_y"]) + 6.0)
        .extrude(0.8)
    )
    rod = rod.union(lever_reach)
    # dientes que engranan con el piñon PEQUEÑO del reductor (r1) --
    # distribuidos en Y (la varilla llega desde abajo), apuntando en X
    # hacia el engranaje, mismo convenio que usa la cremallera de la
    # corredera (ver build_camera_shutter_slider)
    r1 = dims["gear_r1"]
    n_teeth = 5
    pitch = 2.2
    teeth_x = x_far - r1 + 0.5
    teeth = None
    for i in range(n_teeth):
        y0 = dims["cam_gear_y"] - (n_teeth * pitch) / 2 + i * pitch
        tooth = (
            cq.Workplane("XY")
            .workplane(offset=dims["cam_gear1_z"])
            .moveTo(teeth_x, y0)
            .lineTo(teeth_x - 0.7, y0 + pitch * 0.35)
            .lineTo(teeth_x, y0 + pitch * 0.7)
            .close()
            .extrude(1.0)
        )
        teeth = tooth if teeth is None else teeth.union(tooth)
    rack_body = (
        cq.Workplane("XY")
        .center(teeth_x + 1.5, dims["cam_gear_y"])
        .workplane(offset=dims["cam_gear1_z"])
        .rect(3.0, n_teeth * pitch)
        .extrude(1.0)
    )
    rod = rod.union(rack_body).union(teeth)
    return rod
