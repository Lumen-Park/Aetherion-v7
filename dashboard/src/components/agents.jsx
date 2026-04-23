import React, { useEffect, useState } from 'react';
import { agentsAPI } from '../api/client';

function Agents() {
  const [agents, setAgents] = useState([]);
  const [filter, setFilter] = useState('');
  const [collegeFilter, setCollegeFilter] = useState('All');

  useEffect(() => {
    agentsAPI.list().then(res => setAgents(res.data.agents));
  }, []);

  const colleges = ['All', ...new Set(agents.map(a => a.college))];

  const filteredAgents = agents.filter(a =>
    a.name.toLowerCase().includes(filter.toLowerCase()) &&
    (collegeFilter === 'All' || a.college === collegeFilter)
  );

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Agent Roster ({agents.length} agents)</h2>
      <div className="flex gap-4 mb-6">
        <input
          type="text"
          placeholder="Search agents..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="flex-1 p-3 border rounded-lg"
        />
        <select
          value={collegeFilter}
          onChange={(e) => setCollegeFilter(e.target.value)}
          className="p-3 border rounded-lg"
        >
          {colleges.map(c => <option key={c}>{c}</option>)}
        </select>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredAgents.map(agent => (
          <div key={agent.name} className="bg-white p-4 rounded-lg shadow hover:shadow-md transition">
            <h3 className="font-bold text-lg text-indigo-800">{agent.name}</h3>
            <p className="text-sm text-gray-600">{agent.college}</p>
            <p className="text-sm mt-2">{agent.expertise}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
export default Agents;
