'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Bookmark, Trash2, Clock, Share2 } from 'lucide-react';
import { useStore, SavedStory } from '@/lib/store';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

export default function SavedView() {
  const savedStories = useStore((s) => s.savedStories);
  const unsaveStory = useStore((s) => s.unsaveStory);

  const handleShare = async (story: SavedStory) => {
    const shareText = `${story.title}\n\nVía Plural`;
    const shareUrl = typeof window !== 'undefined' ? window.location.href : '';

    if (navigator.share) {
      try {
        await navigator.share({ title: story.title, text: shareText, url: shareUrl });
      } catch {}
    } else {
      const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(`${shareText}\n${shareUrl}`)}`;
      window.open(whatsappUrl, '_blank');
    }
  };

  return (
    <div className="min-h-screen bg-base">
      {/* Header */}
      <div className="sticky top-0 z-30 bg-base/90 backdrop-blur-xl border-b paper-divider">
        <div className="px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-ink">Guardado</h1>
            <span className="text-xs text-ink/30 font-sans">
              {savedStories.length} historia{savedStories.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      </div>

      <div className="px-4 sm:px-6 py-6 pb-24">
        {savedStories.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <div className="w-16 h-16 rounded-2xl bg-ink/[0.04] flex items-center justify-center mx-auto mb-4">
              <Bookmark className="w-7 h-7 text-ink/20" />
            </div>
            <h3 className="text-lg font-semibold text-ink/60 mb-1">Nada guardado aún</h3>
            <p className="text-sm text-ink/30 font-sans max-w-xs mx-auto">
              Guarda historias tocando el ícono de bookmark en cualquier card para leerlas después.
            </p>
          </motion.div>
        ) : (
          <div className="space-y-3">
            <AnimatePresence>
              {savedStories.map((story, i) => (
                <motion.div
                  key={story.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ delay: i * 0.03 }}
                  className="paper-card rounded-xl overflow-hidden"
                >
                  <div className="flex">
                    {/* Image */}
                    {story.image_url && (
                      <div className="w-24 sm:w-32 shrink-0 relative overflow-hidden">
                        <div
                          className="absolute inset-0 bg-cover bg-center"
                          style={{ backgroundImage: `url(${story.image_url})` }}
                        />
                      </div>
                    )}

                    {/* Content */}
                    <div className="flex-1 p-3.5 sm:p-4 flex flex-col justify-between min-w-0">
                      <div>
                        <h3 className="text-sm font-semibold text-ink leading-snug line-clamp-2 mb-1">
                          {story.title}
                        </h3>
                        <p className="text-xs text-ink-muted line-clamp-1 font-sans">
                          {story.summary}
                        </p>
                      </div>
                      <div className="flex items-center justify-between mt-2.5">
                        <div className="flex items-center gap-1 text-[10px] text-ink/30 font-sans">
                          <Clock className="w-3 h-3" />
                          <span>
                            Guardada {formatDistanceToNow(new Date(story.saved_at), {
                              addSuffix: true,
                              locale: es,
                            })}
                          </span>
                        </div>
                        <div className="flex items-center gap-0.5">
                          <button
                            onClick={() => handleShare(story)}
                            className="p-1.5 rounded-md hover:bg-ink/[0.06] transition-colors text-ink/25 hover:text-ink/50"
                            aria-label="Compartir"
                          >
                            <Share2 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => unsaveStory(story.id)}
                            className="p-1.5 rounded-md hover:bg-accent-warm/10 transition-colors text-ink/25 hover:text-accent-warm"
                            aria-label="Eliminar de guardados"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}
