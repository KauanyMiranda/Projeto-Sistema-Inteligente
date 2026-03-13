import os, cv2, qrcode
from pathlib import Path

def gerar_qrcode(conteudo: str, caminho_arquivo: str) -> None:
    destino = Path(caminho_arquivo).parent
    destino.mkdir(parents=True, exist_ok=True)

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(conteudo)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(caminho_arquivo)

def ler_qrcode(caminho_arquivo: str) -> str:
    img = cv2.imread(caminho_arquivo)

    detector = cv2.QRCodeDetector()
    dados, pontos, _ = detector.detectAndDecode(img)

    return dados

def main() -> None:
    try:
        conteudo_qr = "ITEM: COMPUTADOR ACER | REGIAO: SUL"
        arquivo_saida = "saida/qrcode_item.png"

        gerar_qrcode(conteudo_qr, arquivo_saida)
        print(f"QRCode salvo em:{arquivo_saida}")

        conteudo_lido = ler_qrcode(arquivo_saida)
        print(f"Conteudo lido: {conteudo_lido}")
    except Exception as e:
        print(f"Erro na execução: {e}")

if __name__ == "__main__":
    main()