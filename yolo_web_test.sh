#!/bin/bash

# YOLO Model Test - Hızlı Başlangıç Rehberi
# ==========================================

echo ""
echo "🎯 Web'de YOLO Model ile Fotoğraf Testi"
echo "========================================"
echo ""

# Model kontrolü
if [ -f "runs/detect/train/weights/best.pt" ]; then
    echo "✅ YOLO modeli bulundu: runs/detect/train/weights/best.pt"
else
    echo "⚠️  YOLO modeli bulunamadı!"
    echo ""
    echo "Model eğitmek için:"
    echo "  python train_yolo_model.py --mode train --epochs 50 --batch 8"
    echo ""
    read -p "Yine de devam etmek istiyor musunuz? (e/h): " devam
    if [ "$devam" != "e" ]; then
        exit 1
    fi
fi

echo ""
echo "📋 Adımlar:"
echo "  1. Web tarayıcınızda uygulama açılacak"
echo "  2. Sol menüden 'YOLO Model Yolu' kontrol edin"
echo "  3. 'Tanıma Yöntemi' olarak '🎯 YOLO' seçin"
echo "  4. 'Browse files' ile fotoğraf yükleyin"
echo "  5. '🔍 Analiz Et' butonuna tıklayın"
echo ""
echo "🎨 Göreceğiniz Sonuçlar:"
echo "  • Bounding box'larla işaretlenmiş görüntü"
echo "  • Her nesne için güven skoru"
echo "  • Türkçe parça isimleri"
echo "  • Detaylı parça bilgileri"
echo ""
echo "⏳ Web uygulaması başlatılıyor..."
echo ""

# Streamlit'i başlat
streamlit run app.py

