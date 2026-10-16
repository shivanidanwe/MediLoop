import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import DashboardHome from '../pages/Dashboard/DashboardHome';
import PrescriptionVerification from '../pages/PrescriptionVerification/PrescriptionVerification';
import PrescriptionDetails from '../pages/PrescriptionVerification/PrescriptionDetails';
import Orders from '../pages/Orders/Orders';
import Medicines from '../pages/Medicines/Medicines';
import Customers from '../pages/Customers/Customers';
import Notifications from '../pages/Notifications/Notifications';
import Reports from '../pages/Reports/Reports';
import Profile from '../pages/Profile/Profile';
import Settings from '../pages/Settings/Settings';
import Login from '../pages/Login/Login';

// Private Route Guard
const ProtectedRoute = ({ children }) => {
  return children;
};
const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Auth route */}
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />}
      />

      {/* Main App Layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardHome />} />
        <Route path="prescriptions" element={<PrescriptionVerification />} />
        <Route path="prescriptions/:id" element={<PrescriptionDetails />} />
        <Route path="orders" element={<Orders />} />
        <Route path="medicines" element={<Medicines />} />
        <Route path="customers" element={<Customers />} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="reports" element={<Reports />} />
        <Route path="profile" element={<Profile />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
    </Routes>
  );
};

export default AppRoutes;
