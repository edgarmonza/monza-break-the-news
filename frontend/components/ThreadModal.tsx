'use client';

import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import { useState, useRef, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { X, Send, Sparkles, ExternalLink, MessageCircle, ChevronLeft, Bookmark, Share2 } from 'lucide-react';

interface ThreadModalProps {
  threadId: string;
  onClose: () => void;
}

export default function ThreadModal({ threadId, onClose }: ThreadModalProps) {
  const [chatMessages, setChatMessages] = useState<Array<{ question: string; answer: any }>>([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Store
  const savedStories = useStore((s) => s.savedStories);
  const saveStory = useStore((s) => s.saveStory);
  const unsaveStory = useStore((s) => s.unsaveStory);

  const { data: thread, isLoading } = useQuery({
    queryKey: ['thread', threadId],
    queryFn: () => api.getThread(threadId),
  });

  const isSaved = savedStories.some((s) => s.id === threadId);

  const chatMutation = useMutation({
    mutationFn: (question: string) => api.chat({ question, thread_id: threadId }),
    onSuccess: (response, question) => {
      setChatMessages(prev => [...prev, { question, answer: response }]);
      setCurrentQuestion('');
    },
  });

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // ESC key to close
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
  }, [onClose]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleAskQuestion = (question: string) => {
    if (question.trim() && !chatMutation.isPending) {
      chatMutation.mutate(question);
    }
  };

  const handleSaveToggle = () => {
    if (!thread) return;
    if (isSaved) {
      unsaveStory(threadId);
    } else {
      saveStory({
        id: threadId,
        title: thread.display_title,
        summary: thread.summary,
        image_url: thread.image_url,
        saved_at: new Date().toISOString(),
      });
    }
  };

  const handleShare = async () => {
    if (!thread) return;
    const shareText = `${thread.display_title}\n\nVía Plural`;
    const shareUrl = typeof window !== 'undefined' ? `${window.location.origin}/?thread=${threadId}` : '';

    if (navigator.share) {
      try {
        await navigator.share({ title: thread.display_title, text: shareText, url: shareUrl });
      } catch {}
    } else {
      const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(`${shareText}\n${shareUrl}`)}`;
      window.open(whatsappUrl, '_blank');
    }
  };

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      >
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full mx-auto mb-4"
          />
          <p className="text-ink-muted text-sm font-sans">Cargando historia...</p>
        </div>
      </motion.div>
    );
  }

  if (!thread) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm sm:flex sm:items-center sm:justify-center sm:p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="thread-modal-title"
    >
      <motion.div
        initial={{ y: '100%' }}
        animate={{ y: 0 }}
        exit={{ y: '100%' }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        onClick={(e) => e.stopPropagation()}
        className="relative w-full h-full sm:h-auto sm:max-h-[90vh] sm:max-w-5xl sm:rounded-2xl bg-surface paper-card overflow-hidden flex flex-col shadow-xl"
      >
        {/* Header */}
        <div className="flex items-center gap-3 p-4 sm:p-6 border-b paper-divider shrink-0">
          <button
            onClick={onClose}
            className="p-1.5 -ml-1.5 hover:bg-ink/[0.06] rounded-lg transition-colors sm:hidden"
            aria-label="Volver"
          >
            <ChevronLeft className="w-6 h-6 text-ink" />
          </button>

          <div className="flex-1 min-w-0">
            <span className="text-ink/40 font-sans text-sm sm:text-lg tracking-wide">{thread.title_id}</span>
            <h2 id="thread-modal-title" className="text-lg sm:text-2xl font-bold mt-0.5 sm:mt-2 line-clamp-2 text-ink">{thread.display_title}</h2>
          </div>

          {/* Action bar */}
          <div className="flex items-center gap-1 shrink-0">
            <motion.button
              onClick={handleSaveToggle}
              whileTap={{ scale: 0.85 }}
              className="p-2 hover:bg-ink/[0.06] rounded-lg transition-colors"
              aria-label={isSaved ? 'Quitar de guardados' : 'Guardar'}
            >
              <Bookmark className={`w-5 h-5 transition-colors ${isSaved ? 'fill-accent text-accent' : 'text-ink-muted'}`} />
            </motion.button>
            <button
              onClick={handleShare}
              className="p-2 hover:bg-ink/[0.06] rounded-lg transition-colors"
              aria-label="Compartir"
            >
              <Share2 className="w-5 h-5 text-ink-muted" />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-ink/[0.06] rounded-lg transition-colors hidden sm:block"
              aria-label="Cerrar"
            >
              <X className="w-6 h-6 text-ink-muted" />
            </button>
          </div>
        </div>

        {/* Content - scrollable */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 sm:space-y-8 overscroll-contain">
          {/* Summary */}
          <section>
            <h3 className="text-base sm:text-lg font-semibold mb-2 sm:mb-3 flex items-center gap-2 font-sans text-ink">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-ink/50" />
              Resumen
            </h3>
            <p className="text-sm sm:text-base text-ink-secondary leading-relaxed font-sans">{thread.summary}</p>
          </section>

          {/* Articles */}
          <section>
            <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4 flex items-center gap-2 font-sans text-ink">
              <ExternalLink className="w-4 h-4 sm:w-5 sm:h-5 text-ink/50" />
              Artículos ({thread.articles?.length || 0})
            </h3>
            <div className="grid gap-2 sm:gap-3">
              {thread.articles?.slice(0, 5).map((article: any) => (
                <a
                  key={article.id}
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-3 sm:p-4 rounded-lg hover:border-accent/30 active:bg-ink/[0.05] paper-card transition-all group"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm leading-snug mb-1 text-ink group-hover:text-ink/70 transition-colors font-sans line-clamp-2">
                        {article.title}
                      </h4>
                      <p className="text-xs text-ink/35 font-sans">{article.source}</p>
                    </div>
                    <ExternalLink className="w-4 h-4 text-ink/20 group-hover:text-ink/50 transition-colors shrink-0 mt-0.5" />
                  </div>
                </a>
              ))}
            </div>
          </section>

          {/* Suggested Questions */}
          {thread.suggested_questions && thread.suggested_questions.length > 0 && (
            <section>
              <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4 flex items-center gap-2 font-sans text-ink">
                <MessageCircle className="w-4 h-4 sm:w-5 sm:h-5 text-ink/50" />
                Pregúntale a Plural
              </h3>
              <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1 sm:grid sm:grid-cols-1 sm:overflow-visible scrollbar-hide">
                {thread.suggested_questions.map((q: string, i: number) => (
                  <button
                    key={i}
                    onClick={() => handleAskQuestion(q)}
                    disabled={chatMutation.isPending}
                    className="text-left p-3 rounded-lg hover:border-accent/30 active:bg-ink/[0.05] border border-ink/[0.08] bg-card transition-all text-sm text-ink-secondary disabled:opacity-50 shrink-0 w-[75vw] sm:w-auto font-sans"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </section>
          )}

          {/* Chat History */}
          {chatMessages.length > 0 && (
            <section>
              <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4 font-sans text-ink">Conversación</h3>
              <div className="space-y-3 sm:space-y-4">
                {chatMessages.map((msg, i) => (
                  <div key={i} className="space-y-2 sm:space-y-3">
                    {/* Question */}
                    <div className="flex justify-end">
                      <div className="max-w-[85%] sm:max-w-[80%] p-3 sm:p-4 bg-accent/15 border border-accent/25 rounded-lg">
                        <p className="text-sm font-sans text-ink">{msg.question}</p>
                      </div>
                    </div>
                    {/* Answer */}
                    <div className="flex justify-start">
                      <div className="max-w-[85%] sm:max-w-[80%] p-3 sm:p-4 bg-ink/[0.03] border border-ink/[0.08] rounded-lg">
                        <p className="text-sm text-ink-secondary leading-relaxed font-sans">
                          {msg.answer.answer}
                        </p>
                        {msg.answer.sources && msg.answer.sources.length > 0 && (
                          <div className="mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-ink/[0.08]">
                            <p className="text-xs text-ink/35 mb-1.5 font-sans">Fuentes:</p>
                            <div className="space-y-1">
                              {msg.answer.sources.map((source: any, j: number) => (
                                <a
                                  key={j}
                                  href={source.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-2 text-xs text-ink-muted hover:text-ink transition-colors font-sans group"
                                >
                                  <ExternalLink className="w-3 h-3 shrink-0" />
                                  <span className="truncate">{source.title || source.source}</span>
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
            </section>
          )}
        </div>

        {/* Chat Input */}
        <div className="p-3 sm:p-6 border-t paper-divider shrink-0 pb-[env(safe-area-inset-bottom,12px)]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAskQuestion(currentQuestion);
            }}
            className="flex gap-2 sm:gap-3"
          >
            <input
              type="text"
              value={currentQuestion}
              onChange={(e) => setCurrentQuestion(e.target.value)}
              placeholder="Pregúntale a Plural sobre esta historia..."
              disabled={chatMutation.isPending}
              className="flex-1 px-3 sm:px-4 py-3 bg-ink/[0.04] border border-ink/[0.08] rounded-lg text-sm text-ink focus:outline-none focus:ring-2 focus:ring-accent/40 disabled:opacity-50 font-sans placeholder:text-ink/25"
            />
            <button
              type="submit"
              disabled={!currentQuestion.trim() || chatMutation.isPending}
              className="px-4 sm:px-6 py-3 bg-ink text-white font-semibold rounded-lg hover:bg-ink/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shrink-0 font-sans"
            >
              {chatMutation.isPending ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="w-5 h-5 border-2 border-ink border-t-transparent rounded-full"
                />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>
        </div>
      </motion.div>
    </motion.div>
  );
}
