# ============================================================================
# vision.py - Vision BeachBot (v6: pipe dedicado agua, frame completo, lado)
# ============================================================================
#
#  CAMBIOS RESPECTO A v5:
#  1. Pipe DEDICADO para agua: /tmp/water_alert  (W:L / W:R / W:C / C)
#  2. Deteccion de azul en FRAME COMPLETO - sin recorte de ROI
#  3. DANGER_ON = 0.035 (antes 0.30 sobre ROI) - reacciona mucho antes
#  4. Envia lado del agua (L/R/C) para retroceso curvo en maestro
#  5. Apertura del pipe de agua en hilo separado - no bloquea el main
#  6. Validacion de latas: mantiene los filtros estrictos de v5
# ============================================================================

import cv2
import numpy as np
import os
import errno
import time
import threading

SHOW_DEBUG = True

PIPE_PATH       = "/tmp/error_tracking"   # CAN / RED / N
WATER_PIPE_PATH = "/tmp/water_alert"      # W:L / W:R / W:C / C

# -- Parametros camara -------------------------------------------------------
RESOLUCION_W = 640
RESOLUCION_H = 480
FPS          = 20

MAX_DIST_CENTROID = 80
KERNEL            = np.ones((6, 6), np.uint8)

MIN_AREA_CAN = 800
MIN_AREA_RED = 1200

# -- Deteccion de agua: frame completo ---------------------------------------
DANGER_ON  = 0.15  # >3.5% pixeles azules en frame completo = agua
DANGER_OFF = 0.015   # <1.5% = despejado (histeresis)

# -- Calibracion automatica de umbral de negro -------------------------------
def calibrar_umbral(cap, n_frames=10):
    print("[CALIB] Calibrando umbral de negro...")
    valores_v = []
    for _ in range(n_frames):
        ret, frame = cap.read()
        if not ret:
            continue
        h, w = frame.shape[:2]
        hsv     = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        v_ch    = hsv[h // 2:, :, 2].flatten()
        v_medio = v_ch[(v_ch > 30) & (v_ch < 250)]
        valores_v.extend(v_medio.tolist())
        time.sleep(0.05)

    if len(valores_v) < 100:
        return 0.65, 40, 160

    arr            = np.array(valores_v)
    brillo_fondo   = np.percentile(arr, 50)
    umbral_objetos = np.percentile(arr, 20)
    multiplier     = float(np.clip(umbral_objetos / max(1.0, brillo_fondo), 0.35, 0.80))
    min_thr        = int(np.clip(umbral_objetos * 0.70, 20, 60))
    max_thr        = int(np.clip(umbral_objetos * 1.30, 80, 200))
    return multiplier, min_thr, max_thr

# -- Validacion de contornos de lata (filtros estrictos de v5) ---------------
def es_lata_valida(contorno, bbox, min_area=MIN_AREA_CAN):
    x, y, bw, bh  = bbox
    area_contorno = cv2.contourArea(contorno)

    if area_contorno < min_area: return False, "area_pequena"
    if area_contorno > 60000:    return False, "area_grande"
    if bw < 25:                  return False, "ancho_pequeno"

    aspect = bh / max(1, bw)
    if aspect < 0.50 or aspect > 3.5: return False, f"aspect={aspect:.2f}"

    solidez = area_contorno / max(1, bw * bh)
    if solidez < 0.45: return False, f"solidez={solidez:.2f}"

    perimetro = cv2.arcLength(contorno, True)
    if perimetro > 0:
        circularidad = (4 * np.pi * area_contorno) / (perimetro ** 2)
        if circularidad < 0.35: return False, f"circ={circularidad:.2f}"

    hull      = cv2.convexHull(contorno)
    convexidad = area_contorno / max(1, cv2.contourArea(hull))
    if convexidad < 0.80: return False, f"conv={convexidad:.2f}"

    return True, "ok"

# -- Crear pipes FIFO --------------------------------------------------------
for path in [PIPE_PATH, WATER_PIPE_PATH]:
    try:
        os.mkfifo(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

# Pipe principal - bloquea hasta que maestro lo abra (normal en FIFO)
pipe_fd = open(PIPE_PATH, "w", buffering=1)

# Pipe de agua - se abre en hilo separado para no bloquear el main
water_pipe_fd = None
_wp_lock      = threading.Lock()

def _conectar_water_pipe():
    global water_pipe_fd
    fd = open(WATER_PIPE_PATH, "w", buffering=1)
    with _wp_lock:
        water_pipe_fd = fd
    print("[VISION] Pipe de agua conectado.")

_t_wp = threading.Thread(target=_conectar_water_pipe, daemon=True)
_t_wp.start()
_t_wp.join(timeout=15)

# -- Camara ------------------------------------------------------------------
def abrir_camara():
    while True:
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  RESOLUCION_W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUCION_H)
        cap.set(cv2.CAP_PROP_FPS,          FPS)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        if cap.isOpened():
            return cap
        cap.release()
        time.sleep(2)

cap = abrir_camara()
for _ in range(20):
    cap.read()
BRIGHTNESS_MULT, MIN_THR, MAX_THR = calibrar_umbral(cap, n_frames=10)

# -- Error lateral normalizado -----------------------------------------------
def compute_error(cx, w):
    zone_l = 3 * (w // 8)
    zone_r = 5 * (w // 8)
    if cx < zone_l:   raw = (cx - zone_l) / zone_l
    elif cx > zone_r: raw = (cx - zone_r) / (w - zone_r)
    else:             raw = 0.0
    return float(np.clip(raw, -1.0, 1.0))

# -- Escritura segura al pipe de agua ----------------------------------------
def escribir_agua(msg):
    with _wp_lock:
        if water_pipe_fd is None:
            return
        try:
            water_pipe_fd.write(msg + "\n")
            water_pipe_fd.flush()
        except (BrokenPipeError, OSError):
            pass

# -- Estado global -----------------------------------------------------------
blue_warning   = False
last_pos_black = None

# ================================ BUCLE PRINCIPAL ===========================
while True:
    ret, frame = cap.read()
    if not ret:
        cap.release()
        cap = abrir_camara()
        continue

    h, w = frame.shape[:2]
    hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    brillo = np.mean(hsv[h // 2:, :, 2])
    umbral = int(np.clip(brillo * BRIGHTNESS_MULT, MIN_THR, MAX_THR))

    # -- Mascaras ------------------------------------------------------------
    mask_black = cv2.inRange(hsv, np.array([0,   0,   0  ]), np.array([180, 200, umbral]))
    mask_blue = cv2.inRange(hsv, np.array([75, 40, 80]), np.array([135, 255, 255]))
    mask_red1  = cv2.inRange(hsv, np.array([0,   150, 80 ]), np.array([10,  255, 255]))
    mask_red2  = cv2.inRange(hsv, np.array([170, 150, 80 ]), np.array([180, 255, 255]))
    mask_red   = cv2.bitwise_or(mask_red1, mask_red2)

    for m in [mask_black, mask_blue, mask_red]:
        cv2.morphologyEx(m, cv2.MORPH_OPEN,  KERNEL, dst=m)
        cv2.morphologyEx(m, cv2.MORPH_CLOSE, KERNEL, dst=m)

    roi_y_can = int(h * 0.40)
    mask_black[:roi_y_can, :] = 0

    # ========================================================================
    # DETECCION DE AGUA - FRAME COMPLETO, PIPE DEDICADO
    # Se calcula siempre, independientemente de si hay lata detectada.
    # ========================================================================
    ratio_agua = cv2.countNonZero(mask_blue) / max(1, mask_blue.size)

    if blue_warning and ratio_agua < DANGER_OFF:
        blue_warning = False
    elif not blue_warning and ratio_agua > DANGER_ON:
        blue_warning = True

    # Calcular lado donde esta el agua
    water_side = "C"
    if blue_warning:
        cnts_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
        if cnts_blue:
            c_max = max(cnts_blue, key=cv2.contourArea)
            M_b   = cv2.moments(c_max)
            if M_b["m00"] > 0:
                cx_w       = int(M_b["m10"] / M_b["m00"])
                water_side = "L" if cx_w < w // 2 else "R"

    # Siempre escribir al pipe de agua (C = despejado)
    escribir_agua(f"W:{water_side}" if blue_warning else "C")

    # ========================================================================
    # DETECCION DE LATAS Y DEPOSITO ROJO
    # Si hay agua: pipe principal manda N (maestro ya sabe por water_alert)
    # ========================================================================
    try:
        if blue_warning:
            pipe_fd.write("N\n")
            last_pos_black = None
            if SHOW_DEBUG:
                cv2.rectangle(frame, (0, 0), (w, h), (255, 80, 0), 3)
                cv2.putText(frame, f"AGUA:{water_side} ({ratio_agua*100:.1f}%)",
                            (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 80, 0), 2)
        else:
            # -- Latas negras ------------------------------------------------
            cnts_black, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL,
                                             cv2.CHAIN_APPROX_SIMPLE)
            cnts_validos = [c for c in cnts_black
                            if es_lata_valida(c, cv2.boundingRect(c))[0]]

            best_can = None
            if cnts_validos:
                if last_pos_black is None:
                    best_can = max(cnts_validos, key=cv2.contourArea)
                else:
                    min_dist = float('inf')
                    for c in cnts_validos:
                        M = cv2.moments(c)
                        if M["m00"] == 0:
                            continue
                        cx_ = int(M["m10"] / M["m00"])
                        cy_ = int(M["m01"] / M["m00"])
                        dist = np.hypot(cx_ - last_pos_black[0],
                                        cy_ - last_pos_black[1])
                        if dist < MAX_DIST_CENTROID and dist < min_dist:
                            min_dist = dist
                            best_can = c
                    if best_can is None:
                        last_pos_black = None

            can_msg = None
            if best_can is not None:
                x, y, bw, bh  = cv2.boundingRect(best_can)
                cx_can         = x + bw // 2
                cy_can         = y + bh // 2
                last_pos_black = (cx_can, cy_can)
                error          = compute_error(cx_can, w)
                can_msg        = f"CAN:{error:.3f}"
                if SHOW_DEBUG:
                    cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
                    cv2.putText(frame, f"e:{error:.2f}", (x, max(y - 5, 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

            # -- Deposito rojo -----------------------------------------------
            cnts_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)
            red_msg = None
            if cnts_red:
                c = max(cnts_red, key=cv2.contourArea)
                if cv2.contourArea(c) >= MIN_AREA_RED:
                    x, y, rw, rh = cv2.boundingRect(c)
                    cx_red       = x + rw // 2
                    error        = compute_error(cx_red, w)
                    red_msg      = f"RED:{error:.3f}:{rw}"
                    if SHOW_DEBUG:
                        cv2.rectangle(frame, (x, y), (x + rw, y + rh), (0, 0, 255), 2)
                        cv2.putText(frame, f"e:{error:.2f} w:{rw}",
                                    (x, max(y - 5, 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

            if can_msg:   pipe_fd.write(can_msg + "\n")
            elif red_msg: pipe_fd.write(red_msg + "\n")
            else:         pipe_fd.write("N\n")

    except BrokenPipeError:
        print("\n[VISION] Maestro desconectado. Reconectando pipe principal...")
        pipe_fd.close()
        pipe_fd = open(PIPE_PATH, "w", buffering=1)
        print("[VISION] Pipe principal reconectado.")

    if SHOW_DEBUG:
        cv2.imshow("BeachBot Vision", frame)
        cv2.imshow("Mask Blue (agua)", mask_blue)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
