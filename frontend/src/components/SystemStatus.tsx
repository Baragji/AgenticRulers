'use client';

import { useState, useEffect } from 'react';

interface SystemStatusProps {
  health: any;
  onRefresh: () => void;
}

export default function SystemStatus({ health, onRefresh }: SystemStatusProps) {
  const [detailedStatus, setDetailedStatus] = useState<any>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    fetchDetailedStatus();
  }, []);

  const fetchDetailedStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const status = await response.json();
      setDetailedStatus(status);
    } catch (error) {
      console.error('Failed to fetch detailed status:', error);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await Promise.all([onRefresh(), fetchDetailedStatus()]);
    setIsRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
        return 'text-green-400';
      case 'degraded':
        return 'text-yellow-400';
      case 'unhealthy':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
        return '✅';
      case 'degraded':
        return '⚠️';
      case 'unhealthy':
        return '❌';
      default:
        return '❓';
    }
  };

  return (
    <div className="space-y-4">
      {/* Overall Health */}
      {health && (
        <div className="flex items-center justify-between">
          <span className="text-gray-300">Overall Status</span>
          <div className="flex items-center space-x-2">
            <span className={getStatusColor(health.status)}>
              {getStatusIcon(health.status)} {health.status}
            </span>
          </div>
        </div>
      )}

      {/* Service Status */}
      {health?.services && (
        <div className="space-y-2">
          {Object.entries(health.services).map(([service, status]) => (
            <div key={service} className="flex items-center justify-between text-sm">
              <span className="text-gray-300 capitalize">{service}</span>
              <span className={getStatusColor(status as string)}>
                {getStatusIcon(status as string)}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Detailed Metrics */}
      {detailedStatus && (
        <div className="pt-2 border-t border-white/10 space-y-2 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Version</span>
            <span className="text-gray-300">{detailedStatus.version}</span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Environment</span>
            <span className="text-gray-300">{detailedStatus.environment}</span>
          </div>

          {detailedStatus.ollama && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Models Available</span>
              <span className="text-gray-300">{detailedStatus.ollama.models_count}</span>
            </div>
          )}

          {detailedStatus.telemetry && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Tracing</span>
              <span className="text-green-400">
                {detailedStatus.telemetry.traces_enabled ? '✅' : '❌'}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Refresh Button */}
      <button
        onClick={handleRefresh}
        disabled={isRefreshing}
        className="w-full px-3 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded-lg border border-white/20 disabled:opacity-50 transition-colors"
      >
        {isRefreshing ? '🔄 Refreshing...' : '🔄 Refresh Status'}
      </button>

      {/* Last Updated */}
      {health?.timestamp && (
        <div className="text-xs text-gray-500 text-center">
          Updated: {new Date(health.timestamp).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}