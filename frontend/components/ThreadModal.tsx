'use client';

import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Send, Sparkles, ExternalLink, MessageCircle, ChevronLeft } from 'lucide-react';

interface ThreadModalProps {
  threadId: string;
  onClose: () => void;
}

export default function ThreadModal({ threadId, onClose }: ThreadModalProps) {
  const [chatMessages, setChatMessages] = useState<Array<{ question: string; answer: any }>>([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const { data: thread, isLoading } = useQuery({
    queryKey: ['thread', threadId],
    queryFn: () => api.getThread(threadId),
  });

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

  const handleAskQuestion = (question: string) => {
    if (question.trim() && !chatMutation.isPending) {
      chatMutation.mutate(question);
    }
  };

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
      >
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-12 h-12 border-4 border-cyan border-t-transparent rounded-full mx-auto mb-4"
          />
          <p className="text-gray-light text-sm">Cargando historia...</p>
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
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm sm:flex sm:items-center sm:justify-center sm:p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ y: '100%' }}
        animate={{ y: 0 }}
        exit={{ y: '100%' }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        onClick={(e) => e.stopPropagation()}
        className="relative w-full h-full sm:h-auto sm:max-h-[90vh] sm:max-w-5xl sm:rounded-2xl glass-effect overflow-hidden flex flex-col"
      >
        {/* Header - mobile-friendly with back button */}
        <div className="flex items-center gap-3 p-4 sm:p-6 border-b border-white/10 shrink-0">
          <button
            onClick={onClose}
            className="p-1.5 -ml-1.5 hover:bg-white/10 rounded-lg transition-colors sm:hidden"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          <div className="flex-1 min-w-0">
            <span className="text-cyan font-mono text-sm sm:text-lg">{thread.title_id}</span>
            <h2 className="text-lg sm:text-2xl font-bold mt-0.5 sm:mt-2 line-clamp-2">{thread.display_title}</h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors hidden sm:block shrink-0"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content - scrollable */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 sm:space-y-8 overscroll-contain">
          {/* Summary */}
          <section>
            <h3 className="text-base sm:text-lg font-semibold mb-2 sm:mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-cyan" />
              Resumen
            </h3>
            <p className="text-sm sm:text-base text-gray-light leading-relaxed">{thread.summary}</p>
          </section>

          {/* Articles */}
          <section>
            <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4 flex items-center gap-2">
              <ExternalLink className="w-4 h-4 sm:w-5 sm:h-5 text-cyan" />
              Artículos ({thread.articles?.length || 0})
            </h3>
            <div className="grid gap-2 sm:gap-3">
              {thread.articles?.slice(0, 5).map((article: any) => (
                <a
                  key={article.id}
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-3 sm:p-4 glass-effect rounded-lg hover:border-cyan/30 active:bg-white/5 border border-white/10 transition-all group"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm leading-snug mb-1 group-hover:text-cyan transition-colors line-clamp-2">
                        {article.title}
                      </h4>
                      <p className="text-xs text-gray-medium">{article.source}</p>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-medium group-hover:text-cyan transition-colors shrink-0 mt-0.5" />
                  </div>
                </a>
              ))}
            </div>
          </section>

          {/* Suggested Questions */}
          {thread.suggested_questions && thread.suggested_questions.length > 0 && (
            <section>
              <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4 flex items-center gap-2">
                <MessageCircle className="w-4 h-4 sm:w-5 sm:h-5 text-cyan" />
                Pregunta a la IA
              </h3>
              <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1 sm:grid sm:grid-cols-1 sm:overflow-visible scrollbar-hide">
                {thread.suggested_questions.map((q: string, i: number) => (
                  <button
                    key={i}
                    onClick={() => handleAskQuestion(q)}
                    disabled={chatMutation.isPending}
                    className="text-left p-3 glass-effect rounded-lg hover:border-cyan/30 active:bg-cyan/5 border border-white/10 transition-all text-sm disabled:opacity-50 shrink-0 w-[75vw] sm:w-auto"
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
              <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4">Conversación</h3>
              <div className="space-y-3 sm:space-y-4">
                {chatMessages.map((msg, i) => (
                  <div key={i} className="space-y-2 sm:space-y-3">
                    {/* Question */}
                    <div className="flex justify-end">
                      <div className="max-w-[85%] sm:max-w-[80%] p-3 sm:p-4 bg-cyan/10 border border-cyan/30 rounded-lg">
                        <p className="text-sm">{msg.question}</p>
                      </div>
                    </div>
                    {/* Answer */}
                    <div className="flex justify-start">
                      <div className="max-w-[85%] sm:max-w-[80%] p-3 sm:p-4 glass-effect rounded-lg">
                        <p className="text-sm text-gray-light leading-relaxed">
                          {msg.answer.answer}
                        </p>
                        {msg.answer.sources && msg.answer.sources.length > 0 && (
                          <div className="mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-white/10">
                            <p className="text-xs text-gray-medium mb-1.5">Fuentes:</p>
                            <div className="flex flex-wrap gap-1.5">
                              {msg.answer.sources.map((source: string, j: number) => (
                                <span
                                  key={j}
                                  className="text-xs px-2 py-0.5 bg-cyan/10 text-cyan rounded"
                                >
                                  {source}
                                </span>
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

        {/* Chat Input - safe area aware */}
        <div className="p-3 sm:p-6 border-t border-white/10 shrink-0 pb-[env(safe-area-inset-bottom,12px)]">
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
              placeholder="Pregunta sobre esta historia..."
              disabled={chatMutation.isPending}
              className="flex-1 px-3 sm:px-4 py-3 glass-effect rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!currentQuestion.trim() || chatMutation.isPending}
              className="px-4 sm:px-6 py-3 bg-cyan text-navy-dark font-semibold rounded-lg hover:bg-cyan-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shrink-0"
            >
              {chatMutation.isPending ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="w-5 h-5 border-2 border-navy-dark border-t-transparent rounded-full"
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
