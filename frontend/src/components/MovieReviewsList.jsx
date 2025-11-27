import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllReviews, generateSummary } from '../services/api';

function MovieReviewsList() {
    const navigate = useNavigate();
    const [reviews, setReviews] = useState([]);
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedMovie, setSelectedMovie] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [loadingAnalysis, setLoadingAnalysis] = useState(false);
    const [apiKey, setApiKey] = useState(localStorage.getItem('gemini_api_key') || '');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        loadReviews();
    }, []);

    const loadReviews = async () => {
        try {
            setLoading(true);
            const data = await getAllReviews();
            setReviews(data);

            // Agrupar por filme
            const movieMap = {};
            data.forEach(review => {
                if (!movieMap[review.movie]) {
                    movieMap[review.movie] = {
                        title: review.movie,
                        reviews: [],
                        totalRating: 0,
                        sentiments: { positivo: 0, negativo: 0, neutro: 0 }
                    };
                }
                movieMap[review.movie].reviews.push(review);
                movieMap[review.movie].totalRating += review.rating;
                movieMap[review.movie].sentiments[review.predicted_sentiment]++;
            });

            const movieList = Object.values(movieMap).map(movie => ({
                ...movie,
                avgRating: movie.totalRating / movie.reviews.length,
                reviewCount: movie.reviews.length
            }));

            setMovies(movieList);
            setLoading(false);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    const handleGenerateSummary = async (movie) => {
        if (!apiKey) {
            alert('Por favor, insira sua chave de API do Gemini primeiro.');
            const key = prompt('Chave de API do Gemini:');
            if (key) {
                setApiKey(key);
                localStorage.setItem('gemini_api_key', key);
            } else {
                return;
            }
        }

        setSelectedMovie(movie);
        setShowModal(true);
        setLoadingAnalysis(true);
        setAiAnalysis(null);

        try {
            const result = await generateSummary(
                movie.title,
                movie.reviews.slice(0, 15), // Limitar a 15 reviews para evitar erro de quota
                {
                    sentiment_filter: 'all',
                    sort_order: 'helpful',
                    total_reviews: movie.reviews.length
                },
                apiKey
            );
            setAiAnalysis(result);
        } catch (err) {
            setAiAnalysis({ error: err.message });
        } finally {
            setLoadingAnalysis(false);
        }
    };

    const renderStars = (rating) => {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        const stars = [];

        for (let i = 0; i < fullStars; i++) {
            stars.push(<i key={`full-${i}`} className="bi bi-star-fill text-warning"></i>);
        }
        if (hasHalfStar) {
            stars.push(<i key="half" className="bi bi-star-half text-warning"></i>);
        }
        for (let i = 0; i < emptyStars; i++) {
            stars.push(<i key={`empty-${i}`} className="bi bi-star text-warning"></i>);
        }

        return stars;
    };

    const getSentimentBadge = (sentiment, count) => {
        const colors = {
            positivo: 'success',
            negativo: 'danger',
            neutro: 'warning'
        };
        const labels = {
            positivo: 'Positivo',
            negativo: 'Negativo',
            neutro: 'Neutro'
        };

        return (
            <span className={`badge bg-${colors[sentiment]} me-1`}>
                {labels[sentiment]}: {count}
            </span>
        );
    };

    if (loading) {
        return (
            <div className="container mt-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Carregando...</span>
                </div>
                <p className="mt-3">Carregando filmes...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mt-5">
                <div className="alert alert-danger" role="alert">
                    <h4 className="alert-heading">Erro!</h4>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    const filteredMovies = movies.filter(movie =>
        movie.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="container-fluid py-4">
            <div className="row mb-4 align-items-center">
                <div className="col-md-6">
                    <h1 className="display-5 fw-bold mb-0">
                        <i className="bi bi-film me-2"></i>
                        Painel de Filmes
                    </h1>
                </div>
                <div className="col-md-6">
                    <div className="input-group">
                        <span className="input-group-text bg-dark border-secondary text-light">
                            <i className="bi bi-search"></i>
                        </span>
                        <input
                            type="text"
                            className="form-control bg-dark border-secondary text-light"
                            placeholder="Pesquisar filmes..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>
            </div>

            <div className="row g-4">
                {filteredMovies.map((movie) => (
                    <div key={movie.title} className="col-md-6 col-lg-4">
                        <div
                            className="card movie-card h-100 shadow-sm hover-shadow"
                            style={{ cursor: 'pointer', transition: 'transform 0.2s' }}
                            onClick={() => navigate(`/movie/${encodeURIComponent(movie.title)}`)}
                        >
                            <div className="card-body">
                                <h5 className="card-title fw-bold text-truncate" title={movie.title}>
                                    {movie.title}
                                </h5>

                                <div className="mb-3">
                                    <div className="d-flex align-items-center mb-2">
                                        <div className="me-2">
                                            {renderStars(movie.avgRating / 2)}
                                        </div>
                                        <span className="text-muted">
                                            {movie.avgRating.toFixed(1)}/10.0
                                        </span>
                                    </div>
                                    <small className="text-muted">
                                        {movie.reviewCount} {movie.reviewCount === 1 ? 'avaliação' : 'avaliações'}
                                    </small>
                                </div>

                                <div className="mb-3">
                                    <h6 className="small text-muted mb-2">Sentimentos:</h6>
                                    <div>
                                        {getSentimentBadge('positivo', movie.sentiments.positivo)}
                                        {getSentimentBadge('negativo', movie.sentiments.negativo)}
                                        {getSentimentBadge('neutro', movie.sentiments.neutro)}
                                    </div>
                                </div>

                                <button
                                    className="btn btn-primary w-100"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleGenerateSummary(movie);
                                    }}
                                >
                                    <i className="bi bi-magic me-2"></i>
                                    Gerar Resumo AI
                                </button>
                                <button
                                    className="btn btn-outline-secondary w-100 mt-2"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        navigate('/add', { state: { movieTitle: movie.title } });
                                    }}
                                >
                                    <i className="bi bi-plus-circle me-2"></i>
                                    Adicionar Avaliação
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Modal de Análise AI */}
            {showModal && (
                <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
                    <div className="modal-dialog modal-xl modal-dialog-scrollable">
                        <div className="modal-content">
                            <div className="modal-header bg-primary text-white">
                                <h5 className="modal-title">
                                    <i className="bi bi-robot me-2"></i>
                                    Análise AI: {selectedMovie?.title}
                                </h5>
                                <button
                                    type="button"
                                    className="btn-close btn-close-white"
                                    onClick={() => setShowModal(false)}
                                ></button>
                            </div>
                            <div className="modal-body">
                                {loadingAnalysis ? (
                                    <div className="text-center py-5">
                                        <div className="spinner-border text-primary mb-3" role="status">
                                            <span className="visually-hidden">Analisando...</span>
                                        </div>
                                        <p>Analisando {selectedMovie?.reviewCount} avaliações...</p>
                                        <small className="text-muted">
                                            Isso pode levar alguns segundos...
                                        </small>
                                    </div>
                                ) : aiAnalysis?.error ? (
                                    <div className="alert alert-danger">
                                        <h5>Erro na Análise</h5>
                                        <p>{aiAnalysis.error}</p>
                                    </div>
                                ) : aiAnalysis ? (
                                    <div>
                                        {/* Metadata */}
                                        {aiAnalysis.metadata && (
                                            <div className="alert alert-info mb-4">
                                                <h6 className="fw-bold mb-3">
                                                    <i className="bi bi-info-circle me-2"></i>
                                                    Metadados da Análise
                                                </h6>
                                                <div className="row g-3">
                                                    <div className="col-md-4">
                                                        <strong>Avaliações Analisadas:</strong> {aiAnalysis.metadata.reviews_analyzed}
                                                    </div>
                                                    <div className="col-md-4">
                                                        <strong>Nota Média:</strong> {aiAnalysis.metadata.average_rating}/5
                                                    </div>
                                                    <div className="col-md-4">
                                                        <strong>Confiança ML:</strong> {(aiAnalysis.metadata.average_confidence * 100).toFixed(1)}%
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* AI Summary */}
                                        <div className="ai-summary">
                                            {typeof aiAnalysis.summary === 'string' ? (
                                                // Fallback for legacy or error text
                                                <div dangerouslySetInnerHTML={{ __html: formatSummary(aiAnalysis.summary) }} />
                                            ) : (
                                                // Structured JSON Display
                                                <div className="d-flex flex-column gap-4">
                                                    {/* Executive Summary */}
                                                    <div className="bg-light p-4 rounded-3 border-start border-5 border-primary">
                                                        <h4 className="text-primary mb-3">
                                                            <i className="bi bi-card-text me-2"></i>
                                                            Resumo Executivo
                                                        </h4>
                                                        <p className="lead mb-0">{aiAnalysis.summary.resumo_executivo}</p>
                                                    </div>

                                                    {/* Sentiment Analysis */}
                                                    <div className="card border-0 shadow-sm">
                                                        <div className="card-body">
                                                            <h5 className="card-title text-secondary">
                                                                <i className="bi bi-graph-up-arrow me-2"></i>
                                                                Análise de Sentimento
                                                            </h5>
                                                            <p className="card-text fst-italic text-muted">
                                                                "{aiAnalysis.summary.analise_sentimento}"
                                                            </p>
                                                        </div>
                                                    </div>

                                                    {/* Pros & Cons Grid */}
                                                    <div className="row g-4">
                                                        <div className="col-md-6">
                                                            <div className="card h-100 border-success border-opacity-25 bg-success bg-opacity-10">
                                                                <div className="card-header bg-transparent border-success border-opacity-25 text-success fw-bold">
                                                                    <i className="bi bi-hand-thumbs-up-fill me-2"></i>
                                                                    Pontos Positivos
                                                                </div>
                                                                <ul className="list-group list-group-flush bg-transparent">
                                                                    {aiAnalysis.summary.pontos_positivos?.map((point, idx) => (
                                                                        <li key={idx} className="list-group-item bg-transparent border-success border-opacity-25">
                                                                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                                                                            {point}
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        </div>
                                                        <div className="col-md-6">
                                                            <div className="card h-100 border-danger border-opacity-25 bg-danger bg-opacity-10">
                                                                <div className="card-header bg-transparent border-danger border-opacity-25 text-danger fw-bold">
                                                                    <i className="bi bi-hand-thumbs-down-fill me-2"></i>
                                                                    Pontos Negativos
                                                                </div>
                                                                <ul className="list-group list-group-flush bg-transparent">
                                                                    {aiAnalysis.summary.pontos_negativos?.map((point, idx) => (
                                                                        <li key={idx} className="list-group-item bg-transparent border-danger border-opacity-25">
                                                                            <i className="bi bi-x-circle-fill text-danger me-2"></i>
                                                                            {point}
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Public Highlights */}
                                                    <div className="alert alert-secondary mb-0">
                                                        <h6 className="alert-heading fw-bold">
                                                            <i className="bi bi-chat-quote-fill me-2"></i>
                                                            Destaques do Público
                                                        </h6>
                                                        <p className="mb-0">{aiAnalysis.summary.destaques_do_publico}</p>
                                                    </div>

                                                    {/* Tags / Keywords */}
                                                    {aiAnalysis.summary.tags && (
                                                        <div className="mb-2">
                                                            <h6 className="fw-bold text-secondary mb-3">
                                                                <i className="bi bi-tags-fill me-2"></i>
                                                                Tags & Temas
                                                            </h6>
                                                            <div className="d-flex flex-wrap gap-2">
                                                                {aiAnalysis.summary.tags.map((tag, idx) => (
                                                                    <span key={idx} className="badge rounded-pill bg-light text-dark border border-secondary bg-opacity-10 px-3 py-2">
                                                                        #{tag}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Verdict & Recommendation */}
                                                    <div className="bg-dark text-white p-4 rounded-3 text-center position-relative overflow-hidden">
                                                        <div className="position-relative z-1">
                                                            <h3 className="display-6 fw-bold text-warning mb-3">
                                                                <i className="bi bi-trophy-fill me-2"></i>
                                                                Veredito Final
                                                            </h3>
                                                            <p className="fs-4 mb-4">"{aiAnalysis.summary.veredito_final}"</p>
                                                            <div className="d-inline-block bg-white text-dark px-4 py-2 rounded-pill fw-bold">
                                                                <i className="bi bi-people-fill me-2 text-primary"></i>
                                                                Recomendado para: {aiAnalysis.summary.recomendacao}
                                                            </div>
                                                        </div>
                                                        <div className="position-absolute top-0 start-0 w-100 h-100 bg-gradient opacity-25" style={{ background: 'linear-gradient(45deg, #ffc107, #fd7e14)' }}></div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ) : null}
                            </div>
                            <div className="modal-footer">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => setShowModal(false)}
                                >
                                    Fechar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}</div >
    );
}

// Função para formatar o texto do Gemini (Legacy Support)
function formatSummary(text) {
    if (!text) return '';
    // Basic markdown support for fallback
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br />');
}

export default MovieReviewsList;
