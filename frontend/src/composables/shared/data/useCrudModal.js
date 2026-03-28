/**
 * CRUD Modal Composable
 * Reusable logic for Create/Edit/Delete modal operations
 * Reduces boilerplate code in list views
 */
import { ref } from 'vue'
import { useAlert } from '../form/useFormHelpers'

export const useCrudModal = (options = {}) => {
    const {
        entityName = 'item',
        createFn,
        updateFn,
        deleteFn,
        onSuccess,
        defaultForm = {}
    } = options

    // Alert management
    const { alert, showAlert, clearAlert, showSuccess, showError, showWarning, showInfo } = useAlert()

    // Modal states
    const showModal = ref(false)
    const showDeleteModal = ref(false)
    const editMode = ref(false)
    const submitting = ref(false)
    const deleting = ref(false)

    // Data states
    const form = ref({ ...defaultForm })
    const selectedItem = ref(null)

    /**
     * Open create modal
     */
    const openCreateModal = () => {
        editMode.value = false
        form.value = { ...defaultForm }
        showModal.value = true
    }

    /**
     * Open edit modal
     */
    const openEditModal = (item) => {
        editMode.value = true
        selectedItem.value = item
        form.value = { ...item }
        showModal.value = true
    }

    /**
     * Close modal and reset
     */
    const closeModal = () => {
        showModal.value = false
        editMode.value = false
        selectedItem.value = null
        form.value = { ...defaultForm }
    }

    /**
     * Handle form submission (create or update)
     */
    const handleSubmit = async (formData = null) => {
        const payload = formData || form.value
        submitting.value = true

        try {
            if (editMode.value) {
                await updateFn(selectedItem.value.id, payload)
                showSuccess(`${entityName} updated successfully!`)
            } else {
                await createFn(payload)
                showSuccess(`${entityName} created successfully!`)
            }

            closeModal()
            if (onSuccess) await onSuccess()
        } catch (error) {
            console.error(`Error saving ${entityName}:`, error)
            showError(`Failed to save ${entityName}. Please try again.`)
        } finally {
            submitting.value = false
        }
    }

    /**
     * Confirm delete
     */
    const confirmDelete = (item) => {
        selectedItem.value = item
        showDeleteModal.value = true
    }

    /**
     * Handle delete
     */
    const handleDelete = async () => {
        deleting.value = true

        try {
            await deleteFn(selectedItem.value.id)
            showSuccess(`${entityName} deleted successfully!`)
            showDeleteModal.value = false
            selectedItem.value = null
            if (onSuccess) await onSuccess()
        } catch (error) {
            console.error(`Error deleting ${entityName}:`, error)
            showError(`Failed to delete ${entityName}. Please try again.`)
        } finally {
            deleting.value = false
        }
    }

    return {
        // Alert
        alert,
        showAlert,
        clearAlert,
        showSuccess,
        showError,
        showWarning,
        showInfo,

        // Modal states
        showModal,
        showDeleteModal,
        editMode,
        submitting,
        deleting,

        // Data
        form,
        selectedItem,

        // Actions
        openCreateModal,
        openEditModal,
        closeModal,
        handleSubmit,
        confirmDelete,
        handleDelete
    }
}
