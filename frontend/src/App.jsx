import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import MovieReviewsList from './components/MovieReviewsList';
import MovieReviewsPage from './components/MovieReviewsPage';
import MovieDetail from './components/MovieDetail';
import MovieReviewForm from './components/MovieReviewForm';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                <Header />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<MovieReviewsList />} />
                        <Route path="/reviews" element={<MovieReviewsPage />} />
                        <Route path="/movie/:movieTitle" element={<MovieDetail />} />
                        <Route path="/add" element={<MovieReviewForm />} />
                        <Route path="/edit/:id" element={<MovieReviewForm />} />
                    </Routes>
                </main>
                <footer className="footer mt-auto py-3 bg-light">
                    <div className="container text-center">
                        <span className="text-muted">
                            <i className="bi bi-film me-2"></i>
                            Cine Pulse © 2025 - Painel de Avaliações de Filmes
                        </span>
                    </div>
                </footer>
            </div>
        </Router>
    );
}

export default App;
