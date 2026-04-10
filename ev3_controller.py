import time
import os

DEFAULT_ARM_TURN_DEGREES = 360

try:
    from ev3dev2.motor import Motor as EV3Dev2Motor
    from ev3dev2.motor import OUTPUT_B, OUTPUT_C, OUTPUT_D
except ImportError:
    EV3Dev2Motor = None
    OUTPUT_B = None
    OUTPUT_C = None
    OUTPUT_D = None

try:
    from pybricks.hubs import EV3Brick
    from pybricks.ev3devices import Motor as PybricksMotor
    from pybricks.parameters import Port
except ImportError:
    EV3Brick = None
    PybricksMotor = None
    Port = None

DEFAULT_REGION_ROUTING = {
    "NORTE": {
        "esteira_speed": -200,
        "esteira_time_ms": 1600,
        "braco": "BRACO_1",
        "braco_speed": 300,
        "braco_target": -90,
    },
    "NORDESTE": {
        "esteira_speed": -200,
        "esteira_time_ms": 1600,
        "braco": "BRACO_1",
        "braco_speed": 300,
        "braco_target": 90,
    },
    "SUL": {
        "esteira_speed": -200,
        "esteira_time_ms": 2200,
        "braco": "BRACO_2",
        "braco_speed": 350,
        "braco_target": -90,
    },
    "SUDESTE": {
        "esteira_speed": -200,
        "esteira_time_ms": 2200,
        "braco": "BRACO_2",
        "braco_speed": 350,
        "braco_target": 90,
    },
    "CENTRO-OESTE": {
        "esteira_speed": -200,
        "esteira_time_ms": 2600,
        "braco": None,
        "braco_speed": None,
        "braco_target": None,
    },
}

class EV3Actuator:
    def __init__(
        self,
        simulation_mode=False,
        region_routing=None,
        **_ignored_legacy_kwargs
    ):
        self.simulation_mode = simulation_mode
        self.region_routing = region_routing or DEFAULT_REGION_ROUTING

        self.backend = "simulation"
        self.ready = False
        self.ev3 = None
        self.motor_esteira = None
        self.motor_braco1 = None
        self.motor_braco2 = None

        if self.simulation_mode:
            print("EV3 em modo simulacao.")
            return

        if self._init_ev3dev2():
            return

        if self._init_pybricks():
            return

        print(
            "Nenhum backend de motor disponivel. "
            "Instale python3-ev3dev2 no EV3 ou use firmware Pybricks."
        )
        self.simulation_mode = True

    def _init_ev3dev2(self):
        if EV3Dev2Motor is None:
            return False

        try:
            connected_outputs = self._get_connected_outputs()
            selected = self._select_ev3dev2_ports(connected_outputs)

            esteira_port = selected["esteira"]
            braco1_port = selected["braco1"]
            braco2_port = selected["braco2"]

            if esteira_port is None:
                raise RuntimeError(
                    "Nenhum motor detectado para esteira. "
                    "Conecte ao menos um motor em outA/outB/outC/outD."
                )

            self.motor_esteira = EV3Dev2Motor(esteira_port)
            self.motor_braco1 = EV3Dev2Motor(braco1_port) if braco1_port else None
            self.motor_braco2 = EV3Dev2Motor(braco2_port) if braco2_port else None
            self._reset_arm_positions()

            self.ready = True
            self.backend = "ev3dev2"
            print(
                "EV3 pronto com ev3dev2: esteira em {}, "
                "braco1 em {}, braco2 em {}.".format(
                    esteira_port or "N/A",
                    braco1_port or "N/A",
                    braco2_port or "N/A",
                )
            )
            return True
        except Exception as e:
            print("Falha ao inicializar ev3dev2. Indo para fallback:", e)
            self.motor_esteira = None
            self.motor_braco1 = None
            self.motor_braco2 = None
            self.ready = False
            return False

    def _reset_arm_positions(self):
        for motor_name, motor in (
            ("braco1", self.motor_braco1),
            ("braco2", self.motor_braco2),
        ):
            if motor is None:
                continue
            try:
                motor.position = 0
                print("Encoder do {} zerado no startup.".format(motor_name))
            except Exception as e:
                print(
                    "Aviso: nao foi possivel zerar encoder do {}: {}".format(
                        motor_name,
                        e,
                    )
                )

    def _get_connected_outputs(self):
        connected = []
        base = "/sys/class/tacho-motor"

        try:
            entries = sorted(os.listdir(base))
        except Exception:
            return connected

        for entry in entries:
            address_path = os.path.join(base, entry, "address")
            try:
                with open(address_path, "r") as fh:
                    address = fh.read().strip()
            except Exception:
                continue

            normalized = self._normalize_output_port(address)
            if normalized is not None and normalized not in connected:
                connected.append(normalized)

        return connected

    def _select_ev3dev2_ports(self, connected_outputs):
        est_override = os.getenv("EV3_ESTEIRA_PORT")
        br1_override = os.getenv("EV3_BRACO1_PORT")
        br2_override = os.getenv("EV3_BRACO2_PORT")

        taken = set()
        result = {"esteira": None, "braco1": None, "braco2": None}

        est_pref = ["outB", "outA", "outC", "outD"]
        br1_pref = ["outC", "outA", "outD", "outB"]
        br2_pref = ["outD", "outA", "outC", "outB"]

        result["esteira"] = self._pick_port(
            override=est_override,
            preferred=est_pref,
            connected=connected_outputs,
            taken=taken,
            required=True,
            role="esteira",
        )
        if result["esteira"]:
            taken.add(result["esteira"])

        result["braco1"] = self._pick_port(
            override=br1_override,
            preferred=br1_pref,
            connected=connected_outputs,
            taken=taken,
            required=False,
            role="braco1",
        )
        if result["braco1"]:
            taken.add(result["braco1"])

        result["braco2"] = self._pick_port(
            override=br2_override,
            preferred=br2_pref,
            connected=connected_outputs,
            taken=taken,
            required=False,
            role="braco2",
        )

        return result

    def _pick_port(
        self,
        override,
        preferred,
        connected,
        taken,
        required,
        role,
    ):
        if override:
            override = self._normalize_output_port(override)
            if override is None:
                if required:
                    raise RuntimeError(
                        "Porta configurada para {} e invalida. "
                        "Use outA/outB/outC/outD.".format(role)
                    )
                print(
                    "Aviso: porta configurada para {} e invalida. "
                    "Ignorando este motor.".format(role)
                )
                return None
            if override not in connected:
                if required:
                    raise RuntimeError(
                        "Porta {} configurada para {} nao esta conectada. "
                        "Portas conectadas: {}.".format(
                            override,
                            role,
                            connected,
                        )
                    )
                print(
                    "Aviso: porta {} configurada para {} nao esta conectada. "
                    "Ignorando este motor.".format(override, role)
                )
                return None
            if override in taken:
                raise RuntimeError(
                    "Porta {} duplicada entre motores configurados.".format(override)
                )
            return override

        for port in preferred:
            if port in connected and port not in taken:
                return port

        for port in connected:
            if port not in taken:
                return port

        if required:
            raise RuntimeError(
                "Nao ha porta livre para {}. Portas conectadas: {}.".format(
                    role,
                    connected,
                )
            )
        return None

    def _normalize_output_port(self, value):
        if value is None:
            return None

        text = str(value).strip()
        if not text:
            return None

        if ":" in text:
            text = text.split(":")[-1].strip()

        lower = text.lower()
        if lower == "outa":
            return "outA"
        if lower == "outb":
            return "outB"
        if lower == "outc":
            return "outC"
        if lower == "outd":
            return "outD"

        return None

    def _init_pybricks(self):
        if EV3Brick is None or PybricksMotor is None or Port is None:
            return False

        try:
            self.ev3 = EV3Brick()
            self.motor_esteira = PybricksMotor(Port.B)
            self.motor_braco1 = PybricksMotor(Port.C)
            self.motor_braco2 = PybricksMotor(Port.D)
            self.ready = True
            self.backend = "pybricks"
            print("EV3 pronto com pybricks: esteira em B, braco1 em C, braco2 em D.")
            return True
        except Exception as e:
            print("Falha ao inicializar pybricks. Indo para simulacao:", e)
            self.ready = False
            return False

    def execute_region(self, region):
        route = self.region_routing.get(region)
        if route is None:
            print("Regiao nao mapeada para atuacao: {}".format(region))
            return False

        esteira_speed = route["esteira_speed"]
        esteira_time_ms = route["esteira_time_ms"]
        braco = route["braco"]
        braco_speed = route["braco_speed"]
        braco_target = route["braco_target"]

        if self.simulation_mode or not self.ready:
            print(
                "[SIMULACAO] {}: esteira speed={}, time={}ms".format(
                    region,
                    esteira_speed,
                    esteira_time_ms,
                )
            )
            if braco is not None:
                turn_direction = "anti-horario" if (braco_target or 0) < 0 else "horario"
                print(
                    "[SIMULACAO] {}: {} giro completo ({}), speed={}".format(
                        region,
                        braco,
                        turn_direction,
                        braco_speed,
                    )
                )
            return True

        if self.backend == "ev3dev2":
            return self._execute_ev3dev2(
                region=region,
                esteira_speed=esteira_speed,
                esteira_time_ms=esteira_time_ms,
                braco=braco,
                braco_speed=braco_speed,
                braco_target=braco_target,
            )

        if self.backend == "pybricks":
            return self._execute_pybricks(
                esteira_speed=esteira_speed,
                esteira_time_ms=esteira_time_ms,
                braco=braco,
                braco_speed=braco_speed,
                braco_target=braco_target,
            )

        print("Backend de atuacao nao suportado: {}".format(self.backend))
        return False

    def _execute_pybricks(
        self,
        esteira_speed,
        esteira_time_ms,
        braco,
        braco_speed,
        braco_target,
    ):
        self.motor_esteira.run_time(esteira_speed, esteira_time_ms, wait=True)

        if braco is None:
            return True

        if braco == "BRACO_1":
            self.motor_braco1.run_target(braco_speed, braco_target, wait=True)
        elif braco == "BRACO_2":
            self.motor_braco2.run_target(braco_speed, braco_target, wait=True)
        else:
            return False

        return True

    def _execute_ev3dev2(
        self,
        region,
        esteira_speed,
        esteira_time_ms,
        braco,
        braco_speed,
        braco_target,
    ):
        try:
            if not self._run_timed(
                motor=self.motor_esteira,
                speed=esteira_speed,
                time_ms=esteira_time_ms,
            ):
                print("Timeout/erro na atuacao da esteira.")
                return False

            if braco is None:
                return True

            if braco == "BRACO_1":
                target_motor = self.motor_braco1
            elif braco == "BRACO_2":
                target_motor = self.motor_braco2
            else:
                print("Braco nao mapeado para atuacao: {}".format(braco))
                return False

            if target_motor is None:
                print("Motor do {} nao configurado/conectado.".format(braco))
                return False

            turn_direction = -1 if braco_target < 0 else 1
            if not self._run_full_turn(
                motor=target_motor,
                speed=braco_speed,
                direction=turn_direction,
            ):
                print("Timeout/erro na atuacao do {}.".format(braco))
                return False
            return True
        except Exception as e:
            print(
                "Falha na atuacao ev3dev2 para regiao {}: {}".format(
                    region,
                    e,
                )
            )
            return False

    def _run_timed(self, motor, speed, time_ms):
        motor.speed_sp = int(speed)
        motor.time_sp = int(time_ms)
        try:
            motor.stop_action = "hold"
        except Exception:
            pass
        motor.command = "run-timed"
        return self._wait_motor(motor=motor, fallback_seconds=float(time_ms) / 1000.0)

    def _run_to_abs_pos(self, motor, speed, target):
        motor.speed_sp = int(abs(speed))
        motor.position_sp = int(target)
        try:
            motor.stop_action = "hold"
        except Exception:
            pass
        motor.command = "run-to-abs-pos"
        return self._wait_motor(motor=motor, fallback_seconds=2.0)

    def _run_full_turn(self, motor, speed, direction):
        turn_degrees = self._get_arm_turn_degrees()
        position_delta = turn_degrees if direction >= 0 else -turn_degrees
        return self._run_to_rel_pos(
            motor=motor,
            speed=speed,
            delta=position_delta,
        )

    def _run_to_rel_pos(self, motor, speed, delta):
        speed_abs = int(max(1, abs(speed)))
        position_delta = int(delta)

        motor.speed_sp = speed_abs
        motor.position_sp = position_delta
        try:
            motor.stop_action = "hold"
        except Exception:
            pass
        motor.command = "run-to-rel-pos"

        fallback_seconds = float(abs(position_delta)) / float(speed_abs) + 1.0
        fallback_seconds = max(1.5, fallback_seconds)
        return self._wait_motor(motor=motor, fallback_seconds=fallback_seconds)

    def _get_arm_turn_degrees(self):
        raw = os.getenv("EV3_ARM_TURN_DEGREES")
        if raw is None:
            return DEFAULT_ARM_TURN_DEGREES

        try:
            value = int(raw.strip())
        except Exception:
            print(
                "Aviso: EV3_ARM_TURN_DEGREES invalido ({}). "
                "Usando {}.".format(raw, DEFAULT_ARM_TURN_DEGREES)
            )
            return DEFAULT_ARM_TURN_DEGREES

        if value <= 0:
            print(
                "Aviso: EV3_ARM_TURN_DEGREES deve ser > 0 ({}). "
                "Usando {}.".format(value, DEFAULT_ARM_TURN_DEGREES)
            )
            return DEFAULT_ARM_TURN_DEGREES

        return value

    def _wait_motor(self, motor, fallback_seconds):
        timeout_ms = max(500, int(fallback_seconds * 1000.0) + 500)

        try:
            motor.wait_while("running", timeout=timeout_ms)
            return True
        except TypeError:
            try:
                motor.wait_while("running")
                return True
            except Exception:
                pass
        except Exception:
            pass

        deadline = time.time() + max(0.1, fallback_seconds)
        while time.time() < deadline:
            try:
                state = getattr(motor, "state", None)
                if state is None:
                    break
                if "running" not in state:
                    return True
            except Exception:
                break
            time.sleep(0.05)

        try:
            motor.stop()
        except Exception:
            try:
                motor.command = "stop"
            except Exception:
                pass

        return False
