import axios from 'axios';

const getBaseUrl = () =>
  localStorage.getItem('extrusionai_api_url') || 'http://localhost:8000';

const api = axios.create({ timeout: 120000 });

api.interceptors.request.use((config) => {
  config.baseURL = getBaseUrl();
  return config;
});

// ── Health ──
export const healthCheck = () => api.get('/');

// ── Problems ──
export const getProblems = (params = {}) => api.get('/problems', { params });
export const getTroubleshootingSteps = (problemId) =>
  api.get(`/get_troubleshooting_steps/${problemId}`);

// ── Analysis ──
export const analyzeProblem = (processType, machineParameters) =>
  api.post('/analyze_problem', {
    process_type: processType,
    machine_parameters: machineParameters,
  });

// ── Photo Detection ──
export const uploadDefectPhoto = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload_defect_photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// ── Troubleshooting Session ──
export const startTroubleshooting = (problemId, machineParameters = null) =>
  api.post('/start_troubleshooting', {
    problem_id: problemId,
    machine_parameters: machineParameters,
  });

export const sendStepFeedback = (sessionId, solved, notes = null, customSolution = null) =>
  api.post('/step_feedback', {
    session_id: sessionId,
    solved,
    notes,
    custom_solution: customSolution,
  });

export const getSession = (sessionId) => api.get(`/session/${sessionId}`);

// ── Similar Problems ──
export const getSimilarProblems = (processType, machineParameters = {}) =>
  api.post('/get_similar_problems', {
    process_type: processType,
    machine_parameters: machineParameters,
  });

// ── Learning System ──
export const saveSolutionCase = (data) => api.post('/save_solution_case', data);

// ── Listings ──
export const getMachines = () => api.get('/machines');
export const getMaterials = () => api.get('/materials');

export default api;
