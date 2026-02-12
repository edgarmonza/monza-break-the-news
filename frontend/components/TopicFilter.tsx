'use client';

import { motion } from 'framer-motion';
import {
  Globe, Scale, Shield, TrendingUp, Leaf, Zap, Trophy, LayoutGrid
} from 'lucide-react';

const TOPICS = [
  { id: 'all', label: 'Todas', icon: LayoutGrid },
  { id: 'politica', label: 'Política', icon: Scale, keywords: ['petro', 'congreso', 'gobierno', 'reforma', 'ministro', 'senado', 'presidente', 'ley', 'fiscal', 'elecciones'] },
  { id: 'economia', label: 'Economía', icon: TrendingUp, keywords: ['dólar', 'economía', 'inflación', 'banco', 'petróleo', 'impuesto', 'tributar', 'brent', 'crudo', 'mercado', 'precio'] },
  { id: 'seguridad', label: 'Seguridad', icon: Shield, keywords: ['farc', 'eln', 'narcotráfico', 'cocaína', 'bomba', 'militar', 'policía', 'guerrilla', 'paz', 'seguridad', 'crimen'] },
  { id: 'internacional', label: 'Internacional', icon: Globe, keywords: ['eeuu', 'trump', 'estados unidos', 'venezuela', 'mundial', 'internacional', 'eeuu', 'biden'] },
  { id: 'deportes', label: 'Deportes', icon: Trophy, keywords: ['gol', 'fútbol', 'liga', 'selección', 'díaz', 'liverpool', 'premier', 'copa', 'deportivo'] },
  { id: 'ambiente', label: 'Ambiente', icon: Leaf, keywords: ['inundación', 'lluvia', 'deforestación', 'ambiental', 'clima', 'sequía', 'río', 'desastre'] },
  { id: 'tech', label: 'Tech', icon: Zap, keywords: ['ciber', 'tecnología', 'digital', 'app', 'inteligencia artificial', 'hackeo', 'vacuna', 'ciencia'] },
];

interface TopicFilterProps {
  activeTopic: string;
  onSelect: (topicId: string) => void;
}

export default function TopicFilter({ activeTopic, onSelect }: TopicFilterProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 sm:mx-0 sm:px-0 scrollbar-hide">
      {TOPICS.map((topic) => {
        const isActive = activeTopic === topic.id;
        const Icon = topic.icon;

        return (
          <motion.button
            key={topic.id}
            onClick={() => onSelect(topic.id)}
            whileTap={{ scale: 0.95 }}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap shrink-0 transition-all ${
              isActive
                ? 'bg-cyan text-navy-dark shadow-lg shadow-cyan/20'
                : 'glass-effect text-gray-light hover:text-white hover:border-cyan/30'
            }`}
          >
            <Icon className="w-4 h-4" />
            <span>{topic.label}</span>
          </motion.button>
        );
      })}
    </div>
  );
}

// Helper to categorize a thread based on its content
export function categorizeThread(title: string, summary: string): string[] {
  const text = `${title} ${summary}`.toLowerCase();
  const categories: string[] = [];

  for (const topic of TOPICS) {
    if (topic.id === 'all') continue;
    if (topic.keywords?.some(kw => text.includes(kw))) {
      categories.push(topic.id);
    }
  }

  return categories.length > 0 ? categories : ['general'];
}

export { TOPICS };
