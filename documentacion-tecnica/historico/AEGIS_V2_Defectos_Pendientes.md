# AEGIS V2 — Registro de defectos de validación

Método: barrido cinemático automático de 18–22 posiciones del recorrido (x = 0 … 30 mm) con
intersección booleana exacta (`TemporaryBRepManager`, `IntersectionBooleanType`) de todos los pares
de sólidos, con filtrado previo por caja envolvente. Umbral de error: **volumen de intersección > 0.001 cm³**.

Barrido de referencia (previo a correcciones): **25 pares con interferencia**.

---

## A. DEFECTOS CORREGIDOS (pendientes de re-verificación en el siguiente barrido)

| ID | Par | V máx | Causa | Corrección aplicada |
|---|---|---|---|---|
| D-01 | CASE_SHELL × FRONT_TRANSFER_BAR | 75.76 mm³ | Canales `SK_CUT_BARLEG` / `SK_CUT_BARARM` cortados sólo para X ≥ 24; la barra retrocede 3 mm hasta X = 21.5 | Canales ampliados a X ≥ 21 (`SK_FIX_BARLEG_WIDE`, `SK_FIX_BARARM_WIDE`, `SK_FIX_BARARM_LEDGE`) |
| D-02 | CASE_SHELL × ACOUSTIC_GATE | 6.75 mm³ | El brazo (X 27–31) invade la repisa de apoyo exterior del carro (X 30.5–34) | Brazo recortado a X ≤ 30.3 (`SK_FIX_AG_ARM_TRIM`) |
| D-03 | REAR_SHUTTER_S1 × REAR_SHUTTER_S2 | 5.35 mm³ | Las poleas de tendón de S1 se extendían hasta Z 13.50, invadiendo el plano de S2 (13.50–14.20) | Poleas recortadas a Z ≥ 14.45 (`SK_FIX_S1_PULLEY_TRIM`) |
| D-04 | RF_FOIL_REAR × REAR_SHUTTER_S1 | 0.31 mm³ | Cordón/anclajes de S2 fuera del plano del tendón | Anclajes de S2 elevados a Z 14.20–15.00 (`SK_FIX_S2_ANCHORS_UP`) |

---

## B. DEFECTOS ABIERTOS — ARQUITECTURA

### D-10 · KEEP_OUT × MASTER_CARRIAGE — 45.06 mm³ · **CRÍTICO**
**CAUSA:** el carro maestro ocupa Z 11.15–12.35; la envolvente de la isla de cámaras llega a
Z 12.14 (11.84 + 0.30 de holgura). En X 6.0–8.3 el carro solapa la isla en 0.99 mm de altura.
No depende de la posición del slider: la pared izquierda de la ranura CAM-01 debe existir en
X 6.0–7.1 y esa zona está siempre bajo la isla (Y global ≈ 36 mm).

**CORRECCIÓN REQUERIDA (paramétrica, en cascada):**
`Z_CAR_0 = Z_OUT_1 + 1.39 mm` → 12.24 mm, `MECH_GAP = 4.30 mm`.
Consecuencias: `Z_CAV_1` 12.55 → 13.65 · `Z_SHELL_1` 13.75 → 14.85 · pila de la meseta +1.10 mm ·
`SLIDER_SLOT_Z0/Z1` +1.10 mm · espesor total 20.25 → 21.35 mm.
Requiere reconstruir `CASE_SHELL`, `MASTER_CARRIAGE`, `SLIDER_TAB`, `REAR_SHUTTER_S1/S2`.

**Alternativa descartada:** escalonar el carro sobre la isla — imposible, la zona afectada es fija
en coordenadas globales pero móvil en coordenadas del carro.

### D-11 · KEEP_OUT × RF_FRAME — 92.95 mm³ · **CRÍTICO**
### D-12 · KEEP_OUT × RF_WEDGE_R / RF_WEDGE_L — 66.50 / 33.70 mm³ · **CRÍTICO**
**CAUSA:** el canal del marco RF (X 36.2–38.2, Z 2.8–11.35) atraviesa las zonas de botón lateral
`KO_BTN_PLUSX` (X 35.3–37.9, Y −8.7…40.3, Z 1.0–7.5) y `KO_BTN_MINUSX` (X −37.9…−35.3, Y −11.7…13.3).
El marco RF (Z 4.85–7.35) y las varillas de cuña ocupan literalmente el espacio de los botones del teléfono.

**CORRECCIÓN REQUERIDA:** practicar entalladuras en `RF_FRAME`, `RF_GASKET`, `RF_WEDGE_R` y `RF_WEDGE_L`
en Y ∈ [−10.5, 42.1] (lado +X) y Y ∈ [−13.5, 15.1] (lado −X), reubicando los resaltes de apoyo
(`BOSS`) y las rampas fuera de esas ventanas.
**Consecuencia RF:** el blindaje queda interrumpido en las zonas de botón. Esto **no empeora** la
situación real, porque los recortes de botón de la carcasa ya son aperturas del blindaje; exige
membranas conductoras sobre los botones (elemento de compra, ya listado).

### D-13 · RF_PUSH_BAR × RF_WEDGE_L / RF_WEDGE_R — 27.98 / 17.98 mm³ · **ALTO**
**CAUSA:** el perno de la lengüeta de cuña (Ø2, en (±24, −18)) y la ranura a 45° de `RF_PUSH_BAR`
comparten el plano Z 9.45–10.15. La lengüeta completa —no sólo el perno— entra en la ranura.
**CORRECCIÓN REQUERIDA:** separar en Z (perno en Z 10.15–10.85 y ranura en la barra a esa cota) o
estrechar la lengüeta a la anchura del perno.

### D-14 · CASE_SHELL × RF_WEDGE_R / RF_WEDGE_L — 6.56 mm³ (s = 30) · **MEDIO**
**CAUSA:** con el recorrido completo (−8 mm en Y) el extremo de la varilla alcanza Y = −76,
fuera del tramo recto del canal (radio de esquina). **CORRECCIÓN:** acortar la varilla a Y ∈ [−64, 68].

### D-15 · FRONT_TRANSFER_BAR × RF_FRAME — 3.76 mm³ (s = 30) · **MEDIO**
### D-16 · ACOUSTIC_GATE × RF_FRAME — 0.32 mm³ · **BAJO**
### D-17 · SLIDER_TAB × RF_FRAME / RF_WEDGE_R — 0.14 mm³ · **BAJO**
**CAUSA común:** en OFFLINE el marco RF sube a Z 7.85–10.35 e invade la capa de seguidores (9.45–10.85).
**CORRECCIÓN REQUERIDA:** bajar la cota del marco (`Z_RF_0` = 3.35, `RF_CONTACT_Z` = 9.85) o subir la
capa de seguidores. Ligado a D-10.

### D-18 · RF_WEDGE_R/L × RF_FRAME — 1.84 mm³ (s = 30) · **ESPERADO / A REVISAR**
Contacto de diseño rampa–resalte. Debe convertirse en contacto tangente (0 mm³) ajustando el perfil
de rampa en 0.05 mm.

---

## C. DEFECTOS ABIERTOS — DETALLE

| ID | Par | V máx | Nota |
|---|---|---|---|
| D-20 | CASE_SHELL × MASTER_CARRIAGE | 11.04 mm³ (s = 28) | Pendiente de localizar la cara concreta; probablemente tope de fin de recorrido |
| D-21 | CASE_SHELL × REAR_SHUTTER_S1 | 3.14 mm³ (s = 0) | Poleas de tendón contra la pared de la cámara de láminas |
| D-22 | CASE_SHELL × REAR_SHUTTER_S2 | 1.75 mm³ (s = 11.5) | Extremo desplegado contra la pared X = −31 |
| D-23 | CASE_SHELL × SLIDER_TAB | 1.08 mm³ (s = 0) | Cabeza de la pestaña contra el rebaje |
| D-24 | KEEP_OUT × REAR_SHUTTER_S1 | 0.80 mm³ (s = 11.5) | Poleas contra la envolvente de la isla |
| D-25 | FRONT_TRANSFER_BAR × FRONT_CAM_FLAP | 0.15 mm³ (s = 12) | Perno de yugo contra el extremo de la ranura en el punto muerto |
| D-26 | CASE_SHELL × RF_FRAME | 1.64 mm³ (s = 30) | Ligado a D-11/D-17 |
| D-27 | RF_GASKET × repisa de contacto | por diseño | La junta se modela rígida; en OFFLINE se comprime 1.0 mm (50 %) |

---

## D. ORDEN DE CORRECCIÓN RECOMENDADO

1. **D-10** (cota del carro) — reconstrucción en cascada; resuelve además D-15/16/17 si se
   reordena la pila Z de una vez.
2. **D-11 / D-12** (entalladuras del marco RF en zonas de botón).
3. **D-13** (acoplamiento cuña–barra).
4. **D-14, D-20 … D-26** (detalle).
5. Repetir el barrido completo hasta **0 pares con interferencia**.

Hasta completar los puntos 1–5 el modelo **NO** cumple el criterio de finalización del proyecto y
**NO** debe exportarse a STL ni a STEP para fabricación.
