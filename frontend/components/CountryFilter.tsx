'use client';

import { motion } from 'framer-motion';

const COUNTRIES = [
  { id: 'all', label: 'Latam', flag: '\u{1F30E}' },
  { id: 'mexico', label: 'México', flag: '\u{1F1F2}\u{1F1FD}' },
  { id: 'colombia', label: 'Colombia', flag: '\u{1F1E8}\u{1F1F4}' },
  { id: 'argentina', label: 'Argentina', flag: '\u{1F1E6}\u{1F1F7}' },
];

// Keywords to match country from thread content
const COUNTRY_KEYWORDS: Record<string, string[]> = {
  mexico: ['méxico', 'mexico', 'mexicano', 'mexicana', 'cdmx', 'amlo', 'claudia sheinbaum', 'sheinbaum', 'pemex', 'peso mexicano', 'liga mx', 'azteca'],
  colombia: ['colombia', 'colombiano', 'colombiana', 'bogotá', 'bogota', 'medellín', 'medellin', 'petro', 'ecopetrol', 'peso colombiano', 'barranquilla', 'cali'],
  argentina: ['argentina', 'argentino', 'argentinos', 'buenos aires', 'milei', 'peso argentino', 'boca', 'river', 'afa', 'kirchner', 'libertadores'],
};

interface CountryFilterProps {
  activeCountry: string;
  onSelect: (countryId: string) => void;
}

export default function CountryFilter({ activeCountry, onSelect }: CountryFilterProps) {
  return (
    <div className="flex items-center gap-1">
      {COUNTRIES.map((country) => {
        const isActive = activeCountry === country.id;

        return (
          <motion.button
            key={country.id}
            onClick={() => onSelect(country.id)}
            whileTap={{ scale: 0.95 }}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-[12px] font-medium whitespace-nowrap transition-all font-sans ${
              isActive
                ? 'bg-accent/20 text-ink'
                : 'text-ink/30 hover:text-ink/50 hover:bg-ink/[0.04]'
            }`}
          >
            <span className="text-sm leading-none">{country.flag}</span>
            <span>{country.label}</span>
          </motion.button>
        );
      })}
    </div>
  );
}

// Helper to match a thread to a country based on its content
export function matchCountry(title: string, summary: string): string[] {
  const text = `${title} ${summary}`.toLowerCase();
  const matches: string[] = [];

  for (const [countryId, keywords] of Object.entries(COUNTRY_KEYWORDS)) {
    if (keywords.some(kw => text.includes(kw))) {
      matches.push(countryId);
    }
  }

  return matches;
}

export { COUNTRIES };
