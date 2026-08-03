def compute_aqi(pm25: float) -> int:
    """Calcula um AQI simplificado a partir do PM2.5 (faixas EPA).

    Retorna um inteiro entre 0 e 500. Um PM2.5 ausente ou inválido
    assume 0 (ar bom).
    """
    if pm25 is None or pm25 < 0:
        return 0
    # (concentracao_min, concentracao_max, aqi_min, aqi_max)
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    for cmin, cmax, amin, amax in breakpoints:
        if pm25 <= cmax:
            if cmin == cmax:
                return amax
            return int(round(((amax - amin) / (cmax - cmin)) * (pm25 - cmin) + amin))
    return 500


def aqi_band(aqi: int) -> str:
    if aqi <= 50:
        return "Bom"
    if aqi <= 100:
        return "Moderado"
    if aqi <= 150:
        return "Ruim"
    if aqi <= 200:
        return "Muito ruim"
    return "Péssimo"
