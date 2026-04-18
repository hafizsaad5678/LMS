import { computed, unref } from 'vue'

const toArray = (source) => {
    const value = unref(source)
    return Array.isArray(value) ? value : []
}

/**
 * Reusable computed stats helpers for list pages.
 */
export const useListStats = (sourceRef) => {
    const getList = () => toArray(sourceRef)

    const count = (predicate = null) => computed(() => {
        const list = getList()
        return predicate ? list.filter(predicate).length : list.length
    })

    const sum = (selector) => computed(() => getList()
        .reduce((total, item) => total + (Number(selector(item)) || 0), 0))

    const average = (selector, precision = 0) => computed(() => {
        const list = getList()
        if (!list.length) return 0

        const total = list.reduce((acc, item) => acc + (Number(selector(item)) || 0), 0)
        const avg = total / list.length
        return precision > 0 ? Number(avg.toFixed(precision)) : Math.round(avg)
    })

    const uniqueCount = (selector) => computed(() => new Set(getList()
        .map(selector)
        .filter((value) => value !== null && value !== undefined && value !== '')).size)

    const summary = (definitions) => computed(() => {
        const list = getList()
        return Object.entries(definitions).reduce((acc, [key, resolver]) => {
            acc[key] = resolver(list)
            return acc
        }, {})
    })

    return {
        count,
        sum,
        average,
        uniqueCount,
        summary
    }
}

export default useListStats