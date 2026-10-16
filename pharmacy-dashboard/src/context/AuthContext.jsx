import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/apiClient';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

const defaultProfile = {
  name: 'Dr. Pharmacist',
  email: 'pharmacist@mediloop.com',
  phone: '+91 9876543210',
  registrationNumber: 'PH-99281',
  pharmacyName: 'Central MediLoop Pharmacy',
  address: '123 Medical Boulevard, Suite 100',
  photoUrl: ''
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('mediLoopToken'));
  const [user, setUser] = useState(() => {
    const savedProfile = localStorage.getItem('mediLoopProfile');
    return savedProfile ? JSON.parse(savedProfile) : defaultProfile;
  });

  const [isAuthenticated, setIsAuthenticated] = useState(!!token);

  useEffect(() => {
    if (token) {
      localStorage.setItem('mediLoopToken', token);
      setIsAuthenticated(true);
    } else {
      localStorage.removeItem('mediLoopToken');
      localStorage.removeItem('mediLoopProfile');
      setIsAuthenticated(false);
    }
  }, [token]);

  const login = async (email, password) => {
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
        phone: pharmacist.mobile_number || pharmacist.phone || '+91 9876543210',
        registrationNumber: pharmacist.license_number || 'PH-99281',
        pharmacyId: pharmacist.pharmacy_id || 1,
        pharmacyName: pharmacist.pharmacy_name || 'Central MediLoop Pharmacy',
        address: '123 Medical Boulevard, Suite 100',
        photoUrl: ''
      };

      setToken(access_token);
      setUser(profile);
      localStorage.setItem('mediLoopProfile', JSON.stringify(profile));

      return { success: true, token: access_token, user: profile };
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Invalid email or password';
      throw new Error(errorMsg);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(defaultProfile);
    setIsAuthenticated(false);
    localStorage.removeItem('mediLoopToken');
    localStorage.removeItem('mediLoopProfile');
  };

  const updateProfile = (updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem('mediLoopProfile', JSON.stringify(updatedUser));
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
};
