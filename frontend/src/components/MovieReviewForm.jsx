import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { createReview, updateReview, getReview } from '../services/api';

function MovieReviewForm() {
    const navigate = useNavigate();
    const { id } = useParams();
    const location = useLocation();
    const isEditMode = Boolean(id);

    const [formData, setFormData] = useState({
        review_id: '',
        reviewer: '',
        movie: location.state?.movieTitle || '',
        rating: 3,
        review_summary: '',
        review_detail: '',
        review_date: new Date().toISOString().split('T')[0],
        spoiler_tag: 0,
        helpful_from: '',
        helpful_to: '',
        source_movie: '',
        predicted_sentiment: 'neutro',
        prediction_confidence: 0.5,
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (isEditMode) {
            loadReview();
        } else {
            // Gerar ID aleatório para nova avaliação
            setFormData(prev => ({
                ...prev,
                review_id: `rw${Date.now()}${Math.floor(Math.random() * 1000)}`
            }));
        }
    }, [id]);

    const loadReview = async () => {
        try {
            setLoading(true);
            const review = await getReview(id);
            setFormData(review);
            setLoading(false);
        } catch (err) {
            setError('Erro ao carregar avaliação: ' + err.message);
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'number' ? parseFloat(value) || 0 : value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            if (isEditMode) {
                await updateReview(id, formData);
            } else {
                await createReview(formData);
            }
            setSuccess(true);
            setTimeout(() => {
                navigate('/reviews');
            }, 1500);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    const renderStarSelector = () => {
        const stars = [];
        for (let i = 1; i <= 5; i++) {
            stars.push(
                <button
                    key={i}
                    type="button"
                    className="btn btn-link p-1"
                    onClick={() => setFormData((prev) => ({ ...prev, rating: i }))}
                >
                    <i
                        className={`bi bi-star${i <= formData.rating ? '-fill' : ''} fs-3 ${i <= formData.rating ? 'text-warning' : 'text-secondary'
                            }`}
                    ></i>
                </button>
            );
        }
        return <div className="star-selector">{stars}</div>;
    };

    if (loading && isEditMode) {
        return (
            <div className="container mt-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Carregando...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="container py-4">
            <div className="row justify-content-center">
                <div className="col-lg-8">
                    <div className="card shadow">
                        <div className="card-header bg-primary text-white">
                            <h3 className="mb-0">
                                <i className={`bi bi-${isEditMode ? 'pencil' : 'plus-circle'} me-2`}></i>
                                {isEditMode ? 'Editar Avaliação' : 'Adicionar Nova Avaliação'}
                            </h3>
                        </div>
                        <div className="card-body">
                            {error && (
                                <div className="alert alert-danger" role="alert">
                                    <i className="bi bi-exclamation-triangle me-2"></i>
                                    {error}
                                </div>
                            )}

                            {success && (
                                <div className="alert alert-success" role="alert">
                                    <i className="bi bi-check-circle me-2"></i>
                                    Avaliação {isEditMode ? 'atualizada' : 'criada'} com sucesso! Redirecionando...
                                </div>
                            )}

                            <form onSubmit={handleSubmit}>
                                {/* ID da Avaliação (Oculto) */}
                                <input type="hidden" name="review_id" value={formData.review_id} />

                                <div className="row">
                                    {/* Avaliador */}
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label fw-bold">Nome do Avaliador *</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            name="reviewer"
                                            value={formData.reviewer}
                                            onChange={handleChange}
                                            required
                                            placeholder="Digite seu nome"
                                        />
                                    </div>

                                    {/* Filme */}
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label fw-bold">Filme *</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            name="movie"
                                            value={formData.movie}
                                            onChange={handleChange}
                                            required
                                            placeholder="Nome do filme"
                                        />
                                    </div>
                                </div>

                                {/* Rating */}
                                <div className="mb-3">
                                    <label className="form-label fw-bold">Avaliação *</label>
                                    {renderStarSelector()}
                                    <div className="text-muted">
                                        Nota: {formData.rating}/5 estrelas
                                    </div>
                                </div>

                                {/* Resumo */}
                                <div className="mb-3">
                                    <label className="form-label fw-bold">Resumo da Avaliação *</label>
                                    <textarea
                                        className="form-control"
                                        name="review_summary"
                                        value={formData.review_summary}
                                        onChange={handleChange}
                                        required
                                        rows="3"
                                        placeholder="Escreva um resumo breve da sua opinião sobre o filme"
                                    />
                                </div>

                                {/* Detalhes */}
                                <div className="mb-3">
                                    <label className="form-label fw-bold">Avaliação Detalhada</label>
                                    <textarea
                                        className="form-control"
                                        name="review_detail"
                                        value={formData.review_detail}
                                        onChange={handleChange}
                                        rows="6"
                                        placeholder="Escreva sua avaliação completa (opcional)"
                                    />
                                </div>

                                <div className="row">
                                    {/* Data */}
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label fw-bold">Data da Avaliação</label>
                                        <input
                                            type="date"
                                            className="form-control"
                                            name="review_date"
                                            value={formData.review_date}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    {/* Spoiler */}
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label fw-bold">Contém Spoilers?</label>
                                        <select
                                            className="form-select"
                                            name="spoiler_tag"
                                            value={formData.spoiler_tag}
                                            onChange={handleChange}
                                        >
                                            <option value={0}>Não</option>
                                            <option value={1}>Sim</option>
                                        </select>
                                    </div>
                                </div>



                                {/* Seção Avançada (opcional) */}
                                <div className="mb-3">
                                    <button
                                        type="button"
                                        className="btn btn-link p-0 text-decoration-none"
                                        data-bs-toggle="collapse"
                                        data-bs-target="#advancedOptions"
                                    >
                                        <i className="bi bi-gear me-2"></i>
                                        Opções Avançadas (opcional)
                                    </button>
                                    <div className="collapse mt-3" id="advancedOptions">
                                        <div className="row">
                                            <div className="col-md-4 mb-3">
                                                <label className="form-label">Votos Úteis (De)</label>
                                                <input
                                                    type="text"
                                                    className="form-control"
                                                    name="helpful_from"
                                                    value={formData.helpful_from}
                                                    onChange={handleChange}
                                                    placeholder="Ex: 42"
                                                />
                                            </div>
                                            <div className="col-md-4 mb-3">
                                                <label className="form-label">Votos Úteis (Total)</label>
                                                <input
                                                    type="text"
                                                    className="form-control"
                                                    name="helpful_to"
                                                    value={formData.helpful_to}
                                                    onChange={handleChange}
                                                    placeholder="Ex: 50"
                                                />
                                            </div>
                                            <div className="col-md-4 mb-3">
                                                <label className="form-label">Fonte do Filme</label>
                                                <input
                                                    type="text"
                                                    className="form-control"
                                                    name="source_movie"
                                                    value={formData.source_movie}
                                                    onChange={handleChange}
                                                    placeholder="Ex: IMDb"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Botões */}
                                <div className="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <button
                                        type="button"
                                        className="btn btn-secondary"
                                        onClick={() => navigate('/reviews')}
                                        disabled={loading}
                                    >
                                        <i className="bi bi-x-circle me-2"></i>
                                        Cancelar
                                    </button>
                                    <button
                                        type="submit"
                                        className="btn btn-primary"
                                        disabled={loading}
                                    >
                                        {loading ? (
                                            <>
                                                <span className="spinner-border spinner-border-sm me-2"></span>
                                                Salvando...
                                            </>
                                        ) : (
                                            <>
                                                <i className="bi bi-check-circle me-2"></i>
                                                {isEditMode ? 'Atualizar' : 'Criar'} Avaliação
                                            </>
                                        )}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default MovieReviewForm;
