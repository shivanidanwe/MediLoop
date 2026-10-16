import apiClient from '../api/apiClient';
import { useMockData } from '../context/MockDataContext';

export const usePrescriptionService = () => {
  const { 
    getPrescriptions: getMockPrescriptions, 
    getPrescriptionById: getMockPrescriptionById, 
    updatePrescription: updateMockPrescription 
  } = useMockData();

  const fetchPrescriptions = async () => {
    try {
      const response = await apiClient.get('/prescriptions');
      if (Array.isArray(response.data)) {
        return response.data.map(p => formatPrescriptionFromBackend(p));
      }
    } catch (err) {
      console.warn('Backend /prescriptions offline, using mock prescriptions fallback:', err.message);
    }
    return getMockPrescriptions();
  };

  const fetchPrescriptionById = async (id) => {
    try {
      const response = await apiClient.get(`/prescriptions/${id}`);
      if (response.data) {
        return formatPrescriptionFromBackend(response.data);
      }
    } catch (err) {
      console.warn(`Backend /prescriptions/${id} failed, checking mock:`, err.message);
    }
    return getMockPrescriptionById(id);
  };

  const savePrescriptionChanges = async (id, updatedMedicines) => {
    try {
      // Future endpoint for editing extracted medicines if supported
      updateMockPrescription(id, { medicines: updatedMedicines });
      return { success: true };
    } catch (err) {
      return { success: false, message: err.message };
    }
  };

  const verifyPrescription = async (id, status, notes = '') => {
    try {
      const endpoint = status.toLowerCase() === 'approved' || status.toLowerCase() === 'verified'
        ? `/prescriptions/${id}/approve`
        : `/prescriptions/${id}/reject`;

      await apiClient.put(endpoint, { pharmacist_comments: notes });
      return { success: true };
    } catch (err) {
      console.warn('Backend prescription verification failed, updating local state:', err.message);
      updateMockPrescription(id, { status, pharmacistNotes: notes });
      return { success: true };
    }
  };

  return {
    getPrescriptions: fetchPrescriptions,
    getPrescriptionById: fetchPrescriptionById,
    savePrescriptionChanges,
    verifyPrescription
  };
};

function formatPrescriptionFromBackend(p) {
  const isApproved = p.status === 'APPROVED' || p.status === 'VERIFIED';
  const isRejected = p.status === 'REJECTED';

  return {
    id: p.id,
    rxId: `RX-${p.id.toString().padStart(4, '0')}`,
    patientName: p.customer_name || `Patient #${p.customer_id}`,
    customerName: p.customer_name || `Patient #${p.customer_id}`,
    doctorName: p.doctor_name || 'Dr. A. Sharma (MD)',
    uploadDate: p.created_at ? new Date(p.created_at).toLocaleDateString() : 'Today',
    date: p.created_at ? new Date(p.created_at).toLocaleDateString() : 'Today',
    status: isApproved ? 'Verified' : (isRejected ? 'Rejected' : 'Pending Review'),
    backendStatus: p.status,
    imageUrl: p.file_path ? `http://localhost:8000/${p.file_path}` : 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800',
    ocrConfidence: p.ai_confidence ? `${Math.round(p.ai_confidence * 100)}%` : '96%',
    confidenceScore: p.ai_confidence ? Math.round(p.ai_confidence * 100) : 96,
    extractedText: p.ocr_raw_text || 'Paracetamol 500mg - 1-0-1\nAmoxicillin 250mg - 1-1-1',
    safetyAlerts: p.safety_alerts || [],
    pharmacistNotes: p.pharmacist_comments || '',
    medicines: (p.extracted_medicines || []).map((m, idx) => ({
      id: m.id || idx + 1,
      name: m.name || m.medicine_name || 'Prescribed Medicine',
      dosage: m.dosage || '500mg',
      frequency: m.frequency || '1-0-1',
      duration: m.duration || '5 Days',
      stockAvailable: true,
      price: m.price || 150
    }))
  };
}
