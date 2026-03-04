'use client';

import { motion } from 'framer-motion';
import { Flame, Clock, ArrowRight, Newspaper, Bookmark, Share2 } from 'lucide-react';
import { Thread } from '@/lib/types';
import { useStore } from '@/lib/store';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { getThreadColor } from './TopicFilter';

// Thin bar color only — no backgrounds
const COLOR_BAR: Record<string, string> = {
  yellow: 'bg-accent',
  coral: 'bg-accent-warm',
  blue: 'bg-accent-blue',
};

// Gradient fallbacks when thread has no image
const HERO_GRADIENT: Record<string, string> = {
  yellow: 'from-accent/20 via-accent/5 to-base',
  coral: 'from-accent-warm/20 via-accent-warm/5 to-base',
  blue: 'from-accent-blue/25 via-accent-blue/5 to-base',
};

interface FeedCardProps {
  thread: Thread;
  index: number;
  isHero?: boolean;
  onOpenDetail: () => void;
}

function ShareButton({ thread, className }: { thread: Thread; className?: string }) {
  const handleShare = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const shareText = `${thread.display_title}\n\nVía Plural`;
    const shareUrl = typeof window !== 'undefined' ? `${window.location.origin}/?thread=${thread.id}` : '';

    if (navigator.share) {
      try {
        await navigator.share({ title: thread.display_title, text: shareText, url: shareUrl });
      } catch {}
    } else {
      const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(`${shareText}\n${shareUrl}`)}`;
      window.open(whatsappUrl, '_blank');
    }
  };

  return (
    <button
      onClick={handleShare}
      className={`p-2 rounded-lg hover:bg-ink/[0.06] transition-colors ${className || ''}`}
      aria-label="Compartir"
    >
      <Share2 className="w-4 h-4" />
    </button>
  );
}

function SaveButton({ thread, className }: { thread: Thread; className?: string }) {
  const savedStories = useStore((s) => s.savedStories);
  const saveStory = useStore((s) => s.saveStory);
  const unsaveStory = useStore((s) => s.unsaveStory);
  const isSaved = savedStories.some((s) => s.id === thread.id);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isSaved) {
      unsaveStory(thread.id);
    } else {
      saveStory({
        id: thread.id,
        title: thread.display_title,
        summary: thread.summary,
        image_url: thread.image_url,
        saved_at: new Date().toISOString(),
      });
    }
  };

  return (
    <motion.button
      onClick={handleToggle}
      whileTap={{ scale: 0.85 }}
      className={`p-2 rounded-lg hover:bg-ink/[0.06] transition-colors ${className || ''}`}
      aria-label={isSaved ? 'Quitar de guardados' : 'Guardar historia'}
    >
      <Bookmark className={`w-4 h-4 transition-colors ${isSaved ? 'fill-accent text-accent' : ''}`} />
    </motion.button>
  );
}

export default function FeedCard({ thread, index, isHero = false, onOpenDetail }: FeedCardProps) {
  const timeAgo = formatDistanceToNow(new Date(thread.created_at), {
    addSuffix: true,
    locale: es,
  });

  if (isHero) {
    return <HeroVariant thread={thread} index={index} timeAgo={timeAgo} onOpenDetail={onOpenDetail} />;
  }

  return <StoryVariant thread={thread} index={index} timeAgo={timeAgo} onOpenDetail={onOpenDetail} />;
}

/* ── Hero: first card, full cinematic treatment ── */
function HeroVariant({
  thread, index, timeAgo, onOpenDetail,
}: {
  thread: Thread; index: number; timeAgo: string; onOpenDetail: () => void;
}) {
  const color = getThreadColor(thread.display_title, thread.summary);

  return (
    <motion.article
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative min-h-[400px] sm:min-h-[480px] lg:min-h-[520px] rounded-2xl overflow-hidden group cursor-pointer"
      onClick={onOpenDetail}
    >
      {/* Background */}
      {thread.image_url ? (
        <>
          <div
            className="absolute inset-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-105"
            style={{ backgroundImage: `url(${thread.image_url})` }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/60 to-black/20" />
        </>
      ) : (
        <>
          <div className={`absolute inset-0 bg-gradient-to-br ${HERO_GRADIENT[color]}`} />
        </>
      )}

      {/* Thin color accent bar at bottom */}
      <div className={`absolute bottom-0 left-0 right-0 h-1 ${COLOR_BAR[color]}`} />

      {/* Content */}
      <div className="relative h-full flex flex-col justify-between p-5 sm:p-8 lg:p-10">
        {/* Top */}
        <div className="flex justify-between items-start">
          <span className={`text-6xl sm:text-7xl lg:text-8xl font-bold select-none leading-none font-sans ${
            thread.image_url ? 'text-white/[0.08]' : 'text-ink/[0.06]'
          }`}>
            {(index + 1).toString().padStart(2, '0')}
          </span>
          <div className="flex items-center gap-1">
            <span className="px-3 py-1.5 rounded-full text-[10px] font-semibold uppercase tracking-widest font-sans bg-ink/[0.06] text-ink/50 backdrop-blur-sm">
              Trending
            </span>
            <SaveButton thread={thread} className={thread.image_url ? 'text-white/50 hover:text-white hover:bg-white/10' : 'text-ink/30 hover:text-ink'} />
            <ShareButton thread={thread} className={thread.image_url ? 'text-white/50 hover:text-white hover:bg-white/10' : 'text-ink/30 hover:text-ink'} />
          </div>
        </div>

        {/* Bottom content */}
        <div className="space-y-4">
          <span className={`text-sm font-sans tracking-wide ${
            thread.image_url ? 'text-white/50' : 'text-ink/40'
          }`}>{thread.title_id}</span>

          <h2 className={`text-2xl sm:text-3xl lg:text-4xl font-bold leading-tight max-w-2xl ${
            thread.image_url ? 'text-white' : 'text-ink'
          }`}>
            {thread.display_title}
          </h2>

          <p className={`text-sm sm:text-base line-clamp-3 max-w-2xl leading-relaxed font-sans ${
            thread.image_url ? 'text-white/70' : 'text-ink-secondary'
          }`}>
            {thread.summary}
          </p>

          <div className="flex items-center gap-4 pt-1">
            <div className={`flex items-center gap-1.5 text-xs tracking-wide font-sans ${
              thread.image_url ? 'text-white/40' : 'text-ink/35'
            }`}>
              <Flame className="w-3.5 h-3.5" />
              <span>{thread.trending_score.toFixed(1)}</span>
            </div>
            <div className={`flex items-center gap-1.5 text-xs tracking-wide font-sans ${
              thread.image_url ? 'text-white/40' : 'text-ink/35'
            }`}>
              <Newspaper className="w-3.5 h-3.5" />
              <span>{thread.article_count} fuentes</span>
            </div>
            <div className={`flex items-center gap-1.5 text-xs tracking-wide font-sans ${
              thread.image_url ? 'text-white/40' : 'text-ink/35'
            }`}>
              <Clock className="w-3.5 h-3.5" />
              <span>{timeAgo}</span>
            </div>
          </div>

          <button
            onClick={(e) => { e.stopPropagation(); onOpenDetail(); }}
            className={`inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold rounded-full transition-all group/btn font-sans ${
              thread.image_url
                ? 'bg-white text-ink hover:bg-accent'
                : 'bg-ink text-white hover:bg-ink/80'
            }`}
          >
            Explorar Historia
            <ArrowRight className="w-4 h-4 transition-transform group-hover/btn:translate-x-0.5" />
          </button>
        </div>
      </div>
    </motion.article>
  );
}

/* ── Story: subsequent cards, editorial newspaper style ── */
function StoryVariant({
  thread, index, timeAgo, onOpenDetail,
}: {
  thread: Thread; index: number; timeAgo: string; onOpenDetail: () => void;
}) {
  const color = getThreadColor(thread.display_title, thread.summary);

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.4, delay: 0.05 }}
      onClick={onOpenDetail}
      className="group cursor-pointer rounded-xl overflow-hidden paper-card hover:border-ink/[0.12] hover:bg-card transition-all duration-300"
    >
      <div className="flex flex-col sm:flex-row">
        {/* Thin color accent bar (left on desktop, top on mobile) */}
        <div className={`h-1 sm:h-auto sm:w-1 shrink-0 ${COLOR_BAR[color]}`} />

        {/* Image side */}
        {thread.image_url && (
          <div className="sm:w-[240px] lg:w-[280px] shrink-0 h-[180px] sm:h-auto relative overflow-hidden">
            <div
              className="absolute inset-0 bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
              style={{ backgroundImage: `url(${thread.image_url})` }}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/20 hidden sm:block" />
            <div className="absolute inset-0 bg-gradient-to-t from-white/30 to-transparent sm:hidden" />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 p-4 sm:p-5 lg:p-6 flex flex-col justify-between min-h-[160px]">
          <div className="space-y-2.5">
            {/* Top meta row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl font-bold text-ink/[0.08] leading-none select-none font-sans">
                  {(index + 1).toString().padStart(2, '0')}
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-ink/35 font-sans">
                  {thread.title_id}
                </span>
              </div>
              {/* Action buttons */}
              <div className="flex items-center gap-0.5" onClick={(e) => e.stopPropagation()}>
                <SaveButton thread={thread} className="text-ink/25 hover:text-ink/60" />
                <ShareButton thread={thread} className="text-ink/25 hover:text-ink/60" />
              </div>
            </div>

            {/* Title */}
            <h3 className="text-lg sm:text-xl font-bold leading-snug text-ink group-hover:text-ink/70 transition-colors">
              {thread.display_title}
            </h3>

            {/* Summary */}
            <p className="text-sm text-ink-muted line-clamp-2 leading-relaxed font-sans">
              {thread.summary}
            </p>
          </div>

          {/* Bottom metrics */}
          <div className="flex items-center justify-between mt-4 pt-3 border-t paper-divider">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-xs text-ink/35 font-sans">
                <Flame className="w-3 h-3" />
                <span>{thread.trending_score.toFixed(1)}</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-ink/35 font-sans">
                <Newspaper className="w-3 h-3" />
                <span>{thread.article_count} fuentes</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-ink/35 font-sans">
                <Clock className="w-3 h-3" />
                <span>{timeAgo}</span>
              </div>
            </div>

            <ArrowRight className="w-4 h-4 text-ink/20 group-hover:text-ink/50 transition-all group-hover:translate-x-0.5" />
          </div>
        </div>
      </div>
    </motion.article>
  );
}
