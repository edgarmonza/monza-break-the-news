'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp, ChevronRight, ArrowRight, ExternalLink, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import { Thread, SearchResult } from '@/lib/types';
import { TOPICS } from './TopicFilter';
import ThreadModal from './ThreadModal';

const OUTLETS_BY_COUNTRY = [
  {
    country: 'Colombia 🇨🇴',
    outlets: ['El Tiempo', 'Semana', 'El Espectador', 'Portafolio', 'Blu Radio'],
  },
  {
    country: 'México 🇲🇽',
    outlets: ['Infobae México', 'El Universal', 'Reforma', 'Animal Político'],
  },
  {
    country: 'Argentina 🇦🇷',
    outlets: ['La Nación', 'Clarín', 'Infobae', 'Página 12'],
  },
  {
    country: 'Internacional 🌎',
    outlets: ['BBC Mundo', 'CNN en Español', 'DW Español', 'France 24'],
  },
];

interface ExploreViewProps {
  onNavigateHome?: () => void;
}

export default function ExploreView({ onNavigateHome }: ExploreViewProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);
  const followedTopics = useStore((s) => s.followedTopics);
  const toggleFollowTopic = useStore((s) => s.toggleFollowTopic);

  const selectableTopics = TOPICS.filter((t) => t.id !== 'all');

  // Fetch real trending threads
  const { data: feedData } = useQuery({
    queryKey: ['feed-explore'],
    queryFn: () => api.getFeed({ limit: 8, offset: 0 }),
  });

  const trendingThreads = feedData?.threads ?? [];

  // Search mutation
  const searchMutation = useMutation({
    mutationFn: (query: string) => api.search(query, 10),
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim().length >= 3) {
      searchMutation.mutate(searchQuery.trim());
    }
  };

  return (
    <div className="min-h-screen bg-base">
      {/* Header */}
      <div className="sticky top-0 z-30 bg-base/90 backdrop-blur-xl border-b paper-divider">
        <div className="px-4 sm:px-6 py-3">
          <h1 className="text-xl font-bold text-ink mb-3">Explorar</h1>
          <form onSubmit={handleSearch} className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg border border-ink/[0.08] bg-ink/[0.03]">
            <Search className="w-4 h-4 text-ink/25 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Buscar temas, medios, historias..."
              className="flex-1 bg-transparent text-sm text-ink font-sans outline-none placeholder:text-ink/25"
            />
            {searchQuery.trim().length >= 3 && (
              <button type="submit" className="p-1 rounded bg-accent/20 hover:bg-accent/30 transition-colors">
                <ArrowRight className="w-3.5 h-3.5 text-ink/50" />
              </button>
            )}
          </form>
        </div>
      </div>

      <div className="px-4 sm:px-6 py-6 space-y-8 pb-24">
        {/* Search Results */}
        <AnimatePresence>
          {searchMutation.data && (
            <motion.section
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-ink/40 font-sans">
                  Resultados para &ldquo;{searchMutation.data.query}&rdquo;
                </h2>
                <button
                  onClick={() => { searchMutation.reset(); setSearchQuery(''); }}
                  className="text-xs text-ink/30 hover:text-ink/60 font-sans transition-colors"
                >
                  Limpiar
                </button>
              </div>
              {searchMutation.data.results.length === 0 ? (
                <p className="text-sm text-ink/35 font-sans py-4">No se encontraron resultados.</p>
              ) : (
                <div className="space-y-2">
                  {searchMutation.data.results.map((result: SearchResult) => (
                    <a
                      key={result.id}
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-start gap-3 p-3 rounded-lg paper-card hover:border-ink/[0.15] transition-all group"
                    >
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-ink group-hover:text-ink/70 transition-colors font-sans line-clamp-2">
                          {result.title}
                        </h4>
                        <p className="text-[11px] text-ink/35 font-sans mt-1">{result.source}</p>
                      </div>
                      <ExternalLink className="w-4 h-4 text-ink/20 group-hover:text-ink/40 transition-colors shrink-0 mt-0.5" />
                    </a>
                  ))}
                </div>
              )}
            </motion.section>
          )}
        </AnimatePresence>

        {searchMutation.isPending && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-5 h-5 text-ink/30 animate-spin" />
          </div>
        )}

        {/* Trending — real threads from API */}
        {!searchMutation.data && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-4 h-4 text-accent-warm" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-ink/40 font-sans">Trending ahora</h2>
            </div>
            {trendingThreads.length === 0 ? (
              <div className="py-6 space-y-2">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-12 rounded-lg bg-ink/[0.04] animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="space-y-0">
                {trendingThreads.map((thread: Thread, i: number) => (
                  <motion.button
                    key={thread.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    onClick={() => setSelectedThreadId(thread.id)}
                    className="w-full text-left flex items-center gap-4 py-3 border-b paper-divider last:border-0 hover:bg-ink/[0.03] transition-colors -mx-2 px-2 rounded group"
                  >
                    <span className="text-lg font-bold text-ink/[0.10] leading-none tabular-nums font-sans w-7">
                      {(i + 1).toString().padStart(2, '0')}
                    </span>
                    <div className="flex-1 min-w-0">
                      <span className="text-sm font-medium text-ink group-hover:text-ink/70 transition-colors font-sans line-clamp-1">
                        {thread.display_title}
                      </span>
                      <span className="text-[10px] text-ink/25 font-sans block mt-0.5">
                        {thread.article_count} fuentes
                      </span>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <div className="w-12 h-1 bg-ink/[0.06] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-accent-warm/60 rounded-full"
                          style={{ width: `${Math.min(thread.trending_score * 100, 100)}%` }}
                        />
                      </div>
                      <ChevronRight className="w-3.5 h-3.5 text-ink/15 group-hover:text-ink/30 transition-colors" />
                    </div>
                  </motion.button>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Browse Topics */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-ink/40 font-sans mb-4">Temas</h2>
          <div className="grid grid-cols-2 gap-2.5">
            {selectableTopics.map((topic) => {
              const Icon = topic.icon;
              const isFollowed = followedTopics.includes(topic.id);
              return (
                <button
                  key={topic.id}
                  onClick={() => toggleFollowTopic(topic.id)}
                  className={`p-3.5 rounded-xl border text-left transition-all font-sans ${
                    isFollowed
                      ? 'border-ink bg-ink/[0.05]'
                      : 'border-ink/[0.08] bg-card hover:border-ink/[0.15]'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${
                      isFollowed ? 'bg-ink text-white' : 'bg-ink/[0.06] text-ink/40'
                    }`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className={`text-sm font-medium block truncate ${
                        isFollowed ? 'text-ink' : 'text-ink/60'
                      }`}>
                        {topic.label}
                      </span>
                      <span className="text-[10px] text-ink/30 font-sans">
                        {isFollowed ? 'Siguiendo' : 'Seguir'}
                      </span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </section>

        {/* Browse Outlets by Country */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-ink/40 font-sans mb-4">Medios por país</h2>
          <div className="space-y-5">
            {OUTLETS_BY_COUNTRY.map((group) => (
              <div key={group.country}>
                <h3 className="text-xs font-semibold text-ink/50 mb-2.5 font-sans">{group.country}</h3>
                <div className="flex gap-2 flex-wrap">
                  {group.outlets.map((outlet) => (
                    <span
                      key={outlet}
                      className="px-3 py-1.5 rounded-full border border-ink/[0.08] bg-card text-xs text-ink/60 font-sans hover:border-ink/[0.15] hover:text-ink/80 cursor-pointer transition-all"
                    >
                      {outlet}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
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
