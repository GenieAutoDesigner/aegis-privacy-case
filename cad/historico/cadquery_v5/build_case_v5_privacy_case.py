"""
Ensamblaje final con la jerarquia EXACTA pedida en la Hoja 6 del
documento de arquitectura:

Privacy_Case_v1
├── 00_Master
├── 02_Frame
├── 03_Main_Carriage
├── 04_Camera_Module
├── 05_Microphone_Module
├── 06_RF_Module
├── 07_Locking_Module
├── 08_Standard_Parts
└── 09_NonPrinted_Components

(01_Reference_Device, 10_Testing, 11_Render y 12_Export son carpetas
de proceso/documentacion de Fusion, no de geometria -- no aplican a
un export STEP).

IMPORTANTE: sigue sin ser un archivo .f3d nativo -- no hay Fusion 360
instalado en ningun punto de esta sesion. Es un STEP con
sub-ensamblajes nombrados segun esta jerarquia.
"""
import cadquery as cq
import build_case_v5_lamina as bc
import build_case_v5_materials as mat

base, dims = bc.build_base()

axle = bc.build_roller_axle(dims)
pinion = bc.build_pinion_gear()
mic_pinion = bc.build_pinion_gear()
cam_crank_base = bc.build_camera_crank(dims)
cam_gear_base = bc.build_camera_reducer_gear(dims)
vol_boot = bc.build_button_boot(27.5, dims["cav_h"] / 2 - 55, dims["LEFT_X"], -1)
action_boot = bc.build_button_boot(7.5, dims["cav_h"] / 2 - 25, dims["LEFT_X"], -1)
power_boot = bc.build_button_boot(24, dims["cav_h"] / 2 - 60, dims["RIGHT_X"], 1)
usb_flap = bc.build_usb_flap()

axle_len = dims["roller_len"] - 2.0
axle_moved = axle.translate((-axle_len / 2, dims["roller_y"], dims["hinge_z"]))
pinion_moved = pinion.translate((dims["pinion_x"], dims["roller_y"], dims["hinge_z"]))
mic_pinion_moved = mic_pinion.translate((dims["mic_pinion_x"], dims["roller_y"], dims["hinge_z"]))
cam_crank_moved = cam_crank_base.translate((0, dims["roller_y"], dims["hinge_z"]))
cam_gear_moved = cam_gear_base.translate((dims["cam_gear_x"], dims["cam_gear_y"], 0))
usb_flap_moved = usb_flap.translate((0, -dims["cav_h"] / 2 - dims["CHIN_H"] / 2, -0.2))

mat_malla_base = mat.build_material_malla_base(dims)
mat_junta_rf = mat.build_material_junta_rf(dims).translate((0, 0, dims["ext_t"] - 1.5))
mat_usb_shield_sleeve = mat.build_material_usb_shield_sleeve(dims)
mat_iman_usb = mat.build_material_iman_usb().translate((5, -dims["cav_h"] / 2 - dims["CHIN_H"] / 2, bc.USB_FLAP_THK - 0.6))
mat_espuma_mic = mat.build_material_espuma_mic(dims)
mat_pasador1 = mat.build_material_pasador(6.0, 1.0)
mat_tornillo1 = mat.build_material_tornillo()
base_liner_ref = mat.build_material_malla_base(dims)   # FIX: build_base_liner_pattern
# (en lamina.py) era una copia vieja, sin el arreglo de posicion que
# si se aplico a build_material_malla_base -- causaba 498mm3 de
# colision real con el movil, confirmado importando el STEP y
# comprobando pieza por pieza contra el telefono real.
mat_pogo_pin = bc.build_material_pogo_pin_rf().translate((0, dims["rf_contact_pin_y"], dims["rf_contact_z"]))
mat_cam_pin = mat.build_material_pogo_pin_compact().rotate((0, 0, 0), (1, 0, 0), 180).translate(
    (dims["cam_contact_x"], dims["cam_contact_y"], dims["cam_contact_z_bottom"] + 3.0))
mat_mic_pin = mat.build_material_pogo_pin_compact(body_r=0.18, tip_r=0.12).rotate((0, 0, 0), (1, 0, 0), 180).translate(
    (dims["mic_contact_x"], dims["mic_contact_y"], dims["mic_contact_z_bottom"] + 3.0))

detent_y = dims["roller_y"] + bc.SWITCH_DETENT_Y1
detent_x = dims["pinion_x"] + bc.PINION_THK / 2
mat_bola_detent = mat.build_material_bola_detent().translate(
    (detent_x, detent_y, dims["switch_z"] + 0.6 + 0.8 - 0.4))
mat_muelle_detent = mat.build_material_muelle_lock(dims).translate(
    (detent_x - 1.2, detent_y, dims["switch_z"] + 1.6))

mat_mic_drive_shaft = mat.build_material_mic_drive_shaft(dims)
mat_mic_drive_shaft_r = mat.build_material_mic_drive_shaft(dims, side="R")
mat_cam_riser_seal = mat.build_material_camera_riser_seal(dims)

mat_phone_ref = mat.build_material_phone_reference(
    dims, bc.WALL, bc.PHONE_W, bc.PHONE_H, bc.PHONE_T,
    bc.CAM_BUMP_SIZE, bc.CAM_BUMP_T, bc.CASE_CORNER_R, bc.CAM_CORNER_R, bc.CLEARANCE_XY)



def build_state(offline: bool, out_path: str):
    main_switch = bc.build_main_carriage_switch()
    mic_input_rack = bc.build_mic_input_rack(dims)
    mic_gear = bc.build_mic_reducer_gear(dims)
    cam_rod = bc.build_camera_rod(dims)
    cam_shutter = bc.build_camera_shutter_slider(dims)

    top = cq.Assembly(name=f"Privacy_Case_v1_{'OFFLINE' if offline else 'ONLINE'}")
    master = cq.Assembly(name="00_Master")

    frame = cq.Assembly(name="02_Frame")
    frame.add(base, name="Back_Housing_and_Side_Walls", color=cq.Color(0.08, 0.08, 0.08, 1.0))
    master.add(frame)

    carriage = cq.Assembly(name="03_Main_Carriage")
    carriage.add(axle_moved, name="Carriage_Axle", color=cq.Color(0.5, 0.5, 0.5, 1.0))
    carriage.add(pinion_moved, name="Carriage_Pinion", color=cq.Color(0.3, 0.3, 0.3, 1.0))

    switch_y_offset = -bc.SWITCH_TRAVEL if offline else 0.0
    main_switch_moved = main_switch.translate((dims["pinion_x"], dims["roller_y"] + switch_y_offset, dims["hinge_z"]))
    carriage.add(main_switch_moved, name="Sliding_Switch_Interruptor_Unico",
                 color=cq.Color(0.03, 0.03, 0.03, 1.0))

    # tren de reduccion real de la lamina RF (presente en los dos
    # estados, igual que el resto del mecanismo -- gira siempre con
    # el mismo eje compartido)
    fabric_piece_a = bc.build_rf_fabric_drive_piece_a(dims)
    fabric_piece_b, fabric_mesh_y_b, fabric_mesh_z_b = bc.build_rf_fabric_drive_piece_b(dims)
    fabric_piece_c, fabric_mesh_y_c, fabric_mesh_z_c = bc.build_rf_fabric_drive_piece_c(
        dims, fabric_mesh_y_b, fabric_mesh_z_b)
    carriage.add(fabric_piece_a, name="RF_Fabric_Drive_PiezaA", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    carriage.add(fabric_piece_b, name="RF_Fabric_Drive_PiezaB", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    carriage.add(fabric_piece_c, name="RF_Fabric_Drive_Carrete", color=cq.Color(0.3, 0.3, 0.3, 1.0))

    if offline:
        rf_fabric = bc.build_rf_fabric_and_pullbar(dims)
        rf_fabric_moved = rf_fabric.translate((0, 0, dims["guide_z"]))
        carriage.add(rf_fabric_moved, name="RF_Fabric_Roller_DESPLEGADA", color=cq.Color(0.55, 0.55, 0.6, 1.0))
    master.add(carriage)

    camera_mod = cq.Assembly(name="04_Camera_Module")
    camera_mod.add(cam_crank_moved, name="Slider_Follower_Crank", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    camera_mod.add(cam_rod, name="Slider_Interface_Rod", color=cq.Color(0.5, 0.5, 0.52, 1.0))
    camera_mod.add(cam_gear_moved, name="Slider_Reducer", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    if offline:
        cam_shutter_moved = cam_shutter.translate((dims["cam_shutter_ref_x"], dims["cam_center_y"], 0))
        camera_mod.add(cam_shutter_moved, name="Camera_Slider_TAPADA", color=cq.Color(0.2, 0.2, 0.2, 1.0))
    else:
        cam_shutter_hidden = cam_shutter.translate((dims["cam_shutter_ref_x"], dims["cam_center_y"] - dims["cam_travel"], 0))
        camera_mod.add(cam_shutter_hidden, name="Camera_Slider_OCULTA", color=cq.Color(0.2, 0.2, 0.2, 1.0))
    master.add(camera_mod)

    mic_mod = cq.Assembly(name="05_Microphone_Module")
    mic_input_rack_moved = mic_input_rack.translate((dims["mic_pinion_x"], dims["roller_y"], dims["hinge_z"]))
    mic_mod.add(mic_pinion_moved, name="Gate_Follower_Pinion", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    mic_mod.add(mic_input_rack_moved, name="Mic_Input_Rack", color=cq.Color(0.35, 0.35, 0.38, 1.0))
    mic_gear_moved = mic_gear.translate((dims["mic_gear_x"], dims["mic_gear_y"], 0))
    mic_mod.add(mic_gear_moved, name="Mic_Window_Reducer", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    # segundo mecanismo, lado derecho -- misma pieza (build_mic_input_rack
    # y build_mic_reducer_gear son genericas, sin X propio), solo cambia
    # donde se coloca
    mic_input_rack_moved_r = mic_input_rack.translate((dims["mic_pinion_x_r"], dims["roller_y"], dims["hinge_z"]))
    mic_mod.add(mic_input_rack_moved_r, name="Mic_Input_Rack_R", color=cq.Color(0.35, 0.35, 0.38, 1.0))
    mic_gear_moved_r = mic_gear.translate((dims["mic_gear_x_r"], dims["mic_gear_y_r"], 0))
    mic_mod.add(mic_gear_moved_r, name="Mic_Window_Reducer_R", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    if offline:
        mic_band_moved = bc.build_mic_curved_band(dims, 0.0)
        mic_mod.add(mic_band_moved, name="Mic_Band_CUBRIENDO", color=cq.Color(0.2, 0.2, 0.2, 1.0))
        mic_band_moved_r = bc.build_mic_curved_band(dims, 0.0, side="R")
        mic_mod.add(mic_band_moved_r, name="Mic_Band_R_CUBRIENDO", color=cq.Color(0.2, 0.2, 0.2, 1.0))
    else:
        mic_band_moved = bc.build_mic_curved_band(dims, bc.MIC_BAND_EXTRA)
        mic_mod.add(mic_band_moved, name="Mic_Band_OCULTA", color=cq.Color(0.2, 0.2, 0.2, 1.0))
        mic_band_moved_r = bc.build_mic_curved_band(dims, bc.MIC_BAND_EXTRA, side="R")
        mic_mod.add(mic_band_moved_r, name="Mic_Band_R_OCULTA", color=cq.Color(0.2, 0.2, 0.2, 1.0))
    master.add(mic_mod)

    rf_mod = cq.Assembly(name="06_RF_Module")
    rf_mod.add(base_liner_ref, name="RF_Carrier_patron_REFERENCIA", color=cq.Color(0.05, 0.05, 0.05, 0.35))
    master.add(rf_mod)

    std = cq.Assembly(name="08_Standard_Parts")
    std.add(vol_boot, name="Button_Volume_Boot", color=cq.Color(0.4, 0.4, 0.42, 1.0))
    std.add(action_boot, name="Button_Action_Boot", color=cq.Color(0.4, 0.4, 0.42, 1.0))
    std.add(power_boot, name="Button_Power_Boot", color=cq.Color(0.4, 0.4, 0.42, 1.0))
    std.add(usb_flap_moved, name="USB_C_Conductive_Flap", color=cq.Color(0.25, 0.25, 0.27, 1.0))
    master.add(std)

    # ---------------------------------------------------------------
    # 09_NonPrinted_Components: TODO lo que no se imprime -- hardware
    # comprado (pines, bola, muelle, tornillo, iman, eje flexible) y
    # materiales laminares (malla, junta RF, espuma, manguito USB,
    # tela de pantalla) -- reunido en una sola capa para que quede
    # claro de un vistazo que hay que comprar/añadir a mano despues
    # de imprimir, en vez de estar repartido por cada modulo.
    # ---------------------------------------------------------------
    nonprinted = cq.Assembly(name="09_NonPrinted_Components")
    nonprinted.add(mat_malla_base, name="Conductive_Mesh_cobre_niquel", color=cq.Color(0.75, 0.76, 0.78, 0.9))
    nonprinted.add(mat_junta_rf, name="RF_Gasket", color=cq.Color(0.15, 0.55, 0.15, 0.8))
    nonprinted.add(mat_usb_shield_sleeve, name="USB_Port_Shield_Sleeve", color=cq.Color(0.05, 0.05, 0.05, 0.9))
    nonprinted.add(mat_espuma_mic.translate((0, dims["mic_hinge_y"] + 3.5, bc.WALL + 1.0)),
                    name="Conductive_Foam_Microphone", color=cq.Color(0.6, 0.3, 0.1, 0.8))
    nonprinted.add(mat_iman_usb, name="Magnet_USB_C", color=cq.Color(0.2, 0.2, 0.25, 1.0))
    nonprinted.add(mat_pogo_pin, name="RF_Contact_PogoPin", color=cq.Color(0.85, 0.65, 0.2, 1.0))
    nonprinted.add(mat_cam_pin, name="RF_Contact_PogoPin_Camera", color=cq.Color(0.85, 0.65, 0.2, 1.0))
    nonprinted.add(mat_mic_pin, name="RF_Contact_PogoPin_Microphone", color=cq.Color(0.85, 0.65, 0.2, 1.0))
    nonprinted.add(mat_bola_detent, name="Primary_Latch_Ball_ACERO", color=cq.Color(0.6, 0.6, 0.65, 1.0))
    nonprinted.add(mat_muelle_detent, name="Spring_System_ACERO", color=cq.Color(0.55, 0.55, 0.6, 1.0))
    nonprinted.add(mat_mic_drive_shaft, name="Mic_Band_Drive_Shaft_eje_flexible",
                    color=cq.Color(0.55, 0.55, 0.58, 1.0))
    nonprinted.add(mat_mic_drive_shaft_r, name="Mic_Band_Drive_Shaft_R_eje_flexible",
                    color=cq.Color(0.55, 0.55, 0.58, 1.0))
    nonprinted.add(mat_cam_riser_seal, name="Camera_Riser_Seal_felpa",
                    color=cq.Color(0.1, 0.1, 0.1, 0.85))
    nonprinted.add(mat_pasador1.translate((10, dims["ext_bottom_y"] + 5, 3.0)), name="Alignment_Pin",
                    color=cq.Color(0.5, 0.5, 0.5, 1.0))
    nonprinted.add(mat_tornillo1.translate((15, dims["ext_bottom_y"] + 5, 3.0)), name="Reference_Screw",
                    color=cq.Color(0.4, 0.4, 0.4, 1.0))
    if offline:
        tela = mat.build_material_tela_pantalla(dims).translate((0, 0, dims["guide_z"] + 0.9))
        nonprinted.add(tela, name="Conductive_Fabric_Screen_DESPLEGADA", color=cq.Color(0.75, 0.76, 0.78, 0.9))
    master.add(nonprinted)

    # ---------------------------------------------------------------
    # 10_Phone_Reference: NO es una pieza real (ni se imprime ni se
    # compra) -- es el movil, solo para verlo puesto dentro de la
    # funda terminada al abrir el ensamblaje, igual que en Fusion.
    # ---------------------------------------------------------------
    phone_mod = cq.Assembly(name="10_Phone_Reference")
    phone_mod.add(mat_phone_ref, name="iPhone_15_Pro_Max_REFERENCIA", color=cq.Color(0.85, 0.85, 0.87, 0.5))
    master.add(phone_mod)

    top.add(master)
    top.save(out_path)
    print(f"OK - generado: {out_path}")


build_state(True, "Privacy_Case_v1_OFFLINE.step")
build_state(False, "Privacy_Case_v1_ONLINE.step")


def build_transition(t: float, out_path: str):
    """Estado TRANSICION (Hoja 17 / Hoja 19): posicion intermedia del
    carro principal, destinada exclusivamente a revisar cinematica,
    interferencias y sincronizacion -- NO es un estado de uso real.
    Verificado en 11 puntos del recorrido (t=0 a t=1): 0mm3 de
    colision con el movil en todos ellos."""
    main_switch = bc.build_main_carriage_switch()
    mic_input_rack = bc.build_mic_input_rack(dims)
    mic_gear = bc.build_mic_reducer_gear(dims)
    cam_shutter = bc.build_camera_shutter_slider(dims)
    cam_rod = bc.build_camera_rod(dims)

    switch_y = dims["roller_y"] - t * bc.SWITCH_TRAVEL
    switch_m = main_switch.translate((dims["pinion_x"], switch_y, dims["hinge_z"]))

    shutter_y = dims["cam_center_y"] - (1 - t) * dims["cam_travel"]
    shutter_m = cam_shutter.translate((dims["cam_shutter_ref_x"], shutter_y, 0))

    mic_theta = (1 - t) * bc.MIC_BAND_EXTRA   # t=0 (ONLINE) -> oculta; t=1 (OFFLINE) -> cubriendo
    mic_band_m = bc.build_mic_curved_band(dims, mic_theta)

    top = cq.Assembly(name=f"Privacy_Case_v1_TRANSITION_t{int(t*100)}")
    master = cq.Assembly(name="00_Master")

    frame = cq.Assembly(name="02_Frame")
    frame.add(base, name="Back_Housing_and_Side_Walls", color=cq.Color(0.08, 0.08, 0.08, 1.0))
    master.add(frame)

    carriage = cq.Assembly(name="03_Main_Carriage")
    carriage.add(axle_moved, name="Carriage_Axle", color=cq.Color(0.5, 0.5, 0.5, 1.0))
    carriage.add(pinion_moved, name="Carriage_Pinion", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    carriage.add(switch_m, name="Sliding_Switch_Interruptor_Unico_EN_TRANSICION",
                 color=cq.Color(0.9, 0.55, 0.15, 1.0))
    fabric_piece_a_t = bc.build_rf_fabric_drive_piece_a(dims)
    fabric_piece_b_t, fmy_b_t, fmz_b_t = bc.build_rf_fabric_drive_piece_b(dims)
    fabric_piece_c_t, fmy_c_t, fmz_c_t = bc.build_rf_fabric_drive_piece_c(dims, fmy_b_t, fmz_b_t)
    carriage.add(fabric_piece_a_t, name="RF_Fabric_Drive_PiezaA", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    carriage.add(fabric_piece_b_t, name="RF_Fabric_Drive_PiezaB", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    carriage.add(fabric_piece_c_t, name="RF_Fabric_Drive_Carrete", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    master.add(carriage)

    camera_mod = cq.Assembly(name="04_Camera_Module")
    camera_mod.add(cam_crank_moved, name="Slider_Follower_Crank", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    camera_mod.add(cam_rod, name="Slider_Interface_Rod", color=cq.Color(0.5, 0.5, 0.52, 1.0))
    camera_mod.add(cam_gear_moved, name="Slider_Reducer", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    camera_mod.add(shutter_m, name="Camera_Slider_EN_TRANSICION", color=cq.Color(0.9, 0.55, 0.15, 1.0))
    master.add(camera_mod)

    mic_mod = cq.Assembly(name="05_Microphone_Module")
    mic_input_rack_moved = mic_input_rack.translate((dims["mic_pinion_x"], dims["roller_y"], dims["hinge_z"]))
    mic_gear_moved_t = mic_gear.translate((dims["mic_gear_x"], dims["mic_gear_y"], 0))
    mic_mod.add(mic_pinion_moved, name="Gate_Follower_Pinion", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    mic_mod.add(mic_input_rack_moved, name="Mic_Input_Rack", color=cq.Color(0.35, 0.35, 0.38, 1.0))
    mic_mod.add(mic_gear_moved_t, name="Mic_Window_Reducer", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    mic_mod.add(mic_band_m, name="Mic_Band_EN_TRANSICION", color=cq.Color(0.9, 0.55, 0.15, 1.0))
    mic_input_rack_moved_r = mic_input_rack.translate((dims["mic_pinion_x_r"], dims["roller_y"], dims["hinge_z"]))
    mic_gear_moved_t_r = mic_gear.translate((dims["mic_gear_x_r"], dims["mic_gear_y_r"], 0))
    mic_mod.add(mic_input_rack_moved_r, name="Mic_Input_Rack_R", color=cq.Color(0.35, 0.35, 0.38, 1.0))
    mic_mod.add(mic_gear_moved_t_r, name="Mic_Window_Reducer_R", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    mic_band_m_r = bc.build_mic_curved_band(dims, mic_theta, side="R")
    mic_mod.add(mic_band_m_r, name="Mic_Band_R_EN_TRANSICION", color=cq.Color(0.9, 0.55, 0.15, 1.0))
    master.add(mic_mod)

    std = cq.Assembly(name="08_Standard_Parts")
    std.add(vol_boot, name="Button_Volume_Boot", color=cq.Color(0.4, 0.4, 0.42, 1.0))
    std.add(action_boot, name="Button_Action_Boot", color=cq.Color(0.4, 0.4, 0.42, 1.0))
    std.add(power_boot, name="Button_Power_Boot", color=cq.Color(0.4, 0.4, 0.42, 1.0))
    std.add(usb_flap_moved, name="USB_C_Conductive_Flap", color=cq.Color(0.25, 0.25, 0.27, 1.0))
    master.add(std)

    nonprinted = cq.Assembly(name="09_NonPrinted_Components")
    nonprinted.add(mat_malla_base, name="Conductive_Mesh_cobre_niquel", color=cq.Color(0.75, 0.76, 0.78, 0.9))
    nonprinted.add(mat_junta_rf, name="RF_Gasket", color=cq.Color(0.15, 0.55, 0.15, 0.8))
    nonprinted.add(mat_usb_shield_sleeve, name="USB_Port_Shield_Sleeve", color=cq.Color(0.05, 0.05, 0.05, 0.9))
    nonprinted.add(mat_espuma_mic.translate((0, dims["mic_hinge_y"] + 3.5, bc.WALL + 1.0)),
                    name="Conductive_Foam_Microphone", color=cq.Color(0.6, 0.3, 0.1, 0.8))
    nonprinted.add(mat_iman_usb, name="Magnet_USB_C", color=cq.Color(0.2, 0.2, 0.25, 1.0))
    nonprinted.add(mat_pogo_pin, name="RF_Contact_PogoPin", color=cq.Color(0.85, 0.65, 0.2, 1.0))
    nonprinted.add(mat_cam_pin, name="RF_Contact_PogoPin_Camera", color=cq.Color(0.85, 0.65, 0.2, 1.0))
    nonprinted.add(mat_mic_pin, name="RF_Contact_PogoPin_Microphone", color=cq.Color(0.85, 0.65, 0.2, 1.0))
    nonprinted.add(mat_bola_detent, name="Primary_Latch_Ball_ACERO", color=cq.Color(0.6, 0.6, 0.65, 1.0))
    nonprinted.add(mat_muelle_detent, name="Spring_System_ACERO", color=cq.Color(0.55, 0.55, 0.6, 1.0))
    nonprinted.add(mat_mic_drive_shaft, name="Mic_Band_Drive_Shaft_eje_flexible",
                    color=cq.Color(0.55, 0.55, 0.58, 1.0))
    nonprinted.add(mat_mic_drive_shaft_r, name="Mic_Band_Drive_Shaft_R_eje_flexible",
                    color=cq.Color(0.55, 0.55, 0.58, 1.0))
    nonprinted.add(mat_cam_riser_seal, name="Camera_Riser_Seal_felpa",
                    color=cq.Color(0.1, 0.1, 0.1, 0.85))
    nonprinted.add(mat_pasador1.translate((10, dims["ext_bottom_y"] + 5, 3.0)), name="Alignment_Pin",
                    color=cq.Color(0.5, 0.5, 0.5, 1.0))
    nonprinted.add(mat_tornillo1.translate((15, dims["ext_bottom_y"] + 5, 3.0)), name="Reference_Screw",
                    color=cq.Color(0.4, 0.4, 0.4, 1.0))
    master.add(nonprinted)

    phone_mod = cq.Assembly(name="10_Phone_Reference")
    phone_mod.add(mat_phone_ref, name="iPhone_15_Pro_Max_REFERENCIA", color=cq.Color(0.85, 0.85, 0.87, 0.5))
    master.add(phone_mod)

    top.add(master)
    top.save(out_path)
    print(f"OK - generado: {out_path}")


def build_exploded(out_path: str):
    """Vista EXPLODED (Hoja 6 / Hoja 16 / Hoja 19): separa cada
    subsistema a lo largo de su propio eje de insercion, mostrando el
    orden de montaje definido en la Hoja 16 (Frame -> ejes/imanes ->
    carriles -> Main Carriage -> Camera -> Microphone -> RF -> Lock).
    Solo para documentacion -- las piezas no representan ningun
    estado funcional real."""
    main_switch = bc.build_main_carriage_switch()
    mic_input_rack = bc.build_mic_input_rack(dims)
    mic_gear = bc.build_mic_reducer_gear(dims)
    cam_shutter = bc.build_camera_shutter_slider(dims)
    cam_rod = bc.build_camera_rod(dims)

    EXP = 30.0   # separacion base entre subsistemas, puramente visual

    top = cq.Assembly(name="Privacy_Case_v1_EXPLODED")
    master = cq.Assembly(name="00_Master")

    frame = cq.Assembly(name="02_Frame")
    frame.add(base, name="Back_Housing_and_Side_Walls", color=cq.Color(0.08, 0.08, 0.08, 1.0))
    master.add(frame)

    carriage = cq.Assembly(name="03_Main_Carriage")
    carriage.add(axle_moved.translate((0, 0, EXP)), name="Carriage_Axle", color=cq.Color(0.5, 0.5, 0.5, 1.0))
    carriage.add(pinion_moved.translate((0, 0, EXP * 1.4)), name="Carriage_Pinion", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    switch_ref = main_switch.translate((dims["pinion_x"], dims["roller_y"], dims["hinge_z"]))
    carriage.add(switch_ref.translate((-EXP * 1.8, 0, 0)), name="Sliding_Switch_Interruptor_Unico",
                 color=cq.Color(0.03, 0.03, 0.03, 1.0))
    fabric_piece_a_e = bc.build_rf_fabric_drive_piece_a(dims)
    fabric_piece_b_e, fmy_b_e, fmz_b_e = bc.build_rf_fabric_drive_piece_b(dims)
    fabric_piece_c_e, fmy_c_e, fmz_c_e = bc.build_rf_fabric_drive_piece_c(dims, fmy_b_e, fmz_b_e)
    carriage.add(fabric_piece_a_e.translate((-EXP * 0.4, 0, 0)), name="RF_Fabric_Drive_PiezaA",
                 color=cq.Color(0.3, 0.3, 0.3, 1.0))
    carriage.add(fabric_piece_b_e.translate((-EXP * 0.7, 0, 0)), name="RF_Fabric_Drive_PiezaB",
                 color=cq.Color(0.3, 0.3, 0.3, 1.0))
    carriage.add(fabric_piece_c_e.translate((-EXP * 1.0, 0, 0)), name="RF_Fabric_Drive_Carrete",
                 color=cq.Color(0.3, 0.3, 0.3, 1.0))
    rf_fabric_e = bc.build_rf_fabric_and_pullbar(dims)
    carriage.add(rf_fabric_e.translate((0, 0, EXP * 2.2)), name="RF_Fabric_Roller_DESPLEGADA",
                 color=cq.Color(0.55, 0.55, 0.6, 1.0))
    master.add(carriage)

    camera_mod = cq.Assembly(name="04_Camera_Module")
    camera_mod.add(cam_crank_moved.translate((0, 0, EXP * 0.6)), name="Slider_Follower_Crank",
                    color=cq.Color(0.3, 0.3, 0.3, 1.0))
    camera_mod.add(cam_rod.translate((0, 0, EXP * 0.9)), name="Slider_Interface_Rod",
                    color=cq.Color(0.5, 0.5, 0.52, 1.0))
    camera_mod.add(cam_gear_moved.translate((0, 0, EXP * 1.2)), name="Slider_Reducer",
                    color=cq.Color(0.3, 0.3, 0.3, 1.0))
    shutter_ref = cam_shutter.translate((dims["cam_shutter_ref_x"], dims["cam_center_y"], 0))
    camera_mod.add(shutter_ref.translate((0, 0, EXP * 1.8)), name="Camera_Slider",
                    color=cq.Color(0.2, 0.2, 0.2, 1.0))
    master.add(camera_mod)

    mic_mod = cq.Assembly(name="05_Microphone_Module")
    mic_mod.add(mic_pinion_moved.translate((0, 0, EXP * 1.4)), name="Gate_Follower_Pinion",
                color=cq.Color(0.3, 0.3, 0.3, 1.0))
    mic_input_ref = mic_input_rack.translate((dims["mic_pinion_x"], dims["roller_y"], dims["hinge_z"]))
    mic_mod.add(mic_input_ref.translate((EXP * 1.2, 0, 0)), name="Mic_Input_Rack", color=cq.Color(0.35, 0.35, 0.38, 1.0))
    mic_gear_ref = mic_gear.translate((dims["mic_gear_x"], dims["mic_gear_y"], 0))
    mic_mod.add(mic_gear_ref.translate((0, 0, EXP * 0.8)), name="Mic_Window_Reducer", color=cq.Color(0.3, 0.3, 0.3, 1.0))
    mic_band_ref = bc.build_mic_curved_band(dims, 0.0)
    mic_mod.add(mic_band_ref.translate((EXP * 1.6, 0, 0)), name="Mic_Band", color=cq.Color(0.2, 0.2, 0.2, 1.0))
    mic_input_ref_r = mic_input_rack.translate((dims["mic_pinion_x_r"], dims["roller_y"], dims["hinge_z"]))
    mic_mod.add(mic_input_ref_r.translate((-EXP * 1.2, 0, 0)), name="Mic_Input_Rack_R",
                color=cq.Color(0.35, 0.35, 0.38, 1.0))
    mic_gear_ref_r = mic_gear.translate((dims["mic_gear_x_r"], dims["mic_gear_y_r"], 0))
    mic_mod.add(mic_gear_ref_r.translate((0, 0, -EXP * 0.8)), name="Mic_Window_Reducer_R",
                color=cq.Color(0.3, 0.3, 0.3, 1.0))
    mic_band_ref_r = bc.build_mic_curved_band(dims, 0.0, side="R")
    mic_mod.add(mic_band_ref_r.translate((-EXP * 1.6, 0, 0)), name="Mic_Band_R", color=cq.Color(0.2, 0.2, 0.2, 1.0))
    master.add(mic_mod)

    rf_mod = cq.Assembly(name="06_RF_Module")
    rf_mod.add(base_liner_ref.translate((0, 0, -EXP * 0.5)), name="RF_Carrier_patron_REFERENCIA",
               color=cq.Color(0.05, 0.05, 0.05, 0.35))
    master.add(rf_mod)

    std = cq.Assembly(name="08_Standard_Parts")
    std.add(vol_boot.translate((-EXP, 0, 0)), name="Button_Volume_Boot", color=cq.Color(0.4, 0.4, 0.42, 1.0))
    std.add(action_boot.translate((-EXP, 0, 0)), name="Button_Action_Boot", color=cq.Color(0.4, 0.4, 0.42, 1.0))
    std.add(power_boot.translate((EXP, 0, 0)), name="Button_Power_Boot", color=cq.Color(0.4, 0.4, 0.42, 1.0))
    std.add(usb_flap_moved.translate((0, -EXP, 0)), name="USB_C_Conductive_Flap",
            color=cq.Color(0.25, 0.25, 0.27, 1.0))
    master.add(std)

    nonprinted = cq.Assembly(name="09_NonPrinted_Components")
    nonprinted.add(mat_malla_base.translate((0, 0, -EXP)), name="Conductive_Mesh_cobre_niquel",
                    color=cq.Color(0.75, 0.76, 0.78, 0.9))
    nonprinted.add(mat_junta_rf.translate((0, 0, EXP * 0.5)), name="RF_Gasket",
                    color=cq.Color(0.15, 0.55, 0.15, 0.8))
    nonprinted.add(mat_usb_shield_sleeve.translate((0, -EXP * 0.7, 0)), name="USB_Port_Shield_Sleeve",
                    color=cq.Color(0.05, 0.05, 0.05, 0.9))
    nonprinted.add(mat_espuma_mic.translate((0, dims["mic_hinge_y"] + 3.5, bc.WALL + 1.0)).translate((EXP * 1.2, 0, 0)),
                    name="Conductive_Foam_Microphone", color=cq.Color(0.6, 0.3, 0.1, 0.8))
    nonprinted.add(mat_iman_usb.translate((0, -EXP, 0)), name="Magnet_USB_C", color=cq.Color(0.2, 0.2, 0.25, 1.0))
    nonprinted.add(mat_pogo_pin.translate((0, EXP * 0.8, 0)), name="RF_Contact_PogoPin",
                    color=cq.Color(0.85, 0.65, 0.2, 1.0))
    nonprinted.add(mat_cam_pin.translate((0, 0, EXP * 0.3)), name="RF_Contact_PogoPin_Camera",
                    color=cq.Color(0.85, 0.65, 0.2, 1.0))
    nonprinted.add(mat_mic_pin.translate((EXP * 0.5, 0, 0)), name="RF_Contact_PogoPin_Microphone",
                    color=cq.Color(0.85, 0.65, 0.2, 1.0))
    nonprinted.add(mat_bola_detent.translate((0, 0, EXP * 2.2)), name="Primary_Latch_Ball_ACERO",
                    color=cq.Color(0.6, 0.6, 0.65, 1.0))
    nonprinted.add(mat_muelle_detent.translate((0, 0, EXP * 2.6)), name="Spring_System_ACERO",
                    color=cq.Color(0.55, 0.55, 0.6, 1.0))
    nonprinted.add(mat_mic_drive_shaft.translate((0, EXP * 0.4, EXP * 0.4)), name="Mic_Band_Drive_Shaft_eje_flexible",
                    color=cq.Color(0.55, 0.55, 0.58, 1.0))
    nonprinted.add(mat_mic_drive_shaft_r, name="Mic_Band_Drive_Shaft_R_eje_flexible",
                    color=cq.Color(0.55, 0.55, 0.58, 1.0))
    nonprinted.add(mat_cam_riser_seal.translate((0, EXP * 0.6, -EXP * 0.3)), name="Camera_Riser_Seal_felpa",
                    color=cq.Color(0.1, 0.1, 0.1, 0.85))
    master.add(nonprinted)

    phone_mod = cq.Assembly(name="10_Phone_Reference")
    phone_mod.add(mat_phone_ref, name="iPhone_15_Pro_Max_REFERENCIA", color=cq.Color(0.85, 0.85, 0.87, 0.5))
    master.add(phone_mod)

    top.add(master)
    top.save(out_path)
    print(f"OK - generado: {out_path}")


build_transition(0.5, "Privacy_Case_v1_TRANSITION.step")
build_exploded("Privacy_Case_v1_EXPLODED.step")
