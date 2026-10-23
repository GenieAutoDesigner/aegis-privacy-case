# AEGIS — V7 · Informe de validación mecánica (DFM/DFA)

**Base:** `AEGIS_iPhone15Pro_V6` (intacta, no modificada)
**Trabajo:** `AEGIS_iPhone15Pro_V7` (copia exacta creada con Save As, id `abe626d0-54c1-4555-bb35-e9a185000e71`)
**Fecha:** 2026-08-09
**Restricción absoluta:** geometría exterior de V6 congelada.

---

## 1. Estado real leído del CAD (no de imágenes ni de versiones anteriores)

| Concepto | Valor real medido en V7 |
|---|---|
| Parámetros de usuario | 232 |
| Features en timeline | 533 |
| Componentes con geometría | 17 (+30 componentes `TMP_*` vacíos) |
| Joints | 0 en raíz, 15 as-built (4 rígidos, 9 deslizantes, 2 de revolución) |
| Unidades | mm |

### Cadena cinemática reconstruida (verificada contra los parámetros KD_*)

| Ventana del slider `s` | Mecanismo | Movimiento |
|---|---|---|
| 0.5 → 11.5 mm | CAM-01 → seguidor S1 | X: 0 → −19.0 mm |
| ” | engranaje compuesto m0.7 z12/z27 | 0 → +259.19° |
| ” | cubrecámaras | Y: 0 → +42.75 mm |
| 4.0 → 12.0 mm | CAM-02 → barra de transferencia frontal | X: 0 → −4.098 mm |
| ” | yugo escocés → lámina frontal | 0 → 90° |
| 12.2 → 19.8 mm | CAM-03 → compuerta acústica | X: 0 → −12.0 mm |
| 20.0 → 24.0 mm | CAM-04 → empujador RF (posicionamiento) | X: 0 → −4.0 mm / Z contacto 0 → +1.5 mm |
| 24.0 → 30.0 mm | CAM-05 → empujador RF (compresión) | X: −4 → −8 mm / Z contacto +1.5 → +2.0 mm |

---

## 2. Métodos de validación empleados

1. **Análisis de interferencias real de Fusion** (`Design.analyzeInterference`) sobre 15–18 componentes, en **31 pasos** del recorrido del slider (s = 0…30 mm en incrementos de 1 mm). No sólo en los extremos.
2. **Test de cobertura óptica**: intersección booleana de un cilindro con el diámetro de cada apertura (C1, C2, C3, flash, LiDAR, micrófono trasero) contra el cubrecámaras en su posición transformada.
3. **Test de continuidad de aire** (decisivo para acústica): construcción del volumen de aire de la pared inferior por diferencia booleana contra carcasa, forro, compuerta y teléfono, y **recuento de lumps** (volúmenes conectados). Si el sellado funciona, el aire debe partirse en ≥2 lumps.
4. **Medición de distancias mínimas reales** (`MeasureManager.measureMinimumDistance`) entre pares críticos.
5. **Descomposición por bandas** (X/Y/Z) de los cuerpos para separar función de envolvente.

---

## 3. Defectos confirmados

### D1 — CRÍTICO · La capa Faraday frontal tapa toda la pantalla
`AEGIS_FARADAY_LAYER_2` era una placa **sólida** de 0.2 mm, 69 × 145 mm, sin ninguna abertura (V = 1981.3 mm³ ≡ rectángulo redondeado macizo), unida **rígidamente** al chasis. Obstrucción medida dentro del volumen de visión de la pantalla: **1834.1 mm³**.
Incumple el requisito ONLINE «pantalla completamente accesible» de forma permanente, en ambos estados.

**Estado: CORREGIDO** — convertida en marco perimetral bajo el labio (V 1981.3 → 195.9 mm³). Obstrucción de pantalla = 0.

### D2 — CRÍTICO · La lámina de cámara frontal gira en sentido equivocado
- Sentido actual: **+90°** → la lámina sale **13.9 mm fuera** de la funda (bbox Y máx 96.0 mm frente a Y exterior 82.1 mm).
- Interferencia sólida contra `AEGIS_CASE_FRONT`: **21.39 mm³ máx**, presente de forma continua desde s = 5 hasta s = 30 (26 de los 31 pasos).
- Interferencia adicional contra la barra de transferencia: 2.83 mm³.
- **Cobertura de la cámara frontal medida: 0 % en ONLINE y 0 % en OFFLINE.**
- Defecto secundario: aun invirtiendo el giro, el arco barrido cruza el labio frontal (banda Y 70.1…73.3 mm) y **no existe ranura de paso**.

### D3 — CRÍTICO · El aislamiento acústico no existe
Geometría real:
- Orificios exteriores: 2 grupos de 5 taladros Ø1.0 mm, paso 1.45 mm, **Z 3.62…4.62 mm**, atravesando la piel Y −81.10…−80.30.
- Compuerta acústica: **Z 6.60…13.45 mm**.

Los rangos en Z son **disjuntos**: la compuerta no puede interceptar los orificios en ninguna posición.

Test de continuidad de aire (X −24…24, Y −81.5…−73.0, Z 1.5…10.5):

| Estado | Volumen de aire | Lumps | Camino exterior→teléfono |
|---|---|---|---|
| ONLINE | 1767.05 mm³ | **1** | abierto |
| OFFLINE | 1729.87 mm³ | **1** | **abierto** |

La compuerta sólo elimina 37 mm³ de aire y **no separa el camino**. Aislamiento acústico = 0.

Defecto adicional: en OFFLINE el orificio de X ≈ +16.8…+17.3 queda además fuera del recorrido de la pala.

**Causa raíz del problema (importante para el rediseño):** a la altura de los orificios (Z 3.2…5.2) **no existe espacio de aparcamiento en X** para una pala deslizante: el conector USB-C ocupa X ±6.5 mm en Z 1.90…6.35, y la cavidad termina en X = ±17.6. Por eso la compuerta original se colocó a Z 6.4…9.3, donde sí hay hueco — pero ahí no hay nada que cerrar.

### D4 — CRÍTICO · La jaula de Faraday no cierra
- `AEGIS_RF_CONTACT` sube hasta **Z 12.95 mm** en OFFLINE.
- Capa conductora trasera `AEGIS_FARADAY_LAYER_1`: **Z 15.05…15.15 mm**.
- Distancia mínima medida contacto ↔ `AEGIS_CASE_REAR`: **2.70 mm**.

No hay ninguna superficie conductora en el plano de cierre (`Z_SPLIT` = 13.65 mm) contra la que cerrar. **No hay continuidad eléctrica.**

### D5 — GRAVE · Las juntas RF están unidas al componente equivocado
`J_AEGIS_SEALS_RIGID` une `AEGIS_SEALS` a `AEGIS_CASE_FRONT` en lugar de a `AEGIS_RF_CONTACT`.
Consecuencia: las juntas no acompañan al contacto y éste las atraviesa 0.8 mm sobre una altura libre de 1.2 mm.

Nota: el **presupuesto de cotas sí es correcto** (contacto 10.95 + junta 1.2 = 12.15; elevación 1.5 → 13.65 = `Z_SPLIT` = primer contacto; +0.5 de compresión = `RF_COMPRESSION_TRAVEL`). El error es de **parentesco de junta**, no de dimensionado.

### D6 — GRAVE · Los limpiadores acústicos no son fabricables
`AEGIS_AC_WIPER`: 4 cuerpos de **0.40 mm (Y) × 0.25 mm (Z)**, volúmenes de 0.5–0.8 mm³.
Con boquilla de 0.4 mm y capa de 0.15 mm eso es 1 extrusión × 1.7 capas: no es una pieza, es un artefacto de CAD. Además interfieren con la carcasa en ONLINE (0.16 / 0.098 / 0.040 mm³).

### D7 — MEDIO · Holguras nulas en pares deslizantes
| Par | Distancia mínima medida |
|---|---|
| `MASTER_CARRIAGE` ↔ `CASE_FRONT` | **0.0000 mm** |
| `CAMERA_COVER` ↔ `CASE_REAR` | **0.0000 mm** |
| `SLIDER` ↔ `CASE_FRONT` | 0.1000 mm |
| `SLIDER` ↔ `MASTER_CARRIAGE` | 0.1500 mm |

`FDM_CLEARANCE_SLIDE` está declarado como 0.25 mm pero **no se ha aplicado** en los dos pares principales. Agarrotamiento garantizado en la pieza impresa.

### D8 — MEDIO · Engranaje al límite
- Backlash medido piñón ↔ cremallera CAM-01: **0.10 mm**; piñón ↔ cremallera cubrecámaras: **0.30 mm**.
- Módulo 0.7, z = 12 (r primitivo 4.2 mm), giro de 259°.
0.10 mm de juego es insuficiente para FDM (se requiere ≥ 0.20–0.25 mm). Riesgo de bloqueo por dilatación de perímetros.

### D9 — MENOR
- `COVER_T` = 0.8 mm pero el cuerpo real del cubrecámaras mide **0.70 mm** (confirmado: la cobertura óptica medida da exactamente 87.5 % = 0.7/0.8).
- 30 componentes `TMP_*` vacíos en el árbol.

---

## 4. Lo que SÍ funciona (validado, no supuesto)

| Función | Resultado |
|---|---|
| Obturador de cámaras traseras — cobertura OFFLINE | **100 % lateral** sobre C1, C2, C3, flash, LiDAR y micrófono trasero (medido por intersección de aperturas) |
| Obturador de cámaras traseras — ocultación ONLINE | **0 % de obstrucción**; totalmente retraído |
| Tren de engranajes | relación coherente: 19 mm × 27/12 = 42.75 mm; sentido de giro correcto |
| Cubrecámaras ↔ isla de cámaras del teléfono | sin interferencia en todo el recorrido; holgura 3.00 mm al teléfono |
| Slider ↔ zona de botones del iPhone | sin invasión (slider Y máx −18 mm; keep-out empieza en −8.7 mm) |
| Recorrido del carro maestro | sin colisión con teléfono (2.33 mm) ni forro (1.80 mm) |
| Presupuesto de cotas RF | aritméticamente correcto (ver D5) |

---

## 5. Conclusión honesta sobre la jaula de Faraday

Con la pantalla accesible en ONLINE, **la envolvente conductora no puede cerrarse por la cara frontal**. Una apertura de 65 × 141 mm domina completamente la atenuación a frecuencias celulares/Wi-Fi: la atenuación real del conjunto será baja con independencia de la calidad del contacto trasero.

Se mantiene por tanto:
- capa conductora trasera + marco perimetral frontal + contacto conmutado (atenuación útil en el hemisferio trasero),
- **sin** afirmar bloqueo integral de comunicaciones.

Declararlo como «jaula de Faraday completa» sería un dato no validado. Requiere medida real con analizador de espectro sobre el prototipo antes de cualquier afirmación.

---

*Documento en curso — se completa con el registro de correcciones y la revalidación.*
