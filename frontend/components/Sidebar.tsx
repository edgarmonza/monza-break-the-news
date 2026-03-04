'use client';

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Thread } from '@/lib/types';
import { Flame, Clock, Zap } from 'lucide-react';
import { getThreadColor } from './TopicFilter';

type SortMode = 'hot' | 'new' | 'developing';
type ColorFilter = 'all' | 'yellow' | 'coral' | 'blue';

const SORT_TABS: { id: SortMode; label: string; icon: React.ElementType }[] = [
  { id: 'hot', label: 'Hot', icon: Flame },
  { id: 'new', label: 'New', icon: Clock },
  { id: 'developing', label: 'En Des.', icon: Zap },
];

const DOT_FILTERS: { id: ColorFilter; bg: string; activeBg: string }[] = [
  { id: 'all', bg: 'bg-ink/15', activeBg: 'bg-ink' },
  { id: 'yellow', bg: 'bg-accent/30', activeBg: 'bg-accent' },
  { id: 'blue', bg: 'bg-accent-blue/30', activeBg: 'bg-accent-blue' },
  { id: 'coral', bg: 'bg-accent-warm/30', activeBg: 'bg-accent-warm' },
];

interface SidebarProps {
  threads: Thread[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onOpenDetail?: (id: string) => void;
}

export default function Sidebar({ threads, activeId, onSelect, onOpenDetail }: SidebarProps) {
  const [sortMode, setSortMode] = useState<SortMode>('hot');
  const [colorFilter, setColorFilter] = useState<ColorFilter>('all');

  const maxScore = useMemo(() => {
    return Math.max(...threads.map(t => t.trending_score), 1);
  }, [threads]);

  const filteredAndSorted = useMemo(() => {
    let result = [...threads];

    // Filter by color category
    if (colorFilter !== 'all') {
      result = result.filter(t => {
        const color = getThreadColor(t.display_title, t.summary);
        return color === colorFilter;
      });
    }

    // Sort
    switch (sortMode) {
      case 'hot':
        result.sort((a, b) => b.trending_score - a.trending_score);
        break;
      case 'new':
        result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        break;
      case 'developing':
        result.sort((a, b) => b.article_count - a.article_count);
        break;
    }

    return result;
  }, [threads, sortMode, colorFilter]);

  return (
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="hidden lg:block fixed left-0 top-[60px] h-[calc(100vh-60px)] w-[280px] bg-base border-r paper-divider overflow-y-auto"
    >
      <div className="p-5">
        {/* Sort Tabs */}
        <div className="flex gap-1 mb-3">
          {SORT_TABS.map((tab) => {
            const isActive = sortMode === tab.id;
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setSortMode(tab.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[11px] font-medium transition-all font-sans ${
                  isActive
                    ? 'bg-ink text-white'
                    : 'text-ink/30 hover:text-ink/50 hover:bg-ink/[0.04]'
                }`}
              >
                <Icon className="w-3 h-3" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Color Dot Filters */}
        <div className="flex items-center gap-2.5 mb-4 pb-4 border-b paper-divider">
          {DOT_FILTERS.map((dot) => (
            <button
              key={dot.id}
              onClick={() => setColorFilter(dot.id)}
              className={`w-3 h-3 rounded-full transition-all ${
                colorFilter === dot.id
                  ? `${dot.activeBg} ring-2 ring-offset-2 ring-offset-base ring-ink/10 scale-110`
                  : `${dot.bg} hover:scale-125`
              }`}
              aria-label={`Filter ${dot.id}`}
            />
          ))}
          {colorFilter !== 'all' && (
            <span className="text-[10px] text-ink/25 font-sans ml-0.5">
              {filteredAndSorted.length}
            </span>
          )}
        </div>

        {/* Thread List */}
        <div className="space-y-0.5">
          {filteredAndSorted.map((thread, index) => (
            <StoryItem
              key={thread.id}
              number={index + 1}
              thread={thread}
              isActive={thread.id === activeId}
              maxScore={maxScore}
              onClick={() => {
                onSelect(thread.id);
                onOpenDetail?.(thread.id);
              }}
            />
          ))}

          {filteredAndSorted.length === 0 && (
            <p className="text-xs text-ink/25 text-center py-8 font-sans">
              Sin historias en esta categoría
            </p>
          )}
        </div>
      </div>
    </motion.aside>
  );
}

/* ── Enhanced Story Item ── */

interface StoryItemProps {
  number: number;
  thread: Thread;
  isActive: boolean;
  maxScore: number;
  onClick: () => void;
}

function StoryItem({ number, thread, isActive, maxScore, onClick }: StoryItemProps) {
  const color = getThreadColor(thread.display_title, thread.summary);
  const intensity = (thread.trending_score / maxScore) * 100;

  const barColor = color === 'yellow' ? 'bg-accent' : color === 'coral' ? 'bg-accent-warm' : 'bg-accent-blue';
  const dotColor = barColor;

  // Badge logic
  const hoursAgo = (Date.now() - new Date(thread.created_at).getTime()) / (1000 * 60 * 60);
  const isNew = hoursAgo < 3;
  const isDeveloping = thread.article_count >= 5;

  return (
    <motion.button
      onClick={onClick}
      whileHover={{ x: 3 }}
      whileTap={{ scale: 0.98 }}
      className={`w-full text-left p-3 rounded-lg transition-all ${
        isActive
          ? 'bg-ink/[0.05]'
          : 'hover:bg-ink/[0.03]'
      }`}
    >
      <div className="flex items-start gap-2.5">
        {/* Color dot + number */}
        <div className="flex items-center gap-1.5 mt-0.5 shrink-0">
          <span className={`w-2 h-2 rounded-full ${dotColor}`} />
          <span className={`text-lg font-bold tabular-nums font-sans leading-none ${
            isActive ? 'text-ink/30' : 'text-ink/10'
          }`}>
            {number.toString().padStart(2, '0')}
          </span>
        </div>

        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className={`text-[13px] leading-snug line-clamp-2 font-sans ${
            isActive ? 'text-ink font-medium' : 'text-ink-secondary font-normal'
          }`}>
            {thread.display_title}
          </h3>

          {/* Meta: sources + badge */}
          <div className="flex items-center gap-2 mt-1.5">
            <span className="text-[10px] text-ink/25 font-sans">
              {thread.article_count} fuentes
            </span>
            {isNew && (
              <span className="text-[9px] font-semibold uppercase tracking-wider text-ink/40 font-sans">
                Nuevo
              </span>
            )}
            {!isNew && isDeveloping && (
              <span className="text-[9px] font-semibold uppercase tracking-wider text-ink/40 font-sans">
                En desarrollo
              </span>
            )}
          </div>

          {/* Intensity bar */}
          <div className="mt-2 flex items-center gap-2">
            <div className="flex-1 h-[3px] rounded-full bg-ink/[0.06] overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${intensity}%` }}
                transition={{ duration: 0.6, delay: 0.1 }}
                className={`h-full rounded-full ${barColor}`}
              />
            </div>
            <span className="text-[10px] font-medium tabular-nums text-ink/25 font-sans shrink-0">
              {thread.trending_score.toFixed(1)}
            </span>
          </div>
        </div>
      </div>
    </motion.button>
  );
}
