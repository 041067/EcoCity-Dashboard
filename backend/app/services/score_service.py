from app.utils.air_quality import compute_aqi


class ScoreService:
    """Índice Eco Score (0-100) calculado a partir de uma leitura ambiental."""

    WEIGHTS = {
        "aqi": 0.35,
        "temperature": 0.25,
        "humidity": 0.20,
        "wind_speed": 0.15,
        "uv_index": 0.05,
    }

    def compute_score(self, temperature: float, humidity: float,
                      wind_speed: float, aqi: float, uv_index: float = 0.0) -> float:
        scores = [
            self._aqi_score(aqi) * self.WEIGHTS["aqi"],
            self._temperature_score(temperature) * self.WEIGHTS["temperature"],
            self._humidity_score(humidity) * self.WEIGHTS["humidity"],
            self._wind_score(wind_speed) * self.WEIGHTS["wind_speed"],
            self._uv_score(uv_index) * self.WEIGHTS["uv_index"],
        ]
        total = sum(scores)
        return round(max(0.0, min(100.0, total)), 1)

    def classify(self, score: float) -> dict:
        if score >= 70:
            classification = "Excelente"
            symbol = "🟢"
        elif score >= 40:
            classification = "Moderado"
            symbol = "🟡"
        else:
            classification = "Crítico"
            symbol = "🔴"
        return {"classification": classification, "symbol": symbol}

    def aqi_from_readings(self, pm25: float) -> int:
        return compute_aqi(pm25)

    def _aqi_score(self, aqi: float) -> float:
        if aqi <= 50:
            return 100.0
        if aqi <= 100:
            return 100 - (aqi - 50)  # 50 a 0
        if aqi <= 200:
            return max(0.0, 50 - (aqi - 100) * 0.5)
        return 0.0

    def _temperature_score(self, temperature: float) -> float:
        if 18 <= temperature <= 26:
            return 100.0
        if temperature < 18:
            return max(0.0, 100 - (18 - temperature) * 4)
        return max(0.0, 100 - (temperature - 26) * 4)

    def _humidity_score(self, humidity: float) -> float:
        if 40 <= humidity <= 65:
            return 100.0
        if humidity < 40:
            return max(0.0, 100 - (40 - humidity) * 3)
        return max(0.0, 100 - (humidity - 65) * 2)

    def _wind_score(self, wind_speed: float) -> float:
        if wind_speed <= 10:
            return 100.0
        if wind_speed <= 40:
            return max(0.0, 100 - (wind_speed - 10) * 2)
        return 0.0

    def _uv_score(self, uv_index: float) -> float:
        if uv_index <= 2:
            return 100.0
        if uv_index <= 7:
            return 100 - (uv_index - 2) * 10
        return 30.0
