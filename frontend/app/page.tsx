'use client';

import { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Thread } from '@/lib/types';
import { useStore } from '@/lib/store';
import { motion, AnimatePresence } from 'framer-motion';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import MobileDrawer from '@/components/MobileDrawer';
import FeedCard from '@/components/FeedCard';
import ThreadModal from '@/components/ThreadModal';
import TopicFilter, { categorizeThread, getThreadColor } from '@/components/TopicFilter';
import CountryFilter, { matchCountry } from '@/components/CountryFilter';
import MacroWidget from '@/components/MacroWidget';
import ChatPanel from '@/components/ChatPanel';
import Onboarding from '@/components/Onboarding';
import BottomNav, { TabId } from '@/components/BottomNav';
import ExploreView from '@/components/ExploreView';
import SavedView from '@/components/SavedView';
import SettingsView from '@/components/SettingsView';

export default function Home() {
  const onboardingComplete = useStore((s) => s.onboardingComplete);

  // Show onboarding on first visit
  if (!onboardingComplete) {
    return <Onboarding />;
  }

  return <App />;
}

function App() {
  const [activeTab, setActiveTab] = useState<TabId>('home');

  return (
    <>
      {/* Tab content */}
      {activeTab === 'home' && <Feed />}
      {activeTab === 'explore' && <ExploreView onNavigateHome={() => setActiveTab('home')} />}
      {activeTab === 'saved' && <SavedView />}
      {activeTab === 'settings' && <SettingsView />}

      {/* Bottom navigation (mobile only) */}
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </>
  );
}

/* ── Feed: the main landing page — UNTOUCHED layout ── */
function Feed() {
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatQuestion, setChatQuestion] = useState('');

  // Persisted filters from Zustand store
  const activeTopic = useStore((s) => s.activeTopic);
  const activeCountry = useStore((s) => s.activeCountry);
  const setActiveTopic = useStore((s) => s.setActiveTopic);
  const setActiveCountry = useStore((s) => s.setActiveCountry);
  const followedTopics = useStore((s) => s.followedTopics);

  // Apply onboarding topic preferences on first load
  const [prefsApplied, setPrefsApplied] = useState(false);
  useEffect(() => {
    if (!prefsApplied && followedTopics.length > 0 && activeTopic === 'all') {
      setActiveTopic(followedTopics[0]);
      setPrefsApplied(true);
    } else {
      setPrefsApplied(true);
    }
  }, [prefsApplied, followedTopics, activeTopic, setActiveTopic]);

  // Thread-specific URL: open modal if ?thread= param present
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const threadParam = params.get('thread');
    if (threadParam) {
      setSelectedThreadId(threadParam);
    }
  }, []);

  const [allThreads, setAllThreads] = useState<Thread[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['feed'],
    queryFn: () => api.getFeed({ limit: 20, offset: 0 }),
  });

  // Initialize threads from first fetch
  useEffect(() => {
    if (data?.threads) {
      setAllThreads(data.threads);
      setHasMore(data.threads.length >= 20);
    }
  }, [data]);

  const loadMore = useCallback(async () => {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    try {
      const moreData = await api.getFeed({ limit: 20, offset: allThreads.length });
      if (moreData.threads.length === 0) {
        setHasMore(false);
      } else {
        setAllThreads((prev) => [...prev, ...moreData.threads]);
        if (moreData.threads.length < 20) setHasMore(false);
      }
    } catch {
      // Silently fail — user can scroll again to retry
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, hasMore, allThreads.length]);

  // Intersection Observer for infinite scroll
  useEffect(() => {
    const el = loadMoreRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) loadMore();
      },
      { rootMargin: '200px' }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [loadMore]);

  const threads = allThreads;

  // Filter threads by country and topic
  const filteredThreads = useMemo(() => {
    let result = threads;

    // Country filter
    if (activeCountry !== 'all') {
      result = result.filter(t => {
        const countries = matchCountry(t.display_title, t.summary);
        return countries.includes(activeCountry);
      });
    }

    // Topic filter
    if (activeTopic !== 'all') {
      result = result.filter(t => {
        const categories = categorizeThread(t.display_title, t.summary);
        return categories.includes(activeTopic);
      });
    }

    return result;
  }, [threads, activeTopic, activeCountry]);

  useEffect(() => {
    if (threads.length > 0 && !activeThreadId) {
      setActiveThreadId(threads[0].id);
    }
  }, [threads, activeThreadId]);

  const handleChatSubmit = (question: string) => {
    setChatQuestion(question);
    setChatOpen(true);
  };

  // Lock body scroll when mobile menu, modal, or chat is open
  useEffect(() => {
    if (mobileMenuOpen || selectedThreadId || chatOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [mobileMenuOpen, selectedThreadId, chatOpen]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-base">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-5">
          {/* Hero skeleton */}
          <div className="h-[400px] sm:h-[480px] rounded-2xl bg-ink/[0.04] animate-pulse" />
          {/* Card skeletons */}
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex gap-4 p-5 rounded-xl bg-ink/[0.03] animate-pulse">
              <div className="w-[240px] h-[140px] rounded-lg bg-ink/[0.06] hidden sm:block shrink-0" />
              <div className="flex-1 space-y-3">
                <div className="h-4 w-24 rounded bg-ink/[0.06]" />
                <div className="h-6 w-3/4 rounded bg-ink/[0.06]" />
                <div className="h-4 w-full rounded bg-ink/[0.04]" />
                <div className="h-4 w-2/3 rounded bg-ink/[0.04]" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || threads.length === 0) {
    return (
      <div className="min-h-screen bg-base flex items-center justify-center px-6">
        <div className="text-center">
          <h2 className="text-xl sm:text-2xl font-bold text-ink mb-2">
            No hay historias disponibles
          </h2>
          <p className="text-ink-muted text-sm font-sans mb-4">
            {error ? 'Error al cargar las noticias.' : 'Ejecuta el pipeline para generar contenido.'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-5 py-2.5 bg-ink text-white text-sm font-semibold rounded-lg hover:bg-ink/80 transition-colors font-sans"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base pb-16 lg:pb-0">
      <Header
        onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
        isMobileMenuOpen={mobileMenuOpen}
        onChatSubmit={handleChatSubmit}
        countryFilter={<CountryFilter activeCountry={activeCountry} onSelect={setActiveCountry} />}
      />

      {/* AI Chat Panel */}
      <ChatPanel
        isOpen={chatOpen}
        initialQuestion={chatQuestion}
        onClose={() => setChatOpen(false)}
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
          onOpenDetail={(id) => setSelectedThreadId(id)}
        />

        {/* Main Content */}
        <main className="flex-1 lg:ml-[280px] px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          <div className="max-w-7xl mx-auto">

            {/* Mobile: Macro ticker strip at top */}
            <div className="xl:hidden mb-4">
              <MacroWidget />
            </div>

            {/* Mobile: Country filter (desktop is in header) */}
            <div className="lg:hidden mb-3">
              <CountryFilter activeCountry={activeCountry} onSelect={setActiveCountry} />
            </div>

            {/* Topic Filter */}
            <div className="mb-5 sm:mb-6">
              <TopicFilter activeTopic={activeTopic} onSelect={setActiveTopic} />
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

                {/* Infinite scroll sentinel */}
                {hasMore && filteredThreads.length > 0 && (
                  <div ref={loadMoreRef} className="flex justify-center py-8">
                    {loadingMore && (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        className="w-8 h-8 border-3 border-accent border-t-transparent rounded-full"
                      />
                    )}
                  </div>
                )}

                {/* Empty state for filtered results */}
                {filteredThreads.length === 0 && (activeTopic !== 'all' || activeCountry !== 'all') && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center py-20"
                  >
                    <p className="text-ink/35 text-sm font-sans">
                      No hay historias con estos filtros ahora mismo.
                    </p>
                    <button
                      onClick={() => { setActiveTopic('all'); setActiveCountry('all'); }}
                      className="mt-3 text-ink/50 text-sm hover:text-ink transition-colors font-sans"
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
                  <div className="pt-4 border-t paper-divider">
                    <h4 className="text-[10px] font-medium text-ink/30 uppercase tracking-[0.2em] mb-3 font-sans">
                      Más leídas
                    </h4>
                    <div className="space-y-0">
                      {threads.slice(0, 5).map((thread, i) => {
                        const dotColor = getThreadColor(thread.display_title, thread.summary);
                        const dotClass = dotColor === 'yellow' ? 'bg-accent' : dotColor === 'coral' ? 'bg-accent-warm' : 'bg-accent-blue';
                        return (
                          <button
                            key={thread.id}
                            onClick={() => setSelectedThreadId(thread.id)}
                            className="w-full text-left flex items-start gap-3 py-2.5 border-b paper-divider last:border-0 hover:bg-ink/[0.03] transition-colors -mx-2 px-2 rounded group"
                          >
                            <div className="flex items-center gap-2 mt-1 shrink-0">
                              <span className={`w-2 h-2 rounded-full ${dotClass}`} />
                              <span className="text-sm font-bold text-ink/[0.12] leading-none tabular-nums font-sans">
                                {(i + 1).toString().padStart(2, '0')}
                              </span>
                            </div>
                            <span className="text-xs leading-snug text-ink-muted group-hover:text-ink transition-colors line-clamp-2 font-sans">
                              {thread.display_title}
                            </span>
                          </button>
                        );
                      })}
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
