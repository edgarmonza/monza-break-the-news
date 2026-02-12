'use client';

import { motion } from 'framer-motion';
import { Thread } from '@/lib/types';

interface SidebarProps {
  threads: Thread[];
  activeId: string | null;
  onSelect: (id: string) => void;
}

export default function Sidebar({ threads, activeId, onSelect }: SidebarProps) {
  return (
    <motion.aside
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="hidden lg:block fixed left-0 top-[73px] h-[calc(100vh-73px)] w-[280px] glass-effect border-r border-white/10 overflow-y-auto"
    >
      <div className="p-6">
        <h2 className="text-sm font-semibold text-gray-medium uppercase tracking-wider mb-6">
          Historias Trending
        </h2>

        <div className="space-y-2">
          {threads.map((thread, index) => (
            <StoryItem
              key={thread.id}
              number={index + 1}
              thread={thread}
              isActive={thread.id === activeId}
              onClick={() => onSelect(thread.id)}
            />
          ))}
        </div>
      </div>
    </motion.aside>
  );
}

interface StoryItemProps {
  number: number;
  thread: Thread;
  isActive: boolean;
  onClick: () => void;
}

function StoryItem({ number, thread, isActive, onClick }: StoryItemProps) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.02, x: 4 }}
      whileTap={{ scale: 0.98 }}
      className={`w-full text-left p-4 rounded-lg transition-all ${
        isActive
          ? 'bg-cyan/10 border border-cyan/30'
          : 'hover:bg-white/5 border border-transparent'
      }`}
    >
      <div className="flex items-start gap-4">
        <span className={`text-3xl font-bold ${
          isActive ? 'text-cyan' : 'text-gray-medium'
        }`}>
          {number.toString().padStart(2, '0')}
        </span>

        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold text-sm line-clamp-2 mb-1 ${
            isActive ? 'text-cyan' : 'text-white'
          }`}>
            {thread.display_title}
          </h3>
          <div className="flex items-center gap-2 text-xs text-gray-medium">
            <span>{thread.article_count} artículos</span>
            {isActive && (
              <span className="w-1.5 h-1.5 rounded-full bg-cyan animate-pulse" />
            )}
          </div>
        </div>
      </div>
    </motion.button>
  );
}
