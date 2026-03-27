import cv2
import requests

URL_API = "http://127.0.0.1:8000/api/v1/qrcode/read-text"

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
detector = cv2.QRCodeDetector()

ultimo_qr = None

print("Webcam iniciada... Pressione ESC para sair")

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
                json={"payload": data}
            )

            print("\nResposta da API:")
            print(response.json())

        except Exception as e:
            print("Erro ao chamar API:", e)

        cv2.waitKey(2000)

    # desenhar o quadrado no QR
    if bbox is not None:
        for i in range(len(bbox)):
            pt1 = tuple(map(int, bbox[i][0]))
            pt2 = tuple(map(int, bbox[(i + 1) % len(bbox)][0]))
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

    cv2.imshow("Leitor QR Code", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()