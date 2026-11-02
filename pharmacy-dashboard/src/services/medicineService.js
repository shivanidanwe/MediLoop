import apiClient from '../api/apiClient';

export const useMedicineService = () => {
  const fetchMedicines = async () => {
    try {
      const response = await apiClient.get('/medicines');
      if (Array.isArray(response.data)) {
        return response.data.map(med => ({
          id: med.id,
          name: med.brand_name || med.name,
          brandName: med.brand_name || med.name,
          genericName: med.generic_name || med.name,
          category: med.category || 'General',
          strength: med.strength || '500mg',
          dosageForm: med.dosage_form || 'Tablet',
          stock: med.stock_quantity ?? med.stock ?? 100,
          stockQuantity: med.stock_quantity ?? med.stock ?? 100,
          reorderLevel: med.reorder_level ?? 20,
          price: med.price ? `₹${med.price}` : (med.selling_price ? `₹${med.selling_price}` : '₹45'),
          numericPrice: med.selling_price || med.price || 45,
          sellingPrice: med.selling_price || med.price || 45,
          mrp: med.mrp || Math.round((med.selling_price || med.price || 45) * 1.25),
          batchNumber: med.batch_number || 'BAT-2026-01',
          expiryDate: med.expiry_date || '2027-12-31',
          manufacturer: med.manufacturer || 'Cipla / Sun Pharma',
          requiresPrescription: med.prescription_required ?? true,
          prescriptionRequired: med.prescription_required ?? true,
          availability: med.availability || ((med.stock_quantity ?? 100) > 20 ? 'In Stock' : ((med.stock_quantity ?? 100) > 0 ? 'Low Stock' : 'Out of Stock')),
          status: med.status || ((med.stock_quantity ?? 100) > 20 ? 'In Stock' : ((med.stock_quantity ?? 100) > 0 ? 'Low Stock' : 'Out of Stock'))
        }));
      }
    } catch (err) {
      console.error('Backend /medicines error:', err.message);
    }
    return [];
  };

  const createMedicine = async (medicine) => {
    try {
      const payload = {
        brand_name: medicine.name || medicine.brand_name,
        generic_name: medicine.genericName || medicine.generic_name || medicine.name,
        strength: medicine.strength || '500mg',
        dosage_form: medicine.dosageForm || medicine.dosage_form || 'Tablet',
        price: parseFloat(medicine.numericPrice || medicine.price?.toString().replace(/[^0-9.]/g, '') || '45'),
        manufacturer: medicine.manufacturer || 'Cipla / Sun Pharma',
        prescription_required: medicine.requiresPrescription ?? medicine.prescriptionRequired ?? true,
        category: medicine.category || 'General'
      };

      const res = await apiClient.post('/medicines', payload);
      return { success: true, data: res.data };
    } catch (err) {
      console.error('Backend medicine create error:', err.message);
      return { success: false, message: err.response?.data?.detail || err.message };
    }
  };

  const editMedicine = async (id, updatedMed) => {
    try {
      const payload = {
        brand_name: updatedMed.name || updatedMed.brand_name,
        generic_name: updatedMed.genericName || updatedMed.generic_name,
        strength: updatedMed.strength,
        dosage_form: updatedMed.dosageForm,
        manufacturer: updatedMed.manufacturer,
        prescription_required: updatedMed.requiresPrescription ?? updatedMed.prescriptionRequired,
        category: updatedMed.category
      };

      await apiClient.put(`/medicines/${id}`, payload);
      return { success: true };
    } catch (err) {
      console.error('Backend medicine update error:', err.message);
      return { success: false, message: err.response?.data?.detail || err.message };
    }
  };

  const removeMedicine = async (id) => {
    try {
      await apiClient.delete(`/medicines/${id}`);
      return { success: true };
    } catch (err) {
      console.error('Backend medicine delete error:', err.message);
      return { success: false, message: err.response?.data?.detail || err.message };
    }
  };

  const previewCatalogueUpload = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post('/medicines/import-preview', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return { success: true, data: res.data };
    } catch (err) {
      console.error('Preview catalogue error:', err);
      return { success: false, message: err.response?.data?.detail || err.message };
    }
  };

  const executeCatalogueImport = async (file, mode, mapping) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mode', mode || 'add');
      formData.append('mapping_json', JSON.stringify(mapping || {}));

      const res = await apiClient.post('/medicines/import-execute', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return { success: true, data: res.data };
    } catch (err) {
      console.error('Execute catalogue import error:', err);
      return { success: false, message: err.response?.data?.detail || err.message };
    }
  };

  const adjustStock = async (id, payload) => {
    try {
      const res = await apiClient.post(`/medicines/${id}/stock`, payload);
      return { success: true, data: res.data };
    } catch (err) {
      console.error('Adjust stock error:', err);
      return { success: false, message: err.response?.data?.detail || err.message };
    }
  };

  const getStockMovements = async () => {
    try {
      const res = await apiClient.get('/medicines/movements');
      return Array.isArray(res.data) ? res.data : [];
    } catch (err) {
      console.error('Get stock movements error:', err);
      return [];
    }
  };

  const getExpiringMedicines = async (days = 180) => {
    try {
      const res = await apiClient.get(`/medicines/expiring?days=${days}`);
      return Array.isArray(res.data) ? res.data : [];
    } catch (err) {
      console.error('Get expiring error:', err);
      return [];
    }
  };

  return {
    getMedicines: fetchMedicines,
    fetchMedicines,
    addMedicine: createMedicine,
    updateMedicine: editMedicine,
    deleteMedicine: removeMedicine,
    previewCatalogueUpload,
    executeCatalogueImport,
    adjustStock,
    getStockMovements,
    getExpiringMedicines
  };
};
