import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'Imtiyoz-AI | Tadbirkorlar uchun imtiyozlar yordamchisi',
    description: 'AI-powered smart assistant for Uzbek entrepreneur privileges and subsidies. Discover grants, tax holidays, and government support programs.',
    keywords: 'imtiyoz, subsidiya, tadbirkorlik, uzbekistan, grant, soliq, kichik biznes',
    authors: [{ name: 'LumenAI Team' }],
    robots: 'index, follow',
    openGraph: {
        title: 'Imtiyoz-AI | Smart Privilege Finder',
        description: 'Find government subsidies, grants, and tax benefits for your business',
        locale: 'uz_UZ',
        type: 'website',
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="uz" className="dark">
            <body className="min-h-screen bg-dark-950">
                {/* Background gradient */}
                <div className="fixed inset-0 -z-10">
                    <div className="absolute inset-0 bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950" />
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl" />
                    <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl" />
                </div>

                {children}
            </body>
        </html>
    );
}
