import apiClient from '../api/apiClient';
import { useMockData } from '../context/MockDataContext';

export const useMedicineService = () => {
  const { 
    getMedicines: getMockMedicines, 
    addMedicine: addMockMedicine, 
    updateMedicine: updateMockMedicine, 
    deleteMedicine: deleteMockMedicine 
  } = useMockData();

  const fetchMedicines = async () => {
    try {
      const response = await apiClient.get('/medicines');
      if (Array.isArray(response.data)) {
        return response.data.map(med => ({
          id: med.id,
          name: med.brand_name || med.name,
          genericName: med.generic_name || med.name,
          category: med.category || 'General',
          strength: med.strength || '500mg',
          stock: med.stock_quantity ?? med.stock ?? 120,
          price: med.price ? `₹${med.price}` : '₹120',
          numericPrice: med.price || 120,
          manufacturer: med.manufacturer || 'MediLoop Pharma',
          requiresPrescription: med.requires_prescription ?? true,
          status: (med.stock_quantity ?? med.stock ?? 120) > 20 ? 'In Stock' : ((med.stock_quantity ?? med.stock ?? 120) > 0 ? 'Low Stock' : 'Out of Stock')
        }));
      }
    } catch (err) {
      console.warn('Backend /medicines offline, using mock medicines fallback:', err.message);
    }
    return getMockMedicines();
  };

  const createMedicine = async (medicine) => {
    try {
      const payload = {
        brand_name: medicine.name || medicine.brand_name,
        generic_name: medicine.genericName || medicine.generic_name || medicine.name,
        strength: medicine.strength || '500mg',
        price: parseFloat(medicine.numericPrice || medicine.price?.toString().replace(/[^0-9.]/g, '') || '100'),
        manufacturer: medicine.manufacturer || 'MediLoop Pharma',
        requires_prescription: medicine.requiresPrescription ?? true,
        category: medicine.category || 'General',
        stock_quantity: parseInt(medicine.stock || '100', 10)
      };

      await apiClient.post('/medicines', payload);
      return { success: true };
    } catch (err) {
      console.warn('Backend medicine create failed, saving locally:', err.message);
      addMockMedicine(medicine);
      return { success: true };
    }
  };

  const editMedicine = async (id, updatedMed) => {
    try {
      const payload = {
        brand_name: updatedMed.name || updatedMed.brand_name,
        generic_name: updatedMed.genericName || updatedMed.generic_name,
        strength: updatedMed.strength,
        price: parseFloat(updatedMed.numericPrice || updatedMed.price?.toString().replace(/[^0-9.]/g, '') || '100'),
        manufacturer: updatedMed.manufacturer,
        requires_prescription: updatedMed.requiresPrescription,
        category: updatedMed.category,
        stock_quantity: parseInt(updatedMed.stock || '100', 10)
      };

      await apiClient.put(`/medicines/${id}`, payload);
      return { success: true };
    } catch (err) {
      console.warn('Backend medicine update failed, updating locally:', err.message);
      updateMockMedicine(id, updatedMed);
      return { success: true };
    }
  };

  const removeMedicine = async (id) => {
    try {
      await apiClient.delete(`/medicines/${id}`);
      return { success: true };
    } catch (err) {
      console.warn('Backend medicine delete failed, removing locally:', err.message);
      deleteMockMedicine(id);
      return { success: true };
    }
  };

  return {
    getMedicines: fetchMedicines,
    addMedicine: createMedicine,
    updateMedicine: editMedicine,
    deleteMedicine: removeMedicine
  };
};
