import { Marker } from 'react-leaflet';
import { City } from '../../types';

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
    />
  );
}

export default CityMarker;