import { Marker, Popup } from 'react-leaflet';
import type { City } from '../../types';
import { scoreIcon } from './markerUtils';

interface CityMarkerProps {
  city: City;
  isSelected: boolean;
  onSelect: () => void;
}

export function CityMarker({ city, isSelected, onSelect }: CityMarkerProps) {
  return (
    <Marker
      position={[city.latitude, city.longitude]}
      icon={scoreIcon(city)}
      zIndexOffset={isSelected ? 1000 : 0}
      eventHandlers={{ click: onSelect }}
    >
      <Popup>
        <div className="text-center">
          <h3 className="font-bold text-lg">{city.name}</h3>
          <p className="text-sm text-gray-600">{city.state}</p>
          {city.score !== undefined && (
            <p className="text-sm font-semibold">Eco Score: {Math.round(city.score)}</p>
          )}
        </div>
      </Popup>
    </Marker>
  );
}
