import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/client';

function Constitution() {
  const { workspaceId } = useParams();
  const [constitution, setConstitution] = useState({ judges: {}, thresholds: {} });
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    apiClient.get(`/constitution/${workspaceId}`).then(res => {
      setConstitution(res.data.constitution);
    });
  }, [workspaceId]);

  const updateJudge = (name, field, value) => {
    setConstitution(prev => ({
      ...prev,
      judges: {
        ...prev.judges,
        [name]: { ...prev.judges[name], [field]: value }
      }
    }));
  };

  const updateThreshold = (name, value) => {
    setConstitution(prev => ({
      ...prev,
      thresholds: { ...prev.thresholds, [name]: parseFloat(value) }
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await apiClient.put(`/constitution/${workspaceId}`, constitution);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      alert('Failed to save constitution');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Constitution Editor – {workspaceId}</h2>

      {/* Thresholds */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h3 className="text-xl font-semibold mb-4">Voting Thresholds</h3>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block mb-2">Approved Threshold</label>
            <input
              type="range"
              min="5.0"
              max="9.0"
              step="0.1"
              value={constitution.thresholds.approved || 7.0}
              onChange={(e) => updateThreshold('approved', e.target.value)}
              className="w-full"
            />
            <span className="text-lg font-bold">{constitution.thresholds.approved || 7.0}</span>
          </div>
          <div>
            <label className="block mb-2">Revision Required Threshold</label>
            <input
              type="range"
              min="3.0"
              max="7.0"
              step="0.1"
              value={constitution.thresholds.revision || 5.0}
              onChange={(e) => updateThreshold('revision', e.target.value)}
              className="w-full"
            />
            <span className="text-lg font-bold">{constitution.thresholds.revision || 5.0}</span>
          </div>
        </div>
      </div>

      {/* Judges */}
      <div className="space-y-4">
        {Object.entries(constitution.judges).map(([name, config]) => (
          <div key={name} className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">{name}</h3>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.enabled !== false}
                  onChange={(e) => updateJudge(name, 'enabled', e.target.checked)}
                  className="mr-2"
                />
                Enabled
              </label>
            </div>
            <textarea
              value={config.prompt || ''}
              onChange={(e) => updateJudge(name, 'prompt', e.target.value)}
              rows="4"
              className="w-full p-3 border rounded-lg font-mono text-sm"
              disabled={!config.enabled}
            />
          </div>
        ))}
      </div>

      <div className="mt-6 flex justify-end">
        <button
          onClick={handleSave}
          disabled={loading}
          className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Saving...' : 'Save Constitution'}
        </button>
        {saved && <span className="ml-4 text-green-600">Saved!</span>}
      </div>
    </div>
  );
}

export default Constitution;
