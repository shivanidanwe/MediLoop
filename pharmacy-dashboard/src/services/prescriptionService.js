import apiClient from '../api/apiClient';

export const usePrescriptionService = () => {
  const fetchPrescriptions = async () => {
    try {
      const response = await apiClient.get('/prescriptions');
      if (Array.isArray(response.data)) {
        return response.data.map(p => formatPrescriptionFromBackend(p)).filter(Boolean);
      }
    } catch (err) {
      console.error('Backend /prescriptions error:', err.message);
    }
    return [];
  };

  const fetchPrescriptionById = async (id) => {
    try {
      const response = await apiClient.get(`/prescriptions/${id}`);
      if (response.data) {
        return formatPrescriptionFromBackend(response.data);
      }
    } catch (err) {
      console.error(`Backend /prescriptions/${id} failed:`, err.message);
    }
    return null;
  };

  const verifyPrescription = async (id, status, notes = '') => {
    try {
      const isApproval = status.toLowerCase() === 'approved' || status.toLowerCase() === 'verified';
      const endpoint = isApproval
        ? `/prescriptions/${id}/approve`
        : `/prescriptions/${id}/reject`;

      const payload = isApproval
        ? { pharmacist_comments: notes }
        : { rejection_reason: notes || 'Prescription rejected by pharmacist', pharmacist_comments: notes };

      const response = await apiClient.put(endpoint, payload);
      return { success: true, data: formatPrescriptionFromBackend(response.data) };
    } catch (err) {
      console.error('Backend prescription verification failed:', err.message);
      return { success: false, message: err.response?.data?.detail || err.message };
    }
  };

  const requestClarification = async (id, notes = '') => {
    try {
      const response = await apiClient.put(`/prescriptions/${id}/clarify`, {
        clarification_notes: notes,
        pharmacist_comments: notes
      });
      return { success: true, data: formatPrescriptionFromBackend(response.data) };
    } catch (err) {
      console.error('Backend clarification request failed:', err.message);
      return { success: false, message: err.response?.data?.detail || err.message };
    }
  };

  return {
    getPrescriptions: fetchPrescriptions,
    getPrescriptionById: fetchPrescriptionById,
    verifyPrescription,
    requestClarification
  };
};

export function formatPrescriptionFromBackend(p) {
  if (!p || typeof p !== 'object') return null;

  const vStatus = (p.verification_status || p.status || '').toUpperCase();
  const isApproved = vStatus === 'APPROVED' || vStatus === 'VERIFIED';
  const isRejected = vStatus === 'REJECTED';
  const isClarification = vStatus === 'REQUIRES_CLARIFICATION';
  const isUnderReview = vStatus === 'UNDER_REVIEW';

  let uiStatus = 'Pending';
  if (isApproved) uiStatus = 'Approved';
  else if (isRejected) uiStatus = 'Rejected';
  else if (isClarification) uiStatus = 'Requires Clarification';
  else if (isUnderReview) uiStatus = 'Under Review';

  const rawImg = p.uploaded_image_path || p.file_path || '';
  const cleanImgPath = rawImg ? rawImg.replace(/\\/g, '/') : '';
  const imageUrl = cleanImgPath.startsWith('http')
    ? cleanImgPath
    : `http://localhost:8000/api/v1/prescriptions/${p.id || 0}/image`;

  const downloadUrl = `http://localhost:8000/api/v1/prescriptions/${p.id || 0}/image?download=true`;

  const itemsList = Array.isArray(p.items) ? p.items : (Array.isArray(p.extracted_medicines) ? p.extracted_medicines : []);
  const confidenceVal = p.overall_confidence != null ? p.overall_confidence : (p.ai_confidence != null ? p.ai_confidence : 0.95);
  const safeId = p.id != null ? p.id : Math.floor(Math.random() * 1000);

  return {
    id: safeId,
    rxId: `RX-${safeId.toString().padStart(4, '0')}`,
    patientName: p.customer_name || 'Patient',
    customerName: p.customer_name || 'Patient',
    doctorName: p.doctor_name || 'Medical Practitioner',
    uploadTime: p.uploaded_at || p.created_at || new Date().toISOString(),
    uploadDate: p.uploaded_at ? new Date(p.uploaded_at).toLocaleDateString() : 'Today',
    date: p.uploaded_at ? new Date(p.uploaded_at).toLocaleDateString() : 'Today',
    status: uiStatus,
    backendStatus: vStatus,
    isFinalized: isApproved || isRejected,
    aiStatus: itemsList.length > 0 ? 'Success' : (confidenceVal > 0 ? 'Pending' : 'Failed'),
    imageUrl: imageUrl,
    downloadUrl: downloadUrl,
    fileName: p.original_filename || 'prescription.jpeg',
    originalFilename: p.original_filename || 'prescription.jpeg',
    ocrConfidence: `${Math.round(confidenceVal * 100)}%`,
    confidenceScore: Math.round(confidenceVal * 100),
    extractedText: p.extracted_text || p.ocr_raw_text || 'No extracted prescription text',
    safetyAlerts: Array.isArray(p.safety_alerts) ? p.safety_alerts : [],
    pharmacistNotes: p.pharmacist_comments || '',
    rejectionReason: p.rejection_reason || '',
    verifiedAt: p.verified_at ? new Date(p.verified_at).toLocaleString() : null,
    clarificationRequestedAt: p.clarification_requested_at ? new Date(p.clarification_requested_at).toLocaleString() : null,
    patientDetails: {
      name: p.customer_name || 'Patient',
      phone: p.customer_phone || '+91 9876543210',
      email: p.customer_email || 'patient@example.com',
      age: p.customer_age != null ? p.customer_age : 'N/A',
      gender: p.customer_gender || 'Not specified',
      address: p.delivery_address || 'Pandharpur, Maharashtra'
    },
    medicines: itemsList.map((m, idx) => ({
      id: m.id || idx + 1,
      name: m.medicine_name || m.name || 'Prescribed Medicine',
      medicineName: m.medicine_name || m.name || 'Prescribed Medicine',
      strength: m.strength || 'Standard',
      dosage: m.dosage_pattern || m.dosage || m.strength || '1 tab',
      dosagePattern: m.dosage_pattern || m.dosage || '1-0-1',
      frequency: m.frequency ? `${m.frequency} times/day` : (m.dosage_pattern || '1-0-1'),
      duration: m.duration_days ? `${m.duration_days} Days` : (m.duration || '5 Days'),
      durationDays: m.duration_days || 5,
      quantity: m.calculated_quantity || m.quantity || 10,
      instructions: m.dosage_instructions || 'Take as prescribed after meals',
      confidence: Math.round((m.confidence_score || m.confidence || 0.95) * 100),
      confidenceScore: Math.round((m.confidence_score || m.confidence || 0.95) * 100),
      stockAvailable: true,
      price: m.price || 45.0
    }))
  };
}
