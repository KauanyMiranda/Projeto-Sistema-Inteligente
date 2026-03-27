try:
    import socket
except ImportError:
    import usocket as socket

try:
    import json
except ImportError:
    import ujson as json

from ev3_controller import EV3Actuator

HOST = "0.0.0.0"
PORT = 8765


def _recv_line(conn):
    chunks = []
    while True:
        chunk = conn.recv(1)
        if not chunk:
            break
        chunks.append(chunk)
        if chunk == b"\n":
            break
    return b"".join(chunks)


def _send_json(conn, payload):
    data = (json.dumps(payload) + "\n").encode("utf-8")
    conn.sendall(data)


def _build_ack(cmd_id, region, ok, message):
    return {
        "type": "ack",
        "cmd_id": cmd_id,
        "region": region,
        "ok": ok,
        "message": message,
    }


def main():
    actuator = EV3Actuator(simulation_mode=False)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass

    server.bind((HOST, PORT))
    server.listen(1)
    print("EV3 listener ativo em {}:{}".format(HOST, PORT))

    while True:
        conn, addr = server.accept()
        print("Conexao recebida de:", addr)
        try:
            raw = _recv_line(conn)
            if not raw:
                _send_json(
                    conn,
                    _build_ack(
                        cmd_id=None,
                        region=None,
                        ok=False,
                        message="Payload vazio.",
                    ),
                )
                continue

            request = json.loads(raw.decode("utf-8").strip())
            cmd_id = request.get("cmd_id")
            region = request.get("region")
            cmd_type = request.get("type")

            if cmd_type != "route":
                _send_json(
                    conn,
                    _build_ack(
                        cmd_id=cmd_id,
                        region=region,
                        ok=False,
                        message="Tipo de comando invalido.",
                    ),
                )
                continue

            if not region:
                _send_json(
                    conn,
                    _build_ack(
                        cmd_id=cmd_id,
                        region=region,
                        ok=False,
                        message="Campo region ausente.",
                    ),
                )
                continue

            ok = actuator.execute_region(region)
            if ok:
                ack = _build_ack(
                    cmd_id=cmd_id,
                    region=region,
                    ok=True,
                    message="Comando executado.",
                )
            else:
                ack = _build_ack(
                    cmd_id=cmd_id,
                    region=region,
                    ok=False,
                    message="Falha ao executar rota.",
                )

            _send_json(conn, ack)
        except Exception as e:
            _send_json(
                conn,
                _build_ack(
                    cmd_id=None,
                    region=None,
                    ok=False,
                    message="Erro interno: {}".format(e),
                ),
            )
        finally:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
