'use client';

import { Sparkles, Menu, X, User, Bell } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface HeaderProps {
  onToggleMobileMenu?: () => void;
  isMobileMenuOpen?: boolean;
}

export default function Header({ onToggleMobileMenu, isMobileMenuOpen }: HeaderProps) {
  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="sticky top-0 z-50 glass-effect border-b border-white/10"
    >
      <div className="max-w-[1920px] mx-auto px-4 sm:px-6 py-3 sm:py-4">
        <div className="flex items-center justify-between">
          {/* Left: Menu + Logo */}
          <div className="flex items-center gap-3">
            <button
              onClick={onToggleMobileMenu}
              className="p-2 -ml-2 hover:bg-white/5 rounded-lg transition-colors lg:hidden"
              aria-label={isMobileMenuOpen ? 'Cerrar menú' : 'Abrir menú'}
            >
              <AnimatePresence mode="wait">
                {isMobileMenuOpen ? (
                  <motion.div key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.15 }}>
                    <X className="w-6 h-6" />
                  </motion.div>
                ) : (
                  <motion.div key="menu" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.15 }}>
                    <Menu className="w-6 h-6" />
                  </motion.div>
                )}
              </AnimatePresence>
            </button>

            <div className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 sm:w-8 sm:h-8 text-cyan" />
              <h1 className="text-lg sm:text-2xl font-bold gradient-text">
                Colombia News
              </h1>
            </div>
          </div>

          {/* Center: CTA (desktop only) */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="hidden lg:flex items-center gap-3 px-6 py-3 glass-effect rounded-full hover:border-cyan/30 transition-all group"
          >
            <span className="gradient-text text-sm font-medium">
              Pregunta sobre las noticias de hoy
            </span>
            <motion.div
              animate={{ x: [0, 4, 0] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              <Sparkles className="w-4 h-4 text-cyan" />
            </motion.div>
          </motion.button>

          {/* Right: Actions */}
          <div className="flex items-center gap-1 sm:gap-3">
            <button className="relative p-2 hover:bg-white/5 rounded-lg transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-magenta rounded-full animate-pulse" />
            </button>
            <button className="p-2 hover:bg-white/5 rounded-lg transition-colors hidden sm:block">
              <User className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
