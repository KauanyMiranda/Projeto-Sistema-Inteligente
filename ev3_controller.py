try:
    from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent
except ImportError:
    LargeMotor = None
    OUTPUT_A = None
    OUTPUT_B = None
    SpeedPercent = None

DEFAULT_REGION_TO_ACTION = {
    "NORTE": ("MOTOR_1", "CW"),
    "SUL": ("MOTOR_1", "CCW"),
    "NORDESTE": ("MOTOR_2", "CW"),
    "SUDESTE": ("MOTOR_2", "CCW"),
    "CENTRO-OESTE": ("STRAIGHT", None),
}

class EV3Actuator:
    def __init__(
        self,
        simulation_mode: bool = True,
        turn_degrees: int = 90,
        turn_speed_percent: int = 25,
        cw_sign: int = 1,
        ccw_sign: int = -1,
        region_to_action: dict[str, tuple[str, str | None]] | None = None,
    ):
        self.simulation_mode = simulation_mode
        self.turn_degrees = turn_degrees
        self.turn_speed_percent = turn_speed_percent
        self.cw_sign = cw_sign
        self.ccw_sign = ccw_sign
        self.region_to_action = region_to_action or DEFAULT_REGION_TO_ACTION

        self.ready = False
        self.motor_1 = None
        self.motor_2 = None

        if self.simulation_mode:
            print("EV3 em modo simulacao.")
            return

        if LargeMotor is None:
            print(
                "Biblioteca ev3dev2 nao encontrada. Instalando sugestao: pip install python-ev3dev2"
            )
            self.simulation_mode = True
            return

        try:
            self.motor_1 = LargeMotor(OUTPUT_A)
            self.motor_2 = LargeMotor(OUTPUT_B)
            self.ready = True
            print("EV3 conectado: Motor 1 em A, Motor 2 em B.")
        except Exception as e:
            print("Falha ao inicializar EV3. Indo para simulacao:", e)
            self.simulation_mode = True

    def execute_region(self, region: str) -> None:
        action = self.region_to_action.get(region)
        if action is None:
            print(f"Regiao nao mapeada para atuacao: {region}")
            return

        motor_name, direction = action

        if motor_name == "STRAIGHT":
            print("CENTRO-OESTE: segue reto na esteira (sem giro).")
            return

        sign = self.cw_sign if direction == "CW" else self.ccw_sign
        speed = sign * self.turn_speed_percent

        if self.simulation_mode or not self.ready:
            print(
                f"[SIMULACAO] Acionando {motor_name} no sentido {direction} "
                f"({self.turn_degrees} graus, {abs(self.turn_speed_percent)}%)."
            )
            return

        motor = self.motor_1 if motor_name == "MOTOR_1" else self.motor_2
        motor.on_for_degrees(
            SpeedPercent(speed), self.turn_degrees, brake=True, block=True
        )
        print(
            f"[EV3] Acionou {motor_name} no sentido {direction} "
            f"({self.turn_degrees} graus, {abs(self.turn_speed_percent)}%)."
        )