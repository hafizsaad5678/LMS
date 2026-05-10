import { computed } from 'vue'

/**
 * Composable for common form field formatting
 */
export function useFormFormatting(formData) {
  /**
   * Format CNIC into 12345-1234567-1 format
   */
  const formatCNIC = (value) => {
    const digits = String(value || '').replace(/\D/g, '').slice(0, 13)
    if (digits.length <= 5) return digits
    if (digits.length <= 12) return `${digits.slice(0, 5)}-${digits.slice(5)}`
    return `${digits.slice(0, 5)}-${digits.slice(5, 12)}-${digits.slice(12)}`
  }

  /**
   * Computed property for CNIC two-way binding with formatting
   */
  const cnicModel = computed({
    get: () => formatCNIC(formData.value?.cnic),
    set: (value) => {
      if (formData.value) {
        formData.value.cnic = formatCNIC(value)
      }
    }
  })

  return {
    formatCNIC,
    cnicModel
  }
}
