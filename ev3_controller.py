import time

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
            self.motor_esteira = EV3Dev2Motor(OUTPUT_B)
            self.motor_braco1 = EV3Dev2Motor(OUTPUT_C)
            self.motor_braco2 = EV3Dev2Motor(OUTPUT_D)

            self.ready = True
            self.backend = "ev3dev2"
            print(
                "EV3 pronto com ev3dev2: esteira em B, "
                "braco1 em C, braco2 em D."
            )
            return True
        except Exception as e:
            print("Falha ao inicializar ev3dev2. Indo para fallback:", e)
            self.motor_esteira = None
            self.motor_braco1 = None
            self.motor_braco2 = None
            self.ready = False
            return False

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
                print(
                    "[SIMULACAO] {}: {} run_target(speed={}, target={})".format(
                        region,
                        braco,
                        braco_speed,
                        braco_target,
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
            self._run_timed(
                motor=self.motor_esteira,
                speed=esteira_speed,
                time_ms=esteira_time_ms,
            )

            if braco is None:
                return True

            if braco == "BRACO_1":
                target_motor = self.motor_braco1
            elif braco == "BRACO_2":
                target_motor = self.motor_braco2
            else:
                print("Braco nao mapeado para atuacao: {}".format(braco))
                return False

            self._run_to_abs_pos(
                motor=target_motor,
                speed=braco_speed,
                target=braco_target,
            )
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
        self._wait_motor(motor=motor, fallback_seconds=float(time_ms) / 1000.0)

    def _run_to_abs_pos(self, motor, speed, target):
        motor.speed_sp = int(abs(speed))
        motor.position_sp = int(target)
        try:
            motor.stop_action = "hold"
        except Exception:
            pass
        motor.command = "run-to-abs-pos"
        self._wait_motor(motor=motor, fallback_seconds=2.0)

    def _wait_motor(self, motor, fallback_seconds):
        try:
            motor.wait_while("running")
            return
        except TypeError:
            try:
                motor.wait_while("running", timeout=int(fallback_seconds * 1000))
                return
            except Exception:
                pass
        except Exception:
            pass

        time.sleep(max(0.05, fallback_seconds))
