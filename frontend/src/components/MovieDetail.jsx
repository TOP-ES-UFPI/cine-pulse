import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAllReviews } from '../services/api';

function MovieDetail() {
    const { movieTitle } = useParams();
    const navigate = useNavigate();
    const [reviews, setReviews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadReviews();
    }, [movieTitle]);

    const loadReviews = async () => {
        try {
            setLoading(true);
            const allReviews = await getAllReviews();
            // Filter reviews for this movie (case insensitive)
            const movieReviews = allReviews.filter(
                r => r.movie.toLowerCase() === decodeURIComponent(movieTitle).toLowerCase()
            );
            setReviews(movieReviews);
            setLoading(false);
        } catch (err) {
            setError('Erro ao carregar avaliações: ' + err.message);
            setLoading(false);
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

    if (loading) {
        return (
            <div className="container mt-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Carregando...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mt-5">
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
                <button className="btn btn-secondary" onClick={() => navigate('/')}>
                    Voltar
                </button>
            </div>
        );
    }

    return (
        <div className="container py-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 className="text-white mb-0">
                    <i className="bi bi-film me-2 text-primary"></i>
                    {decodeURIComponent(movieTitle)}
                </h2>
                <div>
                    <button
                        className="btn btn-outline-light me-2"
                        onClick={() => navigate('/')}
                    >
                        <i className="bi bi-arrow-left me-2"></i>
                        Voltar
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={() => navigate('/add', { state: { movieTitle: decodeURIComponent(movieTitle) } })}
                    >
                        <i className="bi bi-plus-circle me-2"></i>
                        Nova Avaliação
                    </button>
                </div>
            </div>

            {reviews.length === 0 ? (
                <div className="alert alert-info">
                    Nenhuma avaliação encontrada para este filme. Seja o primeiro a avaliar!
                </div>
            ) : (
                <div className="row">
                    {reviews.map((review) => (
                        <div key={review.review_id} className="col-md-6 mb-4">
                            <div className="card h-100 review-card">
                                <div className="card-body">
                                    <div className="d-flex justify-content-between align-items-start mb-3">
                                        <div>
                                            <h5 className="card-title mb-1">{review.reviewer}</h5>
                                            <div className="text-warning mb-2">
                                                {renderStars(review.rating / 2)}
                                            </div>
                                        </div>
                                        <span className="badge bg-light text-dark">
                                            {new Date(review.review_date).toLocaleDateString()}
                                        </span>
                                    </div>

                                    <h6 className="fw-bold mb-2">{review.review_summary}</h6>
                                    <p className="card-text text-muted small mb-3">
                                        {review.review_detail}
                                    </p>

                                    <div className="d-flex justify-content-between align-items-center mt-auto">
                                        <span className={`badge ${review.predicted_sentiment === 'positivo' ? 'bg-success' :
                                            review.predicted_sentiment === 'negativo' ? 'bg-danger' : 'bg-secondary'
                                            }`}>
                                            {review.predicted_sentiment}
                                        </span>
                                        {review.spoiler_tag === 1 && (
                                            <span className="badge bg-warning text-dark">
                                                <i className="bi bi-exclamation-triangle me-1"></i>
                                                Spoiler
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default MovieDetail;
