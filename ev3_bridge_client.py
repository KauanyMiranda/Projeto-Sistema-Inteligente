import json
import socket
import time


class EV3BridgeClient:
    def __init__(self, host, port=8765, connect_timeout=2.0, read_timeout=10.0):
        self.host = host
        self.port = port
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout

    def send_region(self, region, item_id=None, cmd_id=None):
        payload = {
            "type": "route",
            "region": region,
            "item_id": item_id,
            "cmd_id": cmd_id or str(int(time.time() * 1000)),
        }
        return self.send_payload(payload)

    def send_payload(self, payload):
        raw = (json.dumps(payload) + "\n").encode("utf-8")

        with socket.create_connection(
            (self.host, self.port), timeout=self.connect_timeout
        ) as conn:
            conn.settimeout(self.read_timeout)
            conn.sendall(raw)
            response_line = self._readline(conn)

        if not response_line:
            raise RuntimeError("Sem resposta do EV3 (ACK vazio).")

        response = json.loads(response_line.decode("utf-8").strip())
        return response

    @staticmethod
    def _readline(conn):
        chunks = []
        while True:
            chunk = conn.recv(1)
            if not chunk:
                break
            chunks.append(chunk)
            if chunk == b"\n":
                break
        return b"".join(chunks)
