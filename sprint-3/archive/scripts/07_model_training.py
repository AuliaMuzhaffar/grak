"""
07_model_training.py — Pelatihan Model Machine Learning (Fase 4)
GRAK 2026 · Sprint 3

Tujuan:
Membangun model Machine Learning untuk mengklasifikasikan Topik (8 Kelas) 
dan Sentimen (3 Kelas) berdasarkan 'Golden Dataset' hasil Ingestion Shield V2.

Langkah-langkah:
1. Load 'combined_text.csv' (7.097 baris).
2. TF-IDF Vectorization: Mengubah teks menjadi angka (vektor).
3. Model Training (Topic): Melatih model untuk menebak 8 pilar ekosistem.
4. Model Training (Sentiment): Melatih model untuk menebak sentimen (dengan penanganan Imbalanced Data).
5. Evaluasi & Export: Menyimpan model ke disk (format .joblib).
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

# Machine Learning Packages (Scikit-Learn)
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# Direktori Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

INPUT_DATA = os.path.join(PROCESSED_DIR, "combined_text.csv")

# Buat folder models jika belum ada
os.makedirs(MODELS_DIR, exist_ok=True)

def load_data():
    if not os.path.exists(INPUT_DATA):
        print(f"❌ ERROR: Dataset tidak ditemukan di {INPUT_DATA}")
        sys.exit(1)
    
    df = pd.read_csv(INPUT_DATA)
    
    # Drop data yang mungkin masih kosong teksnya (Safety Guard)
    df = df.dropna(subset=['text', 'topic', 'sentiment'])
    
    # Pastikan tidak ada label "out_of_domain" yang lolos (Assertion V2)
    assert not (df['topic'] == 'out_of_domain').any(), "FATAL: Ada data 'out_of_domain' yang bocor ke Fase ML!"
    
    return df

def train_topic_model(X_train, y_train, X_test, y_test):
    print("\n" + "="*50)
    print("🤖 Melatih Model TOPIC CLASSIFICATION (8 Kelas)")
    print("="*50)
    
    # Menggunakan Logistic Regression karena sangat cepat dan performanya bagus untuk TF-IDF Text
    model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Akurasi Model Topic: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
    print(classification_report(y_test, y_pred))
    
    return model

def train_sentiment_model(X_train, y_train, X_test, y_test):
    print("\n" + "="*50)
    print("🤖 Melatih Model SENTIMENT CLASSIFICATION (3 Kelas)")
    print("="*50)
    
    # Class Imbalance Handling: 
    # Karena class 'Negative' (133) sangat sedikit dibanding 'Neutral' (5629),
    # kita WAJIB memakai 'balanced' weight agar mesin tidak asal menebak Netral semua.
    model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Akurasi Model Sentiment: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
    print(classification_report(y_test, y_pred))
    
    return model

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Memulai Pipeline Training Machine Learning...")
    
    df = load_data()
    print(f"✅ Data berhasil dimuat: {len(df)} baris (Golden Dataset).")
    
    # ==========================================
    # 1. VEKTORISASI TEKS (TF-IDF)
    # ==========================================
    print("\n🚀 Membangun TF-IDF Vectorizer...")
    # ngram_range=(1,2) artinya kita mengambil kata tunggal (startup) dan frasa 2 kata (startup digital)
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    
    # Transformasi teks menjadi matriks angka
    X = vectorizer.fit_transform(df['text'])
    
    # Simpan Vectorizer
    vec_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
    joblib.dump(vectorizer, vec_path)
    print(f"💾 Vectorizer disimpan di: {vec_path}")
    
    # ==========================================
    # 2. TRAINING TOPIC MODEL
    # ==========================================
    y_topic = df['topic']
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(X, y_topic, test_size=0.2, random_state=42, stratify=y_topic)
    
    topic_model = train_topic_model(X_train_t, y_train_t, X_test_t, y_test_t)
    
    topic_model_path = os.path.join(MODELS_DIR, "topic_classifier.joblib")
    joblib.dump(topic_model, topic_model_path)
    print(f"💾 Model Topic disimpan di: {topic_model_path}")

    # ==========================================
    # 3. TRAINING SENTIMENT MODEL
    # ==========================================
    y_sentiment = df['sentiment']
    # Harus pakai stratify agar proporsi kelas Negative yang langka tetap terjaga saat data dibagi
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X, y_sentiment, test_size=0.2, random_state=42, stratify=y_sentiment)
    
    sentiment_model = train_sentiment_model(X_train_s, y_train_s, X_test_s, y_test_s)
    
    sentiment_model_path = os.path.join(MODELS_DIR, "sentiment_classifier.joblib")
    joblib.dump(sentiment_model, sentiment_model_path)
    print(f"💾 Model Sentiment disimpan di: {sentiment_model_path}")
    
    print("\n🎉 PHASE 4 SELESAI: Pipeline Model Training berhasil dieksekusi!")

if __name__ == "__main__":
    main()
