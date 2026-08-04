import { useEffect, useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { sendChatMessage } from '../../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Olá! Sou o assistente ambiental do EcoCity. Pergunte-me sobre qualquer cidade, por exemplo: "Como está Curitiba?"',
    },
  ]);
  const [input, setInput] = useState('');
  const listRef = useRef<HTMLDivElement>(null);

  const mutation = useMutation({
    mutationFn: (message: string) => sendChatMessage({ message }),
  });

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, mutation.isPending]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || mutation.isPending) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    mutation.mutate(text, {
      onSuccess: (res) => {
        setMessages((prev) => [...prev, { role: 'assistant', content: res.answer }]);
      },
      onError: () => {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: 'Não consegui obter uma resposta agora. Tente novamente em instantes.',
          },
        ]);
      },
    });
  };

  return (
    <div className="mx-auto flex h-[calc(100vh-14rem)] max-w-3xl flex-col">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Chat Ambiental</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Pergunte sobre as condições ambientais das cidades monitoradas
        </p>
      </div>

      <div
        ref={listRef}
        className="mt-4 flex-1 space-y-4 overflow-y-auto rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
      >
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm shadow-sm ${
                msg.role === 'user'
                  ? 'rounded-br-sm bg-emerald-600 text-white'
                  : 'rounded-bl-sm bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {mutation.isPending && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm bg-gray-100 px-4 py-2 text-sm text-gray-500 dark:bg-gray-800 dark:text-gray-400">
              <span className="flex items-center gap-1">
                IA está pensando
                <span className="animate-pulse">...</span>
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ex.: Como está Curitiba?"
          className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 focus:border-emerald-500 focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={!input.trim() || mutation.isPending}
          className="rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Enviar
        </button>
      </div>
    </div>
  );
}
