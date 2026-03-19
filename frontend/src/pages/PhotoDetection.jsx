import { useState, useRef } from 'react';
import { uploadDefectPhoto } from '../api';
import { Camera, UploadCloud, Loader2, AlertTriangle, CheckCircle2, X } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function PhotoDetection() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile) => {
    // Only accept images
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select a valid image file.');
      return;
    }
    
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setError(null);
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const res = await uploadDefectPhoto(file);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to detect defects. Please try again.');
    } finally {
      setLoading(false);
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
            <Camera className="w-8 h-8 text-teal-400" />
            Photo Detection
          </h1>
          <p className="text-industrial-400">Upload an image of a defective part for instant AI classification.</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="card flex flex-col items-center justify-center p-8">
          {!preview ? (
            <div
              className={`w-full aspect-square md:aspect-video rounded-xl border-2 border-dashed flex flex-col items-center justify-center p-8 transition-colors cursor-pointer
                ${isDragging ? 'border-teal-500 bg-teal-500/10' : 'border-industrial-600 bg-industrial-900 hover:border-teal-500/50 hover:bg-industrial-800'}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadCloud className={`w-12 h-12 mb-4 ${isDragging ? 'text-teal-400' : 'text-industrial-500'}`} />
              <p className="text-white font-medium mb-1">Drag and drop your image here</p>
              <p className="text-industrial-400 text-sm mb-4">or click to browse from your device</p>
              <span className="btn-secondary pointer-events-none">Select File</span>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleChange}
                accept="image/jpeg, image/png, image/webp"
                className="hidden"
              />
            </div>
          ) : (
            <div className="w-full">
              <div className="relative rounded-xl overflow-hidden border border-industrial-700 bg-industrial-950 aspect-square md:aspect-video flex items-center justify-center">
                <img src={preview} alt="Defect preview" className="max-w-full max-h-full object-contain" />
                <button
                  onClick={clearFile}
                  className="absolute top-3 right-3 p-2 bg-industrial-900/80 hover:bg-red-500/20 hover:text-red-400 text-white rounded-lg backdrop-blur-sm transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="mt-6 btn-primary bg-teal-600 hover:bg-teal-500 text-white w-full flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Scanning Image...
                  </>
                ) : (
                  <>
                    <Camera className="w-5 h-5" />
                    Detect Defect
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          {error && (
            <div className="card border-red-500/50 bg-red-500/10">
              <div className="flex gap-3">
                <AlertTriangle className="w-6 h-6 text-red-500 shrink-0" />
                <div>
                  <h3 className="text-red-400 font-semibold">Detection Failed</h3>
                  <p className="text-red-300/80 text-sm mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {!result && !error && !loading && (
            <div className="card h-full flex flex-col items-center justify-center text-center p-12 border-dashed">
              <Camera className="w-16 h-16 text-industrial-600 mb-4" />
              <h3 className="text-xl font-medium text-industrial-300 mb-2">Ready to Scan</h3>
              <p className="text-industrial-500 text-sm max-w-xs">Upload a clear photo of the produced part to identify visual defects.</p>
            </div>
          )}

          {loading && (
            <div className="card h-full flex flex-col items-center justify-center text-center p-12 border-teal-500/20 bg-teal-900/10 animate-pulse">
              <Loader2 className="w-16 h-16 text-teal-500 animate-spin mb-4" />
              <h3 className="text-xl font-medium text-teal-400 mb-2">Analyzing image...</h3>
              <p className="text-teal-500/60 text-sm max-w-xs">Using computer vision to detect surface anomalies and structural flaws.</p>
            </div>
          )}

          {result && (
            <div className="card border-teal-500/30 shadow-lg shadow-teal-500/5 animate-in fade-in slide-in-from-bottom-2 duration-500">
              {result.detected_defects && result.detected_defects.length > 0 ? (
                <div>
                  <h2 className="text-industrial-400 text-sm font-medium uppercase tracking-wider mb-4">Detected Defects</h2>
                  <div className="space-y-4 mb-6">
                    {result.detected_defects.map((defect, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 rounded-lg bg-industrial-900 border border-industrial-700">
                        <span className="text-lg font-bold text-white capitalize">{defect.defect_name.replace(/_/g, ' ')}</span>
                        <div className={`flex flex-col items-end px-3 py-1.5 rounded-lg border ${getConfidenceColor(defect.confidence)}`}>
                          <span className="text-[10px] font-bold uppercase tracking-wide">Confidence</span>
                          <span className="text-lg font-black">{Math.round(defect.confidence * 100)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {result.ai_raw_response && (
                    <div className="mb-6">
                      <h4 className="text-industrial-400 text-xs font-semibold uppercase tracking-wider mb-2">AI Explanation</h4>
                      <div className="p-4 rounded-lg bg-industrial-950 text-sm text-industrial-300 border border-industrial-800">
                        {result.ai_raw_response}
                      </div>
                    </div>
                  )}

                  {result.matched_problems && result.matched_problems.length > 0 && (
                    <div>
                      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-teal-400" />
                        Related Knowledge Base Entries
                      </h4>
                      <ul className="space-y-2 text-sm text-industrial-300">
                        {result.matched_problems.map((p) => (
                          <li key={p.id} className="flex gap-2">
                            <span className="text-teal-500 font-bold">•</span>
                            <span>{p.problem_name}</span>
                          </li>
                        ))}
                      </ul>
                      
                      <div className="mt-6 pt-6 border-t border-industrial-700">
                        <Link 
                          to={`/troubleshoot?problem_id=${result.matched_problems[0].id}`} 
                          className="btn-secondary w-full text-center block hover:border-teal-500/50 hover:text-teal-400"
                        >
                          Start Interactive Troubleshooting
                        </Link>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center p-6">
                  <CheckCircle2 className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-white mb-2">No Defects Detected</h3>
                  <p className="text-industrial-400 text-sm">The part appears to meet quality standards based on the provided image.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
