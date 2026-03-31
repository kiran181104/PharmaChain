import React, { useState, useEffect } from 'react';
import { getAuditStatistics, getAnomalies, getAllUsers } from '../services/api';
import './Dashboard.css';

const RegulatorDashboard = ({ account }) => {
  const [stats, setStats] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsData, anomaliesData, usersData] = await Promise.all([
        getAuditStatistics(),
        getAnomalies(),
        getAllUsers()
      ]);
      setStats(statsData);
      setAnomalies(anomaliesData);
      setUsers(usersData || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="container">
      <div className="dashboard">
        <h2>📊 Regulator Dashboard</h2>
        <p className="dashboard-subtitle">Monitor system-wide drug traceability</p>

        {stats && (
          <div className="stats-grid">
            <div className="stat-card">
              <h3>{stats.totalDrugs}</h3>
              <p>Total Drugs</p>
            </div>
            <div className="stat-card">
              <h3>{stats.totalUsers}</h3>
              <p>Registered Users</p>
            </div>
            <div className="stat-card">
              <h3>{stats.totalTransfers}</h3>
              <p>Total Transfers</p>
            </div>
            <div className="stat-card">
              <h3>{stats.drugsWithAnomalies}</h3>
              <p>Drugs with Anomalies</p>
            </div>
            <div className="stat-card">
              <h3>{stats.expiredDrugs}</h3>
              <p>Expired Drugs</p>
            </div>
          </div>
        )}

        {anomalies && anomalies.length > 0 && (
          <div className="anomalies-table">
            <h3>Detected Anomalies</h3>
            <table>
              <thead>
                <tr>
                  <th>Batch ID</th>
                  <th>Drug Name</th>
                  <th>Anomaly Type</th>
                  <th>Transfers</th>
                </tr>
              </thead>
              <tbody>
                {anomalies.map((item, index) => (
                  <tr key={index}>
                    <td>{item.batchId}</td>
                    <td>{item.drugName}</td>
                    <td>{item.anomalyType}</td>
                    <td>{item.ownershipCount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {users && users.length > 0 && (
          <div className="anomalies-table">
            <h3>Registered Users</h3>
            <table>
              <thead>
                <tr>
                  <th>Wallet Address</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Registered</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user, index) => (
                  <tr key={index}>
                    <td>{user.walletAddress}</td>
                    <td>{user.name || '-'}</td>
                    <td>{user.role}</td>
                    <td>{user.isRegistered ? 'Yes' : 'No'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default RegulatorDashboard;

