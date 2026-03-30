import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import Navbar from './components/Navbar';
import MetaMaskConnect from './components/MetaMaskConnect';
import RoleSelection from './components/RoleSelection';

// Pages
import ManufacturerDashboard from './pages/ManufacturerDashboard';
import DistributorDashboard from './pages/DistributorDashboard';
import PharmacyDashboard from './pages/PharmacyDashboard';
import ConsumerPage from './pages/ConsumerPage';
import RegulatorDashboard from './pages/RegulatorDashboard';

// Services
import web3Service from './services/web3';
import { getUser, registerUser } from './services/api';

function App() {
  const [account, setAccount] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [needsRoleSelection, setNeedsRoleSelection] = useState(false);

  useEffect(() => {
    initializeApp();
    
    // Setup MetaMask event listeners
    if (window.ethereum) {
      // Handle account changes
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      
      // Handle chain changes
      window.ethereum.on('chainChanged', handleChainChanged);
    }

    // Cleanup listeners on unmount
    return () => {
      if (window.ethereum) {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
        window.ethereum.removeListener('chainChanged', handleChainChanged);
      }
    };
  }, []);

  const handleAccountsChanged = (accounts) => {
    console.log('Account changed:', accounts);
    if (accounts.length === 0) {
      // User disconnected all accounts
      handleDisconnect();
    } else if (accounts[0] !== account) {
      // Account switched
      console.log('Switching from', account, 'to', accounts[0]);
      // Reset state and reload
      setAccount(null);
      setUserRole(null);
      setNeedsRoleSelection(false);
      setLoading(true);
      // Re-initialize with new account
      initializeApp();
    }
  };

  const handleChainChanged = () => {
    console.log('Chain changed, reloading...');
    window.location.reload();
  };

  const initializeApp = async () => {
    try {
      setLoading(true);
      const { account: connectedAccount } = await web3Service.init();
      setAccount(connectedAccount);
      console.log('Connected account:', connectedAccount);
      
      // Check if user is registered
      try {
        const userData = await getUser(connectedAccount);
        console.log('User data from backend:', userData);
        setUserRole(userData.role);
        setNeedsRoleSelection(false);
      } catch (error) {
        console.log('User not registered, showing role selection');
        setNeedsRoleSelection(true);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to initialize app:', error);
      setError(error.message);
      setLoading(false);
    }
  };

  const handleRoleSelection = async (role, name) => {
    try {
      setLoading(true);
      setError('');
      
      console.log('Registering user:', { account, role, name });
      
      await registerUser({
        walletAddress: account,
        role: role,
        name: name
      });
      
      console.log('User registered successfully');
      setUserRole(role);
      setNeedsRoleSelection(false);
      setLoading(false);
    } catch (error) {
      console.error('Failed to register user:', error);
      const networkMsg = error.message?.includes('Network Error') ?
        `Backend unreachable at ${process.env.REACT_APP_API_URL || 'http://localhost:8000'}; check backend server and CORS` : null;
      setError(
        networkMsg ||
        'Failed to register: ' + (error.response?.data?.detail || error.message || 'Unknown error')
      );
      setLoading(false);
    }
  };

  const handleDisconnect = () => {
    console.log('Disconnecting...');
    
    // Clear all state
    setAccount(null);
    setUserRole(null);
    setNeedsRoleSelection(false);
    setError('');
    
    // Clear any cached data
    localStorage.clear();
    sessionStorage.clear();
    
    // Don't auto-reload, just set loading state
    setLoading(false);
  };

  const handleReconnect = () => {
    setLoading(true);
    initializeApp();
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner-large"></div>
        <p>Connecting to MetaMask...</p>
      </div>
    );
  }

  if (!account) {
    return <MetaMaskConnect onConnect={handleReconnect} error={error} />;
  }

  if (needsRoleSelection) {
    return (
      <RoleSelection 
        account={account} 
        onSelectRole={handleRoleSelection}
        error={error}
      />
    );
  }

  const getDashboardComponent = () => {
    console.log('Rendering dashboard for role:', userRole);
    
    switch (userRole) {
      case 'MANUFACTURER':
        return <ManufacturerDashboard account={account} />;
      case 'DISTRIBUTOR':
        return <DistributorDashboard account={account} />;
      case 'PHARMACY':
        return <PharmacyDashboard account={account} />;
      case 'REGULATOR':
        return <RegulatorDashboard account={account} />;
      case 'CONSUMER':
      default:
        return <ConsumerPage account={account} />;
    }
  };

  return (
    <Router>
      <div className="App">
        <Navbar 
          account={account} 
          userRole={userRole} 
          onDisconnect={handleDisconnect} 
        />
        <div className="app-content">
          <Routes>
            <Route path="/" element={getDashboardComponent()} />
            <Route path="/verify" element={<ConsumerPage account={account} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;