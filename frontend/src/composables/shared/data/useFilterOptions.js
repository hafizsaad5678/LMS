import { computed, unref } from 'vue'

const isPresent = (value) => value !== null && value !== undefined && String(value).trim() !== ''

const readValue = (item, getter) => {
    if (typeof getter === 'function') return getter(item)
    if (typeof getter === 'string') return item?.[getter]
    return item
}

const sortAlpha = (a, b) => String(a).localeCompare(String(b))

/**
 * Build unique options from a source list.
 */
export const buildUniqueOptions = (source, config = {}) => {
    const {
        value,
        label = value,
        as = 'primitive',
        isValid = isPresent,
        uniqueBy,
        sort = 'alpha',
        sortFn
    } = config

    const list = Array.isArray(source) ? source : []
    const seen = new Set()
    const options = []

    list.forEach((item) => {
        const optionValue = readValue(item, value)
        if (!isValid(optionValue, item)) return

        const optionLabel = readValue(item, label)
        const keySource = uniqueBy ? readValue(item, uniqueBy) : optionValue
        const uniqueKey = String(keySource)
        if (seen.has(uniqueKey)) return

        seen.add(uniqueKey)
        if (as === 'object') {
            options.push({ value: optionValue, label: optionLabel })
            return
        }

        options.push(optionValue)
    })

    if (sortFn) {
        return [...options].sort(sortFn)
    }

    if (sort === 'none') {
        return options
    }

    if (as === 'object') {
        return [...options].sort((a, b) => sortAlpha(a.label, b.label))
    }

    return [...options].sort(sortAlpha)
}

/**
 * Composable for building deduped select options from reactive data.
 */
export const useFilterOptions = (sourceRef) => {
    const sourceList = () => {
        const value = unref(sourceRef)
        return Array.isArray(value) ? value : []
    }

    const createPrimitiveOptions = (config = {}) => computed(() => buildUniqueOptions(sourceList(), {
        ...config,
        as: 'primitive'
    }))

    const createObjectOptions = (config = {}) => computed(() => buildUniqueOptions(sourceList(), {
        ...config,
        as: 'object'
    }))

    return {
        createPrimitiveOptions,
        createObjectOptions
    }
}

export default useFilterOptions