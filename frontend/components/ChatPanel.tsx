'use client';

import { useEffect, useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { ChatResponse } from '@/lib/types';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, ExternalLink, Send } from 'lucide-react';

interface ChatPanelProps {
  isOpen: boolean;
  initialQuestion: string;
  onClose: () => void;
}

export default function ChatPanel({ isOpen, initialQuestion, onClose }: ChatPanelProps) {
  const [messages, setMessages] = useState<Array<{ question: string; answer: ChatResponse | null; isLoading: boolean }>>([]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const chatMutation = useMutation({
    mutationFn: (question: string) => api.chat({ question }),
    onSuccess: (response) => {
      setMessages(prev => {
        const updated = [...prev];
        let lastLoading = -1;
        for (let i = updated.length - 1; i >= 0; i--) { if (updated[i].isLoading) { lastLoading = i; break; } }
        if (lastLoading !== -1) {
          updated[lastLoading] = { ...updated[lastLoading], answer: response, isLoading: false };
        }
        return updated;
      });
    },
    onError: () => {
      setMessages(prev => {
        const updated = [...prev];
        let lastLoading = -1;
        for (let i = updated.length - 1; i >= 0; i--) { if (updated[i].isLoading) { lastLoading = i; break; } }
        if (lastLoading !== -1) {
          updated[lastLoading] = {
            ...updated[lastLoading],
            answer: { answer: 'Lo siento, hubo un error al procesar tu pregunta. Intenta de nuevo.', sources: [] },
            isLoading: false,
          };
        }
        return updated;
      });
    },
  });

  // Send initial question when panel opens
  useEffect(() => {
    if (isOpen && initialQuestion) {
      setMessages([{ question: initialQuestion, answer: null, isLoading: true }]);
      chatMutation.mutate(initialQuestion);
    }
    if (!isOpen) {
      setMessages([]);
      setInput('');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, initialQuestion]);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const handleFollowUp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || chatMutation.isPending) return;
    const question = input.trim();
    setInput('');
    setMessages(prev => [...prev, { question, answer: null, isLoading: true }]);
    chatMutation.mutate(question);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.98 }}
            transition={{ type: 'spring', damping: 25, stiffness: 350 }}
            className="fixed top-[70px] left-1/2 -translate-x-1/2 z-50 w-[95vw] sm:w-full sm:max-w-2xl max-h-[75vh] bg-surface paper-card rounded-2xl overflow-hidden flex flex-col shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b paper-divider shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-accent/15 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-ink/50" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-ink font-sans">Plural</h3>
                  <p className="text-[10px] text-ink/30 font-sans tracking-wide uppercase">Tu asistente de noticias</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-1.5 hover:bg-ink/[0.06] rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-ink-muted" />
              </button>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 space-y-5">
              {messages.map((msg, i) => (
                <div key={i} className="space-y-3">
                  {/* Question */}
                  <div className="flex justify-end">
                    <div className="max-w-[85%] px-4 py-2.5 bg-accent/15 border border-accent/25 rounded-2xl rounded-br-md">
                      <p className="text-sm text-ink font-sans">{msg.question}</p>
                    </div>
                  </div>

                  {/* Answer */}
                  <div className="flex justify-start">
                    {msg.isLoading ? (
                      <LoadingBubble />
                    ) : msg.answer ? (
                      <div className="max-w-[90%] space-y-3">
                        <div className="px-4 py-3 bg-ink/[0.03] border border-ink/[0.08] rounded-2xl rounded-bl-md">
                          <p className="text-sm text-ink-secondary leading-relaxed font-sans whitespace-pre-wrap">
                            {msg.answer.answer}
                          </p>
                        </div>

                        {/* Sources */}
                        {msg.answer.sources && msg.answer.sources.length > 0 && (
                          <div className="pl-1 space-y-1.5">
                            <span className="text-[10px] text-ink/25 uppercase tracking-widest font-sans">Fuentes</span>
                            {msg.answer.sources.map((source, j) => (
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
                        )}
                      </div>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>

            {/* Follow-up input */}
            <div className="px-5 py-4 border-t paper-divider shrink-0">
              <form onSubmit={handleFollowUp} className="flex items-center gap-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Pregúntale algo más a Plural..."
                  disabled={chatMutation.isPending}
                  className="flex-1 px-4 py-2.5 bg-ink/[0.03] border border-ink/[0.08] rounded-xl text-sm text-ink font-sans outline-none focus:border-accent/40 transition-colors placeholder:text-ink/20 disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || chatMutation.isPending}
                  className="p-2.5 bg-accent/20 hover:bg-accent/30 rounded-xl transition-colors disabled:opacity-30"
                >
                  <Send className="w-4 h-4 text-ink/50" />
                </button>
              </form>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function LoadingBubble() {
  return (
    <div className="px-4 py-3 bg-ink/[0.03] border border-ink/[0.08] rounded-2xl rounded-bl-md">
      <div className="flex items-center gap-1.5">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            animate={{ y: [0, -4, 0] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
            className="w-1.5 h-1.5 rounded-full bg-ink/30"
          />
        ))}
      </div>
    </div>
  );
}
