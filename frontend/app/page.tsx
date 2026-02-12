'use client';

import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import MobileDrawer from '@/components/MobileDrawer';
import FeedCard from '@/components/FeedCard';
import ThreadModal from '@/components/ThreadModal';
import TopicFilter, { categorizeThread } from '@/components/TopicFilter';
import MacroWidget from '@/components/MacroWidget';

export default function Home() {
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeTopic, setActiveTopic] = useState('all');

  const { data, isLoading, error } = useQuery({
    queryKey: ['feed'],
    queryFn: () => api.getFeed({ limit: 20, offset: 0 }),
  });

  const threads = data?.threads || [];

  // Filter threads by selected topic
  const filteredThreads = useMemo(() => {
    if (activeTopic === 'all') return threads;
    return threads.filter(t => {
      const categories = categorizeThread(t.display_title, t.summary);
      return categories.includes(activeTopic);
    });
  }, [threads, activeTopic]);

  useEffect(() => {
    if (threads.length > 0 && !activeThreadId) {
      setActiveThreadId(threads[0].id);
    }
  }, [threads, activeThreadId]);

  const handleTopicSelect = (topicId: string) => {
    setActiveTopic(topicId);
  };

  // Lock body scroll when mobile menu or modal is open
  useEffect(() => {
    if (mobileMenuOpen || selectedThreadId) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [mobileMenuOpen, selectedThreadId]);

  if (isLoading) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center">
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-12 h-12 border-4 border-cyan border-t-transparent rounded-full mx-auto mb-4"
          />
          <p className="text-gray-light text-sm">Cargando historias trending...</p>
        </div>
      </div>
    );
  }

  if (error || threads.length === 0) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center px-6">
        <div className="text-center">
          <h2 className="text-xl sm:text-2xl font-bold gradient-text mb-2">
            No hay historias disponibles
          </h2>
          <p className="text-gray-light text-sm">
            Ejecuta el pipeline para generar contenido
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-bg">
      <Header
        onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
        isMobileMenuOpen={mobileMenuOpen}
      />

      {/* Mobile Drawer */}
      <MobileDrawer
        isOpen={mobileMenuOpen}
        threads={threads}
        activeId={activeThreadId}
        onSelect={(id) => { setActiveThreadId(id); setMobileMenuOpen(false); }}
        onClose={() => setMobileMenuOpen(false)}
      />

      <div className="flex">
        {/* Desktop Sidebar */}
        <Sidebar
          threads={threads}
          activeId={activeThreadId}
          onSelect={setActiveThreadId}
        />

        {/* Main Content */}
        <main className="flex-1 lg:ml-[280px] px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <div className="max-w-7xl mx-auto">

            {/* Mobile: Macro ticker strip at top */}
            <div className="xl:hidden mb-4">
              <MacroWidget />
            </div>

            {/* Topic Filter */}
            <div className="mb-5 sm:mb-6">
              <TopicFilter activeTopic={activeTopic} onSelect={handleTopicSelect} />
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-[1fr_300px] gap-8">

              {/* ── Left: Vertical News Feed ── */}
              <div className="space-y-5">
                {filteredThreads.map((thread, i) => (
                  <FeedCard
                    key={thread.id}
                    thread={thread}
                    index={i}
                    isHero={i === 0}
                    onOpenDetail={() => setSelectedThreadId(thread.id)}
                  />
                ))}

                {/* Empty state for filtered topic */}
                {filteredThreads.length === 0 && activeTopic !== 'all' && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center py-20"
                  >
                    <p className="text-gray-medium text-sm">
                      No hay historias sobre este tema ahora mismo.
                    </p>
                    <button
                      onClick={() => setActiveTopic('all')}
                      className="mt-3 text-cyan text-sm hover:underline"
                    >
                      Ver todas las historias
                    </button>
                  </motion.div>
                )}
              </div>

              {/* ── Right: Sticky Sidebar ── */}
              <aside className="hidden xl:block">
                <div className="sticky top-8 space-y-6">
                  <MacroWidget />

                  {/* Trending scores mini-list */}
                  <div className="pt-4 border-t border-white/[0.04]">
                    <h4 className="text-[11px] font-medium text-gray-medium uppercase tracking-[0.15em] mb-3">
                      Más leídas
                    </h4>
                    <div className="space-y-0">
                      {threads.slice(0, 5).map((thread, i) => (
                        <button
                          key={thread.id}
                          onClick={() => setSelectedThreadId(thread.id)}
                          className="w-full text-left flex items-start gap-3 py-2.5 border-b border-white/[0.03] last:border-0 hover:bg-white/[0.02] transition-colors -mx-2 px-2 rounded group"
                        >
                          <span className="text-sm font-bold text-cyan/20 leading-none mt-0.5 tabular-nums">
                            {(i + 1).toString().padStart(2, '0')}
                          </span>
                          <span className="text-xs leading-snug text-gray-light/80 group-hover:text-white transition-colors line-clamp-2">
                            {thread.display_title}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </aside>
            </div>
          </div>
        </main>
      </div>

      {/* Thread Modal */}
      <AnimatePresence>
        {selectedThreadId && (
          <ThreadModal
            threadId={selectedThreadId}
            onClose={() => setSelectedThreadId(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
