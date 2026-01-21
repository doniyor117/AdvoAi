'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import ScoutStatus from '@/components/ScoutStatus';
import Sidebar from '@/components/Sidebar';
import { Sparkles, Menu, X } from 'lucide-react';

export default function Home() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    return (
        <main className="flex h-screen overflow-hidden">
            {/* Mobile menu button */}
            <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="fixed top-4 left-4 z-50 p-2 rounded-lg bg-dark-800/80 backdrop-blur-sm border border-dark-600/50 md:hidden"
            >
                {isSidebarOpen ? (
                    <X className="w-5 h-5 text-dark-200" />
                ) : (
                    <Menu className="w-5 h-5 text-dark-200" />
                )}
            </button>

            {/* Sidebar */}
            <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

            {/* Main content */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <header className="flex items-center justify-between px-4 md:px-6 py-4 border-b border-dark-700/50">
                    <div className="flex items-center gap-3 ml-10 md:ml-0">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg shadow-primary-500/20">
                            <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h1 className="text-lg font-bold text-dark-50">Imtiyoz-AI</h1>
                            <p className="text-xs text-dark-400">Tadbirkorlar uchun aqlli yordamchi</p>
                        </div>
                    </div>

                    {/* Scout Status Widget (Header) */}
                    <ScoutStatus variant="compact" />
                </header>

                {/* Chat Area */}
                <div className="flex-1 overflow-hidden">
                    <ChatInterface />
                </div>
            </div>
        </main>
    );
}
