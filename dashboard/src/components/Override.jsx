import React, { useState } from 'react';
import { tasksAPI } from '../api/client';

function Override() {
  const [taskId, setTaskId] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleOverride = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await tasksAPI.override(taskId, reason);
      setResult({ success: true, message: `Override accepted for task ${taskId}` });
      setTaskId('');
      setReason('');
    } catch (err) {
      setResult({ success: false, message: err.response?.data?.detail || 'Override failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Admin Override Panel</h2>
      <div className="bg-white p-6 rounded-lg shadow max-w-2xl">
        <form onSubmit={handleOverride}>
          <label className="block mb-2 font-medium">Task ID</label>
          <input
            type="text"
            value={taskId}
            onChange={(e) => setTaskId(e.target.value)}
            className="w-full p-3 border rounded-lg mb-4"
            placeholder="Enter the task ID to override"
            required
          />
          <label className="block mb-2 font-medium">Override Reason</label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full p-3 border rounded-lg mb-4"
            rows="3"
            placeholder="Justification for the override"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Apply Override'}
          </button>
        </form>
        {result && (
          <div className={`mt-4 p-4 rounded-lg ${result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {result.message}
          </div>
        )}
      </div>
    </div>
  );
}

export default Override;
