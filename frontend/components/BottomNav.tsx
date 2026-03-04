'use client';

import { Home, Compass, Bookmark, Settings } from 'lucide-react';
import { motion } from 'framer-motion';
import { useStore } from '@/lib/store';

export type TabId = 'home' | 'explore' | 'saved' | 'settings';

const TABS: Array<{ id: TabId; label: string; icon: typeof Home }> = [
  { id: 'home', label: 'Inicio', icon: Home },
  { id: 'explore', label: 'Explorar', icon: Compass },
  { id: 'saved', label: 'Guardado', icon: Bookmark },
  { id: 'settings', label: 'Ajustes', icon: Settings },
];

interface BottomNavProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

export default function BottomNav({ activeTab, onTabChange }: BottomNavProps) {
  const savedCount = useStore((s) => s.savedStories.length);

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 lg:hidden">
      <div className="bg-base/90 backdrop-blur-xl border-t paper-divider pb-[env(safe-area-inset-bottom,0px)]">
        <div className="flex items-center justify-around h-14">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            const Icon = tab.icon;

            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className="relative flex flex-col items-center justify-center gap-0.5 w-full h-full transition-colors"
              >
                <div className="relative">
                  <Icon
                    className={`w-5 h-5 transition-colors ${
                      isActive ? 'text-ink' : 'text-ink/30'
                    }`}
                  />
                  {/* Badge for saved count */}
                  {tab.id === 'saved' && savedCount > 0 && (
                    <span className="absolute -top-1.5 -right-2 min-w-[16px] h-4 px-1 rounded-full bg-accent-warm text-white text-[9px] font-bold flex items-center justify-center font-sans">
                      {savedCount > 99 ? '99+' : savedCount}
                    </span>
                  )}
                </div>
                <span
                  className={`text-[10px] font-medium font-sans transition-colors ${
                    isActive ? 'text-ink' : 'text-ink/30'
                  }`}
                >
                  {tab.label}
                </span>
                {isActive && (
                  <motion.div
                    layoutId="tab-indicator"
                    className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-ink rounded-full"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
