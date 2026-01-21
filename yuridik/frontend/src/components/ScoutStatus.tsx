'use client';

import { useState, useEffect, useCallback } from 'react';
import { Radar, AlertCircle, CheckCircle, Search, Download, Zap } from 'lucide-react';
import { api } from '@/lib/api';
import type { ScoutStatusEvent } from '@/types';
import clsx from 'clsx';

interface ScoutStatusProps {
    variant?: 'compact' | 'full';
}

export default function ScoutStatus({ variant = 'compact' }: ScoutStatusProps) {
    const [isRunning, setIsRunning] = useState(false);
    const [progress, setProgress] = useState(0);
    const [currentStatus, setCurrentStatus] = useState<string>('');
    const [logs, setLogs] = useState<ScoutStatusEvent[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [isExpanded, setIsExpanded] = useState(false);

    const triggerScout = useCallback(async () => {
        if (isRunning) return;

        setIsRunning(true);
        setProgress(0);
        setLogs([]);
        setError(null);
        setCurrentStatus('Scout ishga tushirilmoqda...');
        setIsExpanded(true);

        try {
            // Trigger the scout agent
            await api.triggerScout({ force_refresh: false });

            // Subscribe to status updates
            const eventSource = api.subscribeToScoutStatus(
                (event: ScoutStatusEvent) => {
                    setLogs(prev => [...prev.slice(-20), event]); // Keep last 20 logs
                    setProgress(event.details?.progress || 0);
                    setCurrentStatus(event.message);

                    if (event.event_type === 'complete' || event.event_type === 'error') {
                        setIsRunning(false);
                        eventSource.close();
                    }
                },
                (err) => {
                    setError(err.message);
                    setIsRunning(false);
                }
            );

            // Cleanup on unmount or re-trigger
            return () => eventSource.close();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Scout xatoligi');
            setIsRunning(false);
        }
    }, [isRunning]);

    // Compact variant (header widget)
    if (variant === 'compact') {
        return (
            <div className="flex items-center gap-3">
                <button
                    onClick={triggerScout}
                    disabled={isRunning}
                    className={clsx(
                        'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200',
                        isRunning
                            ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30 cursor-wait'
                            : 'btn-secondary hover:border-primary-500/50'
                    )}
                >
                    {isRunning ? (
                        <>
                            <Radar className="w-4 h-4 animate-pulse" />
                            <span className="hidden sm:inline">Yangilanmoqda...</span>
                            <span className="text-xs text-primary-400">{progress}%</span>
                        </>
                    ) : (
                        <>
                            <Zap className="w-4 h-4" />
                            <span className="hidden sm:inline">Yangilash</span>
                        </>
                    )}
                </button>
            </div>
        );
    }

    // Full variant (sidebar panel)
    return (
        <div className="glass-card p-4">
            <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-dark-100 flex items-center gap-2">
                    <Radar className={clsx('w-4 h-4', isRunning && 'animate-pulse text-primary-400')} />
                    Scout Agent
                </h3>
                <button
                    onClick={triggerScout}
                    disabled={isRunning}
                    className={clsx(
                        'p-2 rounded-lg transition-all',
                        isRunning
                            ? 'bg-primary-500/20 text-primary-400'
                            : 'bg-dark-700 hover:bg-dark-600 text-dark-300'
                    )}
                >
                    <Zap className="w-4 h-4" />
                </button>
            </div>

            {/* Progress bar */}
            {isRunning && (
                <div className="mb-3">
                    <div className="flex items-center justify-between text-xs text-dark-400 mb-1">
                        <span>{currentStatus}</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="h-1.5 bg-dark-700 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}

            {/* Error state */}
            {error && (
                <div className="p-2 mb-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                </div>
            )}

            {/* Logs */}
            {logs.length > 0 && (
                <div className="space-y-1 max-h-48 overflow-y-auto scrollbar-thin">
                    {logs.map((log, idx) => (
                        <LogEntry key={idx} event={log} />
                    ))}
                </div>
            )}

            {!isRunning && logs.length === 0 && !error && (
                <p className="text-xs text-dark-500 text-center py-4">
                    Yangi hujjatlarni qidirish uchun "Yangilash" tugmasini bosing
                </p>
            )}
        </div>
    );
}

function LogEntry({ event }: { event: ScoutStatusEvent }) {
    const getIcon = () => {
        switch (event.event_type) {
            case 'search':
                return <Search className="w-3 h-3 text-blue-400" />;
            case 'judge':
                return event.details?.relevance
                    ? <CheckCircle className="w-3 h-3 text-green-400" />
                    : <AlertCircle className="w-3 h-3 text-yellow-400" />;
            case 'ingest':
                return <Download className="w-3 h-3 text-green-400" />;
            case 'complete':
                return <CheckCircle className="w-3 h-3 text-green-400" />;
            case 'error':
                return <AlertCircle className="w-3 h-3 text-red-400" />;
            default:
                return <Radar className="w-3 h-3 text-dark-400" />;
        }
    };

    return (
        <div className={clsx(
            'scout-log text-xs',
            event.event_type === 'search' && 'scout-log-search',
            event.event_type === 'judge' && 'scout-log-judge',
            event.event_type === 'ingest' && 'scout-log-ingest',
            event.event_type === 'error' && 'scout-log-error',
        )}>
            {getIcon()}
            <span className="line-clamp-1">{event.message}</span>
        </div>
    );
}
