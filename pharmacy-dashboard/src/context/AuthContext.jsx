import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/apiClient';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => {
    return localStorage.getItem('mediLoopToken') || sessionStorage.getItem('mediLoopToken') || null;
  });

  const [user, setUser] = useState(() => {
    const savedProfile = localStorage.getItem('mediLoopProfile') || sessionStorage.getItem('mediLoopProfile');
    if (savedProfile) {
      try {
        return JSON.parse(savedProfile);
      } catch (_) {}
    }
    return null;
  });

  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(token && user));

  const login = async (email, password, rememberMe = true) => {
    try {
      const response = await apiClient.post('/auth/pharmacist/login', {
        email: email.trim(),
        password: password
      });

      const { access_token, pharmacist } = response.data;
      
      const profile = {
        id: pharmacist.id,
        name: pharmacist.full_name || pharmacist.name || 'Pharmacist',
        email: pharmacist.email,
        phone: pharmacist.mobile_number || pharmacist.phone || '+91 9123456780',
        registrationNumber: pharmacist.registration_number || pharmacist.license_number || 'KA-PHARM-2010-8841',
        pharmacyId: pharmacist.pharmacy_id || 6,
        pharmacyName: pharmacist.pharmacy_name || 'Kalawati Medical & General Stores',
        designation: pharmacist.designation || 'Staff Pharmacist',
        photoUrl: ''
      };

      setToken(access_token);
      setUser(profile);
      setIsAuthenticated(true);

      // Clean old sessions
      localStorage.removeItem('mediLoopToken');
      localStorage.removeItem('mediLoopProfile');
      sessionStorage.removeItem('mediLoopToken');
      sessionStorage.removeItem('mediLoopProfile');

      if (rememberMe) {
        localStorage.setItem('mediLoopToken', access_token);
        localStorage.setItem('mediLoopProfile', JSON.stringify(profile));
      } else {
        sessionStorage.setItem('mediLoopToken', access_token);
        sessionStorage.setItem('mediLoopProfile', JSON.stringify(profile));
      }

      return { success: true, token: access_token, user: profile };
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Invalid email or password';
      throw new Error(errorMsg);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('mediLoopToken');
    localStorage.removeItem('mediLoopProfile');
    sessionStorage.removeItem('mediLoopToken');
    sessionStorage.removeItem('mediLoopProfile');
  };

  const updateProfile = (updatedUser) => {
    setUser(updatedUser);
    if (updatedUser) {
      if (localStorage.getItem('mediLoopToken')) {
        localStorage.setItem('mediLoopProfile', JSON.stringify(updatedUser));
      }
      if (sessionStorage.getItem('mediLoopToken')) {
        sessionStorage.setItem('mediLoopProfile', JSON.stringify(updatedUser));
      }
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, token, user, login, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
};
