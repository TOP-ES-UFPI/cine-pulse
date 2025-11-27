import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Header() {
    const location = useLocation();

    const isActive = (path) => {
        return location.pathname === path ? 'active' : '';
    };

    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-gradient-primary sticky-top shadow">
            <div className="container-fluid">
                <Link className="navbar-brand d-flex align-items-center" to="/">
                    <span className="fs-3 me-2">🎬</span>
                    <span className="fw-bold">Cine Pulse</span>
                </Link>

                <button
                    className="navbar-toggler"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarNav"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>

                <div className="collapse navbar-collapse" id="navbarNav">
                    <ul className="navbar-nav ms-auto">
                        <li className="nav-item">
                            <Link className={`nav-link ${isActive('/')}`} to="/">
                                <i className="bi bi-house-fill me-1"></i>
                                Início
                            </Link>
                        </li>
                        <li className="nav-item">
                            <Link className={`nav-link ${isActive('/reviews')}`} to="/reviews">
                                <i className="bi bi-list-ul me-1"></i>
                                Todas as Avaliações
                            </Link>
                        </li>
                        <li className="nav-item">
                            <Link className={`nav-link ${isActive('/add')}`} to="/add">
                                <i className="bi bi-plus-circle-fill me-1"></i>
                                Adicionar Avaliação
                            </Link>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    );
}

export default Header;
