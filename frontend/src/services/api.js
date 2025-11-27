import axios from 'axios';

const BASE_URL = 'http://localhost:5000/api';

// Configurar axios com timeout e interceptors
const api = axios.create({
    baseURL: BASE_URL,
    timeout: 120000, // 2 minutos para AI summary
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
    response => response,
    error => {
        console.error('Erro na API:', error);
        if (error.response) {
            // Servidor respondeu com erro
            const message = error.response.data?.error || error.response.data?.message || 'Erro no servidor';
            return Promise.reject(new Error(message));
        } else if (error.request) {
            // Requisição foi feita mas sem resposta
            return Promise.reject(new Error('Servidor não respondeu. Verifique se o backend está rodando.'));
        } else {
            // Erro ao configurar requisição
            return Promise.reject(new Error('Erro ao fazer requisição'));
        }
    }
);

// API de Reviews
export const getAllReviews = async () => {
    const response = await api.get('/reviews');
    return response.data;
};

export const getReview = async (id) => {
    const response = await api.get(`/reviews/${id}`);
    return response.data;
};

export const createReview = async (reviewData) => {
    const response = await api.post('/reviews', reviewData);
    return response.data;
};

export const updateReview = async (id, reviewData) => {
    const response = await api.put(`/reviews/${id}`, reviewData);
    return response.data;
};

export const deleteReview = async (id) => {
    await api.delete(`/reviews/${id}`);
};

export const generateSummary = async (movieTitle, reviews, analysisParams, apiKey) => {
    const response = await api.post('/summarize', {
        movie_title: movieTitle,
        reviews: reviews,
        analysis_params: analysisParams,
        api_key: apiKey
    });
    return response.data;
};

export default api;
