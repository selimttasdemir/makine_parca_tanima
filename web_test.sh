#!/bin/bash

# Web uygulaması için hızlı başlatma scripti
# Kullanım: ./web_test.sh

echo "🌐 Makine Parçası Tanıma Web Uygulaması"
echo "======================================"
echo ""

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 bulunamadı!"
    exit 1
fi

# Streamlit kontrolü
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "⚠️  Streamlit bulunamadı. Yükleniyor..."
    pip install streamlit
fi

echo "✅ Gereksinimler tamam!"
echo ""
echo "🚀 Web uygulaması başlatılıyor..."
echo ""
echo "📍 Tarayıcınızda açılacak adres: http://localhost:8501"
echo ""
echo "📊 Model Performans Testi için:"
echo "   1. Sol menüden '📊 Model Performans Testi' seçin"
echo "   2. Model dosyası yolunu girin (varsayılan: runs/detect/train/weights/best.pt)"
echo "   3. 'Testi Başlat' butonuna tıklayın"
echo ""
echo "⏳ Uygulama başlatılıyor..."
echo ""

# Streamlit'i başlat
streamlit run app.py
