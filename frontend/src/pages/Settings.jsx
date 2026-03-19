import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, Server, CheckCircle2 } from 'lucide-react';

export default function Settings() {
  const [apiUrl, setApiUrl] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const currentUrl = localStorage.getItem('extrusionai_api_url') || 'http://localhost:8000';
    setApiUrl(currentUrl);
  }, []);

  const handleSave = (e) => {
    e.preventDefault();
    localStorage.setItem('extrusionai_api_url', apiUrl);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <SettingsIcon className="w-8 h-8 text-industrial-400" />
          Settings
        </h1>
        <p className="text-industrial-400">Configure your ExtrusionAI dashboard preferences and connections.</p>
      </header>

      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
          <Server className="w-5 h-5 text-primary-400" />
          API Configuration
        </h2>
        
        <form onSubmit={handleSave} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-industrial-300 block">Backend API URL</label>
            <input 
              type="text" 
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://localhost:8000"
              className="input-field max-w-md font-mono"
            />
            <p className="text-xs text-industrial-500 mt-1">
              By default, this points to your local FastAPI server on port 8000.
            </p>
          </div>

          <div className="flex items-center gap-4 pt-4 border-t border-industrial-700">
            <button type="submit" className="btn-primary flex items-center gap-2">
              <Save className="w-4 h-4" />
              Save Configuration
            </button>
            
            {saved && (
              <span className="text-emerald-500 text-sm font-medium flex items-center gap-2 animate-in fade-in zoom-in duration-300">
                <CheckCircle2 className="w-4 h-4" />
                Settings saved successfully
              </span>
            )}
          </div>
        </form>
      </div>

      <div className="card bg-industrial-900/50 border-dashed">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-medium text-white mb-1">System Information</h3>
            <div className="space-y-1 text-sm text-industrial-400 mt-4">
              <p><strong className="text-industrial-300">Frontend Version:</strong> 2.0.0</p>
              <p><strong className="text-industrial-300">Styling:</strong> Tailwind CSS (Industrial Theme)</p>
              <p><strong className="text-industrial-300">Environment:</strong> Local / Dev</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
