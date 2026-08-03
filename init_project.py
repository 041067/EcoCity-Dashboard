import json
import os

# Read the existing package.json
with open('frontend/package.json', 'r') as f:
    data = json.load(f)

# Add new dependencies
data['dependencies']['react-leaflet'] = '^1.0.0'
data['dependencies']['leaflet'] = '^1.9.4'
data['dependencies']['@tanstack/react-query'] = '^5.0.0'

# Add new dev dependencies
data['devDependencies']['@types/leaflet'] = '^1.9.10'

# Write back to package.json
with open('frontend/package.json', 'w') as f:
    json.dump(data, f, indent=2)

print('Package.json updated successfully')

# Create the necessary directories
os.makedirs('frontend/src/components/charts', exist_ok=True)
os.makedirs('frontend/src/components/map', exist_ok=True)
os.makedirs('frontend/src/components/cards', exist_ok=True)
os.makedirs('frontend/src/components/alerts', exist_ok=True)
os.makedirs('frontend/src/components/chat', exist_ok=True)
os.makedirs('frontend/src/pages/Dashboard', exist_ok=True)
os.makedirs('frontend/src/pages/Reports', exist_ok=True)
os.makedirs('frontend/src/pages/Alerts', exist_ok=True)
os.makedirs('frontend/src/pages/Chat', exist_ok=True)
os.makedirs('frontend/src/hooks', exist_ok=True)
os.makedirs('frontend/src/contexts', exist_ok=True)
os.makedirs('frontend/src/utils', exist_ok=True)
os.makedirs('frontend/src/layouts', exist_ok=True)
os.makedirs('frontend/src/routes', exist_ok=True)

print('Directories created successfully')

# Create MapView.tsx
map_view_content = '''import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { City } from "../../types";

import "leaflet/dist/leaflet.css";

// Fix default icon issue with Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
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
      style={{ height: "100%", width: "100%" }}
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
    if (!city) return "#gray";
    
    if (city.score !== undefined) {
      if (city.score >= 70) return "#10b981"; // verde
      if (city.score >= 40) return "#fbbf24"; // amarelo
      return "#ef4444"; // vermelho
    }
    
    return "#3b82f6"; // azul padrão
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
'''

with open('frontend/src/components/map/MapView.tsx', 'w') as f:
    f.write(map_view_content)

print('MapView.tsx created successfully')

# Create CityMarker.tsx  
city_marker_content = '''import { Marker } from "react-leaflet";
import L from "leaflet";
import { City } from "../../types";

interface CityMarkerProps {
  city: City;
  isSelected: boolean;
  onSelect: () => void;
}

function CityMarker({ city, isSelected, onSelect }: CityMarkerProps) {
  const getMarkerColor = (city: City): string => {
    if (!city) return "#gray";
    
    if (city.score !== undefined) {
      if (city.score >= 70) return "#10b981"; // verde
      if (city.score >= 40) return "#fbbf24"; // amarelo
      return "#ef4444"; // vermelho
    }
    
    return "#3b82f6"; // azul padrão
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
'''

with open('frontend/src/components/map/CityMarker.tsx', 'w') as f:
    f.write(city_marker_content)

print('CityMarker.tsx created successfully')

print("All initial files created successfully!")
print("\nNext steps:")
print("1. Run: cd frontend && npm install")
print("2. Implement the remaining components and pages")
print("3. Run: cd frontend && npm run dev")
