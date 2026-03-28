/**
 * Search and Filtering Utilities
 */

/**
 * Perform a smart multi-word search on an item across multiple fields.
 * Every word in the search query must match at least one of the fields in the item.
 * 
 * @param {Object} item - The object to search within
 * @param {string} query - The raw search query string from user input
 * @param {Array} fields - List of dot-notation strings representing fields to search (e.g., ['name', 'subject.code'])
 * @returns {Boolean} - True if the item matches the query
 */
export const smartSearch = (item, query, fields) => {
    if (!item || !query || !fields || fields.length === 0) return true
    
    const lowerQuery = query.toLowerCase()
    const trimmedQuery = lowerQuery.trim()
    if (!trimmedQuery) return true
    
    const searchTerms = trimmedQuery.split(/\s+/).filter(t => t.length > 0)
    
    /**
     * Helper to get nested value from object path
     */
    const getNestedValue = (obj, path) => {
        if (!path) return ''
        return path.split('.').reduce((acc, part) => acc && acc[part], obj)
    }

    // Every word must match at least something
    return searchTerms.every(term => {
        return fields.some(field => {
            const value = getNestedValue(item, field)
            const stringValue = value?.toString().toLowerCase() || ''
            return stringValue.includes(term)
        })
    })
}
