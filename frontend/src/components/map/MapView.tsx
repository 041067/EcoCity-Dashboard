import { MapContainer, TileLayer } from 'react-leaflet';
import L from 'leaflet';
import type { City } from '../../types';
import { CityMarker } from './CityMarker';

import 'leaflet/dist/leaflet.css';

// Corrige o problema de ícones padrão do Leaflet em bundlers
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: string })._getIconUrl;

interface MapViewProps {
  cities: City[];
  selectedCity: City | null;
  onCitySelect: (city: City) => void;
}

export function MapView({ cities, selectedCity, onCitySelect }: MapViewProps) {
  const center = selectedCity || cities[0];

  if (!center) {
    return (
      <div className="flex h-full w-full items-center justify-center text-gray-500">
        Nenhuma cidade disponível
      </div>
    );
  }

  return (
    <MapContainer
      center={[center.latitude, center.longitude]}
      zoom={selectedCity ? 10 : 5}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {cities.map((city) => (
        <CityMarker
          key={city.id}
          city={city}
          isSelected={selectedCity?.id === city.id}
          onSelect={() => onCitySelect(city)}
        />
      ))}
    </MapContainer>
  );
}
