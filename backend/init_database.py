"""
Database Initialization Script for Cine Pulse
Loads movie reviews from JSON file into PostgreSQL database
"""
import json
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from movie_review_app import db, MovieReview, app
from tqdm import tqdm

def load_reviews_from_json(json_file_path):
    """Load reviews from JSON file"""
    print(f"📂 Carregando avaliações de {json_file_path}...")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
    
    print(f"✅ {len(reviews)} avaliações carregadas do arquivo JSON")
    return reviews

def init_database(drop_existing=False):
    """Initialize database tables"""
    with app.app_context():
        if drop_existing:
            print("🗑️  Removendo tabelas existentes...")
            db.drop_all()
        
        print("🔨 Criando tabelas no banco de dados...")
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")

def insert_reviews(reviews, batch_size=1000):
    """Insert reviews into database in batches"""
    with app.app_context():
        total = len(reviews)
        print(f"\n📝 Inserindo {total} avaliações no banco de dados...")
        
        # Check if reviews already exist
        existing_count = MovieReview.query.count()
        if existing_count > 0:
            response = input(f"⚠️  Já existem {existing_count} avaliações no banco. Deseja continuar? (s/n): ")
            if response.lower() != 's':
                print("❌ Operação cancelada")
                return False
        
        inserted = 0
        errors = 0
        
        for i in tqdm(range(0, total, batch_size), desc="Processando lotes"):
            batch = reviews[i:i + batch_size]
            
            for review_data in batch:
                try:
                    # Check if review already exists
                    existing = MovieReview.query.get(review_data['review_id'])
                    if existing:
                        continue
                    
                    review = MovieReview(
                        review_id=review_data['review_id'],
                        reviewer=review_data.get('reviewer', ''),
                        movie=review_data.get('movie', ''),
                        rating=review_data.get('rating', 0),
                        review_summary=review_data.get('review_summary', ''),
                        review_date=review_data.get('review_date', ''),
                        spoiler_tag=review_data.get('spoiler_tag', 0),
                        review_detail=review_data.get('review_detail', ''),
                        helpful_from=review_data.get('helpful_from', ''),
                        helpful_to=review_data.get('helpful_to', ''),
                        source_movie=review_data.get('source_movie', ''),
                        predicted_sentiment=review_data.get('predicted_sentiment', 'neutro'),
                        prediction_confidence=review_data.get('prediction_confidence', 0.0)
                    )
                    db.session.add(review)
                    inserted += 1
                except Exception as e:
                    errors += 1
                    if errors < 10:  # Only print first 10 errors
                        print(f"\n❌ Erro ao inserir avaliação {review_data.get('review_id', 'unknown')}: {str(e)}")
            
            try:
                db.session.commit()
            except Exception as e:
                print(f"\n❌ Erro ao fazer commit do lote: {str(e)}")
                db.session.rollback()
        
        print(f"\n✅ Inserção concluída!")
        print(f"   📊 Inseridas: {inserted}")
        print(f"   ⚠️  Erros: {errors}")
        
        return True

def verify_data():
    """Verify loaded data"""
    with app.app_context():
        total_reviews = MovieReview.query.count()
        unique_movies = db.session.query(MovieReview.movie).distinct().count()
        
        # Sentiment distribution
        sentiments = db.session.query(
            MovieReview.predicted_sentiment,
            db.func.count(MovieReview.review_id)
        ).group_by(MovieReview.predicted_sentiment).all()
        
        # Average rating
        avg_rating = db.session.query(db.func.avg(MovieReview.rating)).scalar()
        
        print(f"\n📊 Estatísticas do Banco de Dados:")
        print(f"   Total de avaliações: {total_reviews}")
        print(f"   Filmes únicos: {unique_movies}")
        print(f"   Avaliação média: {avg_rating:.2f}/5")
        print(f"\n   Distribuição de sentimentos:")
        for sentiment, count in sentiments:
            print(f"      {sentiment}: {count} ({count/total_reviews*100:.1f}%)")
        
        # Sample reviews
        print(f"\n🎬 Exemplo de avaliações:")
        sample_reviews = MovieReview.query.limit(3).all()
        for review in sample_reviews:
            print(f"\n   Filme: {review.movie}")
            print(f"   Avaliador: {review.reviewer}")
            print(f"   Nota: {review.rating}/5")
            print(f"   Sentimento: {review.predicted_sentiment} ({review.prediction_confidence*100:.1f}%)")
            print(f"   Resumo: {review.review_summary[:100]}...")

def main():
    """Main execution"""
    print("="*60)
    print("🎬 CINE PULSE - Inicialização do Banco de Dados")
    print("="*60)
    
    # Path to JSON file
    json_file = os.path.join(
        os.path.dirname(__file__),
        'dataset_portugues_aplicacao_with_predictions.json'
    )
    
    if not os.path.exists(json_file):
        print(f"❌ Arquivo não encontrado: {json_file}")
        return
    
    # Ask user if they want to drop existing tables
    response = input("\n🔄 Deseja recriar as tabelas? (apagará dados existentes) (s/n): ")
    drop_existing = response.lower() == 's'
    
    # Initialize database
    init_database(drop_existing=drop_existing)
    
    # Load and insert reviews
    reviews = load_reviews_from_json(json_file)
    
    if insert_reviews(reviews):
        # Verify data
        verify_data()
        print("\n✅ Banco de dados inicializado com sucesso!")
    else:
        print("\n❌ Falha na inicialização do banco de dados")

if __name__ == '__main__':
    main()
