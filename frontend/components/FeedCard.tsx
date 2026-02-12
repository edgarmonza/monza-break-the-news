'use client';

import { motion } from 'framer-motion';
import { Flame, Clock, FileText, ArrowRight, Sparkles, Newspaper } from 'lucide-react';
import { Thread } from '@/lib/types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface FeedCardProps {
  thread: Thread;
  index: number;
  isHero?: boolean;
  onOpenDetail: () => void;
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
          <div className="absolute inset-0 bg-gradient-to-t from-navy-dark via-navy-dark/85 to-navy-dark/40" />
        </>
      ) : (
        <>
          <div className="absolute inset-0 bg-gradient-to-br from-navy-medium via-purple-accent/20 to-navy-dark" />
          <div className="absolute inset-0 bg-gradient-to-t from-navy-dark via-navy-dark/80 to-transparent" />
        </>
      )}

      {/* Content */}
      <div className="relative h-full flex flex-col justify-between p-5 sm:p-8 lg:p-10">
        {/* Top */}
        <div className="flex justify-between items-start">
          <span className="text-6xl sm:text-7xl lg:text-8xl font-bold text-cyan/10 select-none leading-none">
            {(index + 1).toString().padStart(2, '0')}
          </span>
          <span className="px-3 py-1.5 glass-effect rounded-full text-[10px] font-semibold text-cyan border border-cyan/20 uppercase tracking-widest">
            Trending
          </span>
        </div>

        {/* Bottom content */}
        <div className="space-y-4">
          <span className="text-cyan/80 text-sm font-mono">{thread.title_id}</span>

          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold leading-tight max-w-2xl">
            {thread.display_title}
          </h2>

          <p className="text-sm sm:text-base text-gray-light/80 line-clamp-2 max-w-2xl leading-relaxed">
            {thread.summary}
          </p>

          <div className="flex items-center gap-4 pt-1">
            <div className="flex items-center gap-1.5 text-xs text-gray-medium">
              <Flame className="w-3.5 h-3.5 text-cyan/70" />
              <span>{thread.trending_score.toFixed(1)}</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-gray-medium">
              <Newspaper className="w-3.5 h-3.5 text-cyan/70" />
              <span>{thread.article_count} fuentes</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-gray-medium">
              <Clock className="w-3.5 h-3.5 text-cyan/70" />
              <span>{timeAgo}</span>
            </div>
          </div>

          <button
            onClick={(e) => { e.stopPropagation(); onOpenDetail(); }}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-cyan text-navy-dark text-sm font-semibold rounded-full hover:bg-cyan-hover transition-all group/btn"
          >
            <Sparkles className="w-4 h-4" />
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
  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.4, delay: 0.05 }}
      onClick={onOpenDetail}
      className="group cursor-pointer rounded-xl overflow-hidden border border-white/[0.06] hover:border-cyan/20 bg-white/[0.02] hover:bg-white/[0.04] transition-all duration-300"
    >
      <div className="flex flex-col sm:flex-row">
        {/* Image side */}
        {thread.image_url && (
          <div className="sm:w-[240px] lg:w-[280px] shrink-0 h-[180px] sm:h-auto relative overflow-hidden">
            <div
              className="absolute inset-0 bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
              style={{ backgroundImage: `url(${thread.image_url})` }}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-transparent to-navy-dark/30 hidden sm:block" />
            <div className="absolute inset-0 bg-gradient-to-t from-navy-dark/40 to-transparent sm:hidden" />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 p-4 sm:p-5 lg:p-6 flex flex-col justify-between min-h-[160px]">
          <div className="space-y-2.5">
            {/* Top meta row */}
            <div className="flex items-center gap-3">
              <span className="text-2xl font-bold text-cyan/15 leading-none select-none">
                {(index + 1).toString().padStart(2, '0')}
              </span>
              <span className="text-cyan/60 text-xs font-mono">{thread.title_id}</span>
            </div>

            {/* Title */}
            <h3 className="text-lg sm:text-xl font-bold leading-snug group-hover:text-cyan/90 transition-colors">
              {thread.display_title}
            </h3>

            {/* Summary */}
            <p className="text-sm text-gray-medium line-clamp-2 leading-relaxed">
              {thread.summary}
            </p>
          </div>

          {/* Bottom metrics */}
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-white/[0.05]">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-xs text-gray-medium">
                <Flame className="w-3 h-3 text-cyan/50" />
                <span>{thread.trending_score.toFixed(1)}</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-gray-medium">
                <Newspaper className="w-3 h-3 text-cyan/50" />
                <span>{thread.article_count} fuentes</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-gray-medium">
                <Clock className="w-3 h-3 text-cyan/50" />
                <span>{timeAgo}</span>
              </div>
            </div>

            <ArrowRight className="w-4 h-4 text-gray-medium group-hover:text-cyan transition-all group-hover:translate-x-0.5" />
          </div>
        </div>
      </div>
    </motion.article>
  );
}
