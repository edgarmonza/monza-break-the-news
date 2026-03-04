'use client';

import { useState, useEffect, useRef } from 'react';
import { Menu, X, Search, ArrowRight, Globe } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const PLACEHOLDER_PHRASES = [
  'Pregúntale lo que sea a Plural',
  '¿Qué está pasando con el dólar en Colombia?',
  'Resúmeme las noticias de México hoy',
  '¿Por qué subió el petróleo?',
  '¿Qué pasa con la economía en Argentina?',
];

interface HeaderProps {
  onToggleMobileMenu?: () => void;
  isMobileMenuOpen?: boolean;
  onChatSubmit?: (question: string) => void;
  countryFilter?: React.ReactNode;
}

export default function Header({ onToggleMobileMenu, isMobileMenuOpen, onChatSubmit, countryFilter }: HeaderProps) {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const mobileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && onChatSubmit) {
      onChatSubmit(query.trim());
      setQuery('');
      setMobileSearchOpen(false);
      inputRef.current?.blur();
    }
  };

  useEffect(() => {
    if (mobileSearchOpen) {
      setTimeout(() => mobileInputRef.current?.focus(), 100);
    }
  }, [mobileSearchOpen]);

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="sticky top-0 z-50"
    >
      {/* ── Tricolor bar (numenu signature) ── */}
      <div className="flex h-[3px]">
        <div className="flex-1 bg-accent" />
        <div className="flex-1 bg-accent-blue" />
        <div className="flex-1 bg-accent-warm" />
      </div>

      <div className="bg-base/90 backdrop-blur-xl border-b paper-divider">
      <div className="max-w-[1920px] mx-auto px-4 sm:px-6">
        <div className="flex items-center h-14 gap-3 lg:gap-5">

          {/* ── Logo ── */}
          <div className="flex items-center gap-2 shrink-0">
            {/* Mobile menu toggle */}
            <button
              onClick={onToggleMobileMenu}
              className="p-1.5 -ml-1.5 hover:bg-ink/5 rounded-lg transition-colors lg:hidden"
              aria-label={isMobileMenuOpen ? 'Cerrar menú' : 'Abrir menú'}
            >
              <AnimatePresence mode="wait">
                {isMobileMenuOpen ? (
                  <motion.div key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.15 }}>
                    <X className="w-5 h-5 text-ink" />
                  </motion.div>
                ) : (
                  <motion.div key="menu" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.15 }}>
                    <Menu className="w-5 h-5 text-ink" />
                  </motion.div>
                )}
              </AnimatePresence>
            </button>

            <h1 className="text-lg lg:text-xl font-display font-extrabold text-gold tracking-tighter leading-none uppercase">
              plural
            </h1>
            <span className="hidden lg:inline text-ink/20 text-[9px] font-medium tracking-[0.15em] uppercase font-sans mt-0.5">
              news.
            </span>
          </div>

          {/* ── Search bar (desktop) ── */}
          <div className="hidden lg:block flex-1 max-w-[480px]">
            <form onSubmit={handleSubmit} className="relative">
              <div className={`flex items-center gap-2.5 px-3.5 py-[7px] rounded-lg border transition-all duration-200 ${
                isFocused
                  ? 'border-accent/40 bg-ink/[0.04]'
                  : 'border-ink/[0.08] bg-ink/[0.03] hover:border-ink/[0.12]'
              }`}>
                <Search className={`w-3.5 h-3.5 shrink-0 transition-colors ${isFocused ? 'text-ink/50' : 'text-ink/25'}`} />
                <div className="relative flex-1">
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    className="w-full bg-transparent text-[13px] text-ink font-sans outline-none placeholder:text-transparent"
                    placeholder="Pregúntale a Plural..."
                  />
                  {!query && !isFocused && (
                    <TypingPlaceholder phrases={PLACEHOLDER_PHRASES} />
                  )}
                  {!query && isFocused && (
                    <span className="absolute inset-0 text-[13px] text-ink/20 font-sans pointer-events-none">
                      Pregúntale a Plural...
                    </span>
                  )}
                </div>
                <AnimatePresence>
                  {query.trim() && (
                    <motion.button
                      type="submit"
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      exit={{ scale: 0, opacity: 0 }}
                      className="p-0.5 rounded bg-accent/20 hover:bg-accent/30 transition-colors"
                    >
                      <ArrowRight className="w-3 h-3 text-ink/50" />
                    </motion.button>
                  )}
                </AnimatePresence>
              </div>
            </form>
          </div>

          {/* ── Country filter (desktop, inline) ── */}
          <div className="hidden lg:flex items-center shrink-0">
            {countryFilter}
          </div>

          {/* ── Spacer ── */}
          <div className="flex-1 lg:hidden" />

          {/* ── Right actions ── */}
          <div className="flex items-center gap-1 lg:gap-2 shrink-0 ml-auto">
            {/* Mobile search */}
            <button
              onClick={() => setMobileSearchOpen(!mobileSearchOpen)}
              className="p-2 hover:bg-ink/5 rounded-lg transition-colors lg:hidden"
            >
              <Search className="w-4.5 h-4.5 text-ink-muted" />
            </button>

            {/* Language pill */}
            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-ink/30 hover:text-ink-muted hover:bg-ink/[0.04] transition-colors cursor-default">
              <Globe className="w-3.5 h-3.5" />
              <span className="text-[11px] font-medium font-sans uppercase tracking-wider">ES</span>
            </div>

            {/* Sign In */}
            <button className="hidden sm:flex items-center px-4 py-1.5 rounded-lg border border-ink/20 text-ink text-[12px] font-semibold font-sans uppercase tracking-wider hover:bg-ink/5 hover:border-ink/30 transition-all">
              Sign In
            </button>

            {/* Menu button */}
            <button
              onClick={onToggleMobileMenu}
              className="hidden lg:flex items-center gap-2 pl-3 pr-2 py-1.5 rounded-lg hover:bg-ink/[0.04] transition-colors ml-1"
            >
              <span className="text-[11px] font-medium text-ink-muted font-sans uppercase tracking-wider">Menu</span>
              <Menu className="w-4 h-4 text-ink-muted" />
            </button>
          </div>
        </div>

        {/* ── Mobile search bar (expandable) ── */}
        <AnimatePresence>
          {mobileSearchOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden lg:hidden"
            >
              <form onSubmit={handleSubmit} className="pb-3">
                <div className="flex items-center gap-3 px-3.5 py-2.5 rounded-lg border border-ink/[0.10] bg-ink/[0.04]">
                  <Search className="w-4 h-4 text-ink/50 shrink-0" />
                  <input
                    ref={mobileInputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Pregúntale a Plural..."
                    className="flex-1 bg-transparent text-sm text-ink font-sans outline-none placeholder:text-ink/25"
                  />
                  {query.trim() && (
                    <button type="submit" className="p-1.5 rounded bg-accent/20">
                      <ArrowRight className="w-3.5 h-3.5 text-ink/50" />
                    </button>
                  )}
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      </div>
    </motion.header>
  );
}

/* ── Typing placeholder animation ── */
function TypingPlaceholder({ phrases }: { phrases: string[] }) {
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  const currentPhrase = phrases[phraseIndex];
  const displayText = currentPhrase.slice(0, charIndex);

  useEffect(() => {
    const speed = isDeleting ? 25 : 45;
    const pauseAfterType = 2500;
    const pauseAfterDelete = 300;

    if (!isDeleting && charIndex === currentPhrase.length) {
      const timeout = setTimeout(() => setIsDeleting(true), pauseAfterType);
      return () => clearTimeout(timeout);
    }

    if (isDeleting && charIndex === 0) {
      const timeout = setTimeout(() => {
        setIsDeleting(false);
        setPhraseIndex((prev) => (prev + 1) % phrases.length);
      }, pauseAfterDelete);
      return () => clearTimeout(timeout);
    }

    const timeout = setTimeout(() => {
      setCharIndex((prev) => prev + (isDeleting ? -1 : 1));
    }, speed);

    return () => clearTimeout(timeout);
  }, [charIndex, isDeleting, currentPhrase, phrases]);

  return (
    <span className="absolute inset-0 text-[13px] text-ink/25 font-sans pointer-events-none flex items-center">
      {displayText}
      <motion.span
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.6, repeat: Infinity, repeatType: 'reverse' }}
        className="inline-block w-[1px] h-3.5 bg-ink/30 ml-[1px]"
      />
    </span>
  );
}
