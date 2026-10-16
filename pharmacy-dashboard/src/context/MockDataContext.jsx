import React, { createContext, useContext, useState } from 'react';

const MockDataContext = createContext();

export const useMockData = () => useContext(MockDataContext);

// Initial placeholder data that uses correct naming guidelines (no fake names, just placeholders)
const initialPrescriptions = [
  {
    id: 'PR-1001',
    customerName: 'Customer Name A',
    uploadTime: '2026-07-04T10:15:00Z',
    aiStatus: 'Success',
    status: 'Pending',
    imageUrl: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=60',
    patientDetails: {
      email: 'customer.a@example.com',
      phone: '+1 (555) 019-2834',
      age: 45,
      gender: 'Male',
      address: 'Address Line 1, City, State'
    },
    medicines: [
      { id: 1, name: 'Medicine Name Alpha', strength: '500mg', dosage: 'Once daily', duration: '7 days', quantity: 7, confidence: 95 },
      { id: 2, name: 'Medicine Name Beta', strength: '10mg', dosage: 'Twice daily', duration: '14 days', quantity: 28, confidence: 88 }
    ]
  },
  {
    id: 'PR-1002',
    customerName: 'Customer Name Beta',
    uploadTime: '2026-07-04T09:30:00Z',
    aiStatus: 'Success',
    status: 'Approved',
    imageUrl: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=60',
    patientDetails: {
      email: 'customer.b@example.com',
      phone: '+1 (555) 014-9988',
      age: 29,
      gender: 'Female',
      address: 'Address Line 2, City, State'
    },
    medicines: [
      { id: 3, name: 'Medicine Name Gamma', strength: '250mg', dosage: 'Three times daily', duration: '5 days', quantity: 15, confidence: 92 }
    ]
  },
  {
    id: 'PR-1003',
    customerName: 'Customer Name Gamma',
    uploadTime: '2026-07-04T08:00:00Z',
    aiStatus: 'Failed',
    status: 'Rejected',
    imageUrl: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=60',
    patientDetails: {
      email: 'customer.c@example.com',
      phone: '+1 (555) 017-7766',
      age: 62,
      gender: 'Female',
      address: 'Address Line 3, City, State'
    },
    medicines: []
  }
];

const initialOrders = [
  {
    id: 'ORD-5001',
    customerName: 'Customer Name A',
    medicineCount: 2,
    prescriptionStatus: 'Verified',
    paymentMethod: 'Credit Card',
    status: 'Pending'
  },
  {
    id: 'ORD-5002',
    customerName: 'Customer Name Beta',
    medicineCount: 1,
    prescriptionStatus: 'Verified',
    paymentMethod: 'Cash on Delivery',
    status: 'Preparing'
  },
  {
    id: 'ORD-5003',
    customerName: 'Customer Name Gamma',
    medicineCount: 0,
    prescriptionStatus: 'Rejected',
    paymentMethod: 'Mobile Pay',
    status: 'Cancelled'
  }
];

const initialMedicines = [
  {
    id: 'MED-001',
    name: 'Medicine Name Alpha',
    strength: '500mg',
    category: 'Category A',
    manufacturer: 'Manufacturer 1',
    prescriptionRequired: true,
    availability: 'In Stock'
  },
  {
    id: 'MED-002',
    name: 'Medicine Name Beta',
    strength: '10mg',
    category: 'Category B',
    manufacturer: 'Manufacturer 2',
    prescriptionRequired: true,
    availability: 'In Stock'
  },
  {
    id: 'MED-003',
    name: 'Medicine Name Gamma',
    strength: '250mg',
    category: 'Category A',
    manufacturer: 'Manufacturer 1',
    prescriptionRequired: false,
    availability: 'Out of Stock'
  },
  {
    id: 'MED-004',
    name: 'Medicine Name Delta',
    strength: '5ml Syrup',
    category: 'Category C',
    manufacturer: 'Manufacturer 3',
    prescriptionRequired: false,
    availability: 'In Stock'
  }
];

const initialCustomers = [
  {
    id: 'CUST-001',
    name: 'Customer Name A',
    phone: '+1 (555) 019-2834',
    email: 'customer.a@example.com',
    orders: 4,
    lastOrder: '2026-07-04'
  },
  {
    id: 'CUST-002',
    name: 'Customer Name Beta',
    phone: '+1 (555) 014-9988',
    email: 'customer.b@example.com',
    orders: 1,
    lastOrder: '2026-07-04'
  },
  {
    id: 'CUST-003',
    name: 'Customer Name Gamma',
    phone: '+1 (555) 017-7766',
    email: 'customer.c@example.com',
    orders: 0,
    lastOrder: 'N/A'
  }
];

const initialNotifications = [
  { id: 1, type: 'New Prescription', message: 'New prescription received for verification', time: '5m ago', read: false },
  { id: 2, type: 'Order Received', message: 'Order ORD-5001 has been placed by Customer Name A', time: '12m ago', read: false },
  { id: 3, type: 'Verification Complete', message: 'Prescription PR-1002 has been verified successfully', time: '1h ago', read: true },
  { id: 4, type: 'System Alert', message: 'System maintenance scheduled for 02:00 AM', time: '5h ago', read: true }
];

export const MockDataProvider = ({ children }) => {
  // Global toggle to turn mock data ON / OFF
  const [mockEnabled, setMockEnabled] = useState(false);

  // States to keep track of mutations in mock data
  const [prescriptions, setPrescriptions] = useState(initialPrescriptions);
  const [orders, setOrders] = useState(initialOrders);
  const [medicines, setMedicines] = useState(initialMedicines);
  const [customers, setCustomers] = useState(initialCustomers);
  const [notifications, setNotifications] = useState(initialNotifications);

  const getPrescriptions = () => (mockEnabled ? prescriptions : []);
  const getOrders = () => (mockEnabled ? orders : []);
  const getMedicines = () => (mockEnabled ? medicines : []);
  const getCustomers = () => (mockEnabled ? customers : []);
  const getNotifications = () => (mockEnabled ? notifications : []);

  const getPrescriptionById = (id) => {
    if (!mockEnabled) return null;
    return prescriptions.find((p) => p.id === id) || null;
  };

  const updatePrescription = (id, updatedData) => {
    setPrescriptions((prev) =>
      prev.map((p) => (p.id === id ? { ...p, ...updatedData } : p))
    );
  };

  const updateOrderStatus = (id, status) => {
    setOrders((prev) =>
      prev.map((o) => (o.id === id ? { ...o, status } : o))
    );
  };

  // Medicine CRUD
  const addMedicine = (medicine) => {
    const newMed = {
      ...medicine,
      id: `MED-${Math.floor(Math.random() * 900) + 100}`
    };
    setMedicines((prev) => [newMed, ...prev]);
  };

  const updateMedicine = (id, updatedMed) => {
    setMedicines((prev) =>
      prev.map((m) => (m.id === id ? { ...m, ...updatedMed } : m))
    );
  };

  const deleteMedicine = (id) => {
    setMedicines((prev) => prev.filter((m) => m.id !== id));
  };

  const markNotificationRead = (id) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  return (
    <MockDataContext.Provider
      value={{
        mockEnabled,
        setMockEnabled,
        getPrescriptions,
        getPrescriptionById,
        updatePrescription,
        getOrders,
        updateOrderStatus,
        getMedicines,
        addMedicine,
        updateMedicine,
        deleteMedicine,
        getCustomers,
        getNotifications,
        markNotificationRead
      }}
    >
      {children}
    </MockDataContext.Provider>
  );
};
