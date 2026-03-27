import cv2
import requests
import time
from ev3_bridge_client import EV3BridgeClient
from ev3_controller import EV3Actuator

URL_API = "http://127.0.0.1:8000/api/v1/qrcode/read-text"
HTTP_TIMEOUT_SECONDS = 5

# Modo de envio ao EV3 via rede.
EV3_BRIDGE_ENABLED = True
EV3_HOST = "192.168.0.50"  # ajuste para o IP real do EV3
EV3_PORT = 8765
EV3_CONNECT_TIMEOUT_SECONDS = 2.0
EV3_ACK_TIMEOUT_SECONDS = 12.0

# Fallback local apenas para teste sem ponte.
SIMULATION_MODE = True

# Controle de duplicidade: so reprocessa o mesmo QR quando ele sair do frame.
EMPTY_FRAMES_TO_RESET = 8

bridge = None
actuator = None

if EV3_BRIDGE_ENABLED:
    bridge = EV3BridgeClient(
        host=EV3_HOST,
        port=EV3_PORT,
        connect_timeout=EV3_CONNECT_TIMEOUT_SECONDS,
        read_timeout=EV3_ACK_TIMEOUT_SECONDS,
    )
    print(f"Ponte EV3 habilitada: {EV3_HOST}:{EV3_PORT}")
else:
    actuator = EV3Actuator(simulation_mode=SIMULATION_MODE)

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
detector = cv2.QRCodeDetector()
WINDOW_NAME = "Leitor QR Code"

ultimo_qr_processado = None
quadros_sem_qr = 0

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

        if data:
            quadros_sem_qr = 0
        else:
            quadros_sem_qr += 1
            if quadros_sem_qr >= EMPTY_FRAMES_TO_RESET:
                ultimo_qr_processado = None

        if data and data != ultimo_qr_processado:
            ultimo_qr_processado = data

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

                api_data = response_data.get("data", {})
                region = (
                    api_data.get("rota", {})
                    .get("region")
                )
                item_id = (
                    api_data.get("item", {})
                    .get("id_item")
                )

                if region:
                    if bridge is not None:
                        ack = bridge.send_region(region=region, item_id=item_id)
                        print("ACK EV3:", ack)
                    elif actuator is not None:
                        actuator.execute_region(region=region)
                else:
                    print("Nao foi possivel obter a regiao na resposta da API.")

            except Exception as e:
                print("Erro ao chamar API:", e)

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
