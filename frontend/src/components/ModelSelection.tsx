'use client';

import { useState, useEffect } from 'react';

interface Model {
  name: string;
  model: string;
  size: number;
  modified_at: string;
  details: {
    parameter_size: string;
    quantization_level: string;
    family: string;
  };
}

interface ModelSelectionProps {
  selectedModel: string;
  onModelSelect: (model: string) => void;
}

export default function ModelSelection({ selectedModel, onModelSelect }: ModelSelectionProps) {
  const [models, setModels] = useState<Model[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/models');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setModels(data.models || []);
    } catch (error) {
      console.error('Failed to fetch models:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch models');
    } finally {
      setIsLoading(false);
    }
  };

  const formatSize = (bytes: number) => {
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(1)} GB`;
  };

  const getModelTypeIcon = (family: string) => {
    switch (family.toLowerCase()) {
      case 'llama':
        return '🦙';
      case 'nomic-bert':
        return '📄';
      default:
        return '🤖';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="flex items-center space-x-2 text-gray-400">
          <div className="w-4 h-4 border-2 border-white/20 border-t-white/60 rounded-full animate-spin"></div>
          <span>Loading models...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-4">
        <div className="text-red-400 text-sm mb-2">❌ {error}</div>
        <button
          onClick={fetchModels}
          className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white text-sm rounded border border-white/20 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (models.length === 0) {
    return (
      <div className="text-center py-4 text-gray-400 text-sm">
        No models available. Make sure Ollama is running and has models installed.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {models.map((model) => (
        <button
          key={model.name}
          className={`w-full p-3 rounded-lg border cursor-pointer transition-all text-left ${
            selectedModel === model.name
              ? 'border-blue-500 bg-blue-500/20'
              : 'border-white/20 bg-white/5 hover:bg-white/10'
          }`}
          onClick={() => onModelSelect(model.name)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onModelSelect(model.name);
            }
          }}
          aria-label={`Select ${model.name} model`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <span className="text-lg">
                  {getModelTypeIcon(model.details.family)}
                </span>
                <span className="text-white font-medium text-sm">
                  {model.name}
                </span>
                {selectedModel === model.name && (
                  <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded">
                    Active
                  </span>
                )}
              </div>
              
              <div className="mt-2 space-y-1 text-xs text-gray-400">
                <div className="flex justify-between">
                  <span>Size:</span>
                  <span>{formatSize(model.size)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Parameters:</span>
                  <span>{model.details.parameter_size}</span>
                </div>
                <div className="flex justify-between">
                  <span>Quantization:</span>
                  <span>{model.details.quantization_level}</span>
                </div>
              </div>
            </div>
          </div>
        </button>
      ))}

      {/* Refresh Models */}
      <button
        onClick={fetchModels}
        disabled={isLoading}
        className="w-full px-3 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded-lg border border-white/20 disabled:opacity-50 transition-colors"
      >
        🔄 Refresh Models
      </button>
    </div>
  );
}