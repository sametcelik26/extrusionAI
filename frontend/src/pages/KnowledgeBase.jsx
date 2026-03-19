import { useState, useEffect } from 'react';
import { BookOpen, Search, Filter, Clock, CheckCircle2, XCircle } from 'lucide-react';

// Using mock data because the `/user_cases` endpoint is not defined in the backend API yet
const mockUserCases = [
  {
    id: 1,
    problem: 'Melt Fracture (Sharkskin)',
    parameters: {
      process_type: 'extrusion',
      material_type: 'PE',
      melt_temperature: 190,
      extrusion_pressure: 210,
    },
    solution_applied: 'Increased die temperature by 10°C and reduced screw speed by 5 rpm.',
    is_resolved: true,
    created_at: '2026-03-18T10:30:00Z'
  },
  {
    id: 2,
    problem: 'Short Shot',
    parameters: {
      process_type: 'injection',
      material_type: 'ABS',
      melt_temperature: 220,
      injection_pressure: 110,
      mold_temperature: 50,
    },
    solution_applied: 'Increased injection pressure and speed. Cleaned the nozzle.',
    is_resolved: true,
    created_at: '2026-03-17T14:15:00Z'
  },
  {
    id: 3,
    problem: 'Burn Marks',
    parameters: {
      process_type: 'injection',
      material_type: 'PVC',
      melt_temperature: 205,
      screw_speed: 120,
    },
    solution_applied: 'Unresolved. Escalate to maintenance. Suspected worn screw tip.',
    is_resolved: false,
    created_at: '2026-03-15T09:45:00Z'
  },
];

export default function KnowledgeBase() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setCases(mockUserCases);
      setLoading(false);
    }, 800);
    return () => clearTimeout(timer);
  }, []);

  const filteredCases = cases.filter(c => 
    c.problem.toLowerCase().includes(searchTerm.toLowerCase()) || 
    c.solution_applied.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header className="mb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-blue-400" />
            Knowledge Base & History
          </h1>
          <p className="text-industrial-400">Review past troubleshooting cases and learned solutions.</p>
        </div>
        
        <div className="relative w-full md:w-72">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-industrial-500" />
          <input 
            type="text" 
            placeholder="Search history..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10 py-2 w-full"
          />
        </div>
      </header>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-industrial-900/50 border-b border-industrial-700">
                <th className="p-4 text-xs font-semibold text-industrial-400 uppercase tracking-wider">Status</th>
                <th className="p-4 text-xs font-semibold text-industrial-400 uppercase tracking-wider">Problem</th>
                <th className="p-4 text-xs font-semibold text-industrial-400 uppercase tracking-wider">Parameters</th>
                <th className="p-4 text-xs font-semibold text-industrial-400 uppercase tracking-wider">Solution Applied</th>
                <th className="p-4 text-xs font-semibold text-industrial-400 uppercase tracking-wider">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-industrial-700/50">
              {loading ? (
                <tr>
                  <td colSpan="5" className="p-8 text-center text-industrial-400">
                    <div className="flex flex-col items-center justify-center gap-3">
                      <div className="w-8 h-8 rounded-full border-2 border-primary-500 border-t-transparent animate-spin"></div>
                      Loading history...
                    </div>
                  </td>
                </tr>
              ) : filteredCases.length === 0 ? (
                <tr>
                  <td colSpan="5" className="p-8 text-center text-industrial-400">
                    No matching cases found.
                  </td>
                </tr>
              ) : (
                filteredCases.map((c) => (
                  <tr key={c.id} className="hover:bg-industrial-800/50 transition-colors">
                    <td className="p-4 whitespace-nowrap">
                      {c.is_resolved ? (
                        <div className="flex items-center gap-2 text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded-md w-fit">
                          <CheckCircle2 className="w-4 h-4" />
                          <span className="text-xs font-medium uppercase tracking-wide">Resolved</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 text-red-500 bg-red-500/10 px-2 py-1 rounded-md w-fit">
                          <XCircle className="w-4 h-4" />
                          <span className="text-xs font-medium uppercase tracking-wide">Escalated</span>
                        </div>
                      )}
                    </td>
                    <td className="p-4">
                      <p className="font-semibold text-white">{c.problem}</p>
                    </td>
                    <td className="p-4 text-sm text-industrial-300">
                      <ul className="space-y-1">
                        {Object.entries(c.parameters).slice(0, 3).map(([k, v]) => (
                          <li key={k} className="flex justify-between gap-4">
                            <span className="capitalize text-industrial-500">{k.replace('_', ' ')}:</span>
                            <span className="font-mono text-white">{v}</span>
                          </li>
                        ))}
                        {Object.keys(c.parameters).length > 3 && (
                          <li className="text-industrial-500 italic">+{Object.keys(c.parameters).length - 3} more</li>
                        )}
                      </ul>
                    </td>
                    <td className="p-4 max-w-md">
                      <p className="text-sm text-industrial-300 line-clamp-3">{c.solution_applied}</p>
                    </td>
                    <td className="p-4 whitespace-nowrap text-sm text-industrial-400 flex items-center gap-2">
                       <Clock className="w-4 h-4" />
                       {new Date(c.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
