/* Shared UI helpers */

export function SeverityBadge({ severity }) {
  const map = {
    low: 'badge-severity-low',
    medium: 'badge-severity-medium',
    high: 'badge-severity-high',
    critical: 'badge-severity-critical',
  };
  return <span className={map[severity] || 'badge bg-industrial-600 text-industrial-300'}>{severity}</span>;
}

export function ProcessBadge({ processType }) {
  const map = {
    extrusion: 'badge-process-extrusion',
    injection: 'badge-process-injection',
    blow_molding: 'badge-process-blow_molding',
  };
  const labels = { extrusion: 'Extrusion', injection: 'Injection', blow_molding: 'Blow Molding' };
  return (
    <span className={map[processType] || 'badge bg-industrial-600 text-industrial-300'}>
      {labels[processType] || processType}
    </span>
  );
}

export function ConfidenceBadge({ confidence }) {
  if (confidence == null) return null;
  const pct = Math.round(confidence * 100);
  let cls = 'bg-red-500/20 text-red-400';
  if (pct >= 70) cls = 'bg-emerald-500/20 text-emerald-400';
  else if (pct >= 40) cls = 'bg-yellow-500/20 text-yellow-400';
  return <span className={`badge ${cls}`}>{pct}% confidence</span>;
}

export function SourceBadge({ source }) {
  if (source === 'user_learned')
    return <span className="badge bg-emerald-500/20 text-emerald-400">Learned</span>;
  return <span className="badge bg-blue-500/20 text-blue-400">Expert</span>;
}

export function Spinner({ size = 'md', text = 'Loading...' }) {
  const s = size === 'sm' ? 'w-5 h-5' : size === 'lg' ? 'w-10 h-10' : 'w-7 h-7';
  return (
    <div className="flex items-center justify-center gap-3 py-8">
      <div className={`${s} border-2 border-industrial-600 border-t-accent-500 rounded-full animate-spin`} />
      {text && <span className="text-industrial-400 text-sm">{text}</span>}
    </div>
  );
}

export function InfoBanner({ children, type = 'info' }) {
  const styles = {
    info: 'bg-blue-500/10 border-blue-500/30 text-blue-300',
    warning: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-300',
    success: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
    error: 'bg-red-500/10 border-red-500/30 text-red-300',
  };
  return (
    <div className={`border rounded-lg px-4 py-3 text-sm ${styles[type] || styles.info}`}>
      {children}
    </div>
  );
}

export function ProgressBar({ current, total }) {
  const pct = total > 0 ? (current / total) * 100 : 0;
  return (
    <div className="w-full bg-industrial-700 rounded-full h-2.5 overflow-hidden">
      <div
        className="bg-accent-500 h-full rounded-full transition-all duration-500"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
