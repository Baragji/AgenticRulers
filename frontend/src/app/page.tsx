'use client';

import { useState, useEffect } from 'react';
import ChatInterface from '@/components/ChatInterface';
import SystemStatus from '@/components/SystemStatus';
import ModelSelection from '@/components/ModelSelection';

export default function Home() {
  const [selectedModel, setSelectedModel] = useState('llama3.1:8b');
  const [systemHealth, setSystemHealth] = useState<any>(null);

  useEffect(() => {
    // Check system health on load
    fetchSystemHealth();
  }, []);

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('/api/health');
      const health = await response.json();
      setSystemHealth(health);
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Chat Interface */}
        <div className="lg:col-span-2">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
            <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
              💬 AI Chat Interface
              <span className="ml-2 px-2 py-1 bg-blue-500/20 text-blue-300 text-sm rounded">
                {selectedModel}
              </span>
            </h2>
            <ChatInterface 
              selectedModel={selectedModel}
            />
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          
          {/* System Status */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              📊 System Status
            </h3>
            <SystemStatus health={systemHealth} onRefresh={fetchSystemHealth} />
          </div>

          {/* Model Selection */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              🤖 Model Selection
            </h3>
            <ModelSelection 
              selectedModel={selectedModel}
              onModelSelect={setSelectedModel}
            />
          </div>

          {/* Sprint Info */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              🎯 Sprint 1-A Progress
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Backend API</span>
                <span className="text-green-400">✅ Ready</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Ollama Integration</span>
                <span className="text-green-400">✅ Connected</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">LangGraph DAG</span>
                <span className="text-green-400">✅ Compiled</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Frontend UI</span>
                <span className="text-blue-400">🔄 Building</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}