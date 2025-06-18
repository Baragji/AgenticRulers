import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AutonomesAI v2.1',
  description: 'Advanced AI orchestration with LangGraph + Ollama',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
          <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-2xl font-bold text-white">
                    🤖 AutonomesAI v2.1
                  </h1>
                  <span className="ml-4 px-3 py-1 bg-green-500/20 text-green-300 text-sm rounded-full">
                    Sprint 1-A
                  </span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-sm text-gray-300">
                    LangGraph + Ollama
                  </div>
                </div>
              </div>
            </div>
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}