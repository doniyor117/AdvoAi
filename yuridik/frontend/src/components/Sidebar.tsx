'use client';

import { useState, useEffect } from 'react';
import {
    MessageSquare,
    Radar,
    Info,
    Settings,
    X,
    ChevronRight,
    Building2,
    MapPin,
    Users,
    Calendar,
    CheckCircle,
    AlertCircle
} from 'lucide-react';
import { api } from '@/lib/api';
import ScoutStatus from './ScoutStatus';
import clsx from 'clsx';

interface SidebarProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
    const [activeTab, setActiveTab] = useState<'scout' | 'business' | 'info'>('scout');
    const [health, setHealth] = useState<any>(null);

    useEffect(() => {
        api.getHealth()
            .then(setHealth)
            .catch(() => setHealth(null));
    }, []);

    return (
        <>
            {/* Backdrop */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-dark-950/80 z-40 md:hidden"
                    onClick={onClose}
                />
            )}

            {/* Sidebar */}
            <aside className={clsx(
                'fixed md:relative z-40 h-full w-80 bg-dark-900/95 backdrop-blur-xl border-r border-dark-700/50 flex flex-col transition-transform duration-300',
                isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
            )}>
                {/* Header */}
                <div className="p-4 border-b border-dark-700/50">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="font-semibold text-dark-100">Boshqaruv paneli</h2>
                        <button
                            onClick={onClose}
                            className="p-1 rounded-lg hover:bg-dark-700 text-dark-400 md:hidden"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Tabs */}
                    <div className="flex gap-1 p-1 bg-dark-800 rounded-lg">
                        {[
                            { id: 'scout', label: 'Scout', icon: Radar },
                            { id: 'business', label: 'Biznes', icon: Building2 },
                            { id: 'info', label: 'Info', icon: Info },
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={clsx(
                                    'flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-md text-xs font-medium transition-all',
                                    activeTab === tab.id
                                        ? 'bg-primary-500/20 text-primary-400'
                                        : 'text-dark-400 hover:text-dark-200'
                                )}
                            >
                                <tab.icon className="w-3.5 h-3.5" />
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
                    {activeTab === 'scout' && (
                        <div className="space-y-4">
                            <ScoutStatus variant="full" />

                            {/* Stats */}
                            <div className="glass-card p-4">
                                <h4 className="text-sm font-medium text-dark-200 mb-3">Statistika</h4>
                                <div className="grid grid-cols-2 gap-3">
                                    <StatCard
                                        label="Hujjatlar"
                                        value={health?.document_count?.toString() || '0'}
                                        icon={MessageSquare}
                                    />
                                    <StatCard
                                        label="LLM"
                                        value={health?.llm_provider || 'N/A'}
                                        icon={Radar}
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'business' && (
                        <BusinessForm />
                    )}

                    {activeTab === 'info' && (
                        <InfoPanel health={health} />
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-dark-700/50">
                    <div className="flex items-center gap-2 text-xs text-dark-500">
                        <div className={clsx(
                            'w-2 h-2 rounded-full',
                            health ? 'bg-green-500' : 'bg-red-500'
                        )} />
                        <span>{health ? 'Tizim ishlayapti' : 'Ulanishda xatolik'}</span>
                    </div>
                </div>
            </aside>
        </>
    );
}

function StatCard({ label, value, icon: Icon }: { label: string; value: string; icon: any }) {
    return (
        <div className="p-3 rounded-lg bg-dark-800/50 border border-dark-700/30">
            <div className="flex items-center gap-2 text-dark-400 mb-1">
                <Icon className="w-3.5 h-3.5" />
                <span className="text-xs">{label}</span>
            </div>
            <p className="text-lg font-semibold text-dark-100">{value}</p>
        </div>
    );
}

function BusinessForm() {
    const [formData, setFormData] = useState({
        industry: '',
        region: '',
        employees: '',
        years: '',
    });

    const industries = [
        'IT va dasturiy ta\'minot',
        'Qishloq xo\'jaligi',
        'Ishlab chiqarish',
        'Savdo',
        'Xizmat ko\'rsatish',
        'Turizm',
        'Qurilish',
        'Boshqa',
    ];

    const regions = [
        'Toshkent shahri',
        'Toshkent viloyati',
        'Samarqand',
        'Buxoro',
        'Farg\'ona',
        'Andijon',
        'Namangan',
        'Xorazm',
        'Qashqadaryo',
        'Surxondaryo',
        'Navoiy',
        'Jizzax',
        'Sirdaryo',
        'Qoraqalpog\'iston',
    ];

    return (
        <div className="space-y-4">
            <div className="glass-card p-4">
                <h4 className="text-sm font-medium text-dark-200 mb-3 flex items-center gap-2">
                    <Building2 className="w-4 h-4" />
                    Biznes ma'lumotlari
                </h4>
                <p className="text-xs text-dark-500 mb-4">
                    Aniqroq tavsiyalar olish uchun biznesingiz haqida ma'lumot kiriting
                </p>

                <div className="space-y-3">
                    <div>
                        <label className="block text-xs text-dark-400 mb-1">Soha</label>
                        <select
                            value={formData.industry}
                            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                            className="input-field text-sm"
                        >
                            <option value="">Tanlang...</option>
                            {industries.map(ind => (
                                <option key={ind} value={ind}>{ind}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-xs text-dark-400 mb-1">Hudud</label>
                        <select
                            value={formData.region}
                            onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                            className="input-field text-sm"
                        >
                            <option value="">Tanlang...</option>
                            {regions.map(reg => (
                                <option key={reg} value={reg}>{reg}</option>
                            ))}
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-xs text-dark-400 mb-1">Xodimlar soni</label>
                            <input
                                type="number"
                                value={formData.employees}
                                onChange={(e) => setFormData({ ...formData, employees: e.target.value })}
                                placeholder="0"
                                className="input-field text-sm"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-dark-400 mb-1">Faoliyat yili</label>
                            <input
                                type="number"
                                value={formData.years}
                                onChange={(e) => setFormData({ ...formData, years: e.target.value })}
                                placeholder="0"
                                className="input-field text-sm"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function InfoPanel({ health }: { health: any }) {
    return (
        <div className="space-y-4">
            <div className="glass-card p-4">
                <h4 className="text-sm font-medium text-dark-200 mb-3">Tizim holati</h4>

                <div className="space-y-2">
                    <div className="flex items-center justify-between py-2 border-b border-dark-700/30">
                        <span className="text-xs text-dark-400">Holat</span>
                        <span className={clsx(
                            'status-badge',
                            health?.status === 'healthy' ? 'status-success' : 'status-error'
                        )}>
                            {health?.status === 'healthy' ? (
                                <><CheckCircle className="w-3 h-3" /> Sog'lom</>
                            ) : (
                                <><AlertCircle className="w-3 h-3" /> Xatolik</>
                            )}
                        </span>
                    </div>

                    <div className="flex items-center justify-between py-2 border-b border-dark-700/30">
                        <span className="text-xs text-dark-400">Versiya</span>
                        <span className="text-xs text-dark-200">{health?.version || 'N/A'}</span>
                    </div>

                    <div className="flex items-center justify-between py-2 border-b border-dark-700/30">
                        <span className="text-xs text-dark-400">LLM Provider</span>
                        <span className="text-xs text-dark-200">{health?.llm_provider || 'N/A'}</span>
                    </div>

                    <div className="flex items-center justify-between py-2 border-b border-dark-700/30">
                        <span className="text-xs text-dark-400">LLM Model</span>
                        <span className="text-xs text-dark-200 truncate max-w-[150px]">{health?.llm_model || 'N/A'}</span>
                    </div>

                    <div className="flex items-center justify-between py-2">
                        <span className="text-xs text-dark-400">Hujjatlar</span>
                        <span className="text-xs text-dark-200">{health?.document_count || 0}</span>
                    </div>
                </div>
            </div>

            <div className="glass-card p-4">
                <h4 className="text-sm font-medium text-dark-200 mb-3">Haqida</h4>
                <p className="text-xs text-dark-400 leading-relaxed">
                    <strong>Imtiyoz-AI</strong> — O'zbekistondagi tadbirkorlar uchun davlat
                    subsidiyalari, grantlari va soliq imtiyozlarini topishda yordam beruvchi
                    sun'iy intellektga asoslangan yordamchi.
                </p>
                <p className="text-xs text-dark-500 mt-2">
                    © 2026 LumenAI Team — Milliy AI Xakaton
                </p>
            </div>
        </div>
    );
}
