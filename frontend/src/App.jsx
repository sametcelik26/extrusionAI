import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import AnalyzeProblem from './pages/AnalyzeProblem';
import PhotoDetection from './pages/PhotoDetection';
import Troubleshooting from './pages/Troubleshooting';
import KnowledgeBase from './pages/KnowledgeBase';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analyze" element={<AnalyzeProblem />} />
          <Route path="/photo" element={<PhotoDetection />} />
          <Route path="/troubleshoot" element={<Troubleshooting />} />
          <Route path="/knowledge" element={<KnowledgeBase />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
