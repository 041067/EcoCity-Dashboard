import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { City } from '../../types';

import 'leaflet/dist/leaflet.css';

// Fix default icon issue with Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface MapViewProps {
  cities: City[];
  selectedCity: City | null;
  onCitySelect: (city: City) => void;
}

export function MapView({ cities, selectedCity, onCitySelect }: MapViewProps) {
  const center = selectedCity || cities[0];

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

interface CityMarkerProps {
  city: City;
  isSelected: boolean;
  onSelect: () => void;
}

function CityMarker({ city, isSelected, onSelect }: CityMarkerProps) {
  const getMarkerColor = (city: City): string => {
    if (!city) return '#gray';
    
    if (city.score !== undefined) {
      if (city.score >= 70) return '#10b981'; // verde
      if (city.score >= 40) return '#fbbf24'; // amarelo
      return '#ef4444'; // vermelho
    }
    
    return '#3b82f6'; // azul padrão
  };

  return (
    <Marker
      position={[city.latitude, city.longitude]}
      color={getMarkerColor(city)}
      eventHandlers={{ click: () => onSelect() }}
    >
      <Popup>
        <div className="text-center">
          <h3 className="font-bold text-lg">{city.name}</h3>
          <p className="text-sm text-gray-600">{city.state}</p>
          <p className="text-xs text-gray-500">ID: {city.id}</p>
        </div>
      </Popup>
    </Marker>
  );
}