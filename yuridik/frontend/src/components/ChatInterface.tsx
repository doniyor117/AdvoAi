'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles, FileText, ExternalLink } from 'lucide-react';
import { api } from '@/lib/api';
import type { Message, DocumentSource, MatchedPrivilege, BusinessContext } from '@/types';
import clsx from 'clsx';

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Auto-resize textarea
    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.style.height = 'auto';
            inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
        }
    }, [input]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        // Add loading message
        const loadingId = (Date.now() + 1).toString();
        setMessages(prev => [...prev, {
            id: loadingId,
            role: 'assistant',
            content: '',
            timestamp: new Date(),
            isLoading: true,
        }]);

        try {
            const response = await api.chat({
                message: userMessage.content,
                conversation_id: conversationId || undefined,
            });

            setConversationId(response.conversation_id);

            // Replace loading message with actual response
            setMessages(prev => prev.map(msg =>
                msg.id === loadingId
                    ? {
                        ...msg,
                        content: response.response,
                        sources: response.sources,
                        privileges: response.matched_privileges,
                        isLoading: false,
                    }
                    : msg
            ));
        } catch (error) {
            // Replace loading with error
            setMessages(prev => prev.map(msg =>
                msg.id === loadingId
                    ? {
                        ...msg,
                        content: `Kechirasiz, xatolik yuz berdi: ${error instanceof Error ? error.message : 'Noma\'lum xatolik'}`,
                        isLoading: false,
                    }
                    : msg
            ));
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex flex-col h-full">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 scrollbar-thin">
                {messages.length === 0 ? (
                    <WelcomeScreen onExampleClick={setInput} />
                ) : (
                    <div className="max-w-3xl mx-auto space-y-6">
                        {messages.map(message => (
                            <MessageBubble key={message.id} message={message} />
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="border-t border-dark-700/50 p-4 md:p-6">
                <div className="max-w-3xl mx-auto">
                    <div className="relative flex items-end gap-2">
                        <div className="flex-1 relative">
                            <textarea
                                ref={inputRef}
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Savolingizni yozing... (masalan: 'IT sohasida qanday soliq imtiyozlari bor?')"
                                rows={1}
                                className="input-field pr-12 resize-none min-h-[48px] max-h-[120px]"
                                disabled={isLoading}
                            />
                        </div>
                        <button
                            onClick={sendMessage}
                            disabled={!input.trim() || isLoading}
                            className={clsx(
                                'p-3 rounded-xl transition-all duration-200',
                                input.trim() && !isLoading
                                    ? 'bg-primary-500 text-white hover:bg-primary-400 shadow-lg shadow-primary-500/25'
                                    : 'bg-dark-700 text-dark-400 cursor-not-allowed'
                            )}
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Send className="w-5 h-5" />
                            )}
                        </button>
                    </div>
                    <p className="text-xs text-dark-500 mt-2 text-center">
                        Imtiyoz-AI sizga subsidiyalar, grantlar va soliq imtiyozlarini topishda yordam beradi
                    </p>
                </div>
            </div>
        </div>
    );
}

function WelcomeScreen({ onExampleClick }: { onExampleClick: (text: string) => void }) {
    const examples = [
        "IT sohasida qanday soliq imtiyozlari bor?",
        "Yoshlar uchun tadbirkorlik grantlari haqida ayting",
        "Kichik biznes uchun imtiyozli kreditlar",
        "Fermer xoʻjaliklari uchun subsidiyalar",
    ];

    return (
        <div className="h-full flex flex-col items-center justify-center px-4">
            <div className="max-w-2xl text-center">
                {/* Logo */}
                <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-2xl shadow-primary-500/30">
                    <Sparkles className="w-10 h-10 text-white" />
                </div>

                <h2 className="text-2xl md:text-3xl font-bold text-dark-50 mb-3">
                    Imtiyoz-AI ga xush kelibsiz!
                </h2>
                <p className="text-dark-400 mb-8">
                    Men sizga O'zbekistondagi tadbirkorlar uchun subsidiyalar, grantlar va soliq imtiyozlarini topishda yordam beraman.
                </p>

                {/* Example Questions */}
                <div className="grid gap-3 md:grid-cols-2">
                    {examples.map((example, idx) => (
                        <button
                            key={idx}
                            onClick={() => onExampleClick(example)}
                            className="p-4 text-left glass-card hover:border-primary-500/30 transition-all duration-200 group"
                        >
                            <span className="text-sm text-dark-300 group-hover:text-dark-100">
                                {example}
                            </span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

function MessageBubble({ message }: { message: Message }) {
    const isUser = message.role === 'user';

    return (
        <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
            <div className={clsx(
                'max-w-[85%] md:max-w-[75%]',
                isUser ? 'message-user' : 'message-ai'
            )}>
                {/* Loading state */}
                {message.isLoading ? (
                    <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                            <span className="w-2 h-2 rounded-full bg-primary-400 typing-dot" />
                            <span className="w-2 h-2 rounded-full bg-primary-400 typing-dot" />
                            <span className="w-2 h-2 rounded-full bg-primary-400 typing-dot" />
                        </div>
                        <span className="text-sm text-dark-400">Javob tayyorlanmoqda...</span>
                    </div>
                ) : (
                    <>
                        {/* Message content */}
                        <div className="prose prose-invert prose-sm max-w-none">
                            <p className="whitespace-pre-wrap">{message.content}</p>
                        </div>

                        {/* Sources */}
                        {message.sources && message.sources.length > 0 && (
                            <div className="mt-4 pt-3 border-t border-dark-600/50">
                                <p className="text-xs font-medium text-dark-400 mb-2 flex items-center gap-1">
                                    <FileText className="w-3 h-3" />
                                    Manbalar
                                </p>
                                <div className="space-y-2">
                                    {message.sources.slice(0, 3).map((source, idx) => (
                                        <SourceCard key={idx} source={source} />
                                    ))}
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}

function SourceCard({ source }: { source: DocumentSource }) {
    return (
        <div className="p-2 rounded-lg bg-dark-800/50 border border-dark-600/30 text-xs">
            <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                    <p className="font-medium text-dark-200 truncate">
                        {source.document_id}: {source.title}
                    </p>
                    <p className="text-dark-400 mt-1 line-clamp-2">{source.excerpt}</p>
                </div>
                {source.url && (
                    <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 rounded hover:bg-dark-700 text-dark-400 hover:text-primary-400"
                    >
                        <ExternalLink className="w-3 h-3" />
                    </a>
                )}
            </div>
            <div className="mt-1 flex items-center gap-2">
                <div className="h-1 flex-1 bg-dark-700 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-primary-500 rounded-full"
                        style={{ width: `${source.relevance_score * 100}%` }}
                    />
                </div>
                <span className="text-dark-500">{Math.round(source.relevance_score * 100)}%</span>
            </div>
        </div>
    );
}
