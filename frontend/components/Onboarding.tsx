'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ChevronRight, Check, Sparkles, Newspaper, Globe, Zap } from 'lucide-react';
import { useStore } from '@/lib/store';
import { TOPICS } from './TopicFilter';

const SLIDES = [
  {
    icon: Sparkles,
    title: 'Tu información,\ncon contexto.',
    description: 'No más titulares sueltos. Cada historia viene con resumen, múltiples fuentes y contexto real.',
    accent: 'accent',
  },
  {
    icon: Globe,
    title: 'Toda Latinoamérica\nen un solo lugar.',
    description: 'Noticias de Colombia, México, Argentina y más. Filtradas por país, tema o tendencia.',
    accent: 'accent-blue',
  },
  {
    icon: Newspaper,
    title: 'Múltiples fuentes,\nuna sola historia.',
    description: 'Agrupamos artículos de diferentes medios para que veas el panorama completo.',
    accent: 'accent-warm',
  },
  {
    icon: Zap,
    title: 'Pregúntale\na Plural.',
    description: 'No entendiste algo? Pregúntale directamente a Plural sobre cualquier noticia.',
    accent: 'accent',
  },
];

const OUTLETS = [
  { id: 'el-tiempo', name: 'El Tiempo', country: '🇨🇴' },
  { id: 'semana', name: 'Semana', country: '🇨🇴' },
  { id: 'el-espectador', name: 'El Espectador', country: '🇨🇴' },
  { id: 'portafolio', name: 'Portafolio', country: '🇨🇴' },
  { id: 'infobae-mx', name: 'Infobae México', country: '🇲🇽' },
  { id: 'el-universal', name: 'El Universal', country: '🇲🇽' },
  { id: 'reforma', name: 'Reforma', country: '🇲🇽' },
  { id: 'la-nacion', name: 'La Nación', country: '🇦🇷' },
  { id: 'clarin', name: 'Clarín', country: '🇦🇷' },
  { id: 'infobae-ar', name: 'Infobae', country: '🇦🇷' },
  { id: 'bbc-mundo', name: 'BBC Mundo', country: '🌎' },
  { id: 'cnn-espanol', name: 'CNN en Español', country: '🌎' },
];

type Step = 'carousel' | 'topics' | 'outlets';

export default function Onboarding() {
  const [step, setStep] = useState<Step>('carousel');
  const [slideIndex, setSlideIndex] = useState(0);
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [selectedOutlets, setSelectedOutlets] = useState<string[]>([]);

  const completeOnboarding = useStore((s) => s.completeOnboarding);
  const setFollowedTopics = useStore((s) => s.setFollowedTopics);
  const setFollowedOutlets = useStore((s) => s.setFollowedOutlets);

  const handleSkip = () => {
    completeOnboarding();
  };

  const handleFinish = () => {
    setFollowedTopics(selectedTopics);
    setFollowedOutlets(selectedOutlets);
    completeOnboarding();
  };

  const toggleTopic = (id: string) => {
    setSelectedTopics((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );
  };

  const toggleOutlet = (id: string) => {
    setSelectedOutlets((prev) =>
      prev.includes(id) ? prev.filter((o) => o !== id) : [...prev, id]
    );
  };

  return (
    <div className="min-h-screen bg-base flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <AnimatePresence mode="wait">
          {step === 'carousel' && (
            <CarouselStep
              key="carousel"
              slideIndex={slideIndex}
              onNext={() => {
                if (slideIndex < SLIDES.length - 1) {
                  setSlideIndex(slideIndex + 1);
                } else {
                  setStep('topics');
                }
              }}
              onSkip={handleSkip}
              onSetSlide={setSlideIndex}
            />
          )}
          {step === 'topics' && (
            <TopicPickerStep
              key="topics"
              selected={selectedTopics}
              onToggle={toggleTopic}
              onNext={() => setStep('outlets')}
              onSkip={handleSkip}
            />
          )}
          {step === 'outlets' && (
            <OutletPickerStep
              key="outlets"
              selected={selectedOutlets}
              onToggle={toggleOutlet}
              onFinish={handleFinish}
              onSkip={handleSkip}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

/* ── Carousel Step ── */
function CarouselStep({
  slideIndex,
  onNext,
  onSkip,
  onSetSlide,
}: {
  slideIndex: number;
  onNext: () => void;
  onSkip: () => void;
  onSetSlide: (i: number) => void;
}) {
  const slide = SLIDES[slideIndex];
  const Icon = slide.icon;
  const isLast = slideIndex === SLIDES.length - 1;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="text-center"
    >
      {/* Logo */}
      <h1 className="text-2xl font-display font-extrabold text-gold tracking-tighter uppercase mb-12">
        plural
      </h1>

      {/* Slide content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={slideIndex}
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -40 }}
          transition={{ duration: 0.3 }}
          className="mb-10"
        >
          <div className={`w-16 h-16 rounded-2xl bg-${slide.accent}/15 flex items-center justify-center mx-auto mb-6`}>
            <Icon className={`w-8 h-8 text-${slide.accent}`} />
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold leading-tight text-ink whitespace-pre-line mb-4">
            {slide.title}
          </h2>
          <p className="text-ink-secondary text-base leading-relaxed font-sans max-w-sm mx-auto">
            {slide.description}
          </p>
        </motion.div>
      </AnimatePresence>

      {/* Dots */}
      <div className="flex items-center justify-center gap-2 mb-8">
        {SLIDES.map((_, i) => (
          <button
            key={i}
            onClick={() => onSetSlide(i)}
            className={`h-1.5 rounded-full transition-all duration-300 ${
              i === slideIndex ? 'w-6 bg-ink' : 'w-1.5 bg-ink/15'
            }`}
          />
        ))}
      </div>

      {/* Actions */}
      <div className="space-y-3">
        <button
          onClick={onNext}
          className="w-full py-3.5 px-6 bg-ink text-white rounded-xl font-semibold text-sm font-sans flex items-center justify-center gap-2 hover:bg-ink/85 transition-colors"
        >
          {isLast ? 'Elegir temas' : 'Siguiente'}
          <ChevronRight className="w-4 h-4" />
        </button>
        <button
          onClick={onSkip}
          className="w-full py-3 text-ink/40 text-sm font-sans hover:text-ink/60 transition-colors"
        >
          Entrar sin configurar
        </button>
      </div>
    </motion.div>
  );
}

/* ── Topic Picker Step ── */
function TopicPickerStep({
  selected,
  onToggle,
  onNext,
  onSkip,
}: {
  selected: string[];
  onToggle: (id: string) => void;
  onNext: () => void;
  onSkip: () => void;
}) {
  const selectableTopics = TOPICS.filter((t) => t.id !== 'all');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="text-center mb-8">
        <h2 className="text-2xl sm:text-3xl font-bold text-ink mb-2">
          Qué temas te interesan?
        </h2>
        <p className="text-ink-muted text-sm font-sans">
          Selecciona al menos 3 para personalizar tu feed.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-8">
        {selectableTopics.map((topic) => {
          const isSelected = selected.includes(topic.id);
          const Icon = topic.icon;
          return (
            <motion.button
              key={topic.id}
              onClick={() => onToggle(topic.id)}
              whileTap={{ scale: 0.95 }}
              className={`relative p-4 rounded-xl border text-left transition-all font-sans ${
                isSelected
                  ? 'border-ink bg-ink/[0.05]'
                  : 'border-ink/[0.08] bg-card hover:border-ink/[0.15]'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center transition-colors ${
                  isSelected ? 'bg-ink text-white' : 'bg-ink/[0.06] text-ink/40'
                }`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className={`text-sm font-medium transition-colors ${
                  isSelected ? 'text-ink' : 'text-ink/60'
                }`}>
                  {topic.label}
                </span>
              </div>
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-2 right-2 w-5 h-5 rounded-full bg-ink flex items-center justify-center"
                >
                  <Check className="w-3 h-3 text-white" />
                </motion.div>
              )}
            </motion.button>
          );
        })}
      </div>

      <div className="space-y-3">
        <button
          onClick={onNext}
          disabled={selected.length < 3}
          className="w-full py-3.5 px-6 bg-ink text-white rounded-xl font-semibold text-sm font-sans flex items-center justify-center gap-2 hover:bg-ink/85 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Siguiente
          <ArrowRight className="w-4 h-4" />
        </button>
        <button
          onClick={onSkip}
          className="w-full py-3 text-ink/40 text-sm font-sans hover:text-ink/60 transition-colors"
        >
          Saltar por ahora
        </button>
      </div>

      {/* Counter */}
      <p className="text-center text-ink/25 text-xs font-sans mt-4">
        {selected.length} seleccionado{selected.length !== 1 ? 's' : ''}
      </p>
    </motion.div>
  );
}

/* ── Outlet Picker Step ── */
function OutletPickerStep({
  selected,
  onToggle,
  onFinish,
  onSkip,
}: {
  selected: string[];
  onToggle: (id: string) => void;
  onFinish: () => void;
  onSkip: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="text-center mb-8">
        <h2 className="text-2xl sm:text-3xl font-bold text-ink mb-2">
          Qué medios sigues?
        </h2>
        <p className="text-ink-muted text-sm font-sans">
          Selecciona los medios que quieres ver en tu feed.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-2.5 mb-8 max-h-[50vh] overflow-y-auto pr-1">
        {OUTLETS.map((outlet) => {
          const isSelected = selected.includes(outlet.id);
          return (
            <motion.button
              key={outlet.id}
              onClick={() => onToggle(outlet.id)}
              whileTap={{ scale: 0.95 }}
              className={`relative p-3.5 rounded-xl border text-left transition-all font-sans ${
                isSelected
                  ? 'border-ink bg-ink/[0.05]'
                  : 'border-ink/[0.08] bg-card hover:border-ink/[0.15]'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span className="text-lg">{outlet.country}</span>
                <span className={`text-sm font-medium transition-colors truncate ${
                  isSelected ? 'text-ink' : 'text-ink/60'
                }`}>
                  {outlet.name}
                </span>
              </div>
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-2 right-2 w-5 h-5 rounded-full bg-ink flex items-center justify-center"
                >
                  <Check className="w-3 h-3 text-white" />
                </motion.div>
              )}
            </motion.button>
          );
        })}
      </div>

      <div className="space-y-3">
        <button
          onClick={onFinish}
          className="w-full py-3.5 px-6 bg-ink text-white rounded-xl font-semibold text-sm font-sans flex items-center justify-center gap-2 hover:bg-ink/85 transition-colors"
        >
          Comenzar
          <Sparkles className="w-4 h-4" />
        </button>
        <button
          onClick={onSkip}
          className="w-full py-3 text-ink/40 text-sm font-sans hover:text-ink/60 transition-colors"
        >
          Saltar por ahora
        </button>
      </div>

      <p className="text-center text-ink/25 text-xs font-sans mt-4">
        {selected.length} medio{selected.length !== 1 ? 's' : ''} seleccionado{selected.length !== 1 ? 's' : ''}
      </p>
    </motion.div>
  );
}
