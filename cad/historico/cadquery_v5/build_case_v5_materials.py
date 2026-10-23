"""
Todos los materiales NO IMPRIMIBLES, modelados como cuerpos reales
(no huecos, no referencias planas) para poder verlos en volumen y
comprobar que encajan de verdad en el mecanismo. Van con prefijo
MAT_ y colores distintos por tipo de material, en su propia carpeta
al ensamblar, separados de las piezas imprimibles.

Ninguno de estos cuerpos se manda a imprimir -- se compran o se
cortan aparte y se pegan/insertan en el montaje.
"""
import cadquery as cq
import build_case_v5_lamina as bc
import math


# ---------------------------------------------------------------
# 1. MALLA CONDUCTORA (cobre/niquel) -- forra el interior de la base
# ---------------------------------------------------------------
def build_material_malla_base(dims):
    # FIX DE FONDO: la malla se pega a la PARED (donde va en la
    # realidad), no se desplaza hacia el centro de la cavidad -- el
    # error anterior la posicionaba mas cerca del movil que de la
    # pared, invadiendo el margen de holgura del movil sin necesidad.
    # Pegada a la pared real, el hueco disponible antes de tocar el
    # movil es el margen de holgura completo (0.35mm), de sobra para
    # una malla de 0.08mm de grosor.
    cav_w, cav_h, ext_t = dims["cav_w"], dims["cav_h"], dims["ext_t"]
    cav = (
        cq.Workplane("XY")
        .workplane(offset=bc.WALL)
        .rect(cav_w - 0.1, cav_h - 0.1)
        .extrude(ext_t - bc.WALL - 1)
        .edges("|Z")
        .fillet(4)
    )
    liner = cav.shell(-0.08)
    # FIX 2: recortar tambien la zona del bulto de camara -- ya tiene
    # su propio tratamiento especial (corredera + mecanismo en el
    # hueco estrecho de 1.6mm), la malla generica no puede solapar ahi
    cam_clear = (
        cq.Workplane("XY")
        .center(dims["cam_center_x"], dims["cam_center_y"])
        .rect(bc.CAM_BUMP_SIZE + 2, bc.CAM_BUMP_SIZE + 2)
        .extrude(ext_t)
    )
    liner = liner.cut(cam_clear)
    return liner


# ---------------------------------------------------------------
# 2. TELA CONDUCTORA (lamina RF de pantalla) -- volumen real, mas
# gruesa que la pieza funcional (que solo necesita representar el
# hueco que ocupa en el mecanismo)
# ---------------------------------------------------------------
def build_material_tela_pantalla(dims):
    w = dims["cav_w"] - 2 * (bc.CHANNEL_D + 0.4)
    h = dims["guide_h"] - 12
    return cq.Workplane("XY").rect(w, h).extrude(0.12)


# ---------------------------------------------------------------
# 3. ESPUMA CONDUCTORA ACUSTICA -- sellado de microfono, pegada a la
# placa de la cremallera esclava
# ---------------------------------------------------------------
def build_material_espuma_mic(dims):
    foam = cq.Workplane("XY").rect(19.0, 5.5).extrude(1.0).edges("|Z").fillet(1.0)
    return foam


# ---------------------------------------------------------------
# 4. JUNTA RF (gasket) -- perimetro del borde de cierre entre base y
# lo que en su dia sea la "tapa"/estructura portadora RF. Aqui se
# modela como tira perimetral en el borde superior de la cavidad,
# tal como se referencio en versiones anteriores (surco de sellado)
# pero nunca se habia modelado como cuerpo real.
# ---------------------------------------------------------------
def build_material_junta_rf(dims):
    cav_w, cav_h = dims["cav_w"], dims["cav_h"]
    outer = (
        cq.Workplane("XY")
        .rect(cav_w + 1.0, cav_h + 1.0)
        .extrude(1.2)
        .edges("|Z")
        .fillet(10)
    )
    inner = (
        cq.Workplane("XY")
        .rect(cav_w - 1.0, cav_h - 1.0)
        .extrude(1.2)
        .edges("|Z")
        .fillet(9)
    )
    ring = outer.cut(inner)
    return ring


# ---------------------------------------------------------------
# 4b. MANGUITO CONDUCTOR DEL PUERTO USB-C -- el puerto tiene que
# quedar fisicamente abierto para poder cargar el movil (no se puede
# proteger por fuera ahi), pero eso no puede dejar un agujero en el
# blindaje. Este manguito forra las 4 paredes del canal real del
# puerto (mismo recorrido, de la posicion real del conector hasta el
# borde exterior) con una lamina conductora fina, a modo de tunel de
# Faraday -- el mismo principio que una funda de aislamiento RF
# comercial usa alrededor de su puerto de carga. Debe quedar en
# contacto electrico con el resto del blindaje (malla de base /
# junta RF) para que el aislamiento sea continuo.
# ---------------------------------------------------------------
def build_material_usb_shield_sleeve(dims):
    w = dims["usb_port_w"] - 0.4
    h = dims["usb_port_h"] - 0.4
    wall = 0.15
    y_span = dims["usb_y_inner"] - dims["usb_y_outer"]
    outer = cq.Workplane("XZ").center(0, dims["usb_port_z_center"]).rect(w, h).extrude(-y_span)
    inner = cq.Workplane("XZ").center(0, dims["usb_port_z_center"]).rect(w - 2 * wall, h - 2 * wall).extrude(-y_span)
    sleeve = outer.cut(inner)
    return sleeve.translate((0, dims["usb_y_outer"], 0))


# ---------------------------------------------------------------
# 5. IMAN (USB-C) -- en el hueco ya existente en la tapa USB
# ---------------------------------------------------------------
def build_material_iman_usb():
    return cq.Workplane("XY").circle(1.4).extrude(0.55)


# ---------------------------------------------------------------
# 6. MUELLE DE BLOQUEO -- especificacion calculada, no solo
# geometria de referencia. Objetivo: F=1.0N en el punto de compresion
# real ya verificado en CAD (0.4mm, ver SWITCH_DETENT_Y1 en
# build_case_v5_lamina.py), dentro del rango tipico de un "click"
# perceptible sin dificultar el deslizamiento (similar a un
# interruptor de silenciador o expulsor de SIM).
#
# k = F/x = 1.0N / 0.4mm = 2.5 N/mm
# Con hilo de acero d=0.25mm y n=4 espiras activas (formula de
# muelle helicoidal, G=80000 N/mm2 acero):
#   D = ((G * d^4) / (8 * k * n))^(1/3) = 1.57mm de diametro de bobina
#
# AVISO HONESTO: esto es un calculo de ingenieria de muelles
# estandar, no una calibracion medida -- sigue haciendo falta un
# muelle fisico real para confirmar que 1.0N es la fuerza de click
# correcta para el usuario final (podria ajustarse tras prototipo).
# ---------------------------------------------------------------
MUELLE_HILO_D = 0.25    # mm, diametro de hilo
MUELLE_BOBINA_D = 1.57  # mm, diametro de bobina (calculado para F=1.0N a 0.4mm)
MUELLE_ESPIRAS = 4
MUELLE_FUERZA_OBJETIVO_N = 1.0   # a 0.4mm de compresion


def build_material_muelle_lock(dims):
    coil = cq.Workplane("XY")
    turns = MUELLE_ESPIRAS
    r_bobina = MUELLE_BOBINA_D / 2
    pts = []
    for i in range(turns * 16 + 1):
        t = i / 16 * 2 * math.pi
        z = i / (turns * 16) * 4.0
        pts.append((r_bobina * math.cos(t), r_bobina * math.sin(t), z))
    spring = cq.Workplane("XY").polyline(pts[:2])
    path = cq.Workplane("XY").spline(pts)
    profile = cq.Workplane("YZ").center(r_bobina, 0).circle(MUELLE_HILO_D / 2)
    try:
        spring_solid = profile.sweep(path, isFrenet=True)
        return spring_solid
    except Exception:
        # si el barrido falla, representacion simplificada (cilindro hueco)
        outer = cq.Workplane("XY").circle(r_bobina + 0.2).extrude(4.0)
        inner = cq.Workplane("XY").circle(r_bobina - 0.2).extrude(4.0)
        return outer.cut(inner)


# NOTA: existia aqui una build_material_adhesivo_generico(w, h) --
# una capa de adhesivo generica pensada para ir bajo la malla de base
# y la espuma de microfono. Se ha quitado: no la llamaba nada del
# ensamblaje real (0 usos). La Hoja de especificacion si contempla
# adhesivo ("solo para componentes cuyo desmontaje no este previsto,
# uso minimizado") asi que esto no es un capricho descartado sin
# base -- si en algun momento quieres modelar esa capa de verdad,
# hay que volver a crearla y llamarla explicitamente bajo la malla y
# la espuma en build_case_v5_privacy_case.py, no dejarla huerfana.

# ---------------------------------------------------------------
# 8. PASADOR (pin) -- ya existe el eje del rodillo como pieza
# comprada; este es un pasador de alineacion mas pequeño, generico,
# por si hace falta en el montaje de la tapa USB o el obturador
# ---------------------------------------------------------------
def build_material_pasador(length=6.0, dia=1.0):
    return cq.Workplane("XY").circle(dia / 2).extrude(length)


# ---------------------------------------------------------------
# 9. TORNILLO (generico, M1.4 aprox) -- este diseño es
# fundamentalmente a presion/adhesivo, no atornillado. Se incluye uno
# de referencia solo por si el cierre final (pendiente) lo necesita.
# ---------------------------------------------------------------
def build_material_tornillo():
    head = cq.Workplane("XY").circle(1.4).extrude(0.6)
    shaft = cq.Workplane("XY").workplane(offset=0.6).circle(0.7).extrude(3.0)
    return head.union(shaft)


# ---------------------------------------------------------------
# 10. BOLA DEL DETENT (Locking Module) -- acero, encaja en el
# alojamiento real de la carcasa (build_base la corta ya conectada
# mecanicamente, no es una posicion conceptual)
# ---------------------------------------------------------------
def build_material_bola_detent():
    return cq.Workplane("XY").sphere(0.8)


# ---------------------------------------------------------------------
# 11. PIN DE CONTACTO COMPACTO (variante del pogo-pin RF, mas corto)
# -- para las dos zonas nuevas de contacto (camara, microfono), donde
# el presupuesto de espacio es mas ajustado que en el contacto de
# pantalla. Mismo principio: cuerpo + punta de resorte, comprado.
# ---------------------------------------------------------------
def build_material_pogo_pin_compact(body_len=2.2, tip_len=0.8, body_r=0.7, tip_r=0.4):
    body = cq.Workplane("XY").circle(body_r).extrude(body_len)
    tip = cq.Workplane("XY").workplane(offset=body_len).circle(tip_r).extrude(tip_len)
    pin = body.union(tip)
    return pin


# ---------------------------------------------------------------
# 10. EJE FLEXIBLE DEL MICROFONO (se compra, no se imprime) --
# ARREGLO del acoplamiento que se habia dejado esquematico entre el
# reductor del microfono (gira en eje Z) y la banda curva (gira en
# un eje paralelo a X). Los dos ejes de giro no se cruzan
# (perpendiculares y separados 13.6mm) asi que un piñon conico
# simple no vale -- la solucion real y habitual para exactamente
# este caso es un eje flexible con una junta universal en cada
# extremo, igual que un cable de velocimetro o un flexible de
# taladro. Se modela como una varilla recta (representa el nucleo
# flexible) con una esfera pequeña en cada punta (representa cada
# junta universal) -- geometria de referencia para comprar la pieza
# real, no para imprimir.
# ---------------------------------------------------------------
def build_material_mic_drive_shaft(dims, side="L"):
    suffix = "" if side == "L" else "_r"
    ax, ay, az = dims["mic_drive_a" + suffix]
    bx, by, bz = dims["mic_drive_b" + suffix]
    shaft_path = cq.Workplane("YZ").workplane(offset=-ax).moveTo(ay, az).lineTo(by, bz)
    profile = cq.Workplane("XY").workplane(offset=az).center(ax, ay).circle(0.9)
    core = profile.sweep(shaft_path)
    # FIX (encontrado real: 0mm3 de contacto verificado): el radio de
    # 1.1mm no llegaba a tocar ni el reductor ni la banda -- quedaba
    # flotando sin conectar a ninguno de los dos extremos.
    joint_a = cq.Workplane("XY").workplane(offset=az).center(ax, ay).sphere(2.4)
    joint_b = cq.Workplane("XY").workplane(offset=bz).center(bx, by).sphere(2.0)
    # FIX REAL (encontrado en auditoria de contacto, no solo colision):
    # joint_b esta en el propio EJE de giro de la banda, pero la banda
    # es una tira delgada al radio MIC_BAND_R=6mm de ese eje -- no hay
    # material real cerca del centro. Un intento anterior agrando
    # joint_b a una esfera de 6.5mm para llegar hasta la tira, pero
    # eso chocaba con la funda en zonas que no hacian falta (362mm3).
    # Ahora se añade un conector CORTO Y DIRIGIDO (no una esfera
    # omnidireccional), que sigue la misma direccion del propio eje
    # flexible unos mm mas alla de b, hasta tocar la tira real --
    # verificado que a partir de 5-6mm de extension en esa direccion
    # ya hay contacto real con la banda.
    dvy, dvz = by - ay, bz - az
    dlen = (dvy ** 2 + dvz ** 2) ** 0.5
    # FIX CRITICO REAL (encontrado con foto del usuario): esta punta
    # se extendia 6.0mm mas alla de b con radio 1.3mm, alcanzando
    # Y=-95.8 -- 1.3mm MAS ALLA del borde real de la funda (-94.5).
    # Esto es lo que se veia como "bolas" sobresaliendo por fuera en
    # la foto. Recortado a 5.0mm de extension y radio 0.95mm --
    # sigue tocando la banda real (contacto verificado) pero se queda
    # dentro del borde real con margen.
    ext_y = by + dvy / dlen * 5.0
    ext_z = bz + dvz / dlen * 5.0
    link_mid_y, link_mid_z = (by + ext_y) / 2, (bz + ext_z) / 2
    link = (
        cq.Workplane("XY")
        .workplane(offset=link_mid_z)
        .center(bx, link_mid_y)
        .rect(2.2, 5.0)
        .extrude(2.2)
    )
    tip = cq.Workplane("XY").workplane(offset=ext_z).center(bx, ext_y).sphere(0.95)
    return core.union(joint_a).union(joint_b).union(link).union(tip)


# ---------------------------------------------------------------
# 10b. JUNTA FLEXIBLE DEL PUENTE DE CAMARA (felpa/goma, se compra,
# no se imprime) -- el puente que conecta el plato de la corredera
# con el engranaje reductor solo cubre 34mm de su propio recorrido
# de 70mm en cada instante; el resto de la ranura, sin esto, queda
# expuesto al interior de la funda. Esta junta es una tira flexible
# que forra TODA la ranura a la altura de la piel real (mismo
# principio que la felpa de una ventanilla de coche): el puente
# rigido la atraviesa y la deforma al moverse, en vez de necesitar
# huecos propios -- por eso no se comprueba colision contra ella
# (es flexible por diseño, se espera que la atraviese).
# ---------------------------------------------------------------
def build_material_camera_riser_seal(dims):
    x_min = dims["cam_gear_x"] + dims["gear_r2"] - 5.5
    x_max = dims["cam_gear_x"] + dims["gear_r2"] + 1.5
    y_min, y_max = -5.0, 67.0
    seal = (
        cq.Workplane("XY")
        .workplane(offset=-0.35)
        .center((x_min + x_max) / 2, (y_min + y_max) / 2)
        .rect(x_max - x_min, y_max - y_min)
        .extrude(0.35)
    )
    return seal


# ---------------------------------------------------------------
# 10c. CONTRATAPA DE OBJETIVOS DE CAMARA (se compra/corta aparte,
# NO se imprime -- una placa fina con solo los 3 huecos reales de
# los objetivos, pegada por fuera para tapar el resto del hueco de
# 35x35mm y esconder el mecanismo de detras). Disposicion real
# investigada (iPhone 15 Pro Max): 3 anillos de ~16.2mm de diametro
# en forma de L -- principal arriba-izq, teleobjetivo arriba-dcha,
# ultra gran angular abajo. Sin esto, mirando la funda por fuera se
# veria todo el hueco de 35x35 y el mecanismo de dentro, no solo los
# objetivos.
# ---------------------------------------------------------------
def build_material_camera_faceplate(dims, cam_bump_size, rim_height, back_slab_extra):
    lens_positions = [(-9.0, 9.0), (9.0, 9.0), (-9.0, -9.0)]
    lens_r = 8.1
    plate_thickness = 0.3
    # FIX: la corredera ocupa Z=[cam_low_z, cam_low_z+0.8] (hasta
    # -2.1 por delante). La contratapa tiene que quedar MAS ALLA
    # (mas negativa) que eso, pegada a la piel exterior real de la
    # zona de camara (back_slab + reborde local), con margen a los
    # dos lados.
    plate_z = -(back_slab_extra + rim_height)   # cara exterior, a ras
    # de la piel real de la zona de camara
    plate = (
        cq.Workplane("XY")
        .workplane(offset=plate_z)
        .center(dims["cam_center_x"], dims["cam_center_y"])
        .rect(cam_bump_size - 2.0, cam_bump_size - 2.0)
        .extrude(plate_thickness)
        .edges("|Z")
        .fillet(3.0)
    )
    for lx, ly in lens_positions:
        hole = (
            cq.Workplane("XY")
            .workplane(offset=plate_z)
            .center(dims["cam_center_x"] + lx, dims["cam_center_y"] + ly)
            .circle(lens_r / 2)
            .extrude(plate_thickness)
        )
        plate = plate.cut(hole)
    return plate


# ---------------------------------------------------------------
# 11. MOVIL DE REFERENCIA (solo visual/verificacion, no es una
# pieza real ni se imprime ni se compra) -- para poder abrir el
# ensamblaje y ver la funda con el movil puesto, "como si estuviera
# terminado en Fusion", en vez de tener que imaginarselo. Mismos
# radios de esquina que ya se usaron para verificar colisiones
# contra el movil real en las auditorias de este proyecto.
# ---------------------------------------------------------------
def build_material_phone_reference(dims, wall, phone_w, phone_h, phone_t,
                                    cam_bump_size, cam_bump_t, case_corner_r,
                                    cam_corner_r, clearance_xy):
    cav_fillet = case_corner_r - wall
    slab = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .center(0, 0)
        .rect(phone_w, phone_h)
        .extrude(phone_t)
        .edges("|Z")
        .fillet(cav_fillet - clearance_xy - 0.05)
    )
    bump = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .center(dims["cam_center_x"], dims["cam_center_y"])
        .rect(cam_bump_size, cam_bump_size)
        .extrude(-cam_bump_t)
        .edges("|Z")
        .fillet(cam_corner_r - 0.05)
    )
    return slab.union(bump)
