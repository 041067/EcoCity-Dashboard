const NODES = [
  { x: 180, y: 260, color: '#67e8f9', label: 'AQI 42' },
  { x: 480, y: 310, color: '#6ee7b7', label: '24.5°C' },
  { x: 740, y: 230, color: '#67e8f9', label: 'Índice UV 3' },
  { x: 980, y: 350, color: '#6ee7b7', label: 'Umidade 61%' },
  { x: 1240, y: 280, color: '#67e8f9', label: 'Vento 12 km/h' },
  { x: 240, y: 620, color: '#34d399' },
  { x: 300, y: 420, color: '#34d399' },
  { x: 420, y: 620, color: '#67e8f9' },
  { x: 640, y: 520, color: '#34d399' },
  { x: 760, y: 700, color: '#67e8f9' },
  { x: 880, y: 640, color: '#6ee7b7' },
  { x: 1100, y: 520, color: '#6ee7b7' },
];

const PATHS = [
  'M180 260 L480 310 L740 230 L980 350 L1240 280',
  'M480 310 L640 520 L980 350 L880 640 L1240 280',
  'M240 620 L300 420 L480 310',
  'M300 420 L420 620 L640 520',
  'M640 520 L760 700 L880 640',
  'M980 350 L1100 520 L1240 280',
];

const V_LINES = Array.from({ length: 13 }, (_, i) => 40 + i * 120);
const H_LINES = Array.from({ length: 9 }, (_, i) => 60 + i * 100);

export function CityMapBackground() {
  return (
    <svg
      role="img"
      aria-label="Mapa da cidade com sensores ambientais conectados"
      className="absolute inset-0 h-full w-full"
      preserveAspectRatio="xMidYMid slice"
      viewBox="0 0 1440 900"
    >
      <defs>
        <linearGradient id="ec-bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#06121f" />
          <stop offset="50%" stopColor="#0a2a3d" />
          <stop offset="100%" stopColor="#07352c" />
        </linearGradient>
        <radialGradient id="ec-glow-blue" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="ec-glow-green" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#34d399" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#34d399" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="ec-line" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#22d3ee" stopOpacity="0" />
          <stop offset="30%" stopColor="#22d3ee" stopOpacity="0.8" />
          <stop offset="70%" stopColor="#34d399" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#34d399" stopOpacity="0" />
        </linearGradient>
      </defs>

      <rect width="1440" height="900" fill="url(#ec-bg)" />

      <circle cx="220" cy="180" r="320" fill="url(#ec-glow-blue)" />
      <circle cx="1180" cy="720" r="360" fill="url(#ec-glow-green)" />

      <g stroke="#94a3b8" strokeOpacity="0.08" strokeWidth="1">
        {V_LINES.map((x) => (
          <line key={`v-${x}`} x1={x} y1="0" x2={x} y2="900" />
        ))}
        {H_LINES.map((y) => (
          <line key={`h-${y}`} x1="0" y1={y} x2="1440" y2={y} />
        ))}
      </g>

      <g fill="none" stroke="#e2e8f0" strokeOpacity="0.12" strokeWidth="2">
        <path d="M-40 470 L1480 360" />
        <path d="M380 -40 L560 940" />
      </g>

      <g fill="none" stroke="url(#ec-line)" strokeWidth="1.5" strokeDasharray="6 10" className="animate-flow-dash">
        {PATHS.map((d) => (
          <path key={d} d={d} />
        ))}
      </g>

      {NODES.map((n) => (
        <g key={`${n.x}-${n.y}`}>
          <circle cx={n.x} cy={n.y} r="11" fill={n.color} opacity="0.15" className="animate-glow" />
          <circle cx={n.x} cy={n.y} r="3.5" fill={n.color} />
        </g>
      ))}

      <g fill="#a5f3fc" fontSize="13" fontWeight="600" stroke="#06121f" strokeWidth="4" paintOrder="stroke">
        {NODES.filter((n) => n.label).map((n) => (
          <text key={n.label} x={n.x + 14} y={n.y - 10}>
            {n.label}
          </text>
        ))}
      </g>

      <circle r="3.5" fill="#34d399" opacity="0.9">
        <animateMotion dur="10s" repeatCount="indefinite" path={PATHS[0]} />
      </circle>
      <circle r="2.5" fill="#22d3ee" opacity="0.8">
        <animateMotion dur="8s" begin="3s" repeatCount="indefinite" path={PATHS[1]} />
      </circle>
      <circle r="2.5" fill="#67e8f9" opacity="0.8">
        <animateMotion dur="9s" begin="5s" repeatCount="indefinite" path={PATHS[3]} />
      </circle>
    </svg>
  );
}
