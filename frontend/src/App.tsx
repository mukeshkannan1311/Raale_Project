import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { DiscrepancyFinderPage } from './pages/DiscrepancyFinderPage';
import { ScanTrailExplorerPage } from './pages/ScanTrailExplorerPage';
import { WarehouseMapPage } from './pages/WarehouseMapPage';
import { AssignmentsPage } from './pages/AssignmentsPage';
import { ExperimentsPage } from './pages/ExperimentsPage';
import { EdgeCasesPage } from './pages/EdgeCasesPage';
import { ValidationPage } from './pages/ValidationPage';
import { EthicsPage } from './pages/EthicsPage';
import { DeploymentChecklistPage } from './pages/DeploymentChecklistPage';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
        <Header />

        <div className="flex-1 flex overflow-hidden">
          <Sidebar />

          <main className="flex-1 overflow-y-auto bg-slate-950/90">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/discrepancies" element={<DiscrepancyFinderPage />} />
              <Route path="/scan-trails" element={<ScanTrailExplorerPage />} />
              <Route path="/warehouse-map" element={<WarehouseMapPage />} />
              <Route path="/assignments" element={<AssignmentsPage />} />
              <Route path="/experiments" element={<ExperimentsPage />} />
              <Route path="/edge-cases" element={<EdgeCasesPage />} />
              <Route path="/validation" element={<ValidationPage />} />
              <Route path="/ethics" element={<EthicsPage />} />
              <Route path="/checklist" element={<DeploymentChecklistPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
