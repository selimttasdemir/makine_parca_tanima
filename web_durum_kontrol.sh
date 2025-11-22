#!/bin/bash

# Web Uygulaması Test ve Sorun Giderme
# =====================================

echo "🔧 Web Uygulaması Durum Kontrolü"
echo "================================="
echo ""

# Python kontrolü
echo "📦 Gerekli paketler kontrol ediliyor..."
echo ""

# Streamlit
if python3 -c "import streamlit" 2>/dev/null; then
    echo "✅ streamlit yüklü"
else
    echo "❌ streamlit bulunamadı"
    echo "   Yüklemek için: pip install streamlit"
fi

# OpenCV
if python3 -c "import cv2" 2>/dev/null; then
    echo "✅ opencv-python yüklü"
else
    echo "❌ opencv-python bulunamadı"
    echo "   Yüklemek için: pip install opencv-python"
fi

# Ultralytics
if python3 -c "import ultralytics" 2>/dev/null; then
    echo "✅ ultralytics yüklü"
    
    # YOLO modeli kontrolü
    if [ -f "runs/detect/train/weights/best.pt" ]; then
        echo "✅ YOLO modeli mevcut: runs/detect/train/weights/best.pt"
        
        # Model bilgisi
        model_size=$(du -h "runs/detect/train/weights/best.pt" | cut -f1)
        echo "   Boyut: $model_size"
    else
        echo "⚠️  YOLO modeli bulunamadı: runs/detect/train/weights/best.pt"
        echo "   Model eğitmek için: python train_yolo_model.py --mode train --epochs 50 --batch 8"
    fi
else
    echo "❌ ultralytics bulunamadı"
    echo "   Yüklemek için: pip install ultralytics"
fi

# PIL
if python3 -c "from PIL import Image" 2>/dev/null; then
    echo "✅ Pillow yüklü"
else
    echo "❌ Pillow bulunamadı"
    echo "   Yüklemek için: pip install Pillow"
fi

echo ""
echo "================================="
echo ""

# Test klasörü kontrolü
if [ -d "test/images" ]; then
    test_count=$(ls -1 test/images/*.jpg test/images/*.png 2>/dev/null | wc -l)
    echo "📂 Test klasörü: $test_count görüntü mevcut"
else
    echo "⚠️  Test klasörü bulunamadı"
fi

echo ""
echo "🚀 Web uygulamasını başlatmak için:"
echo "   ./yolo_web_test.sh"
echo ""
echo "veya"
echo ""
echo "   streamlit run app.py"
echo ""

# Hata çözümleri
echo "💡 Sık Karşılaşılan Hatalar:"
echo ""
echo "1. 'cv2 not defined' hatası:"
echo "   → pip install opencv-python"
echo ""
echo "2. 'YOLO modeli bulunamadı':"
echo "   → python train_yolo_model.py --mode train --epochs 50 --batch 8"
echo ""
echo "3. 'Fotoğrafı kapatınca hata':"
echo "   → '🗑️ Sonuçları Temizle' butonuna basın"
echo "   → Sayfayı yenileyin (F5)"
echo ""
echo "4. 'Port already in use':"
echo "   → streamlit run app.py --server.port 8502"
echo ""

