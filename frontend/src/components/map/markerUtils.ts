import L from 'leaflet';
import type { City } from '../../types';

export function scoreColor(city: City): string {
  if (city.score !== undefined) {
    if (city.score >= 70) return '#10b981'; // verde (Excelente)
    if (city.score >= 40) return '#fbbf24'; // amarelo (Moderado)
    return '#ef4444'; // vermelho (Crítico)
  }
  return '#3b82f6'; // azul padrão
}

export function scoreIcon(city: City): L.DivIcon {
  return L.divIcon({
    className: 'ecocity-marker',
    html: `<div style="
      width: 22px; height: 22px; border-radius: 50%;
      background: ${scoreColor(city)};
      border: 3px solid #fff;
      box-shadow: 0 2px 6px rgba(0,0,0,0.4);
      display: flex; align-items: center; justify-content: center;
      font-size: 11px; color: #fff; font-weight: 700;
    ">${city.score !== undefined ? Math.round(city.score) : ''}</div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -12],
  });
}
