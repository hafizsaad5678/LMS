/**
 * Common Formatting Utilities
 * Reusable formatting functions across all panels
 */

/**
 * Format date to readable string
 * @param {string} dateString - Date string to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(dateString, options = {}) {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'Invalid Date'

    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        ...options
    }
    return date.toLocaleDateString('en-US', defaultOptions)
}

/**
 * Format date with time
 * @param {string} dateString - Date string to format
 * @returns {string} Formatted date time string
 */
export function formatDateTime(dateString) {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'Invalid Date'

    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

/**
 * Format time only
 * @param {string} timeString - Time string (HH:mm or HH:mm:ss)
 * @returns {string} Formatted time string
 */
export function formatTime(timeString) {
    if (!timeString) return 'N/A'
    const [hours, minutes] = timeString.split(':')
    const hour = parseInt(hours)
    const ampm = hour >= 12 ? 'PM' : 'AM'
    const displayHour = hour % 12 || 12
    return `${displayHour}:${minutes} ${ampm}`
}

/**
 * Format relative date (e.g., "2 days ago")
 * @param {string} dateString - Date string
 * @returns {string} Relative date string
 */
export function formatRelativeDate(dateString) {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return formatDate(dateString)
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code
 * @returns {string} Formatted currency string
 */
export function formatCurrency(amount, currency = 'PKR') {
    if (amount === null || amount === undefined) return 'N/A'
    return new Intl.NumberFormat('en-PK', {
        style: 'currency',
        currency,
        minimumFractionDigits: 0
    }).format(amount)
}

/**
 * Format percentage
 * @param {number} value - Value to format
 * @param {number} decimals - Decimal places
 * @returns {string} Formatted percentage string
 */
export function formatPercentage(value, decimals = 0) {
    if (value === null || value === undefined) return 'N/A'
    return `${value.toFixed(decimals)}%`
}

/**
 * Truncate text with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength = 50) {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
}



/**
 * Get icon class for file type
 * @param {string} fileType - File type/extension
 * @returns {string} Bootstrap icon class name (without 'bi bi-')
 */
export function getFileIcon(fileType) {
    const type = (fileType || '').toLowerCase()
    if (type.includes('pdf')) return 'file-earmark-pdf-fill'
    if (type.includes('doc') || type.includes('word')) return 'file-earmark-word-fill'
    if (type.includes('xls') || type.includes('excel')) return 'file-earmark-excel-fill'
    if (type.includes('ppt') || type.includes('powerpoint')) return 'file-earmark-slides-fill'
    if (type.includes('zip') || type.includes('rar') || type.includes('archive')) return 'file-earmark-zip-fill'
    if (type.includes('image') || type.includes('jpg') || type.includes('png')) return 'file-earmark-image-fill'
    if (type.includes('video') || type.includes('mp4')) return 'file-earmark-play-fill'
    if (type.includes('audio') || type.includes('mp3')) return 'file-earmark-music-fill'
    return 'file-earmark-text-fill'
}

/**
 * Format file size
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size string
 */
export function formatFileSize(bytes) {
    if (!bytes) return 'Unknown'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / 1048576).toFixed(1) + ' MB'
}

/**
 * Get initials from name
 * @param {string} name - Full name
 * @returns {string} Initials (max 2 chars)
 */
export function getInitials(name) {
    if (!name) return '?'
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
}

export default {
    formatDate,
    formatDateTime,
    formatTime,
    formatRelativeDate,
    formatCurrency,
    formatPercentage,
    truncateText,
    getFileIcon,
    formatFileSize,
    getInitials
}
