'use client';

import { motion } from 'framer-motion';
import { Flame, Clock, FileText, ArrowRight, Sparkles } from 'lucide-react';
import { Thread } from '@/lib/types';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface HeroCardProps {
  thread: Thread;
  number: number;
  onOpenDetail: () => void;
}

export default function HeroCard({ thread, number, onOpenDetail }: HeroCardProps) {
  const timeAgo = formatDistanceToNow(new Date(thread.created_at), {
    addSuffix: true,
    locale: es,
  });

  return (
    <motion.div
      key={thread.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="relative min-h-[420px] sm:min-h-[500px] lg:h-[600px] rounded-2xl overflow-hidden group"
    >
      {/* Background Image or Gradient */}
      {thread.image_url ? (
        <>
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${thread.image_url})` }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-navy-dark via-navy-dark/90 to-navy-dark/60" />
        </>
      ) : (
        <>
          <div className="absolute inset-0 bg-gradient-to-br from-navy-medium via-purple-accent/20 to-navy-dark" />
          <div className="absolute inset-0 bg-gradient-to-t from-navy-dark via-navy-dark/80 to-transparent" />
        </>
      )}

      {/* Content */}
      <div className="relative h-full flex flex-col justify-between p-5 sm:p-8 lg:p-12">
        {/* Top row */}
        <div className="flex justify-between items-start">
          <span className="text-6xl sm:text-8xl lg:text-9xl font-bold text-cyan opacity-15 select-none">
            {number.toString().padStart(2, '0')}
          </span>

          <motion.span
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="px-3 py-1.5 sm:px-4 sm:py-2 glass-effect rounded-full text-[10px] sm:text-xs font-semibold text-cyan border border-cyan/30 shrink-0"
          >
            TRENDING NOW
          </motion.span>
        </div>

        {/* Story Content */}
        <div className="space-y-4 sm:space-y-6">
          {/* Title ID */}
          <motion.div
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <span className="text-cyan text-base sm:text-xl font-mono">
              {thread.title_id}
            </span>
          </motion.div>

          {/* Main Title */}
          <motion.h2
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-2xl sm:text-4xl lg:text-5xl font-bold leading-tight"
          >
            {thread.display_title}
          </motion.h2>

          {/* Summary */}
          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-sm sm:text-lg text-gray-light line-clamp-2 sm:line-clamp-3 max-w-3xl"
          >
            {thread.summary}
          </motion.p>

          {/* Metrics - horizontal scroll on mobile */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="flex gap-3 sm:gap-6 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-hide"
          >
            <Metric
              icon={<Flame className="w-4 h-4 sm:w-5 sm:h-5" />}
              label="Viralidad"
              value={thread.trending_score.toFixed(1)}
            />
            <Metric
              icon={<Clock className="w-4 h-4 sm:w-5 sm:h-5" />}
              label="Publicado"
              value={timeAgo}
            />
            <Metric
              icon={<FileText className="w-4 h-4 sm:w-5 sm:h-5" />}
              label="Artículos"
              value={thread.article_count.toString()}
            />
          </motion.div>

          {/* Action Button */}
          <motion.button
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7 }}
            onClick={onOpenDetail}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="inline-flex items-center gap-2 sm:gap-3 px-6 sm:px-8 py-3 sm:py-4 bg-cyan text-navy-dark font-semibold rounded-full hover:bg-cyan-hover transition-colors animate-pulse-glow text-sm sm:text-base"
          >
            <Sparkles className="w-4 h-4 sm:w-5 sm:h-5" />
            <span>Explorar Historia</span>
            <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}

interface MetricProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function Metric({ icon, label, value }: MetricProps) {
  return (
    <div className="flex items-center gap-2 sm:gap-3 glass-effect px-3 sm:px-4 py-2 sm:py-3 rounded-lg shrink-0">
      <div className="text-cyan">{icon}</div>
      <div>
        <div className="text-[10px] sm:text-xs text-gray-medium">{label}</div>
        <div className="text-xs sm:text-sm font-semibold whitespace-nowrap">{value}</div>
      </div>
    </div>
  );
}
