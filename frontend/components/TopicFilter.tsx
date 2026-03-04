'use client';

import { motion } from 'framer-motion';
import {
  Globe, Scale, Shield, TrendingUp, Leaf, Zap, Trophy, LayoutGrid
} from 'lucide-react';

// Each topic has an accent color for thin bar indicators: 'yellow' | 'coral' | 'blue'
const TOPICS = [
  { id: 'all', label: 'Todas', icon: LayoutGrid, color: 'yellow' as const },
  { id: 'politica', label: 'Política', icon: Scale, color: 'coral' as const, keywords: ['petro', 'congreso', 'gobierno', 'reforma', 'ministro', 'senado', 'presidente', 'ley', 'fiscal', 'elecciones'] },
  { id: 'economia', label: 'Economía', icon: TrendingUp, color: 'yellow' as const, keywords: ['dólar', 'economía', 'inflación', 'banco', 'petróleo', 'impuesto', 'tributar', 'brent', 'crudo', 'mercado', 'precio'] },
  { id: 'seguridad', label: 'Seguridad', icon: Shield, color: 'coral' as const, keywords: ['farc', 'eln', 'narcotráfico', 'cocaína', 'bomba', 'militar', 'policía', 'guerrilla', 'paz', 'seguridad', 'crimen'] },
  { id: 'internacional', label: 'Internacional', icon: Globe, color: 'blue' as const, keywords: ['eeuu', 'trump', 'estados unidos', 'venezuela', 'mundial', 'internacional', 'eeuu', 'biden'] },
  { id: 'deportes', label: 'Deportes', icon: Trophy, color: 'yellow' as const, keywords: ['gol', 'fútbol', 'liga', 'selección', 'díaz', 'liverpool', 'premier', 'copa', 'deportivo'] },
  { id: 'ambiente', label: 'Ambiente', icon: Leaf, color: 'blue' as const, keywords: ['inundación', 'lluvia', 'deforestación', 'ambiental', 'clima', 'sequía', 'río', 'desastre'] },
  { id: 'tech', label: 'Tech', icon: Zap, color: 'blue' as const, keywords: ['ciber', 'tecnología', 'digital', 'app', 'inteligencia artificial', 'hackeo', 'vacuna', 'ciencia'] },
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
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap shrink-0 transition-all font-sans ${
              isActive
                ? 'bg-ink text-white'
                : 'border border-[rgba(170,150,120,0.15)] text-ink/40 hover:text-ink-secondary hover:border-[rgba(170,150,120,0.25)] bg-surface/50'
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

// Helper to get the accent color for a thread based on its primary topic
export function getThreadColor(title: string, summary: string): 'yellow' | 'coral' | 'blue' {
  const text = `${title} ${summary}`.toLowerCase();

  for (const topic of TOPICS) {
    if (topic.id === 'all') continue;
    if (topic.keywords?.some(kw => text.includes(kw))) {
      return topic.color as 'yellow' | 'coral' | 'blue';
    }
  }

  return 'yellow'; // default
}

export { TOPICS };
