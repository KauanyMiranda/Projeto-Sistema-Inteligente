try:
    from pybricks.hubs import EV3Brick
    from pybricks.ev3devices import Motor
    from pybricks.parameters import Port
except ImportError:
    EV3Brick = None
    Motor = None
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
        simulation_mode: bool = False,
        region_routing: dict[str, dict[str, int | str | None]] | None = None,
        **_ignored_legacy_kwargs,
    ):
        self.simulation_mode = simulation_mode
        self.region_routing = region_routing or DEFAULT_REGION_ROUTING

        self.ready = False
        self.ev3 = None
        self.motor_esteira = None
        self.motor_braco1 = None
        self.motor_braco2 = None

        if self.simulation_mode:
            print("EV3 em modo simulacao.")
            return

        if EV3Brick is None or Motor is None or Port is None:
            print(
                "Pybricks nao encontrado neste Python. "
                "No PC, mantenha simulacao; no EV3, execute com firmware Pybricks."
            )
            self.simulation_mode = True
            return

        try:
            self.ev3 = EV3Brick()
            self.motor_esteira = Motor(Port.B)
            self.motor_braco1 = Motor(Port.C)
            self.motor_braco2 = Motor(Port.D)
            self.ready = True
            print("EV3 pronto: esteira em B, braco1 em C, braco2 em D.")
        except Exception as e:
            print("Falha ao inicializar motores EV3. Indo para simulacao:", e)
            self.simulation_mode = True

    def execute_region(self, region: str) -> None:
        route = self.region_routing.get(region)
        if route is None:
            print(f"Regiao nao mapeada para atuacao: {region}")
            return

        esteira_speed = route["esteira_speed"]
        esteira_time_ms = route["esteira_time_ms"]
        braco = route["braco"]
        braco_speed = route["braco_speed"]
        braco_target = route["braco_target"]

        if self.simulation_mode or not self.ready:
            print(
                f"[SIMULACAO] {region}: esteira speed={esteira_speed}, time={esteira_time_ms}ms"
            )
            if braco is not None:
                print(
                    f"[SIMULACAO] {region}: {braco} run_target(speed={braco_speed}, target={braco_target})"
                )
            return

        self.motor_esteira.run_time(esteira_speed, esteira_time_ms, wait=True)

        if braco is None:
            return

        if braco == "BRACO_1":
            self.motor_braco1.run_target(braco_speed, braco_target, wait=True)
        elif braco == "BRACO_2":
            self.motor_braco2.run_target(braco_speed, braco_target, wait=True)