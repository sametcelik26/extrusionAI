import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getProblems, startTroubleshooting, sendStepFeedback } from '../api';
import { Wrench, CheckCircle2, ChevronRight, XCircle, AlertTriangle, Loader2 } from 'lucide-react';

export default function Troubleshooting() {
  const [searchParams] = useSearchParams();
  const initialProblemId = searchParams.get('problem_id');

  const [problems, setProblems] = useState([]);
  const [selectedProblemId, setSelectedProblemId] = useState(initialProblemId || '');
  
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [customSolution, setCustomSolution] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  useEffect(() => {
    async function loadProblems() {
      try {
        const res = await getProblems();
        setProblems(res.data);
      } catch (err) {
        console.error('Failed to load problems', err);
      }
    }
    loadProblems();
  }, []);

  const handleStart = async () => {
    if (!selectedProblemId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await startTroubleshooting(Number(selectedProblemId));
      setSession(res.data);
      setShowCustomInput(false);
      setCustomSolution('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start session.');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (solved, isCustom = false) => {
    if (!session) return;
    setLoading(true);
    setError(null);

    try {
      const res = await sendStepFeedback(
        session.session_id,
        solved,
        null, // notes placeholder
        isCustom ? customSolution : null
      );
      setSession(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record feedback.');
    } finally {
      setLoading(false);
    }
  };

  const resetSession = () => {
    setSession(null);
    setSelectedProblemId('');
    setShowCustomInput(false);
    setCustomSolution('');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <Wrench className="w-8 h-8 text-accent-500" />
          Smart Troubleshooting
        </h1>
        <p className="text-industrial-400">Step-by-step interactive guide to resolve production anomalies.</p>
      </header>

      {error && (
        <div className="card border-red-500/50 bg-red-500/10 mb-6 flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-red-500 shrink-0" />
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Select Problem / Initialization */}
      {!session && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Select an Issue to Resolve</h2>
          <div className="flex gap-4 items-end">
            <div className="flex-1 space-y-2">
              <label className="text-sm text-industrial-300 font-medium">Common Problems</label>
              <select
                value={selectedProblemId}
                onChange={(e) => setSelectedProblemId(e.target.value)}
                className="input-field py-3"
              >
                <option value="">-- Select a problem --</option>
                {problems.map((p) => (
                  <option key={p.id} value={p.id}>{p.problem_name}</option>
                ))}
              </select>
            </div>
            <button
              onClick={handleStart}
              disabled={loading || !selectedProblemId}
              className="btn-primary w-40 flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Start Session'}
            </button>
          </div>
        </div>
      )}

      {/* Active Session View */}
      {session && session.status === 'in_progress' && (
        <div className="card border-accent-500/30">
          <div className="flex items-center justify-between mb-8 pb-4 border-b border-industrial-700">
            <div>
              <p className="text-sm font-semibold text-accent-500 uppercase tracking-widest mb-1">Active Session</p>
              <h2 className="text-2xl font-bold text-white capitalize">{session.problem_name.replace(/_/g, ' ')}</h2>
            </div>
            <div className="text-right">
              <p className="text-4xl font-black text-industrial-100">{session.current_step_order}<span className="text-2xl text-industrial-500">/{session.total_steps}</span></p>
              <p className="text-xs font-medium text-industrial-400 uppercase tracking-widest mt-1">Current Step</p>
            </div>
          </div>

          <div className="min-h-[200px] flex flex-col justify-center mb-8">
            <div className="bg-industrial-900 border border-industrial-700 p-8 rounded-xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-accent-500"></div>
              <p className="text-xl text-white leading-relaxed font-medium">
                {session.current_step?.description || session.message}
              </p>
              {session.current_step?.details && (
                <p className="mt-4 text-industrial-400 text-sm">
                  <span className="font-semibold text-industrial-300">Details: </span>
                  {session.current_step.details}
                </p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-industrial-700">
            <button
              onClick={() => handleFeedback(true)}
              disabled={loading}
              className="btn-success flex items-center justify-center gap-2 py-4 text-lg"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <CheckCircle2 className="w-6 h-6" />}
              Fixed (Done)
            </button>
            <button
              onClick={() => handleFeedback(false)}
              disabled={loading}
              className="btn-danger flex items-center justify-center gap-2 py-4 text-lg"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <XCircle className="w-6 h-6" />}
              Not Fixed (Next Step)
            </button>
          </div>
          
          <div className="mt-6 pt-4 text-center">
            {!showCustomInput ? (
              <button onClick={() => setShowCustomInput(true)} className="text-sm text-industrial-400 hover:text-white underline underline-offset-4 transition-colors">
                I fixed it using a completely different method
              </button>
            ) : (
              <div className="text-left bg-industrial-900 p-4 rounded-lg border border-industrial-700 max-w-xl mx-auto space-y-3">
                <label className="text-sm font-semibold text-white">Share your custom solution to improve the AI:</label>
                <textarea 
                  className="input-field w-full min-h-[80px]" 
                  placeholder="Describe exactly how you fixed the issue..."
                  value={customSolution}
                  onChange={(e) => setCustomSolution(e.target.value)}
                ></textarea>
                <div className="flex gap-2">
                  <button onClick={() => handleFeedback(true, true)} disabled={!customSolution || loading} className="btn-success text-sm py-2 px-4">
                    Submit Learning & Close
                  </button>
                  <button onClick={() => setShowCustomInput(false)} className="btn-secondary text-sm py-2 px-4 bg-transparent">
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Resolved State */}
      {session && session.status === 'resolved' && (
        <div className="card border-emerald-500/30 bg-emerald-500/5 text-center p-12 animate-in fade-in slide-in-from-bottom-4">
          <CheckCircle2 className="w-20 h-20 text-emerald-500 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-white mb-2">Problem Resolved!</h2>
          <p className="text-industrial-300 max-w-md mx-auto mb-8">
            {session.message} This case has been securely logged to the Knowledge Base to help future operators.
          </p>
          <button onClick={resetSession} className="btn-primary bg-emerald-600 hover:bg-emerald-500">
            Start Another Session
          </button>
        </div>
      )}

      {/* Escalated State */}
      {session && session.status === 'escalated' && (
        <div className="card border-red-500/30 bg-red-500/5 text-center p-12 animate-in fade-in slide-in-from-bottom-4">
          <AlertTriangle className="w-20 h-20 text-red-500 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-white mb-2">Steps Exhausted</h2>
          <p className="text-industrial-300 max-w-md mx-auto mb-8">
            You've reached the end of the standard troubleshooting guide. The issue has been logged as unresolved. 
            Please escalate to Level 2 technical support or maintenance immediately.
          </p>
          <div className="flex justify-center gap-4">
            <button onClick={resetSession} className="btn-secondary">
              Go Back
            </button>
            <button onClick={() => setShowCustomInput(true)} className="btn-primary bg-red-600/80 hover:bg-red-600">
               I Fixed It Manually
            </button>
          </div>
          
          {showCustomInput && (
             <div className="mt-8 text-left bg-industrial-900 p-6 rounded-lg border border-industrial-700 max-w-xl mx-auto space-y-4">
               <label className="text-sm font-semibold text-white">How did you end up fixing it?</label>
               <textarea 
                 className="input-field w-full min-h-[100px]" 
                 placeholder="Maintenance replaced the heater band..."
                 value={customSolution}
                 onChange={(e) => setCustomSolution(e.target.value)}
               ></textarea>
               <div className="flex justify-end">
                 <button onClick={() => handleFeedback(true, true)} disabled={!customSolution || loading} className="btn-success">
                   Submit Resolution
                 </button>
               </div>
             </div>
          )}
        </div>
      )}
    </div>
  );
}
