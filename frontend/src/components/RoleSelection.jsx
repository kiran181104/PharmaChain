import React, { useState } from 'react';
import Button from './common/Button';
import './RoleSelection.css';

const RoleSelection = ({ account, onSelectRole, error: propError }) => {
  const [selectedRole, setSelectedRole] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [localError, setLocalError] = useState('');

  const roles = [
    {
      value: 'MANUFACTURER',
      label: 'Manufacturer',
      icon: '🏭',
      description: 'Register and produce drugs'
    },
    {
      value: 'DISTRIBUTOR',
      label: 'Distributor',
      icon: '🚚',
      description: 'Distribute drugs to pharmacies'
    },
    {
      value: 'PHARMACY',
      label: 'Pharmacy',
      icon: '💊',
      description: 'Dispense drugs to consumers'
    },
    {
      value: 'CONSUMER',
      label: 'Consumer',
      icon: '👤',
      description: 'Verify drug authenticity'
    },
    {
      value: 'REGULATOR',
      label: 'Regulator',
      icon: '📊',
      description: 'Monitor and audit system'
    }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedRole) {
      setLocalError('Please select a role');
      return;
    }

    if (!name.trim()) {
      setLocalError('Please enter your name');
      return;
    }

    setLoading(true);
    setLocalError('');

    try {
      await onSelectRole(selectedRole, name);
    } catch (err) {
      setLocalError(err.message || 'Failed to register');
      setLoading(false);
    }
  };

  const displayError = propError || localError;

  return (
    <div className="role-selection">
      <div className="role-selection-card">
        <h2>🔐 Complete Your Registration</h2>
        <p className="subtitle">Select your role in the drug supply chain</p>
        <p className="account-info">
          <strong>Connected Account:</strong><br/>
          <code>{account}</code>
        </p>

        {displayError && <div className="error-message">{displayError}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Your Name / Organization Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setLocalError('');
              }}
              placeholder="Enter your name or organization name"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Select Your Role *</label>
            <div className="role-cards">
              {roles.map((role) => (
                <div
                  key={role.value}
                  className={`role-card ${selectedRole === role.value ? 'selected' : ''}`}
                  onClick={() => {
                    if (!loading) {
                      setSelectedRole(role.value);
                      setLocalError('');
                    }
                  }}
                >
                  <div className="role-icon">{role.icon}</div>
                  <div className="role-label">{role.label}</div>
                  <div className="role-description">{role.description}</div>
                </div>
              ))}
            </div>
          </div>

          <Button 
            type="submit" 
            loading={loading} 
            disabled={!selectedRole || !name.trim()}
            size="large"
          >
            {loading ? 'Registering...' : 'Complete Registration'}
          </Button>
        </form>

        <div className="info-box">
          <h4>ℹ️ Important Information</h4>
          <ul>
            <li>Your role cannot be changed after registration</li>
            <li>Each Ethereum address can only register once</li>
            <li>Choose the role that matches your function in the supply chain</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RoleSelection;