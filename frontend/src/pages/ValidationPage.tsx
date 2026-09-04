import React, { useState, useEffect } from 'react';
import { CheckCircle2, Star, Send, MessageSquare, ThumbsUp, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { ValidationSummary } from '../types';

export const ValidationPage: React.FC = () => {
  const [data, setData] = useState<ValidationSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [submitted, setSubmitted] = useState<boolean>(false);

  // Form State
  const [role, setRole] = useState('WAREHOUSE_OPERATOR');
  const [understanding, setUnderstanding] = useState(5);
  const [usefulness, setUsefulness] = useState(5);
  const [clarity, setClarity] = useState(5);
  const [safety, setSafety] = useState(5);
  const [reduction, setReduction] = useState(5);
  const [overall, setOverall] = useState(5);
  const [comments, setComments] = useState('');

  const loadValidation = async () => {
    setLoading(true);
    try {
      const res = await api.getValidationSummary();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadValidation();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.submitValidation({
        user_role: role,
        ease_of_understanding: understanding,
        usefulness_rating: usefulness,
        evidence_clarity: clarity,
        workflow_safety: safety,
        search_time_reduction: reduction,
        overall_rating: overall,
        comments: comments,
      });
      setSubmitted(true);
      loadValidation();
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-cyan-400" />
          Stakeholder Operational Validation
        </h2>
        <p className="text-xs text-slate-400">
          User feedback & utility evaluations collected from warehouse leads, inspectors, and pickers
        </p>
      </div>

      {/* Summary Averages Cards */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
            <span className="text-xs text-slate-400">Overall Usefulness</span>
            <div className="text-2xl font-bold text-cyan-400 mt-1 flex items-center justify-center gap-1">
              <span>{data.averages.overall_usefulness}</span>
              <Star className="w-4 h-4 fill-cyan-400 text-cyan-400" />
            </div>
            <span className="text-[10px] text-slate-500">/ 5.0 Rating</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
            <span className="text-xs text-slate-400">Evidence Clarity</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1 flex items-center justify-center gap-1">
              <span>{data.averages.evidence_clarity}</span>
              <Star className="w-4 h-4 fill-emerald-400 text-emerald-400" />
            </div>
            <span className="text-[10px] text-slate-500">/ 5.0 Rating</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
            <span className="text-xs text-slate-400">Workflow Safety</span>
            <div className="text-2xl font-bold text-blue-400 mt-1 flex items-center justify-center gap-1">
              <span>{data.averages.workflow_safety}</span>
              <Star className="w-4 h-4 fill-blue-400 text-blue-400" />
            </div>
            <span className="text-[10px] text-slate-500">/ 5.0 Rating</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
            <span className="text-xs text-slate-400">Time Reduction</span>
            <div className="text-2xl font-bold text-purple-400 mt-1 flex items-center justify-center gap-1">
              <span>{data.averages.search_time_reduction}</span>
              <Star className="w-4 h-4 fill-purple-400 text-purple-400" />
            </div>
            <span className="text-[10px] text-slate-500">/ 5.0 Rating</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
            <span className="text-xs text-slate-400">Total Validations</span>
            <div className="text-2xl font-bold text-white mt-1">{data.total_responses}</div>
            <span className="text-[10px] text-slate-500">Recorded in DB</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-xl">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-cyan-400" />
            Submit Operational Feedback
          </h3>

          {submitted ? (
            <div className="p-6 text-center text-emerald-400 space-y-2">
              <CheckCircle2 className="w-10 h-10 mx-auto" />
              <p className="font-bold">Thank you for your feedback!</p>
              <p className="text-xs text-slate-400">Response recorded in PostgreSQL validation store.</p>
              <button
                onClick={() => setSubmitted(false)}
                className="mt-4 px-4 py-2 rounded-lg bg-slate-800 text-slate-200 text-xs font-bold"
              >
                Submit Another Response
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">User Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200"
                >
                  <option value="WAREHOUSE_OPERATOR">Warehouse Operator / Picker</option>
                  <option value="SAFETY_OFFICER">Safety Officer</option>
                  <option value="LOGISTICS_LEAD">Logistics & Zone Lead</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-300 mb-1">1. Ease of Understanding (1-5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={understanding}
                    onChange={(e) => setUnderstanding(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-bold"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 mb-1">2. Location Usefulness (1-5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={usefulness}
                    onChange={(e) => setUsefulness(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-bold"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-300 mb-1">3. Evidence Clarity (1-5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={clarity}
                    onChange={(e) => setClarity(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-bold"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 mb-1">4. Workflow Safety (1-5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={safety}
                    onChange={(e) => setSafety(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-bold"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Comments / Field Feedback</label>
                <textarea
                  rows={3}
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  placeholder="e.g. Recommendations allowed rapid location of vaccine batch MED-1042..."
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-200"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 transition"
              >
                <Send className="w-4 h-4" />
                <span>Submit Validation Response</span>
              </button>
            </form>
          )}
        </div>

        {/* Existing Responses */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center justify-between">
            <span>Recent Stakeholder Feedback Log</span>
            <span className="text-xs text-slate-400 font-mono">{data?.responses.length || 0} Entries</span>
          </h3>

          <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
            {data?.responses.map((resp) => (
              <div key={resp.id} className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-cyan-400">{resp.user_role}</span>
                  <div className="flex items-center gap-1 font-bold text-amber-400">
                    <span>{resp.overall_rating}</span>
                    <Star className="w-3 h-3 fill-amber-400" />
                  </div>
                </div>
                <p className="text-slate-300 italic text-[11px]">"{resp.comments || 'No comments provided.'}"</p>
                <span className="text-[10px] text-slate-500 block font-mono">
                  {new Date(resp.timestamp).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
