'use client';

import { motion } from 'framer-motion';
import { User, Globe, Tag, Newspaper, RotateCcw, ChevronRight, Check } from 'lucide-react';
import { useStore } from '@/lib/store';
import { TOPICS } from './TopicFilter';

const REGIONS = [
  { id: 'all', label: 'Toda Latinoamérica', flag: '🌎' },
  { id: 'colombia', label: 'Colombia', flag: '🇨🇴' },
  { id: 'mexico', label: 'México', flag: '🇲🇽' },
  { id: 'argentina', label: 'Argentina', flag: '🇦🇷' },
];

export default function SettingsView() {
  const followedTopics = useStore((s) => s.followedTopics);
  const followedOutlets = useStore((s) => s.followedOutlets);
  const toggleFollowTopic = useStore((s) => s.toggleFollowTopic);
  const region = useStore((s) => s.region);
  const setRegion = useStore((s) => s.setRegion);
  const showSummariesByDefault = useStore((s) => s.showSummariesByDefault);
  const setShowSummariesByDefault = useStore((s) => s.setShowSummariesByDefault);
  const resetOnboarding = useStore((s) => s.resetOnboarding);
  const savedStories = useStore((s) => s.savedStories);

  const selectableTopics = TOPICS.filter((t) => t.id !== 'all');

  return (
    <div className="min-h-screen bg-base">
      {/* Header */}
      <div className="sticky top-0 z-30 bg-base/90 backdrop-blur-xl border-b paper-divider">
        <div className="px-4 sm:px-6 py-4">
          <h1 className="text-xl font-bold text-ink">Ajustes</h1>
        </div>
      </div>

      <div className="px-4 sm:px-6 py-6 space-y-8 pb-24">
        {/* Region */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-ink/40 font-sans mb-3 flex items-center gap-2">
            <Globe className="w-4 h-4" />
            Región
          </h2>
          <div className="grid grid-cols-2 gap-2">
            {REGIONS.map((r) => (
              <button
                key={r.id}
                onClick={() => setRegion(r.id)}
                className={`p-3 rounded-xl border text-left transition-all font-sans flex items-center gap-2.5 ${
                  region === r.id
                    ? 'border-ink bg-ink/[0.05]'
                    : 'border-ink/[0.08] bg-card hover:border-ink/[0.15]'
                }`}
              >
                <span className="text-lg">{r.flag}</span>
                <span className={`text-sm font-medium ${region === r.id ? 'text-ink' : 'text-ink/60'}`}>
                  {r.label}
                </span>
                {region === r.id && <Check className="w-4 h-4 text-ink ml-auto" />}
              </button>
            ))}
          </div>
        </section>

        {/* Followed Topics */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-ink/40 font-sans mb-3 flex items-center gap-2">
            <Tag className="w-4 h-4" />
            Temas que sigues ({followedTopics.length})
          </h2>
          <div className="flex flex-wrap gap-2">
            {selectableTopics.map((topic) => {
              const isFollowed = followedTopics.includes(topic.id);
              const Icon = topic.icon;
              return (
                <motion.button
                  key={topic.id}
                  onClick={() => toggleFollowTopic(topic.id)}
                  whileTap={{ scale: 0.95 }}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-full text-sm font-medium font-sans transition-all ${
                    isFollowed
                      ? 'bg-ink text-white'
                      : 'border border-ink/[0.10] text-ink/40 hover:text-ink/60 hover:border-ink/[0.20]'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {topic.label}
                </motion.button>
              );
            })}
          </div>
        </section>

        {/* Preferences */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-ink/40 font-sans mb-3">Preferencias</h2>
          <div className="space-y-1">
            <button
              onClick={() => setShowSummariesByDefault(!showSummariesByDefault)}
              className="w-full flex items-center justify-between p-3.5 rounded-xl border border-ink/[0.08] bg-card hover:border-ink/[0.15] transition-all"
            >
              <span className="text-sm text-ink font-sans">Mostrar resúmenes por defecto</span>
              <div className={`w-10 h-6 rounded-full transition-colors flex items-center ${
                showSummariesByDefault ? 'bg-ink justify-end' : 'bg-ink/[0.10] justify-start'
              }`}>
                <motion.div
                  layout
                  className={`w-5 h-5 rounded-full mx-0.5 ${
                    showSummariesByDefault ? 'bg-white' : 'bg-ink/20'
                  }`}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              </div>
            </button>
          </div>
        </section>

        {/* Stats */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-ink/40 font-sans mb-3">Tu actividad</h2>
          <div className="grid grid-cols-3 gap-2.5">
            <div className="p-3.5 rounded-xl bg-card border border-ink/[0.06] text-center">
              <span className="text-2xl font-bold text-ink block">{followedTopics.length}</span>
              <span className="text-[10px] text-ink/30 font-sans uppercase tracking-wider">Temas</span>
            </div>
            <div className="p-3.5 rounded-xl bg-card border border-ink/[0.06] text-center">
              <span className="text-2xl font-bold text-ink block">{followedOutlets.length}</span>
              <span className="text-[10px] text-ink/30 font-sans uppercase tracking-wider">Medios</span>
            </div>
            <div className="p-3.5 rounded-xl bg-card border border-ink/[0.06] text-center">
              <span className="text-2xl font-bold text-ink block">{savedStories.length}</span>
              <span className="text-[10px] text-ink/30 font-sans uppercase tracking-wider">Guardadas</span>
            </div>
          </div>
        </section>

        {/* Reset */}
        <section>
          <button
            onClick={resetOnboarding}
            className="w-full flex items-center gap-3 p-3.5 rounded-xl border border-ink/[0.08] bg-card hover:border-accent-warm/30 hover:bg-accent-warm/[0.03] transition-all group"
          >
            <RotateCcw className="w-4 h-4 text-ink/30 group-hover:text-accent-warm transition-colors" />
            <span className="text-sm text-ink/50 group-hover:text-accent-warm transition-colors font-sans">
              Repetir onboarding
            </span>
          </button>
        </section>
      </div>
    </div>
  );
}
