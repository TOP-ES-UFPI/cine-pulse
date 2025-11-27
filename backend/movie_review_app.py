from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5433/movie_reviews_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the MovieReview model
class MovieReview(db.Model):
    __tablename__ = 'movie_reviews'
    
    review_id = db.Column(db.String, primary_key=True)
    reviewer = db.Column(db.String)
    movie = db.Column(db.String)
    rating = db.Column(db.Integer)
    review_summary = db.Column(db.Text)
    review_date = db.Column(db.String)
    spoiler_tag = db.Column(db.Integer)
    review_detail = db.Column(db.Text)
    helpful_from = db.Column(db.String)
    helpful_to = db.Column(db.String)
    source_movie = db.Column(db.String)
    predicted_sentiment = db.Column(db.String)
    prediction_confidence = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'review_id': self.review_id,
            'reviewer': self.reviewer,
            'movie': self.movie,
            'rating': self.rating,
            'review_summary': self.review_summary,
            'review_date': self.review_date,
            'spoiler_tag': self.spoiler_tag,
            'review_detail': self.review_detail,
            'helpful_from': self.helpful_from,
            'helpful_to': self.helpful_to,
            'source_movie': self.source_movie,
            'predicted_sentiment': self.predicted_sentiment,
            'prediction_confidence': self.prediction_confidence
        }

# HTML template for the enhanced CRUD interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Movie Reviews Analysis System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .content {
            padding: 30px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .tab {
            padding: 15px 30px;
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 1em;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: bold;
        }
        
        .tab:hover {
            background: #f5f5f5;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .search-bar {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
        }
        
        .search-bar input {
            flex: 1;
            padding: 12px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border 0.3s;
        }
        
        .search-bar input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .analysis-section {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .analysis-controls {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .analysis-controls select,
        .analysis-controls input {
            padding: 10px 15px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 0.95em;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
            font-weight: 600;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .summary-result {
            margin-top: 20px;
            padding: 25px;
            background: white;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .summary-result h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .summary-result .content {
            line-height: 1.8;
            color: #333;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        table { 
            border-collapse: collapse; 
            width: 100%; 
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        th, td { 
            padding: 15px; 
            text-align: left; 
            border-bottom: 1px solid #e0e0e0;
        }
        
        th { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .form-group { 
            margin: 15px 0; 
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input, textarea, select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 1em;
            transition: border 0.3s;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .sentiment-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .sentiment-positivo {
            background: #d4edda;
            color: #155724;
        }
        
        .sentiment-negativo {
            background: #f8d7da;
            color: #721c24;
        }
        
        .sentiment-neutro {
            background: #fff3cd;
            color: #856404;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2em;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-card p {
            color: #666;
            font-size: 0.9em;
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Movie Reviews Analysis System</h1>
            <p>Intelligent Review Management & AI-Powered Insights</p>
        </div>
        
        <div class="content">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('analysis')">📊 Analysis</button>
                <button class="tab" onclick="switchTab('reviews')">📝 Reviews</button>
                <button class="tab" onclick="switchTab('manage')">⚙️ Manage</button>
            </div>
            
            <!-- Analysis Tab -->
            <div id="analysis-tab" class="tab-content active">
                <div class="stats-grid" id="statsGrid">
                    <!-- Stats will be populated by JavaScript -->
                </div>
                
                <div class="analysis-section">
                    <h2 style="margin-bottom: 20px; color: #333;">🤖 AI-Powered Review Analysis</h2>
                    <div class="analysis-controls">
                        <select id="movieSelect" onchange="updateReviewCount()">
                            <option value="">Select a movie...</option>
                        </select>
                        <input type="number" id="reviewLimit" value="25" min="5" max="100" style="width: 100px;" placeholder="Limit">
                        <select id="sentimentFilter">
                            <option value="all">All Sentiments</option>
                            <option value="positivo">Positive Only</option>
                            <option value="negativo">Negative Only</option>
                            <option value="neutro">Neutral Only</option>
                        </select>
                        <select id="sortOrder">
                            <option value="helpful">Most Helpful</option>
                            <option value="recent">Most Recent</option>
                            <option value="rating_high">Highest Rating</option>
                            <option value="rating_low">Lowest Rating</option>
                        </select>
                        <button class="btn btn-primary" onclick="generateSummary()">Generate Analysis</button>
                    </div>
                    <div id="reviewCount" style="margin-top: 15px; color: #666;"></div>
                </div>
                
                <div id="summaryContainer"></div>
            </div>
            
            <!-- Reviews Tab -->
            <div id="reviews-tab" class="tab-content">
                <div class="search-bar">
                    <input type="text" id="searchInput" placeholder="🔍 Search by movie title, reviewer, or content..." onkeyup="searchReviews()">
                </div>
                
                <table id="reviewsTable">
                    <thead>
                        <tr>
                            <th>Movie</th>
                            <th>Reviewer</th>
                            <th>Rating</th>
                            <th>Sentiment</th>
                            <th>Confidence</th>
                            <th>Summary</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="reviewsBody">
                    </tbody>
                </table>
            </div>
            
            <!-- Manage Tab -->
            <div id="manage-tab" class="tab-content">
                <h2 style="margin-bottom: 20px;">Add/Edit Review</h2>
                <form id="reviewForm">
                    <div class="form-group">
                        <label>Review ID:</label>
                        <input type="text" id="review_id" required>
                    </div>
                    <div class="form-group">
                        <label>Reviewer:</label>
                        <input type="text" id="reviewer" required>
                    </div>
                    <div class="form-group">
                        <label>Movie:</label>
                        <input type="text" id="movie" required>
                    </div>
                    <div class="form-group">
                        <label>Rating (1-5):</label>
                        <input type="number" id="rating" min="1" max="5" required>
                    </div>
                    <div class="form-group">
                        <label>Review Summary:</label>
                        <textarea id="review_summary" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Review Detail:</label>
                        <textarea id="review_detail" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Review Date:</label>
                        <input type="text" id="review_date" placeholder="YYYY-MM-DD">
                    </div>
                    <div class="form-group">
                        <label>Spoiler Tag:</label>
                        <select id="spoiler_tag">
                            <option value="0">No Spoilers</option>
                            <option value="1">Contains Spoilers</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Helpful From:</label>
                        <input type="text" id="helpful_from" placeholder="e.g., 42">
                    </div>
                    <div class="form-group">
                        <label>Helpful To:</label>
                        <input type="text" id="helpful_to" placeholder="e.g., 50">
                    </div>
                    <div class="form-group">
                        <label>Source Movie:</label>
                        <input type="text" id="source_movie">
                    </div>
                    <div class="form-group">
                        <label>Predicted Sentiment:</label>
                        <select id="predicted_sentiment">
                            <option value="positivo">Positive</option>
                            <option value="negativo">Negative</option>
                            <option value="neutro">Neutral</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Prediction Confidence (0-1):</label>
                        <input type="number" id="prediction_confidence" step="0.01" min="0" max="1">
                    </div>
                    <div class="action-buttons">
                        <button type="submit" class="btn btn-success">💾 Save Review</button>
                        <button type="button" class="btn btn-secondary" onclick="cancelEdit()">❌ Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script>
        let editingId = null;
        let allReviews = [];
        
        document.addEventListener('DOMContentLoaded', function() {
            loadReviews();
            loadStats();
        });
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
        }
        
        function loadReviews() {
            fetch('/api/reviews')
                .then(response => response.json())
                .then(data => {
                    allReviews = data;
                    displayReviews(data);
                    populateMovieSelect(data);
                    updateReviewCount();
                })
                .catch(error => console.error('Error loading reviews:', error));
        }
        
        function loadStats() {
            fetch('/api/reviews')
                .then(response => response.json())
                .then(data => {
                    const stats = calculateStats(data);
                    displayStats(stats);
                })
                .catch(error => console.error('Error loading stats:', error));
        }
        
        function calculateStats(reviews) {
            const totalReviews = reviews.length;
            const uniqueMovies = [...new Set(reviews.map(r => r.movie))].length;
            const avgRating = reviews.reduce((sum, r) => sum + r.rating, 0) / totalReviews;
            const sentiments = reviews.reduce((acc, r) => {
                acc[r.predicted_sentiment] = (acc[r.predicted_sentiment] || 0) + 1;
                return acc;
            }, {});
            
            return { totalReviews, uniqueMovies, avgRating: avgRating.toFixed(1), sentiments };
        }
        
        function displayStats(stats) {
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <h3>${stats.totalReviews}</h3>
                    <p>Total Reviews</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.uniqueMovies}</h3>
                    <p>Movies</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.avgRating}</h3>
                    <p>Average Rating</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.sentiments.positivo || 0}</h3>
                    <p>Positive Reviews</p>
                </div>
            `;
        }
        
        function populateMovieSelect(reviews) {
            const movies = [...new Set(reviews.map(r => r.movie))].sort();
            const select = document.getElementById('movieSelect');
            select.innerHTML = '<option value="">Select a movie...</option>';
            movies.forEach(movie => {
                const option = document.createElement('option');
                option.value = movie;
                option.textContent = movie;
                select.appendChild(option);
            });
        }
        
        function updateReviewCount() {
            const movie = document.getElementById('movieSelect').value;
            if (!movie) {
                document.getElementById('reviewCount').textContent = '';
                return;
            }
            
            const sentiment = document.getElementById('sentimentFilter').value;
            let filtered = allReviews.filter(r => r.movie === movie);
            
            if (sentiment !== 'all') {
                filtered = filtered.filter(r => r.predicted_sentiment === sentiment);
            }
            
            document.getElementById('reviewCount').textContent = 
                `${filtered.length} reviews available for analysis`;
        }
        
        function displayReviews(reviews) {
            const tbody = document.getElementById('reviewsBody');
            tbody.innerHTML = '';
            
            reviews.forEach(review => {
                const tr = document.createElement('tr');
                const sentimentClass = `sentiment-${review.predicted_sentiment}`;
                
                tr.innerHTML = `
                    <td><strong>${review.movie}</strong></td>
                    <td>${review.reviewer}</td>
                    <td>⭐ ${review.rating}/5</td>
                    <td><span class="sentiment-badge ${sentimentClass}">${review.predicted_sentiment}</span></td>
                    <td>${(review.prediction_confidence * 100).toFixed(0)}%</td>
                    <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${review.review_summary}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn btn-primary" style="padding: 8px 16px; font-size: 0.9em;" onclick="editReview('${review.review_id}')">Edit</button>
                            <button class="btn btn-danger" style="padding: 8px 16px; font-size: 0.9em;" onclick="deleteReview('${review.review_id}')">Delete</button>
                        </div>
                    </td>
                `;
                
                tbody.appendChild(tr);
            });
        }
        
        function generateSummary() {
            const movie = document.getElementById('movieSelect').value;
            const limit = parseInt(document.getElementById('reviewLimit').value);
            const sentiment = document.getElementById('sentimentFilter').value;
            const sortOrder = document.getElementById('sortOrder').value;
            
            if (!movie) {
                alert('Please select a movie first');
                return;
            }
            
            let filtered = allReviews.filter(r => r.movie === movie);
            
            if (sentiment !== 'all') {
                filtered = filtered.filter(r => r.predicted_sentiment === sentiment);
            }
            
            // Sort reviews based on selected order
            filtered.sort((a, b) => {
                switch(sortOrder) {
                    case 'helpful':
                        const aHelpful = parseInt(a.helpful_from) || 0;
                        const bHelpful = parseInt(b.helpful_from) || 0;
                        return bHelpful - aHelpful;
                    case 'recent':
                        return new Date(b.review_date) - new Date(a.review_date);
                    case 'rating_high':
                        return b.rating - a.rating;
                    case 'rating_low':
                        return a.rating - b.rating;
                    default:
                        return 0;
                }
            });
            
            const reviewsToAnalyze = filtered.slice(0, limit);
            
            const container = document.getElementById('summaryContainer');
            container.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Analyzing ${reviewsToAnalyze.length} reviews for "${movie}"...</p>
                </div>
            `;
            
            fetch('/api/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    movie_title: movie,
                    reviews: reviewsToAnalyze,
                    analysis_params: {
                        sentiment_filter: sentiment,
                        sort_order: sortOrder,
                        total_reviews: filtered.length
                    }
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    container.innerHTML = `
                        <div class="alert alert-error">
                            <strong>Error:</strong> ${data.error}
                        </div>
                    `;
                } else {
                    const metadata = data.metadata;
                    container.innerHTML = `
                        <div class="summary-result">
                            <h3>📊 Comprehensive Analysis: "${movie}"</h3>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                                <h4 style="margin-bottom: 10px; color: #667eea;">📈 Analysis Metadata</h4>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                                    <div>
                                        <strong>Reviews Analyzed:</strong> ${metadata.reviews_analyzed}<br>
                                        <strong>Avg Rating:</strong> ${metadata.average_rating}/5 ⭐<br>
                                        <strong>ML Confidence:</strong> ${(metadata.average_confidence * 100).toFixed(1)}%
                                    </div>
                                    <div>
                                        <strong>Rating Distribution:</strong><br>
                                        ${Object.entries(metadata.rating_distribution).map(([stars, count]) => 
                                            `${'⭐'.repeat(stars)}: ${count} reviews`
                                        ).join('<br>')}
                                    </div>
                                    <div>
                                        <strong>Sentiment Breakdown:</strong><br>
                                        ${Object.entries(metadata.sentiment_distribution).map(([sent, count]) => 
                                            `${sent.charAt(0).toUpperCase() + sent.slice(1)}: ${count}`
                                        ).join('<br>')}
                                    </div>
                                    ${metadata.top_helpful_reviewers && metadata.top_helpful_reviewers.length > 0 ? `
                                    <div>
                                        <strong>Top Helpful Reviewers:</strong><br>
                                        ${metadata.top_helpful_reviewers.join('<br>')}
                                    </div>
                                    ` : ''}
                                </div>
                            </div>
                            <div class="content" style="margin-top: 20px;">${formatSummary(data.summary)}</div>
                        </div>
                    `;
                }
            })
            .catch(error => {
                container.innerHTML = `
                    <div class="alert alert-error">
                        <strong>Error:</strong> ${error.message}
                    </div>
                `;
            });
        }
        
        function formatSummary(summary) {
            return summary
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n\n/g, '</p><p>')
                .replace(/\n/g, '<br>')
                .replace(/^/, '<p>')
                .replace(/$/, '</p>');
        }
        
        function editReview(id) {
            fetch(`/api/reviews/${id}`)
                .then(response => response.json())
                .then(review => {
                    document.getElementById('review_id').value = review.review_id;
                    document.getElementById('reviewer').value = review.reviewer;
                    document.getElementById('movie').value = review.movie;
                    document.getElementById('rating').value = review.rating;
                    document.getElementById('review_summary').value = review.review_summary;
                    document.getElementById('review_date').value = review.review_date;
                    document.getElementById('spoiler_tag').value = review.spoiler_tag;
                    document.getElementById('review_detail').value = review.review_detail;
                    document.getElementById('helpful_from').value = review.helpful_from;
                    document.getElementById('helpful_to').value = review.helpful_to;
                    document.getElementById('source_movie').value = review.source_movie;
                    document.getElementById('predicted_sentiment').value = review.predicted_sentiment;
                    document.getElementById('prediction_confidence').value = review.prediction_confidence;
                    
                    editingId = id;
                    switchTab('manage');
                    document.querySelector('.tab:nth-child(3)').click();
                })
                .catch(error => console.error('Error fetching review:', error));
        }
        
        function deleteReview(id) {
            if (confirm('Are you sure you want to delete this review?')) {
                fetch(`/api/reviews/${id}`, { method: 'DELETE' })
                    .then(response => {
                        if (response.ok) {
                            loadReviews();
                            loadStats();
                        } else {
                            alert('Error deleting review');
                        }
                    })
                    .catch(error => console.error('Error deleting review:', error));
            }
        }
        
        function cancelEdit() {
            document.getElementById('reviewForm').reset();
            editingId = null;
        }
        
        document.getElementById('reviewForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const reviewData = {
                review_id: document.getElementById('review_id').value,
                reviewer: document.getElementById('reviewer').value,
                movie: document.getElementById('movie').value,
                rating: parseInt(document.getElementById('rating').value),
                review_summary: document.getElementById('review_summary').value,
                review_date: document.getElementById('review_date').value,
                spoiler_tag: parseInt(document.getElementById('spoiler_tag').value),
                review_detail: document.getElementById('review_detail').value,
                helpful_from: document.getElementById('helpful_from').value,
                helpful_to: document.getElementById('helpful_to').value,
                source_movie: document.getElementById('source_movie').value,
                predicted_sentiment: document.getElementById('predicted_sentiment').value,
                prediction_confidence: parseFloat(document.getElementById('prediction_confidence').value)
            };
            
            const method = editingId ? 'PUT' : 'POST';
            const url = editingId ? `/api/reviews/${editingId}` : '/api/reviews';
            
            fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reviewData)
            })
            .then(response => {
                if (response.ok) {
                    loadReviews();
                    loadStats();
                    document.getElementById('reviewForm').reset();
                    editingId = null;
                    alert('Review saved successfully!');
                } else {
                    alert('Error saving review');
                }
            })
            .catch(error => console.error('Error saving review:', error));
        });
        
        function searchReviews() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            
            const filteredReviews = allReviews.filter(review => 
                review.movie.toLowerCase().includes(searchTerm) || 
                review.reviewer.toLowerCase().includes(searchTerm) ||
                review.review_summary.toLowerCase().includes(searchTerm)
            );
            displayReviews(filteredReviews);
        }
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/test-env', methods=['GET'])
def test_env():
    api_key = os.environ.get('GEMINI_API_KEY')
    return jsonify({
        "gemini_api_key_set": api_key is not None,
        "gemini_api_key_prefix": api_key[:5] if api_key else "None"
    })

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    reviews = MovieReview.query.all()
    return jsonify([review.to_dict() for review in reviews])

@app.route('/api/reviews/<string:review_id>', methods=['GET'])
def get_review(review_id):
    review = MovieReview.query.get_or_404(review_id)
    return jsonify(review.to_dict())

@app.route('/api/reviews', methods=['POST'])
def create_review():
    data = request.json
    review = MovieReview(**data)
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201

@app.route('/api/reviews/<string:review_id>', methods=['PUT'])
def update_review(review_id):
    review = MovieReview.query.get_or_404(review_id)
    data = request.json
    for key, value in data.items():
        if hasattr(review, key):
            setattr(review, key, value)
    db.session.commit()
    return jsonify(review.to_dict())

@app.route('/api/reviews/<string:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = MovieReview.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return '', 204

@app.route('/api/summarize', methods=['POST'])
def summarize_reviews():
    """Enhanced AI-powered review analysis with better abstracts"""
    try:
        data = request.json
        movie_title = data.get('movie_title', '')
        reviews = data.get('reviews', [])
        analysis_params = data.get('analysis_params', {})
        api_key = data.get('api_key', os.environ.get('GEMINI_API_KEY'))

        if not api_key:
            return jsonify({
                "error": "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
            }), 400
        # Configure Gemini client
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Create enhanced review abstracts with better formatting
        review_abstracts = []
        for idx, review in enumerate(reviews, 1):
            # Parse helpful votes safely
            helpful = review.get('helpful', ['0', '0'])
            if isinstance(helpful, list) and len(helpful) >= 2:
                helpful_from = str(helpful[0])
                helpful_to = str(helpful[1])
            else:
                helpful_from = str(review.get('helpful_from', '0'))
                helpful_to = str(review.get('helpful_to', '0'))
            
            # Calculate helpfulness percentage safely
            try:
                h_from = int(helpful_from) if helpful_from else 0
                h_to = int(helpful_to) if helpful_to else 0
                helpful_pct = (h_from / h_to * 100) if h_to > 0 else 0
            except (ValueError, TypeError, ZeroDivisionError):
                helpful_pct = 0
                helpful_from = '0'
                helpful_to = '0'
            
            # Get rating safely
            rating = review.get('rating', 'N/A')
            if rating is not None and rating != 'N/A':
                try:
                    rating = int(rating)
                except (ValueError, TypeError):
                    rating = 'N/A'
            
            # Get confidence safely
            confidence = review.get('prediction_confidence', 0)
            try:
                confidence = float(confidence) if confidence is not None else 0
            except (ValueError, TypeError):
                confidence = 0
            
            abstract = f"""
════════════════════════════════════════════════════════════════
REVIEW #{idx}
════════════════════════════════════════════════════════════════

👤 REVIEWER: {review.get('reviewer', 'Anonymous')}
📅 DATE: {review.get('review_date', 'Unknown')}
⭐ RATING: {rating}/5 stars

💭 SENTIMENT ANALYSIS:
   • Predicted: {str(review.get('predicted_sentiment', 'Unknown')).upper()}
   • Confidence: {(confidence * 100):.1f}%
   • Model Accuracy: {'HIGH' if confidence > 0.8 else 'MEDIUM' if confidence > 0.6 else 'LOW'}

👍 HELPFULNESS METRICS:
   • Votes: {helpful_from}/{helpful_to} found this helpful
   • Helpfulness Score: {helpful_pct:.0f}%
   • Community Trust: {'HIGH' if helpful_pct > 70 else 'MEDIUM' if helpful_pct > 40 else 'LOW'}

{'⚠️  CONTAINS SPOILERS' if review.get('spoiler_tag') == 1 else '✓  NO SPOILERS'}

─────────────────────────────────────────────────────────────────
📝 REVIEW SUMMARY:
{review.get('review_summary', 'No summary available')}

─────────────────────────────────────────────────────────────────
📄 DETAILED REVIEW:
{str(review.get('review_detail', 'No detailed review available'))[:1500]}
{'...\n[Review truncated for length]' if len(str(review.get('review_detail', ''))) > 1500 else ''}

════════════════════════════════════════════════════════════════
"""
            review_abstracts.append(abstract)

        # Calculate detailed statistics with proper None handling
        total_reviews = len(reviews)
        
        # Safely extract ratings
        ratings = []
        for r in reviews:
            rating = r.get('rating')
            if rating is not None:
                try:
                    ratings.append(int(rating))
                except (ValueError, TypeError):
                    pass
        
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        sentiment_counts = {}
        confidence_sum = 0
        spoiler_count = 0
        helpful_reviews = []
        
        for r in reviews:
            # Sentiment counting
            sent = r.get('predicted_sentiment', 'unknown')
            if sent:
                sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1
            
            # Confidence sum
            conf = r.get('prediction_confidence', 0)
            if conf is not None:
                try:
                    confidence_sum += float(conf)
                except (ValueError, TypeError):
                    pass
            
            # Spoiler count
            if r.get('spoiler_tag') == 1:
                spoiler_count += 1
            
            # Track helpful reviews
            helpful = r.get('helpful', ['0', '0'])
            if isinstance(helpful, list) and len(helpful) >= 2:
                try:
                    helpful_from = int(helpful[0])
                    helpful_to = int(helpful[1])
                    if helpful_to > 0:
                        helpful_reviews.append({
                            'reviewer': r.get('reviewer', 'Anonymous'),
                            'ratio': helpful_from / helpful_to
                        })
                except (ValueError, TypeError, ZeroDivisionError):
                    pass
        
        avg_confidence = confidence_sum / total_reviews if total_reviews > 0 else 0
        rating_distribution = {i: ratings.count(i) for i in range(1, 6)}

        # Create comprehensive analysis prompt with better structure
        prompt = f"""Você é um crítico de cinema especialista e analista de dados. Analise as avaliações do filme "{movie_title}" e forneça uma resposta ESTRUTURADA EM JSON.

╔═══════════════════════════════════════════════════════════════╗
║                    DADOS PARA ANÁLISE                          ║
╚═══════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS:
• Total: {total_reviews} avaliações
• Média: {avg_rating:.2f}/5
• Confiança ML: {avg_confidence*100:.1f}%
• Spoilers: {spoiler_count}

 SENTIMENTOS:
{chr(10).join([f"• {sent.title()}: {count}" for sent, count in sentiment_counts.items()])}

📝 AVALIAÇÕES DETALHADAS:
{"".join(review_abstracts)}

╔═══════════════════════════════════════════════════════════════╗
║                  INSTRUÇÕES DE SAÍDA (JSON)                    ║
╚═══════════════════════════════════════════════════════════════╝

Você DEVE retornar APENAS um objeto JSON válido com a seguinte estrutura exata (sem markdown, sem crases):

{{
    "resumo_executivo": "Um parágrafo conciso resumindo a recepção geral do filme e o consenso principal.",
    "analise_sentimento": "Uma análise de 2-3 frases sobre a divisão entre sentimentos positivos e negativos e a confiança da análise.",
    "pontos_positivos": [
        "Ponto positivo 1 (ex: Atuação de fulano)",
        "Ponto positivo 2 (ex: Cinematografia)",
        "Ponto positivo 3"
    ],
    "pontos_negativos": [
        "Ponto negativo 1 (ex: Ritmo lento)",
        "Ponto negativo 2 (ex: Final confuso)",
        "Ponto negativo 3"
    ],
    "destaques_do_publico": "O que o público mais amou ou odiou especificamente (ex: 'A cena do jantar foi muito citada').",
    "veredito_final": "Uma frase de conclusão impactante (ex: 'Uma obra-prima imperdível' ou 'Apenas para fãs do gênero').",
    "recomendacao": "Para quem é este filme? (ex: 'Fãs de terror', 'Família', etc.)",
    "tags": ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5"]
}}

IMPORTANTE:
1. O JSON deve ser válido.
2. Todo o conteúdo deve estar em PORTUGUÊS (pt-BR).
3. "tags" deve conter 5-8 palavras-chave curtas e descritivas (ex: "Suspense", "Plot Twist", "Lento", "Atuação Incrível").
4. Seja específico e use dados das avaliações fornecidas.
"""


        # Call Gemini API
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192,
                "topP": 0.95,
                "topK": 40
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        }

        # Call Gemini 1.5 Flash model
        try:
            response = model.generate_content(prompt)
            summary_text = response.text if hasattr(response, 'text') else str(response)
            
            # Clean up markdown code blocks if present
            clean_json = summary_text.replace('```json', '').replace('```', '').strip()
            
            import json
            try:
                summary_data = json.loads(clean_json)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                summary_data = {
                    "resumo_executivo": summary_text,
                    "error": "Failed to parse structured analysis"
                }

            return jsonify({
                "summary": summary_data,
                "metadata": {
                    "movie": movie_title,
                    "reviews_analyzed": total_reviews,
                    "average_rating": round(avg_rating, 2),
                    "rating_distribution": rating_distribution,
                    "sentiment_distribution": sentiment_counts,
                    "average_confidence": round(avg_confidence, 3),
                    "spoiler_count": spoiler_count,
                    "analysis_params": analysis_params,
                    "top_helpful_reviewers": [r['reviewer'] for r in sorted(helpful_reviews, key=lambda x: x['ratio'], reverse=True)[:3]] if helpful_reviews else []
                }
            })
        except Exception as e:
            return jsonify({"error": f"Gemini generation failed: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
            