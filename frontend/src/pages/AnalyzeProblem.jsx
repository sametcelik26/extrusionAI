import { useState, useRef } from 'react';
import { analyzeProblem, startTroubleshooting, sendStepFeedback } from '../api';
import { Settings2, Cpu, AlertTriangle, CheckCircle2, Loader2, ThermometerSun, Gauge, Zap, XCircle, Camera, UploadCloud, X } from 'lucide-react';

export default function AnalyzeProblem() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [session, setSession] = useState(null);
  const [sessionLoading, setSessionLoading] = useState(false);
  const [customSolution, setCustomSolution] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const [formData, setFormData] = useState({
    process_type: 'extrusion',
    material_type: 'PP',
    problem_description: '',
    melt_temperature: 180,
    extrusion_pressure: 120,
    screw_speed: 60,
    die_temperature: 190,
    mold_temperature: 40,
    cooling_time: 15,
    cycle_time: 30,
    regrind_percentage: 10,
  });

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false); };
  const handleDrop = (e) => {
    e.preventDefault(); setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFileSelection(e.dataTransfer.files[0]);
  };
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) handleFileSelection(e.target.files[0]);
  };
  const handleFileSelection = (selectedFile) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select a valid image file.');
      return;
    }
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setError(null);
  };
  const clearFile = () => {
    setFile(null); setPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: e.target.type === 'range' ? Number(value) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setSession(null);
    setShowCustomInput(false);
    setCustomSolution('');

    try {
      let imageBase64 = null;
      if (file) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        await new Promise((resolve, reject) => {
          reader.onload = () => resolve();
          reader.onerror = reject;
        });
        imageBase64 = reader.result.split(',')[1];
      }

      // Format as expected by backend: process_type string, machine_parameters dict
      const { process_type, ...machineParams } = formData;
      console.log('API Request Payload:', { process_type, machine_parameters: machineParams, has_image: !!imageBase64 });
      
      const res = await analyzeProblem(process_type, machineParams, imageBase64);
      console.log('API Response:', res.data);
      setResult(res.data);

      if (res.data.problem) {
        setSessionLoading(true);
        try {
          const sessionRes = await startTroubleshooting(res.data.problem.id, machineParams);
          setSession(sessionRes.data);
        } catch (sessErr) {
          console.error("Failed to start session:", sessErr);
        } finally {
          setSessionLoading(false);
        }
      }
    } catch (err) {
      console.error("API Error:", err);
      setError('AI analysis failed. Please check backend or Ollama connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (solved, isCustom = false) => {
    if (!session) return;
    setSessionLoading(true);

    try {
      const res = await sendStepFeedback(
        session.session_id,
        solved,
        null,
        isCustom ? customSolution : null
      );
      setSession(res.data);
    } catch (err) {
      console.error('Failed to record feedback:', err);
    } finally {
      setSessionLoading(false);
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
    if (score >= 0.5) return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
    return 'text-red-500 bg-red-500/10 border-red-500/20';
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <Settings2 className="w-8 h-8 text-primary-400" />
            Problem Analysis
          </h1>
          <p className="text-industrial-400">Enter your current machine parameters to get an AI-powered diagnosis.</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form Section */}
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-industrial-300">Process Type</label>
                <select name="process_type" value={formData.process_type} onChange={handleChange} className="input-field py-2">
                  <option value="extrusion">Extrusion</option>
                  <option value="injection">Injection Molding</option>
                  <option value="blow_molding">Blow Molding</option>
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-industrial-300">Material</label>
                <select name="material_type" value={formData.material_type} onChange={handleChange} className="input-field py-2">
                  <option value="PP">Polypropylene (PP)</option>
                  <option value="PE">Polyethylene (PE)</option>
                  <option value="PVC">Polyvinyl Chloride (PVC)</option>
                  <option value="ABS">Acrylonitrile Butadiene Styrene (ABS)</option>
                  <option value="PET">Polyethylene Terephthalate (PET)</option>
                </select>
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-sm font-medium text-industrial-300">Problem Description</label>
              <textarea
                name="problem_description"
                value={formData.problem_description}
                onChange={handleChange}
                className="input-field py-2 w-full"
                placeholder="Describe the issue you are facing..."
                rows="3"
              />
            </div>

            {/* Image Upload Area */}
            <div className="space-y-2">
              <div className="flex justify-between items-end">
                <label className="text-sm font-medium text-industrial-300">Defect Image (Optional)</label>
                <span className="text-[10px] text-industrial-500 uppercase tracking-widest bg-industrial-800 px-2 py-0.5 rounded">Vision AI</span>
              </div>
              {!preview ? (
                <div
                  className={`w-full rounded-lg border-2 border-dashed flex flex-col items-center justify-center p-6 cursor-pointer transition-colors
                    ${isDragging ? 'border-primary-500 bg-primary-500/10' : 'border-industrial-700 bg-industrial-900/50 hover:border-primary-500/50'}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Camera className={`w-8 h-8 mb-2 ${isDragging ? 'text-primary-400' : 'text-industrial-500'}`} />
                  <p className="text-sm text-industrial-300 text-center font-medium">Click to use camera or upload photo</p>
                  <p className="text-xs text-industrial-500 mt-1">Supports drag and drop</p>
                </div>
              ) : (
                <div className="relative rounded-lg overflow-hidden border border-industrial-700 bg-industrial-950 flex items-center justify-center p-2">
                  <img src={preview} alt="Defect" className="max-h-48 rounded object-contain" />
                  <button
                    type="button"
                    onClick={clearFile}
                    className="absolute top-2 right-2 p-1.5 bg-industrial-900/80 hover:bg-red-500/20 hover:text-red-400 text-white rounded backdrop-blur-sm transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                capture="environment"
                className="hidden"
              />
            </div>

            <hr className="border-industrial-700" />

            <div className="space-y-4">
              {/* Sliders */}
              {[
                { name: 'melt_temperature', label: 'Melt Temp (°C)', min: 100, max: 350, icon: ThermometerSun },
                { name: 'die_temperature', label: 'Die Temp (°C)', min: 100, max: 350, icon: ThermometerSun },
                { name: 'extrusion_pressure', label: 'Pressure (bar)', min: 10, max: 300, icon: Gauge },
                { name: 'screw_speed', label: 'Screw Speed (rpm)', min: 5, max: 200, icon: Zap },
                { name: 'mold_temperature', label: 'Mold Temp (°C)', min: 10, max: 150, icon: ThermometerSun },
                { name: 'cooling_time', label: 'Cooling Time (s)', min: 1, max: 120, icon: Zap },
                { name: 'cycle_time', label: 'Cycle Time (s)', min: 2, max: 180, icon: Zap },
                { name: 'regrind_percentage', label: 'Regrind (%)', min: 0, max: 100, icon: Settings2 },
              ].map((field) => (
                <div key={field.name} className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <label className="font-medium text-industrial-300 flex items-center gap-2">
                      <field.icon className="w-4 h-4 text-industrial-500" />
                      {field.label}
                    </label>
                    <span className="text-white font-mono bg-industrial-900 px-2 py-0.5 rounded border border-industrial-700">
                      {formData[field.name]}
                    </span>
                  </div>
                  <input
                    type="range"
                    name={field.name}
                    min={field.min}
                    max={field.max}
                    value={formData[field.name]}
                    onChange={handleChange}
                    className="w-full h-2 bg-industrial-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
                  />
                </div>
              ))}
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Cpu className="w-5 h-5" />
                  Run AI Diagnosis
                </>
              )}
            </button>
          </form>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          {error && (
            <div className="card border-red-500/50 bg-red-500/10">
              <div className="flex gap-3">
                <AlertTriangle className="w-6 h-6 text-red-500 shrink-0" />
                <div>
                  <h3 className="text-red-400 font-semibold">Diagnosis Failed</h3>
                  <p className="text-red-300/80 text-sm mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {!result && !error && !loading && (
            <div className="card h-full flex flex-col items-center justify-center text-center p-12 border-dashed">
              <Cpu className="w-16 h-16 text-industrial-600 mb-4" />
              <h3 className="text-xl font-medium text-industrial-300 mb-2">Awaiting Parameters</h3>
              <p className="text-industrial-500 text-sm max-w-xs">Adjust the sliders on the left and run the diagnosis to view AI insights.</p>
            </div>
          )}

          {loading && (
            <div className="card h-full flex flex-col items-center justify-center text-center p-12 border-primary-500/20 bg-primary-900/10 animate-pulse">
              <Loader2 className="w-16 h-16 text-primary-500 animate-spin mb-4" />
              <h3 className="text-xl font-medium text-primary-400 mb-2">Analyzing problem...</h3>
            </div>
          )}

          {result && (
            <div className="card border-primary-500/30 shadow-lg shadow-primary-500/5 animate-in fade-in slide-in-from-bottom-2 duration-500">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-industrial-400 text-sm font-medium uppercase tracking-wider mb-1">Detected Issue</h2>
                  <h3 className="text-2xl font-bold text-white">
                    {result.ai_suggestion || result.problem?.problem_name || 'Unknown Condition'}
                  </h3>
                </div>
                <div className={`flex flex-col items-end px-3 py-1.5 rounded-lg border ${getConfidenceColor(result.confidence)}`}>
                  <span className="text-xs font-bold uppercase tracking-wide">Confidence</span>
                  <span className="text-xl font-black">{Math.round(result.confidence * 100)}%</span>
                </div>
              </div>

              {result.reasoning && (
                <div className="mb-6 p-4 rounded-lg bg-industrial-900/50 flex gap-3 text-sm text-industrial-300 border border-industrial-700/50">
                  <AlertTriangle className="w-5 h-5 text-accent-500 shrink-0" />
                  <p>{result.reasoning}</p>
                </div>
              )}

              {session && session.status === 'in_progress' && (
                <div className="mt-6 pt-6 border-t border-industrial-700 animate-in fade-in slide-in-from-bottom-2">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-white font-semibold flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-primary-400" />
                      Troubleshooting - Step {session.current_step_order} of {session.total_steps}
                    </h4>
                  </div>
                  <div className="bg-industrial-900 border border-industrial-700 p-6 rounded-xl relative overflow-hidden mb-6">
                    <div className="absolute top-0 left-0 w-1 h-full bg-accent-500"></div>
                    <p className="text-lg text-white font-medium">
                      {session.current_step?.description || session.message}
                    </p>
                    {session.current_step?.details && (
                      <p className="mt-2 text-industrial-400 text-sm">
                        <span className="font-semibold text-industrial-300">Details: </span>
                        {session.current_step.details}
                      </p>
                    )}
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <button
                      onClick={() => handleFeedback(true)}
                      disabled={sessionLoading}
                      className="btn-success flex items-center justify-center gap-2 py-3"
                    >
                      {sessionLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <CheckCircle2 className="w-5 h-5" />}
                      Solved
                    </button>
                    <button
                      onClick={() => handleFeedback(false)}
                      disabled={sessionLoading}
                      className="btn-danger flex items-center justify-center gap-2 py-3"
                    >
                      {sessionLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <XCircle className="w-5 h-5" />}
                      Not Solved
                    </button>
                  </div>
                  
                  <div className="mt-4 text-center">
                    {!showCustomInput ? (
                      <button onClick={() => setShowCustomInput(true)} className="text-sm text-industrial-400 hover:text-white underline underline-offset-4 transition-colors">
                        Fixed using a different method
                      </button>
                    ) : (
                      <div className="text-left bg-industrial-900 p-4 rounded-lg border border-industrial-700 max-w-xl mx-auto space-y-3 mt-4">
                        <label className="text-sm font-semibold text-white">Share your custom solution:</label>
                        <textarea 
                          className="input-field w-full min-h-[80px]" 
                          placeholder="Describe exactly how you fixed the issue..."
                          value={customSolution}
                          onChange={(e) => setCustomSolution(e.target.value)}
                        ></textarea>
                        <div className="flex gap-2">
                          <button onClick={() => handleFeedback(true, true)} disabled={!customSolution || sessionLoading} className="btn-success text-sm py-2 px-4">
                            Save Solution
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

              {session && session.status === 'resolved' && (
                <div className="mt-6 pt-6 border-t border-industrial-700 animate-in fade-in slide-in-from-bottom-2 text-center p-6 bg-emerald-500/10 border-emerald-500/20 rounded-xl">
                  <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
                  <h4 className="text-xl font-bold text-white mb-2">Problem Resolved!</h4>
                  <p className="text-industrial-300 text-sm">{session.message}</p>
                </div>
              )}

              {session && session.status === 'escalated' && (
                <div className="mt-6 pt-6 border-t border-industrial-700 animate-in fade-in slide-in-from-bottom-2 text-center p-6 bg-red-500/10 border-red-500/20 rounded-xl">
                  <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                  <h4 className="text-xl font-bold text-white mb-2">Steps Exhausted</h4>
                  <p className="text-industrial-300 text-sm mb-4">Please manually escalate this issue to maintenance.</p>
                  
                  {!showCustomInput ? (
                    <button onClick={() => setShowCustomInput(true)} className="btn-primary bg-red-600 hover:bg-red-500 text-sm">
                      I Fixed It Manually
                    </button>
                  ) : (
                    <div className="text-left bg-industrial-900 p-4 rounded-lg border border-industrial-700 mt-4 space-y-3">
                      <label className="text-sm font-semibold text-white">How did you end up fixing it?</label>
                      <textarea 
                        className="input-field w-full min-h-[80px]" 
                        placeholder="Maintenance replaced the heater band..."
                        value={customSolution}
                        onChange={(e) => setCustomSolution(e.target.value)}
                      ></textarea>
                      <div className="flex gap-2">
                        <button onClick={() => handleFeedback(true, true)} disabled={!customSolution || sessionLoading} className="btn-success text-sm py-2 px-4">
                          Submit Resolution
                        </button>
                        <button onClick={() => setShowCustomInput(false)} className="btn-secondary text-sm py-2 px-4 bg-transparent">
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
