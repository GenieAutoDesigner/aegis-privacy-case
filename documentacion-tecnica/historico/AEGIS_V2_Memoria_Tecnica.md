# PROJECT AEGIS — Memoria Técnica V2
## Funda mecánica de privacidad física para iPhone 15 Pro — impresión 3D

Documento de ingeniería. Estado: **MODELO CAD COMPLETO — VALIDACIÓN EN CURSO (no apto para fabricación todavía).**
Documento Fusion 360: `AEGIS_V2_3DPrint` (18 componentes, 248 features, 175 parámetros de usuario).

---

## 1. CORRECCIÓN DE PARTIDA

**ERROR detectado en el estado heredado:** los parámetros `PHONE_X = 76.70` / `PHONE_Y = 159.90` corresponden al iPhone 15 Pro **Max**, no al iPhone 15 **Pro**.
**CAUSA:** parámetros arrastrados del linaje V1 (`Privacy_Case_v1_OFFLINE`).
**CORRECCIÓN:** `PHONE_X = 70.60 mm`, `PHONE_Y = 146.60 mm`, `PHONE_Z_BODY = 8.25 mm`. Toda la geometría se deriva de ellos.

---

## 2. SISTEMA DE COORDENADAS

| Eje | Sentido |
|---|---|
| Z = 0 | plano del cristal frontal; **+Z hacia la trasera** |
| Y + | hacia el borde superior del teléfono |
| X + | hacia el lateral de **botones de volumen / acción** (lado del slider) |
| X − | hacia el lateral del botón lateral y de la isla de cámaras |

Teléfono: X ∈ [−35.30, 35.30], Y ∈ [−73.30, 73.30], Z ∈ [0, 8.25]; isla de cámaras X ∈ [−27.90, 8.00], Y ∈ [30.00, 65.90], Z ∈ [8.25, 11.84].

---

## 3. ENVOLVENTE DEL PRODUCTO

| Magnitud | Valor |
|---|---|
| Anchura exterior | 78.0 mm |
| Longitud exterior | 163.2 mm |
| Espesor (zona plana) | 20.25 mm |
| Espesor (meseta de cámara) | 20.25 mm sobre labio, 16.65 mm sobre cristal |
| Radio de esquina exterior | 15.2 mm |
| Volumen de material (todas las piezas) | 66.95 cm³ |
| Masa estimada | 83 g (PLA) / 85 g (PETG) — *sin junta ni láminas conductoras* |

Paredes: lateral 3.4 mm (aloja el canal del marco RF), superior 8.5 mm (aloja la lámina frontal replegada), inferior 7.5 mm (cámaras acústicas + compuerta), trasera 1.2 mm, labio frontal 3.6 × 3.2 mm.

---

## 4. ARQUITECTURA MECÁNICA

Un único **slider lateral** (lado +X, por debajo de la zona de botones) desplaza **30 mm** el **Master Carriage**, una placa de 25.5 × 100 × 1.2 mm alojada en la cavidad trasera. El carro lleva **cuatro pistas de leva** que convierten su traslación en Y en salidas transversales en X.

> **Nota arquitectónica:** un carro que traslada en Y solo puede generar salidas en **X** mediante leva. Cualquier salida en Y o Z exige un conversor (yugo, cuña o palanca). Esto condiciona toda la arquitectura.

### 4.1 Tabla cinemática maestra (KD-010)

| Fase | x slider | Leva | Seguidor | Salida | Recorrido | Ángulo de presión |
|---|---|---|---|---|---|---|
| Óptica trasera | 0.5 → 11.5 | CAM-01 | poste de S1 | X | 19.0 mm | 60.0° |
| Óptica frontal | 4.0 → 12.0 | CAM-02 | FRONT_TRANSFER_BAR | X | 3.0 mm | 20.6° |
| Acústica | 12.2 → 19.8 | CAM-03 | brazo de ACOUSTIC_GATE | X | 12.0 mm | 57.6° |
| RF posición | 20.0 → 24.0 | CAM-45 (tramo 1) | RF_PUSH_BAR | X | 4.0 mm | 45.0° |
| RF compresión | 24.0 → 30.0 | CAM-45 (tramo 2) | RF_PUSH_BAR | X | 4.0 mm | 33.7° |

**Decisión:** CAM-04 y CAM-05 se han fusionado en una **pista única de doble pendiente (CAM-45)**. Razón: ambas accionan el mismo tren RF de forma secuencial; una sola pista elimina un seguidor, un juego de guías y un modo de fallo, y conserva exactamente las dos ventanas congeladas (2 mm de aproximación + 1 mm de compresión).

### 4.2 Obturador trasero telescópico (CAM-01)

La isla mide 35.9 mm y el bolsillo de almacenaje disponible en el lado +X solo 20 mm ⇒ **es obligatorio un obturador de dos etapas**.

- `REAR_SHUTTER_S1` (exterior, Z 14.45–15.15): recorrido **19 mm**, accionada directamente por CAM-01.
- `REAR_SHUTTER_S2` (interior, Z 13.50–14.20): recorrido **38 mm** (2×S1) mediante **doblador por tendón** (polea sobre S1, anclaje fijo en carcasa, anclaje sobre S2). Dos tendones antagonistas (despliegue y retracción), Dyneema Ø0.5 mm — **pieza de compra, no impresa**.
- Cobertura desplegada: S2 [−30.0, −10.0] ∪ S1 [−11.0, 9.0] = **[−30.0, 9.0]**, con 1.0 mm de solape entre láminas y 1.0–2.1 mm de solape sobre los bordes de la isla.
- Guiado: raíles longitudinales en la meseta (S2 entre raíles bajos, S1 sobre raíles altos), holgura en Y de 0.4 mm.

### 4.3 Obturador de cámara frontal (CAM-02)

**DECISIÓN:** lámina **rotativa 90° sobre eje Z**, pivote en (X = 5.5, Y = 77.0), longitud 19 mm, anchura 9 mm, espesor 1.1 mm, alojada en el plano Z ∈ [−3.0, −1.9] (delante del cristal, bajo el labio).
**RAZÓN:** una corredera lineal exigiría una pared superior de ≈ 22 mm (profundidad de lámina + recorrido del accionador, que debe permanecer oculto en todo momento). La rotación almacena la lámina **a lo largo** de la pared superior: bastan 8.5 mm.
**ACCIONAMIENTO:** yugo escocés — perno Ø2 a radio 3.0 mm sobre el cubo de la lámina, alojado en una ranura recta de `FRONT_TRANSFER_BAR`. El recorrido necesario del seguidor cae de 12.7 mm a **3.0 mm**, y el ángulo de presión de CAM-02 de 58° a 20.6°.
**PUNTO MUERTO:** a 90° la velocidad del yugo es nula → **autobloqueo natural en posición OFFLINE** (característica deseada).

### 4.4 Módulo acústico (CAM-03)

**DECISIÓN:** una **única compuerta con ventana**, no dos compuertas con inversor.
**RAZÓN:** las salidas acústicas están a ambos lados del puerto USB-C y una inversión de sentido (balancín o piñón-cremallera) no cabe en una pared inferior de 7.5 mm sin generar barridos en Y de ±6 mm.
**FUNCIONAMIENTO:** barra X ∈ [−9, 35], Y ∈ [−78.8, −76.8], Z ∈ [6.6, 9.0], con ventana en X ∈ [10.5, 21.5].
- ONLINE: la ventana descubre el grupo derecho [11, 21]; el grupo izquierdo [−21, −11] queda fuera de la barra.
- OFFLINE (−12 mm): sólido [−21, −1.5] cierra el grupo izquierdo y sólido [9.5, 23] cierra el derecho.
- El USB-C nunca queda obstruido (puente por encima, Z 8.85–10.2).

### 4.5 Módulo RF (CAM-45)

Arquitectura de jaula conmutable:
- **Fijo:** `RF_FOIL_REAR` (lámina de cobre 0.1 mm sobre el techo de la cavidad) + recubrimiento conductor de paredes + `RF_WINDOW_FRONT` (PET-ITO 0.2 mm bajo el labio).
- **Móvil:** `RF_FRAME` (marco perimetral conductor, sección 0.8 × 2.5 mm, en canal de pared) con **6 resaltes** por lado que apoyan sobre las rampas de `RF_WEDGE_R/L`.
- **Transmisión:** `RF_PUSH_BAR` (traslación −8 mm en X) → **dos ranuras a 45°** → `RF_WEDGE_R/L` (traslación −8 mm en Y) → rampas de doble pendiente (26.6° / 14°) → `RF_FRAME` sube 2 mm + 1 mm.
- **Cierre:** `RF_GASKET` (espuma conductora, 2.0 mm libres) comprimida al 50 % contra la repisa conductora fija en Z = 11.35.
- **Ventaja mecánica en compresión:** 6 mm de slider → 1 mm de recorrido de junta = **6:1**. La rampa fina (14°) es autobloqueante frente al empuje de la junta, pero se retrae de forma positiva por el enlace rígido.

---

## 5. LISTA DE COMPONENTES

| # | Componente | Vol. (cm³) | Proceso | Función |
|---|---|---|---|---|
| 1 | PHONE_REFERENCE | — | referencia | Envolvente del iPhone 15 Pro |
| 2 | KEEP_OUT | — | referencia | Teléfono + holgura + zonas de botón |
| 3 | CASE_SHELL | 47.22 | FDM | Chasis, labio, meseta, cavidades, raíles |
| 4 | CASE_LINER | 8.40 | FDM | Forro interior, cierra la cavidad, 4 clips |
| 5 | SLIDER_TAB | 0.18 | FDM | Pestaña exterior + vástago + espiga |
| 6 | MASTER_CARRIAGE | 2.64 | FDM | Placa con 4 pistas de leva |
| 7 | REAR_SHUTTER_S1 | 0.54 | FDM | Lámina exterior + poste de leva + poleas |
| 8 | REAR_SHUTTER_S2 | 0.50 | FDM | Lámina interior + anclajes de tendón |
| 9 | FRONT_TRANSFER_BAR | 0.62 | FDM | Barra en Z: cavidad → pared superior → frontal |
| 10 | FRONT_CAM_FLAP | 0.19 | FDM | Lámina rotativa de cámara frontal |
| 11 | ACOUSTIC_GATE | 0.32 | FDM | Compuerta acústica con ventana |
| 12 | RF_PUSH_BAR | 0.70 | FDM | Seguidor CAM-45 + 2 ranuras a 45° |
| 13 | RF_WEDGE_R | 0.28 | FDM | Varilla de cuña derecha, 6 rampas |
| 14 | RF_WEDGE_L | 0.28 | FDM | Varilla de cuña izquierda, 6 rampas |
| 15 | RF_FRAME | 0.85 | conductivo | Marco perimetral (2 segmentos) |
| 16 | RF_GASKET | 1.28 | compra | Espuma conductora (2 segmentos) |
| 17 | RF_FOIL_REAR | 0.97 | compra | Lámina de cobre trasera |
| 18 | RF_WINDOW_FRONT | 1.98 | compra | Ventana PET-ITO frontal |

Elementos adicionales de compra: 2 tendones Dyneema Ø0.5, fingerstock deslizante en la ranura del slider, membranas conductoras sobre los recortes de botón.

---

## 6. VALIDACIÓN REALIZADA

Se ha implementado un **barrido cinemático automático** que aplica la ley de movimiento real a cada pieza en 22 posiciones del recorrido (x = 0 … 30 mm) y calcula la **intersección booleana exacta** de todos los pares de sólidos (filtrado previo por caja envolvente).

- Método: `TemporaryBRepManager.booleanOperation(IntersectionBooleanType)` sobre copias transformadas.
- Criterio: cualquier volumen de intersección > 0.001 cm³ se declara **ERROR**.
- Resultado: ver `AEGIS_V2_Defectos_Pendientes.md`.

**VALIDADO:** ley cinemática, secuencia de fases, cobertura óptica del obturador trasero, ángulos de presión, cobertura acústica en ambos estados, no separación de cuerpos (todas las piezas son sólidos únicos salvo RF_FRAME/RF_GASKET, segmentados por diseño).

**NO VALIDADO:** atenuación RF (sin simulación EMC), atenuación acústica (sin ensayo), fuerza de accionamiento (sin cálculo de fricción con material y acabado reales), fatiga, ensamblaje físico.

---

## 7. FABRICACIÓN

Proceso base: FDM, boquilla 0.4 mm, capa 0.15 mm.
Holguras de proyecto: deslizante 0.25 mm, captiva 0.35 mm, guía lateral del carro 0.35 mm.

| Pieza | Orientación recomendada | Soportes | Nota |
|---|---|---|---|
| CASE_SHELL | cara frontal hacia abajo | sí, en cavidades laterales | pieza crítica; considerar dividir por el plano Z = 9.35 |
| CASE_LINER | plano | no | 0.8 mm ⇒ 2 perímetros |
| MASTER_CARRIAGE | plano | no | 1.2 mm; ranuras de leva a 0.1 mm de holgura |
| S1 / S2 | plano | no | 0.7 mm; considerar POM mecanizado si hay alabeo |
| RF_WEDGE_R/L | tumbado sobre el canal | rampas autoportantes < 45° | lubricar (PTFE) |

**Advertencia:** el suelo de la meseta (0.80 mm) y el techo de la meseta (1.20 mm) son puentes largos; imprimir con ventilación máxima.

---

## 8. RIESGOS ABIERTOS

| ID | Riesgo | Severidad |
|---|---|---|
| R-01 | Ángulo de presión de CAM-01 = 60° ⇒ fuerza en el slider ≈ 4.2× la resistencia del obturador | media |
| R-02 | Doblador por tendón: fluencia del cordón y ajuste de longitud en montaje | alta |
| R-03 | Fuga RF por la ranura del slider (37 mm) — requiere fingerstock deslizante | alta |
| R-04 | Fuga RF por los recortes de botón y por el puerto USB-C (guía bajo corte, ≈ 18 dB) | alta |
| R-05 | Marco RF en voladizo ≈ 38 mm en los tramos superior e inferior | media |
| R-06 | Lámina frontal sin retención axial explícita (solo pivote) | baja |
| R-07 | El obturador trasero deja una holgura perimetral de 0.30 mm (laberinto, no sellado óptico absoluto) | baja |

---

*Generado a partir del estado real del documento Fusion 360, no de descripciones previas.*
