import React, { useState } from 'react';
import { tasksAPI, apiClient } from '../api/client';

function Tasks() {
  const [goal, setGoal] = useState('');
  const [mode, setMode] = useState('pipeline');
  const [taskId, setTaskId] = useState('');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(null);

  const generateIdempotencyKey = () => `${Date.now()}-${Math.random().toString(36)}`;

  const submitTask = async () => {
    setLoading(true);
    const key = generateIdempotencyKey();
    try {
      const res = await tasksAPI.runPipeline(goal, mode, key);
      setTaskId(res.data.task_id);
      setProgress(null);
      pollStatus(res.data.task_id);
    } catch (err) {
      alert('Failed to submit task');
      setLoading(false);
    }
  };

  const pollStatus = async (id) => {
    const interval = setInterval(async () => {
      try {
        const [statusRes, progressRes] = await Promise.all([
          tasksAPI.getPipelineStatus(id),
          apiClient.get(`/tasks/pipeline/${id}/progress`).catch(() => null)
        ]);
        setStatus(statusRes.data);
        if (progressRes) setProgress(progressRes.data);
        if (statusRes.data.status === 'completed' || statusRes.data.status === 'failed') {
          clearInterval(interval);
          setLoading(false);
        }
      } catch (err) {
        clearInterval(interval);
        setLoading(false);
      }
    }, 2000);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Task Manager</h2>
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="Enter your task goal..."
          className="w-full p-3 border rounded-lg mb-4"
          rows="3"
        />
        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
          className="w-full md:w-auto p-3 border rounded-lg mr-4 mb-4"
        >
          <option value="pipeline">Pipeline</option>
          <option value="lab">Experiment</option>
          <option value="invent">Invention</option>
        </select>
        <button
          onClick={submitTask}
          disabled={loading || !goal}
          className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Run Task'}
        </button>
      </div>

      {/* Progress Bar */}
      {progress && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h3 className="text-xl font-semibold mb-4">Task Progress: {progress.state}</h3>
          <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
            <div
              className="bg-indigo-600 h-4 rounded-full transition-all duration-500"
              style={{ width: `${progress.progress_percent}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600">
            Estimated remaining: {Math.round(progress.estimated_remaining)} seconds
          </p>
        </div>
      )}

      {status && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-4">Task Status: {status.status}</h3>
          {status.council_verdict && (
            <div className="mb-4">
              <p className="font-semibold">
                Council Verdict:
                <span className={`ml-2 ${
                  status.council_verdict.verdict === 'APPROVED' ? 'text-green-600' :
                  status.council_verdict.verdict === 'REJECTED' ? 'text-red-600' : 'text-yellow-600'
                }`}>
                  {status.council_verdict.verdict} (Score: {status.council_verdict.score?.toFixed(2)})
                </span>
              </p>
            </div>
          )}
          {status.result && (
            <pre className="bg-gray-100 p-4 rounded-lg overflow-auto max-h-96">
              {status.result}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

export default Tasks;
