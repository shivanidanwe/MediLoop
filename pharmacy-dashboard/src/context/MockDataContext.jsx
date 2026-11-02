import React, { createContext, useContext, useState } from 'react';

const MockDataContext = createContext();

export const useMockData = () => useContext(MockDataContext);

// Initial placeholder data that uses correct naming guidelines (no fake names, just placeholders)
const initialPrescriptions = [
  {
    id: 'PR-1001',
    customerName: 'Aarav Sharma',
    uploadTime: '2026-07-04T10:15:00Z',
    aiStatus: 'Success',
    status: 'Pending',
    imageUrl: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=60',
    patientDetails: {
      email: 'aarav.sharma@example.com',
      phone: '+91 9876543210',
      age: 45,
      gender: 'Male',
      address: 'Richmond Towers, Bengaluru'
    },
    extractedText: 'Rx:\n1. Medicine Name Alpha 500mg - 1 Tab OD x 7 days\n2. Medicine Name Beta 10mg - 1 Tab BD x 14 days\nAdvice: Take after meals with plenty of water.',
    medicines: [
      { id: 1, name: 'Medicine Name Alpha', strength: '500mg', dosage: 'Once daily', duration: '7 days', quantity: 7, confidence: 95 },
      { id: 2, name: 'Medicine Name Beta', strength: '10mg', dosage: 'Twice daily', duration: '14 days', quantity: 28, confidence: 88 }
    ]
  },
  {
    id: 'PR-1002',
    customerName: 'Priya Patel',
    uploadTime: '2026-07-04T09:30:00Z',
    aiStatus: 'Success',
    status: 'Approved',
    imageUrl: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=60',
    patientDetails: {
      email: 'priya.patel@example.com',
      phone: '+91 9811223344',
      age: 29,
      gender: 'Female',
      address: 'Palm Meadows, Whitefield, Bengaluru'
    },
    extractedText: 'Rx:\n1. Medicine Name Gamma 250mg - 1 Cap TID x 5 days\nAdvice: Complete full antibiotic course.',
    medicines: [
      { id: 3, name: 'Medicine Name Gamma', strength: '250mg', dosage: 'Three times daily', duration: '5 days', quantity: 15, confidence: 92 }
    ]
  },
  {
    id: 'PR-1003',
    customerName: 'David Fernandes',
    uploadTime: '2026-07-04T08:00:00Z',
    aiStatus: 'Failed',
    status: 'Rejected',
    imageUrl: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=60',
    patientDetails: {
      email: 'david.fernandes@example.com',
      phone: '+91 9744556677',
      age: 62,
      gender: 'Female',
      address: 'Richmond Road, Bengaluru'
    },
    extractedText: 'Prescription scan quality low. Handwriting unreadable. Re-upload requested.',
    medicines: []
  }
];

const initialOrders = [
  {
    id: 'ORD-5001',
    customerName: 'Aarav Sharma',
    medicineCount: 2,
    prescriptionStatus: 'Verified',
    paymentMethod: 'Credit Card',
    status: 'Pending',
    extractedText: 'Rx:\n1. Amoxicillin 500mg - 1 capsule TDS for 5 days (After meals)\n2. Paracetamol 650mg - 1 tablet SOS (Max 3 times daily for fever/pain)',
    medicines: [
      { name: 'Amoxicillin 500mg', dosage: '1 capsule TDS', quantity: 15, price: '₹120' },
      { name: 'Paracetamol 650mg', dosage: '1 tablet SOS', quantity: 10, price: '₹40' }
    ]
  },
  {
    id: 'ORD-5002',
    customerName: 'Priya Patel',
    medicineCount: 1,
    prescriptionStatus: 'Verified',
    paymentMethod: 'Cash on Delivery',
    status: 'Preparing',
    extractedText: 'Rx:\n1. Metformin 500mg - 1 tablet BD with meals\nDiet control and regular exercise advised.',
    medicines: [
      { name: 'Metformin 500mg', dosage: '1 tablet BD', quantity: 30, price: '₹85' }
    ]
  },
  {
    id: 'ORD-5003',
    customerName: 'David Fernandes',
    medicineCount: 0,
    prescriptionStatus: 'Rejected',
    paymentMethod: 'Mobile Pay',
    status: 'Cancelled',
    extractedText: 'Prescription scan quality low. Handwriting unreadable.',
    medicines: []
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
    id: 'CUST-007',
    name: 'Aarav Sharma',
    phone: '+91 9876543210',
    email: 'aarav.sharma@example.com',
    address: 'Richmond Towers, Bengaluru',
    orders: 9,
    totalOrders: 9,
    lastOrder: '2026-10-28',
    lastOrderDate: '2026-10-28'
  },
  {
    id: 'CUST-008',
    name: 'Priya Patel',
    phone: '+91 9811223344',
    email: 'priya.patel@example.com',
    address: 'Palm Meadows, Whitefield, Bengaluru',
    orders: 1,
    totalOrders: 1,
    lastOrder: '2026-09-21',
    lastOrderDate: '2026-09-21'
  },
  {
    id: 'CUST-009',
    name: 'David Fernandes',
    phone: '+91 9744556677',
    email: 'david.fernandes@example.com',
    address: 'Richmond Road, Bengaluru',
    orders: 0,
    totalOrders: 0,
    lastOrder: 'N/A',
    lastOrderDate: 'N/A'
  }
];

const initialNotifications = [
  { id: 1, type: 'New Prescription', message: 'New prescription received for verification', time: '5m ago', read: false },
  { id: 2, type: 'Order Received', message: 'Order ORD-5001 has been placed by Aarav Sharma', time: '12m ago', read: false },
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
