import React, { useState, useEffect } from 'react';
import { getAllReviews, deleteReview } from '../services/api';
import { useNavigate } from 'react-router-dom';

function MovieReviewsPage() {
    const [reviews, setReviews] = useState([]);
    const [filteredReviews, setFilteredReviews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [sentimentFilter, setSentimentFilter] = useState('all');
    const [sortBy, setSortBy] = useState('date');
    const navigate = useNavigate();

    useEffect(() => {
        loadReviews();
    }, []);

    useEffect(() => {
        filterAndSortReviews();
    }, [reviews, searchTerm, sentimentFilter, sortBy]);

    const loadReviews = async () => {
        try {
            setLoading(true);
            const data = await getAllReviews();
            setReviews(data);
            setLoading(false);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    const filterAndSortReviews = () => {
        let filtered = [...reviews];

        // Filtro de busca
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            filtered = filtered.filter(
                (review) =>
                    review.movie?.toLowerCase().includes(term) ||
                    review.reviewer?.toLowerCase().includes(term) ||
                    review.review_summary?.toLowerCase().includes(term) ||
                    review.review_detail?.toLowerCase().includes(term)
            );
        }

        // Filtro de sentimento
        if (sentimentFilter !== 'all') {
            filtered = filtered.filter(
                (review) => review.predicted_sentiment === sentimentFilter
            );
        }

        // Ordenação
        filtered.sort((a, b) => {
            switch (sortBy) {
                case 'date':
                    return new Date(b.review_date) - new Date(a.review_date);
                case 'rating-high':
                    return b.rating - a.rating;
                case 'rating-low':
                    return a.rating - b.rating;
                case 'movie':
                    return (a.movie || '').localeCompare(b.movie || '');
                default:
                    return 0;
            }
        });

        setFilteredReviews(filtered);
    };

    const handleDelete = async (id, movieTitle) => {
        if (window.confirm(`Tem certeza que deseja excluir a avaliação de "${movieTitle}"?`)) {
            try {
                await deleteReview(id);
                setReviews(reviews.filter((r) => r.review_id !== id));
            } catch (err) {
                alert('Erro ao excluir avaliação: ' + err.message);
            }
        }
    };

    const getSentimentBadge = (sentiment) => {
        const config = {
            positivo: { color: 'success', label: 'Positivo', icon: 'emoji-smile' },
            negativo: { color: 'danger', label: 'Negativo', icon: 'emoji-frown' },
            neutro: { color: 'warning', label: 'Neutro', icon: 'emoji-neutral' },
        };
        const { color, label, icon } = config[sentiment] || config.neutro;
        return (
            <span className={`badge bg-${color}`}>
                <i className={`bi bi-${icon} me-1`}></i>
                {label}
            </span>
        );
    };

    const renderStars = (rating) => {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        const stars = [];

        for (let i = 0; i < fullStars; i++) {
            stars.push(
                <i
                    key={`full-${i}`}
                    className="bi bi-star-fill text-warning"
                ></i>
            );
        }
        if (hasHalfStar) {
            stars.push(
                <i
                    key="half"
                    className="bi bi-star-half text-warning"
                ></i>
            );
        }
        for (let i = 0; i < emptyStars; i++) {
            stars.push(
                <i
                    key={`empty-${i}`}
                    className="bi bi-star text-warning"
                ></i>
            );
        }
        return stars;
    };

    if (loading) {
        return (
            <div className="container mt-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Carregando...</span>
                </div>
                <p className="mt-3">Carregando avaliações...</p>
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

    return (
        <div className="container-fluid py-4">
            <div className="row mb-4">
                <div className="col">
                    <h1 className="display-5 fw-bold">
                        <i className="bi bi-list-ul me-2"></i>
                        Todas as Avaliações
                    </h1>
                    <p className="lead text-muted">
                        {filteredReviews.length} de {reviews.length} avaliações
                    </p>
                </div>
            </div>

            {/* Filtros e Busca */}
            <div className="row mb-4">
                <div className="col-md-6 mb-3">
                    <div className="input-group">
                        <span className="input-group-text">
                            <i className="bi bi-search"></i>
                        </span>
                        <input
                            type="text"
                            className="form-control"
                            placeholder="Buscar por filme, avaliador ou conteúdo..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>
                <div className="col-md-3 mb-3">
                    <select
                        className="form-select"
                        value={sentimentFilter}
                        onChange={(e) => setSentimentFilter(e.target.value)}
                    >
                        <option value="all">Todos os Sentimentos</option>
                        <option value="positivo">Apenas Positivo</option>
                        <option value="negativo">Apenas Negativo</option>
                        <option value="neutro">Apenas Neutro</option>
                    </select>
                </div>
                <div className="col-md-3 mb-3">
                    <select
                        className="form-select"
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                    >
                        <option value="date">Mais Recente</option>
                        <option value="rating-high">Maior Nota</option>
                        <option value="rating-low">Menor Nota</option>
                        <option value="movie">Filme (A-Z)</option>
                    </select>
                </div>
            </div>

            {/* Lista de Avaliações */}
            <div className="row">
                {filteredReviews.length === 0 ? (
                    <div className="col-12">
                        <div className="alert alert-info text-center">
                            <i className="bi bi-info-circle me-2"></i>
                            Nenhuma avaliação encontrada com os filtros selecionados.
                        </div>
                    </div>
                ) : (
                    filteredReviews.map((review) => (
                        <div key={review.review_id} className="col-12 mb-3">
                            <div className="card review-card shadow-sm hover-shadow">
                                <div className="card-body">
                                    <div className="row">
                                        <div className="col-md-8">
                                            <h5 className="card-title fw-bold">
                                                <i className="bi bi-film me-2 text-primary"></i>
                                                {review.movie}
                                            </h5>
                                            <p className="text-muted small mb-2">
                                                <i className="bi bi-person me-1"></i>
                                                {review.reviewer} •
                                                <i className="bi bi-calendar ms-2 me-1"></i>
                                                {new Date(review.review_date).toLocaleDateString('pt-BR')}
                                                {review.spoiler_tag === 1 && (
                                                    <span className="badge bg-danger ms-2">
                                                        <i className="bi bi-exclamation-triangle me-1"></i>
                                                        Spoiler
                                                    </span>
                                                )}
                                            </p>
                                            <div className="mb-2">
                                                <strong className="me-2">Resumo:</strong>
                                                {review.review_summary}
                                            </div>
                                            {review.review_detail && (
                                                <details className="mt-2">
                                                    <summary className="text-primary" style={{ cursor: 'pointer' }}>
                                                        Ver detalhes completos
                                                    </summary>
                                                    <p className="mt-2 text-muted small">
                                                        {review.review_detail}
                                                    </p>
                                                </details>
                                            )}
                                        </div>
                                        <div className="col-md-4 text-md-end">
                                            <div className="mb-2">
                                                {renderStars(review.rating / 2)}
                                                <span className="ms-2 fw-bold">{review.rating}/10</span>
                                            </div>
                                            <div className="mb-3">
                                                {getSentimentBadge(review.predicted_sentiment)}
                                                <small className="text-muted d-block mt-1">
                                                    Confiança: {(review.prediction_confidence * 100).toFixed(0)}%
                                                </small>
                                            </div>
                                            <div className="btn-group" role="group">
                                                <button
                                                    className="btn btn-sm btn-outline-primary"
                                                    onClick={() => navigate(`/edit/${review.review_id}`)}
                                                >
                                                    <i className="bi bi-pencil me-1"></i>
                                                    Editar
                                                </button>
                                                <button
                                                    className="btn btn-sm btn-outline-danger"
                                                    onClick={() => handleDelete(review.review_id, review.movie)}
                                                >
                                                    <i className="bi bi-trash me-1"></i>
                                                    Excluir
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default MovieReviewsPage;
