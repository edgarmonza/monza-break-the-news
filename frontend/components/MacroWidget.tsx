'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { MacroIndicator } from '@/lib/types';
import { motion } from 'framer-motion';
import {
  DollarSign, Euro, Fuel, Landmark, TrendingUp, TrendingDown,
  Coffee, Bitcoin, Minus, Activity
} from 'lucide-react';

const ICON_MAP: Record<string, React.ElementType> = {
  dollar: DollarSign,
  euro: Euro,
  fuel: Fuel,
  landmark: Landmark,
  'trending-up': TrendingUp,
  coffee: Coffee,
  bitcoin: Bitcoin,
};

export default function MacroWidget() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['macro'],
    queryFn: () => api.getMacro(),
    refetchInterval: 5 * 60 * 1000,
  });

  if (isLoading) {
    return (
      <div className="space-y-0">
        <WidgetHeader />
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-[52px] border-b border-ink/[0.05] animate-pulse" />
        ))}
      </div>
    );
  }

  if (error || !data) return null;

  return (
    <div>
      <WidgetHeader />

      {/* Desktop: clean vertical list */}
      <div className="hidden xl:block">
        {data.indicators.map((indicator, i) => (
          <IndicatorRow key={indicator.id} indicator={indicator} index={i} isLast={i === data.indicators.length - 1} />
        ))}
      </div>

      {/* Mobile: horizontal ticker strip */}
      <div className="xl:hidden flex gap-4 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
        {data.indicators.map((indicator, i) => (
          <IndicatorChip key={indicator.id} indicator={indicator} index={i} />
        ))}
      </div>
    </div>
  );
}

function WidgetHeader() {
  return (
    <div className="flex items-center gap-2 mb-3 xl:mb-0 xl:px-0 xl:py-3 xl:border-b xl:border-ink/[0.06]">
      <Activity className="w-3.5 h-3.5 text-ink/40" />
      <span className="text-[11px] font-medium text-ink/30 uppercase tracking-[0.2em] font-sans">
        Mercados
      </span>
      <div className="flex-1" />
      <span className="flex items-center gap-1.5 text-[10px] text-ink/25 font-sans">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
        En vivo
      </span>
    </div>
  );
}

/* ── Desktop: minimal row style ── */
function IndicatorRow({
  indicator, index, isLast,
}: {
  indicator: MacroIndicator; index: number; isLast: boolean;
}) {
  const Icon = ICON_MAP[indicator.icon] || TrendingUp;
  const hasChange = indicator.change !== null && indicator.change !== undefined;
  const isPositive = hasChange && (indicator.change ?? 0) > 0;
  const isNegative = hasChange && (indicator.change ?? 0) < 0;

  return (
    <motion.div
      initial={{ opacity: 0, x: 10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.04 }}
      className={`flex items-center gap-3 py-3 ${!isLast ? 'border-b border-ink/[0.05]' : ''} group hover:bg-ink/[0.03] transition-colors -mx-2 px-2 rounded`}
    >
      {/* Icon */}
      <div className="w-6 h-6 rounded-md flex items-center justify-center text-ink/40">
        <Icon className="w-3.5 h-3.5" />
      </div>

      {/* Label */}
      <span className="text-xs text-ink/35 flex-1 min-w-0 truncate font-sans">
        {indicator.label}
      </span>

      {/* Value */}
      <span className="text-sm font-semibold tracking-tight tabular-nums font-sans text-ink">
        {indicator.formatted}
      </span>

      {/* Change badge */}
      {hasChange && (
        <div className={`flex items-center gap-0.5 min-w-[52px] justify-end text-[10px] font-medium tabular-nums font-sans ${
          isPositive ? 'text-emerald-600' :
          isNegative ? 'text-red-500' :
          'text-ink/25'
        }`}>
          {isPositive ? (
            <TrendingUp className="w-2.5 h-2.5" />
          ) : isNegative ? (
            <TrendingDown className="w-2.5 h-2.5" />
          ) : (
            <Minus className="w-2.5 h-2.5" />
          )}
          <span>{isPositive ? '+' : ''}{(indicator.change_pct ?? 0).toFixed(1)}%</span>
        </div>
      )}
    </motion.div>
  );
}

/* ── Mobile: compact chip for horizontal scroll ── */
function IndicatorChip({ indicator, index }: { indicator: MacroIndicator; index: number }) {
  const hasChange = indicator.change !== null && indicator.change !== undefined;
  const isPositive = hasChange && (indicator.change ?? 0) > 0;
  const isNegative = hasChange && (indicator.change ?? 0) < 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
      className="shrink-0 flex items-center gap-2 px-3 py-2 rounded-lg bg-ink/[0.03] border border-ink/[0.06]"
    >
      <span className="text-[11px] text-ink/35 whitespace-nowrap font-sans">{indicator.label}</span>
      <span className="text-xs font-semibold tabular-nums whitespace-nowrap font-sans text-ink">{indicator.formatted}</span>
      {hasChange && (
        <span className={`text-[10px] font-medium tabular-nums whitespace-nowrap font-sans ${
          isPositive ? 'text-emerald-600' : isNegative ? 'text-red-500' : 'text-ink/25'
        }`}>
          {isPositive ? '+' : ''}{(indicator.change_pct ?? 0).toFixed(1)}%
        </span>
      )}
    </motion.div>
  );
}
