import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { healthCheck } from '../api';
import { Database, Cpu, Search, Camera, Wrench, Activity, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function Dashboard() {
  const [health, setHealth] = useState({
    database: 'checking...',
    ollama: 'checking...',
    status: 'checking...',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHealth() {
      try {
        const res = await healthCheck();
        setHealth(res.data);
      } catch (error) {
        setHealth({
          database: 'error',
          ollama: 'error',
          status: 'error',
        });
      } finally {
        setLoading(false);
      }
    }
    fetchHealth();
    
    // Refresh health every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const StatusIcon = ({ status, type }) => {
    if (status === 'checking...') return <Activity className="w-5 h-5 text-industrial-400 animate-pulse" />;
    
    if (type === 'db') {
      return status === 'connected' 
        ? <CheckCircle2 className="w-5 h-5 text-emerald-500" />
        : <AlertTriangle className="w-5 h-5 text-red-500" />;
    }
    
    if (type === 'ai') {
      return status === 'running'
        ? <CheckCircle2 className="w-5 h-5 text-emerald-500" />
        : <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    }
    
    return <AlertTriangle className="w-5 h-5 text-red-500" />;
  };

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Welcome to ExtrusionAI</h1>
        <p className="text-industrial-400">Your intelligent manufacturing assistant. Monitor system status and access quick actions below.</p>
      </header>

      {/* System Status Cards */}
      <section>
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-accent-500" />
          System Status
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="card flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-industrial-900 flex items-center justify-center">
                <Database className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h3 className="text-industrial-300 text-sm font-medium">Database Connection</h3>
                <p className="text-white font-semibold capitalize">{health.database}</p>
              </div>
            </div>
            <StatusIcon status={health.database} type="db" />
          </div>

          <div className="card flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-industrial-900 flex items-center justify-center">
                <Cpu className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <h3 className="text-industrial-300 text-sm font-medium">AI Engine (Ollama)</h3>
                <p className="text-white font-semibold capitalize">
                  {health.ollama === 'running' ? 'Ready' : health.ollama}
                </p>
              </div>
            </div>
            <StatusIcon status={health.ollama} type="ai" />
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="pt-4">
        <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link to="/analyze" className="card-hover group">
            <div className="w-12 h-12 rounded-lg bg-primary-900/50 flex items-center justify-center mb-4 text-primary-400 group-hover:text-primary-300 transition-colors">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Analyze Problem</h3>
            <p className="text-sm text-industrial-400">Input machine parameters to diagnose production issues and get AI suggestions.</p>
          </Link>

          <Link to="/photo" className="card-hover group">
            <div className="w-12 h-12 rounded-lg bg-teal-900/30 flex items-center justify-center mb-4 text-teal-400 group-hover:text-teal-300 transition-colors">
              <Camera className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Upload Defect Photo</h3>
            <p className="text-sm text-industrial-400">Upload a photo of a plastic part to automatically classify visual defects.</p>
          </Link>

          <Link to="/troubleshoot" className="card-hover group">
            <div className="w-12 h-12 rounded-lg bg-accent-900/30 flex items-center justify-center mb-4 text-accent-400 group-hover:text-accent-300 transition-colors">
              <Wrench className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Start Troubleshooting</h3>
            <p className="text-sm text-industrial-400">Follow a step-by-step interactive guide to resolve known machinery problems.</p>
          </Link>
        </div>
      </section>
    </div>
  );
}
