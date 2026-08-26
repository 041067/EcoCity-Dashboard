import type { ReactNode, SVGProps } from 'react';

export type IconName =
  | 'activity'
  | 'air'
  | 'alert'
  | 'bell'
  | 'bot'
  | 'brain'
  | 'building'
  | 'chart'
  | 'check'
  | 'close'
  | 'city'
  | 'cloud'
  | 'document'
  | 'energy'
  | 'folder'
  | 'leaf'
  | 'map'
  | 'menu'
  | 'moon'
  | 'rocket'
  | 'scale'
  | 'sensor'
  | 'sun'
  | 'target'
  | 'water'
  | 'chat';

interface AppIconProps extends SVGProps<SVGSVGElement> {
  name: IconName;
  title?: string;
}

const PATHS: Record<IconName, ReactNode> = {
  activity: <><path d="M3 12h4l3-8 4 16 3-8h4" /></>,
  air: <><path d="M4 8h10a3 3 0 1 0-3-3" /><path d="M4 12h14a3 3 0 1 1-3 3" /><path d="M4 16h7" /></>,
  alert: <><path d="M10.3 3.3 2.7 17a2 2 0 0 0 1.75 3h15.1A2 2 0 0 0 21.3 17L13.7 3.3a2 2 0 0 0-3.4 0Z" /><path d="M12 9v4" /><path d="M12 17h.01" /></>,
  bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" /><path d="M10 21h4" /></>,
  bot: <><rect x="4" y="7" width="16" height="13" rx="2" /><path d="M12 3v4M8 12h.01M16 12h.01M9 16h6" /></>,
  brain: <><path d="M9.5 4.5A3.5 3.5 0 0 1 16 6a4 4 0 0 1 2 7.45A3.5 3.5 0 0 1 14.5 19H13v-6h-2v6H9.5A3.5 3.5 0 0 1 6 15.5 4 4 0 0 1 8 8a3.5 3.5 0 0 1 1.5-3.5Z" /><path d="M8 10h3M13 9h3M7 14h3" /></>,
  building: <><path d="M4 21V4h12v17M2 21h20M8 8h2M8 12h2M8 16h2M14 8h2M14 12h2M14 16h2" /></>,
  chart: <><path d="M4 20V10M10 20V4M16 20v-7M22 20H2" /></>,
  check: <><path d="m5 12 4 4L19 6" /></>,
  close: <><path d="m6 6 12 12M18 6 6 18" /></>,
  city: <><path d="M3 21h18M5 21V9l5-3v15M10 21V4l5 3v14M15 21v-8l4 2v6M7 12h1M7 16h1M12 9h1M12 13h1" /></>,
  cloud: <><path d="M17.5 19H8a5 5 0 1 1 1.1-9.88A5.5 5.5 0 0 1 20 11a4 4 0 0 1-2.5 8Z" /></>,
  document: <><path d="M6 3h8l4 4v14H6z" /><path d="M14 3v5h5M9 13h6M9 17h6" /></>,
  energy: <><path d="m13 2-9 12h7l-1 8 9-12h-7z" /></>,
  folder: <><path d="M3 6a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" /></>,
  leaf: <><path d="M20 4C10 4 4 9 4 17c0 2 1 3 3 3 8 0 13-6 13-16Z" /><path d="M4 20c4-5 8-8 13-11" /></>,
  map: <><path d="m9 18-6 3V6l6-3 6 3 6-3v15l-6 3z" /><path d="M9 3v15M15 6v15" /></>,
  menu: <><path d="M4 7h16M4 12h16M4 17h16" /></>,
  moon: <><path d="M20.5 15.5A8 8 0 1 1 8.5 3.5a6 6 0 0 0 12 12Z" /></>,
  rocket: <><path d="M14 4c3-2 5-2 6-2 0 1 0 3-2 6l-5 5-4-4z" /><path d="m13 13-4 4M9 17l-3 1 1-3M11 5 7 9M4 20l4-1-3-3z" /></>,
  scale: <><path d="M12 3v18M5 6h14M4 6l-3 6h6zm16 0-3 6h6zM7 21h10" /></>,
  sensor: <><circle cx="12" cy="12" r="2" /><path d="M5 5a10 10 0 0 0 0 14M19 5a10 10 0 0 1 0 14M8 8a5 5 0 0 0 0 8M16 8a5 5 0 0 1 0 8" /></>,
  sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" /></>,
  target: <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2" /></>,
  water: <><path d="M12 3s6 6.2 6 11a6 6 0 0 1-12 0c0-4.8 6-11 6-11Z" /></>,
  chat: <><path d="M20 11.5a7.5 7.5 0 0 1-8 7.5 9 9 0 0 1-4-.9L4 20l1.2-3.4A7 7 0 0 1 4 12a7.5 7.5 0 0 1 8-7.5 7.5 7.5 0 0 1 8 7Z" /></>,
};

export function AppIcon({ name, title, className = 'h-5 w-5', ...props }: AppIconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={title ? undefined : true}
      role={title ? 'img' : undefined}
      className={className}
      {...props}
    >
      {title && <title>{title}</title>}
      {PATHS[name]}
    </svg>
  );
}
