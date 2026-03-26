import cv2
import requests
import time
from ev3_controller import EV3Actuator

URL_API = "http://127.0.0.1:8000/api/v1/qrcode/read-text"
HTTP_TIMEOUT_SECONDS = 5

# Deixe True para testar sem EV3 conectado.
SIMULATION_MODE = True
TURN_DEGREES = 90
TURN_SPEED_PERCENT = 25
CW_SIGN = 1
CCW_SIGN = -1

actuator = EV3Actuator(
    simulation_mode=SIMULATION_MODE,
    turn_degrees=TURN_DEGREES,
    turn_speed_percent=TURN_SPEED_PERCENT,
    cw_sign=CW_SIGN,
    ccw_sign=CCW_SIGN,
)

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
detector = cv2.QRCodeDetector()
WINDOW_NAME = "Leitor QR Code"

ultimo_qr = None

def is_gui_available() -> bool:
    try:
        cv2.namedWindow(WINDOW_NAME)
        cv2.destroyWindow(WINDOW_NAME)
        return True
    except cv2.error:
        return False

gui_enabled = is_gui_available()

if gui_enabled:
    print("Webcam iniciada... Pressione ESC para sair")
else:
    print(
        "Webcam iniciada em modo headless (sem janela OpenCV). "
        "Use CTRL+C para encerrar."
    )

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Erro ao acessar webcam")
            break

        data, bbox, _ = detector.detectAndDecode(frame)

        if data and data != ultimo_qr:
            ultimo_qr = data

            print("\nQR Code lido:")
            print(data)

            try:
                response = requests.post(
                    URL_API,
                    json={"payload": data},
                    timeout=HTTP_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                response_data = response.json()

                print("\nResposta da API:")
                print(response_data)

                region = (
                    response_data.get("data", {})
                    .get("rota", {})
                    .get("region")
                )

                if region:
                    actuator.execute_region(region=region)
                else:
                    print("Nao foi possivel obter a regiao na resposta da API.")

            except Exception as e:
                print("Erro ao chamar API:", e)

            if gui_enabled:
                cv2.waitKey(2000)
            else:
                time.sleep(2)

        # desenhar o quadrado no QR
        if bbox is not None:
            for i in range(len(bbox)):
                pt1 = tuple(map(int, bbox[i][0]))
                pt2 = tuple(map(int, bbox[(i + 1) % len(bbox)][0]))
                cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

        if gui_enabled:
            cv2.imshow(WINDOW_NAME, frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        else:
            time.sleep(0.01)
except KeyboardInterrupt:
    print("\nEncerrado por teclado.")

cap.release()
if gui_enabled:
    cv2.destroyAllWindows()