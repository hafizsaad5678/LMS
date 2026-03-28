import api, { apiCall } from '@/services/shared/core/api'

const QUIZ_REQUEST_CONFIG = { timeout: 180000 }

export const aiService = {
    // Long-running AI generation can take longer than normal CRUD endpoints.
    requestConfig: QUIZ_REQUEST_CONFIG,

    /**
     * Step 1 & 2: Get AI suggestions or follow-up configurations
     */
    initQuiz: (data) => apiCall(
        () => api.post('/ai/quiz/init/', data, QUIZ_REQUEST_CONFIG),
        'AI',
        'init_quiz'
    ),

    /**
     * Step 3: Generate full quiz JSON
     */
    generateQuiz: (data) => apiCall(
        () => api.post('/ai/quiz/generate/', data, QUIZ_REQUEST_CONFIG),
        'AI',
        'generate_quiz'
    ),

    /**
     * Regenerate single specific question
     */
    regenerateQuizQuestion: (data) => apiCall(
        () => api.post('/ai/quiz/regenerate-question/', data, QUIZ_REQUEST_CONFIG),
        'AI',
        'regenerate_quiz_question'
    ),

    /**
     * Step 6: Save quiz and handle assignments
     */
    saveQuiz: (data) => apiCall(
        () => api.post('/ai/quiz/save/', data),
        'AI',
        'save_quiz'
    ),

    /**
     * Generic AI Prompt call
     */
    callAI: (prompt) => apiCall(
        () => api.post('/ai/call/', { prompt }),
        'AI',
        'call'
    )
}

export default aiService
