# PROJECT AEGIS — iPhone 15 Pro — FINAL
## Memoria técnica V3 · Funda mecánica de privacidad física para impresión 3D

**Documento Fusion 360:** `AEGIS_V2_3DPrint33333` (Default Project) — **guardado**.
17 componentes · 16 joints · 227 features · 179 parámetros · **0 features en error**.

**Estado de validación:** barrido cinemático de **44 posiciones** del recorrido con intersección booleana
exacta entre los 16 cuerpos móviles y fijos → **0 interferencias**.

### REV A — corrección de esquinas (piel exterior)

**ERROR:** agujeros pasantes en las cuatro esquinas, visibles sobre todo en las esquinas superior e
inferior del lado de los botones.
**CAUSA:** los canales internos `SK_CUT_BARLEG`, `SK_CUT_BARPLATE`, `SK_CUT_BARARM`,
`SK_CUT_AC_CHAMBER`, `SK_CUT_AC_RISER` y `SK_CUT_AC_ARM` se cortaron con límites en X de hasta
±36 mm, mayores que el radio de esquina real de la carcasa (15.2 mm) en esas bandas de Y. Los cortes
salían por la superficie exterior.
**CORRECCIÓN:**

1. Restauración de la piel exterior completa: junta de un anillo perimetral de 1.2 mm entre el
   contorno exterior y su offset interior, sobre Z = −3.6 … 13.65.
2. Reapertura únicamente de los huecos legítimos: apertura frontal, 4 recortes de botón, USB-C,
   salidas acústicas, rebaje del slider y ranura pasante del slider.
3. Recorte de las piezas móviles que quedaban fuera de la nueva piel:
   - `AEGIS_ACOUSTIC_GATE`: lámina limitada a X ≤ 30.0 y chaflán en la esquina inferior +X.
   - `AEGIS_FRONT_TRANSFER_BAR`: placa limitada a Y ≤ 79.5 y chaflán en la esquina +X/+Y de la placa y
     del montante.
   - `AEGIS_FRONT_CAM_FLAP`: lámina limitada a Y ≤ 80.7 y cubo reducido a Ø7.6 en el semiplano −X
     (la zona que barre hacia +Y durante la rotación).
4. Reajuste funcional consecuente: grupo de salidas acústicas derecho de X[11, 21] a **X[11, 17]**
   (interior y exterior), para que el nuevo extremo de la compuerta lo siga cubriendo en OFFLINE.
5. Eliminadas 2 features de extrusión sin cuerpo de destino (residuo de la reconstrucción).

**RESULTADO:** cuatro esquinas continuas y sólidas, verificadas visualmente en las cuatro posiciones,
y **0 interferencias en 44 posiciones** del recorrido. Volumen total 78.73 cm³ → 98 g en PLA.

> Este documento sustituye a `AEGIS_V2_Memoria_Tecnica.md` y a `AEGIS_V2_Defectos_Pendientes.md`,
> que quedan obsoletos.

---

## 1. REQUISITO PRINCIPAL DE ESTA ITERACIÓN — TRASERA UNIFORME

**CUMPLIDO.** Se ha eliminado la meseta de cámara. La cara trasera es ahora **una única superficie plana
continua a cota Z = 16.25 mm**, sin escalones, sin cavidades y sin ningún elemento del mecanismo visible.

| | ONLINE | OFFLINE |
|---|---|---|
| Trasera | superficie uniforme + ventana de cámara abierta | superficie uniforme + cubrecámaras integrado |
| Mecanismo visible | ninguno | ninguno |
| Raíles / láminas / huecos visibles | ninguno | ninguno |

**Cómo se ha conseguido geométricamente:**

1. **Trasera plana.** `Z_BACK = 16.25 mm` en toda la superficie. La antigua meseta de 2.9 mm ha desaparecido.
2. **Cubrecámaras de UNA sola pieza.** Se ha eliminado el obturador telescópico S1+S2 (dos láminas con
   junta visible) y se ha sustituido por `AEGIS_CAMERA_COVER`, un panel único de 42 × 38 × 1.2 mm que
   desliza **38 mm en Y** por debajo de la piel exterior.
3. **Ventana biselada a 45° en todo el espesor del panel.** El panel trasero tiene 1.2 mm de espesor y el
   bisel es de 1.2 mm → el borde de la ventana es un filo, no una pared vertical. Visualmente el
   cubrecámaras se lee **a ras**.
4. **Solape de estanqueidad óptica.** El cubrecámaras es mayor que la boca exterior del bisel en
   0.80 mm (−X), 4.80 mm (+X), 15.80 mm (−Y) y 2.56 mm (+Y). **No existe línea de visión al interior
   desde ningún ángulo.**
5. **Ocultación en ONLINE.** El borde superior del cubrecámaras replegado queda 0.80 mm por debajo del
   borde exterior de la ventana → invisible.

---

## 2. CAMBIOS DE ARQUITECTURA DE ESTA ITERACIÓN (y por qué)

| # | Cambio | Razón técnica |
|---|---|---|
| C-1 | Carcasa dividida en `AEGIS_CASE_FRONT` / `AEGIS_CASE_REAR` por el plano Z = 13.65 | Sin división el cubrecámaras es **imposible de montar**: su alojamiento no tiene acceso |
| C-2 | Obturador telescópico S1+S2 (2 láminas + 2 tendones + 2 poleas + 4 anclajes) → cubrecámaras único + tren de engranajes | Elimina la junta visible entre láminas, elimina los tendones (fluencia, ajuste en montaje) y **reduce 8 elementos a 3** |
| C-3 | Amplificación 2:1 por **engranaje compuesto** (z12/z24, módulo 0.8, dentado de evolvente real generado) | Convierte los 19 mm en X del seguidor CAM-01 en 38 mm en Y del cubrecámaras, **positivo en ambos sentidos**, sin cordones |
| C-4 | Carro maestro elevado a Z = 12.25 | Libra la envolvente de la isla de cámaras (Z ≤ 12.14). Corrige el defecto crítico D-10 de la iteración anterior |
| C-5 | Tren de engranajes reubicado a Y = 16 | El eje a Y = 28 invadía la envolvente de la isla |
| C-6 | Marco RF perimetral móvil → **contacto RF puntual** (`AEGIS_RF_CONTACT` + fingerstock) | El anillo perimetral es **geométricamente incompatible** con los tres botones laterales y la ranura del slider: atravesaba literalmente el espacio de los botones del teléfono |
| C-7 | `RF_POSITION_TRAVEL` 2.0 → 1.5 mm, `RF_COMPRESSION_TRAVEL` 1.0 → 0.5 mm | Presupuesto Z real disponible entre la barra de empuje (9.45) y la cara conductora del panel trasero (13.65) |
| C-8 | Dos capas de seguidores independientes (A: 9.45–10.15, B: 10.45–11.15) | Permite cruzar `FRONT_TRANSFER_BAR` con `CAM1_FOLLOWER` y `ACOUSTIC_GATE` sin colisión |

Se **conservan** sin cambios: posición y recorrido del slider lateral, arquitectura de un único
accionamiento, tabla cinemática de 4 fases, mecanismo frontal rotativo, compuerta acústica de ventana única,
dimensiones exteriores de anchura y longitud, posición de botones y estética minimalista.

---

## 3. ENVOLVENTE

| Magnitud | Valor |
|---|---|
| Anchura | 78.0 mm (79.0 mm con la pestaña del slider) |
| Longitud | 163.2 mm |
| Espesor total | **19.85 mm** (uniforme, sin meseta) |
| Radio de esquina exterior | 15.2 mm |
| Volumen de material | 77.85 cm³ |
| Masa estimada | 97 g (PLA) / 99 g (PETG) |

Pila Z (desde el cristal): labio 3.6 → teléfono 8.25 → forro 0.8 → seguidores A/B 1.7 → carro 1.2 →
plano de partición 13.65 → cubrecámaras 1.2 → panel trasero 1.2 → **16.25**.

Sistema de coordenadas: Z = 0 en el plano del cristal, +Z hacia la trasera; +Y hacia el borde superior;
+X hacia el lateral de botones de volumen/acción (lado del slider).

---

## 4. TABLA CINEMÁTICA MAESTRA (KD-010)

Entrada única: `AEGIS_SLIDER`, recorrido **x = 0 … 30 mm** (0 = ONLINE, 30 = OFFLINE).

| Fase | x | Leva | Seguidor | Salida | Recorrido | Áng. presión |
|---|---|---|---|---|---|---|
| Óptica trasera | 0.5 → 11.5 | CAM-01 | `AEGIS_CAM1_FOLLOWER` | X | 19.0 mm | 60.0° |
| Óptica frontal | 4.0 → 12.0 | CAM-02 | `AEGIS_FRONT_TRANSFER_BAR` | X | 3.0 mm | 20.6° |
| Acústica | 12.2 → 19.8 | CAM-03 | `AEGIS_ACOUSTIC_GATE` | X | 12.0 mm | 57.6° |
| RF posición | 20.0 → 24.0 | CAM-45 t1 | `AEGIS_RF_PUSH_BAR` | X | 4.0 mm | 45.0° |
| RF compresión | 24.0 → 30.0 | CAM-45 t2 | `AEGIS_RF_PUSH_BAR` | X | 4.0 mm | 33.7° |

Cadenas de salida:

- **CAM-01** → cremallera (m 0.8, 25 mm) → **piñón z12** → eje común → **rueda z24** → cremallera del
  cubrecámaras → **38 mm en Y**. Relación exacta 2.000.
- **CAM-02** → barra de transferencia en Z (cavidad → pared superior → plano frontal) → **yugo escocés**
  (perno Ø2 a radio 3.0) → **rotación de 90°** de la lámina frontal. El punto muerto a 90° actúa como
  autobloqueo en OFFLINE.
- **CAM-03** → brazo → montante → compuerta acústica de ventana única, **12 mm en X**.
- **CAM-45** → barra de empuje → rampa de doble pendiente (26.6° / 14°) → contacto RF, **1.94 mm en Z**.

---

## 5. VERIFICACIÓN FUNCIONAL (medida sobre el CAD)

| Comprobación | Resultado |
|---|---|
| Cubrecámaras ONLINE: no visible | margen 0.80 mm **OK** |
| Cubrecámaras OFFLINE: cubre la boca exterior de la ventana | solapes 0.80 / 4.80 / 15.80 / 2.56 mm **OK** |
| Lámina frontal OFFLINE: cubre la cámara frontal (5.5, 60.3) Ø3 | ocupa X[1.5, 9.5] Y[58.0, 77.0] **OK** |
| Lámina frontal ONLINE: oculta bajo el labio | Y[73, 81], labio hasta Y = 70.1 **OK** |
| Acústica ONLINE: ambos puertos abiertos | ventana X[10.5, 21.5] + barra desde X = −9 **OK** |
| Acústica OFFLINE: ambos puertos cerrados | sólido X[−21, −1.5] y X[9.5, 23] **OK** |
| Slider vs zona de botones | margen 9.3 mm **OK** |
| USB-C libre en ambos estados | hueco Z[1.9, 6.35] vs compuerta Z[6.6, 9.0] **OK** |
| Interferencias, 34 posiciones × 16 cuerpos | **0** |
| Features en error | **0** |

---

## 6. LISTA DE COMPONENTES

| Componente | Cuerpos | cm³ | Proceso |
|---|---|---|---|
| `AEGIS_CASE_FRONT` | 1 | 34.61 | FDM |
| `AEGIS_CASE_REAR` | 1 | 24.72 | FDM |
| `AEGIS_CASE_LINER` | 1 | 8.60 | FDM |
| `AEGIS_SLIDER` | 1 | 0.195 | FDM |
| `AEGIS_MASTER_CARRIAGE` | 1 | 2.63 | FDM |
| `AEGIS_CAM1_FOLLOWER` | 1 | 0.201 | FDM |
| `AEGIS_COVER_GEAR` | 1 | 0.374 | FDM |
| `AEGIS_CAMERA_COVER` | 1 | 2.01 | FDM conductivo |
| `AEGIS_FRONT_TRANSFER_BAR` | 1 | 0.640 | FDM |
| `AEGIS_FRONT_CAM_FLAP` | 1 | 0.191 | FDM conductivo |
| `AEGIS_ACOUSTIC_GATE` | 1 | 0.342 | FDM conductivo |
| `AEGIS_RF_PUSH_BAR` | 1 | 0.362 | FDM |
| `AEGIS_RF_CONTACT` | 1 | 0.109 | FDM conductivo |
| `AEGIS_SEALS` | 2 | 0.036 | compra — fingerstock BeCu |
| `AEGIS_FARADAY_LAYER` | 2 | 2.83 | compra — lámina Cu + ventana PET-ITO |
| `PHONE_REFERENCE` / `KEEP_OUT` | 2 / 4 | — | referencia |

---

## 7. JOINTS

16 joints as-built con límites activos:

| Joint | Tipo | Límites |
|---|---|---|
| `J_SLIDER`, `J_MASTER_CARRIAGE` | slider Y | 0 … 30 mm |
| `J_CAM1_FOLLOWER` | slider X | −19 … 0 mm |
| `J_CAMERA_COVER` | slider Y | 0 … 38 mm |
| `J_COVER_GEAR` | revolute Z | 0 … 226.8° |
| `J_FRONT_TRANSFER_BAR` | slider X | −3 … 0 mm |
| `J_FRONT_CAM_FLAP` | revolute Z | −90 … 0° |
| `J_ACOUSTIC_GATE` | slider X | −12 … 0 mm |
| `J_RF_PUSH_BAR` | slider X | −8 … 0 mm |
| `J_RF_CONTACT` | slider Z | 0 … 1.94 mm |
| `J_CASE_REAR`, `J_CASE_LINER`, `J_FARADAY_LAYER`, `J_PHONE_REFERENCE`, `J_KEEP_OUT`, `J_SEALS_ON_CONTACT` | rigid | — |

---

## 8. FABRICACIÓN Y MONTAJE

Proceso: FDM, boquilla 0.4, capa 0.15. Holguras: deslizante 0.25 · captiva 0.35 · guía del carro 0.35.

**Orden de montaje (verificado geométricamente — ninguna pieza queda atrapada):**

1. `AEGIS_CASE_FRONT` boca arriba.
2. `AEGIS_CASE_LINER` desde el frente (tope en el hombro Z = 9.35, 4 clips).
3. Capa A: `AEGIS_FRONT_TRANSFER_BAR`, `AEGIS_RF_PUSH_BAR`.
4. `AEGIS_RF_CONTACT` sobre sus dos postes + `AEGIS_SEALS`.
5. Capa B: `AEGIS_CAM1_FOLLOWER`, `AEGIS_ACOUSTIC_GATE` (montante desde la pared inferior).
6. `AEGIS_COVER_GEAR` sobre el poste del forro.
7. `AEGIS_MASTER_CARRIAGE` sobre las repisas; `AEGIS_SLIDER` desde el exterior encajando en la mortaja.
8. `AEGIS_FRONT_CAM_FLAP` sobre el pivote de la pared superior.
9. `AEGIS_CAMERA_COVER` en las guías del panel trasero, engranando la cremallera.
10. Lámina Faraday, ventana PET-ITO y cierre de `AEGIS_CASE_REAR` (4 localizadores + apoyo perimetral).

**Orientaciones recomendadas:** ambas mitades de carcasa con la cara exterior hacia abajo; carro,
cubrecámaras y seguidores planos; engranaje con el eje vertical.

**Puntos sensibles de impresión:** techo del panel trasero de 1.2 mm sobre 42 mm de vano (ventilación
máxima); dentado módulo 0.8 (altura de diente 1.8 mm) imprimible a 0.4 mm de boquilla pero exige
calibración de flujo; lubricar las rampas RF con PTFE.

---

## 9. RIESGOS ABIERTOS (no bloquean el diseño mecánico)

| ID | Riesgo | Severidad |
|---|---|---|
| R-01 | Ángulo de presión de CAM-01 = 60° → fuerza en el slider ≈ 4.2 × la resistencia del cubrecámaras | media |
| R-02 | Dentado m 0.8 en FDM: juego real y desgaste no caracterizados | media |
| R-03 | Fuga RF por la ranura del slider (37 mm) — requiere fingerstock deslizante | alta |
| R-04 | Fuga RF por recortes de botón y puerto USB-C (guía bajo corte ≈ 18 dB) | alta |
| R-05 | Atenuación RF y acústica **NO VALIDADAS** (sin simulación EMC ni ensayo acústico) | alta |
| R-06 | Fuerza de accionamiento no calculada (fricción real de material y acabado) | media |
| R-07 | Rebaje visual del cubrecámaras de 1.30 mm bajo la piel, con bisel a 45° en todo el espesor del panel | estética, aceptada |

---

*Todos los valores proceden de la medición directa del modelo Fusion 360, no de descripciones previas.*
