import React, { useState } from 'react';
import { Play, CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck, RefreshCw, Zap } from 'lucide-react';
import { api } from '../services/api';

export const DemoScenarioBanner: React.FC = () => {
  const [step, setStep] = useState<number>(1);
  const [status, setStatus] = useState<string>('SUSPECTED');
  const [loading, setLoading] = useState<boolean>(false);

  const handleVerify = async () => {
    setLoading(true);
    try {
      await api.verifyDiscrepancy('DISC-MED-1042', 'Verified physically by supervisor.');
      setStatus('LOCATED');
      setStep(4);
    } catch (e) {
      setStatus('LOCATED');
      setStep(4);
    } finally {
      setLoading(false);
    }
  };

  const handleCorrect = async () => {
    setLoading(true);
    try {
      await api.correctDiscrepancy('DISC-MED-1042', 'COLD-02-R01-B03', 'Inventory location record updated in WMS database.');
      setStatus('CORRECTED');
      setStep(5);
    } catch (e) {
      setStatus('CORRECTED');
      setStep(5);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStep(1);
    setStatus('SUSPECTED');
  };

  return (
    <div className="rounded-xl border border-cyan-500/30 bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 p-5 shadow-xl relative overflow-hidden mb-6">
      <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl -z-10 pointer-events-none" />

      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-white text-base flex items-center gap-2">
              Interactive Demo Scenario: MED-1042 Inventory Search
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono">
                Guided Walkthrough
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Controlled Cold-Storage Vaccine Discrepancy & Machine Learning Resolution Pipeline
            </p>
          </div>
        </div>

        <button
          onClick={handleReset}
          className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset Demo</span>
        </button>
      </div>

      {/* Workflow Progress Steps */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mt-4">
        {/* Step 1 */}
        <div className={`p-3 rounded-lg border text-xs transition ${step === 1 ? 'border-amber-500/50 bg-amber-500/10 text-amber-300' : 'border-slate-800 bg-slate-900/60 text-slate-400'}`}>
          <div className="flex items-center justify-between font-semibold mb-1">
            <span>1. Pick Failure</span>
            <span className="text-[10px] opacity-70">MED-1042</span>
          </div>
          <p className="text-[11px] leading-tight opacity-90">System expected location: <span className="font-mono text-white">A-03-R02-B04</span>. Picker reported "Stock Not Found".</p>
          {step === 1 && (
            <button
              onClick={() => setStep(2)}
              className="mt-2.5 w-full py-1.5 bg-amber-500 text-slate-950 font-bold rounded text-[11px] flex items-center justify-center gap-1"
            >
              <span>Analyze Trails</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>

        {/* Step 2 */}
        <div className={`p-3 rounded-lg border text-xs transition ${step === 2 ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-300' : 'border-slate-800 bg-slate-900/60 text-slate-400'}`}>
          <div className="flex items-center justify-between font-semibold mb-1">
            <span>2. ML Analysis</span>
            <span className="text-[10px] opacity-70">Probabilistic</span>
          </div>
          <p className="text-[11px] leading-tight opacity-90">Engine evaluated 4 scan events + cycle count evidence across candidate bins.</p>
          {step === 2 && (
            <button
              onClick={() => setStep(3)}
              className="mt-2.5 w-full py-1.5 bg-cyan-500 text-slate-950 font-bold rounded text-[11px] flex items-center justify-center gap-1"
            >
              <span>View Prediction</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>

        {/* Step 3 */}
        <div className={`p-3 rounded-lg border text-xs transition ${step === 3 ? 'border-blue-500/50 bg-blue-500/10 text-blue-300' : 'border-slate-800 bg-slate-900/60 text-slate-400'}`}>
          <div className="flex items-center justify-between font-semibold mb-1">
            <span>3. Recommendation</span>
            <span className="text-[10px] text-emerald-400 font-mono font-bold">91.4% Prob</span>
          </div>
          <p className="text-[11px] leading-tight opacity-90">Predicted location: <span className="font-mono text-emerald-400 font-bold">COLD-02-R01-B03</span>. Passed all safety rules.</p>
          {step === 3 && (
            <button
              onClick={handleVerify}
              disabled={loading}
              className="mt-2.5 w-full py-1.5 bg-emerald-500 text-slate-950 font-bold rounded text-[11px] flex items-center justify-center gap-1 hover:bg-emerald-400 transition"
            >
              {loading ? <RefreshCw className="w-3 h-3 animate-spin" /> : <ShieldCheck className="w-3 h-3" />}
              <span>Verify Location</span>
            </button>
          )}
        </div>

        {/* Step 4 */}
        <div className={`p-3 rounded-lg border text-xs transition ${step === 4 ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300' : 'border-slate-800 bg-slate-900/60 text-slate-400'}`}>
          <div className="flex items-center justify-between font-semibold mb-1">
            <span>4. Physical Audit</span>
            <span className="text-[10px] text-emerald-400">LOCATED</span>
          </div>
          <p className="text-[11px] leading-tight opacity-90">Supervisor physically confirmed 100 units at COLD-02-R01-B03.</p>
          {step === 4 && (
            <button
              onClick={handleCorrect}
              disabled={loading}
              className="mt-2.5 w-full py-1.5 bg-emerald-400 text-slate-950 font-bold rounded text-[11px] flex items-center justify-center gap-1 hover:bg-emerald-300 transition"
            >
              {loading ? <RefreshCw className="w-3 h-3 animate-spin" /> : <CheckCircle2 className="w-3 h-3" />}
              <span>Mark Corrected</span>
            </button>
          )}
        </div>

        {/* Step 5 */}
        <div className={`p-3 rounded-lg border text-xs transition ${step === 5 ? 'border-emerald-500 bg-emerald-500/20 text-emerald-300' : 'border-slate-800 bg-slate-900/60 text-slate-400'}`}>
          <div className="flex items-center justify-between font-semibold mb-1">
            <span>5. Resolved</span>
            <span className="text-[10px] font-bold text-emerald-400">COMPLETE</span>
          </div>
          <p className="text-[11px] leading-tight opacity-90">Record updated in database. SLA deadline met; zero safety violations.</p>
          {step === 5 && (
            <div className="mt-2 text-[10px] text-emerald-400 flex items-center gap-1 font-semibold">
              <CheckCircle2 className="w-3 h-3" />
              <span>Resolved in 14.2 min</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
