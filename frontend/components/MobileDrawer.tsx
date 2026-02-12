'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Thread } from '@/lib/types';
import { Flame } from 'lucide-react';

interface MobileDrawerProps {
  isOpen: boolean;
  threads: Thread[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onClose: () => void;
}

export default function MobileDrawer({ isOpen, threads, activeId, onSelect, onClose }: MobileDrawerProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed left-0 top-0 z-40 h-full w-[85vw] max-w-[320px] glass-effect border-r border-white/10 overflow-y-auto pt-[60px] lg:hidden"
          >
            <div className="p-5">
              <h2 className="text-xs font-semibold text-gray-medium uppercase tracking-widest mb-5">
                Historias Trending
              </h2>

              <div className="space-y-1">
                {threads.map((thread, index) => {
                  const isActive = thread.id === activeId;
                  return (
                    <motion.button
                      key={thread.id}
                      onClick={() => {
                        onSelect(thread.id);
                        onClose();
                      }}
                      whileTap={{ scale: 0.97 }}
                      className={`w-full text-left p-3.5 rounded-xl transition-all ${
                        isActive
                          ? 'bg-cyan/10 border border-cyan/30'
                          : 'active:bg-white/5 border border-transparent'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <span className={`text-2xl font-bold leading-none ${
                          isActive ? 'text-cyan' : 'text-gray-medium/50'
                        }`}>
                          {(index + 1).toString().padStart(2, '0')}
                        </span>
                        <div className="flex-1 min-w-0">
                          <h3 className={`font-semibold text-sm leading-snug line-clamp-2 ${
                            isActive ? 'text-cyan' : 'text-white'
                          }`}>
                            {thread.display_title}
                          </h3>
                          <div className="flex items-center gap-2 mt-1.5 text-xs text-gray-medium">
                            <span>{thread.article_count} artículos</span>
                            <span className="text-cyan/70 flex items-center gap-1">
                              <Flame className="w-3 h-3" />
                              {thread.trending_score.toFixed(1)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
