#!/bin/bash

# Model Test Scripti
# Eğitilmiş YOLOv8 modelini test etmek için

echo "======================================================================"
echo "🧪 YOLOv8 Model Test Menüsü"
echo "======================================================================"
echo ""

# Renk kodları
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Model dosyasını kontrol et
MODEL_PATH="runs/detect/train/weights/best.pt"
if [ ! -f "$MODEL_PATH" ]; then
    echo -e "${RED}❌ Model bulunamadı: $MODEL_PATH${NC}"
    echo ""
    echo "Önce modeli eğitmeniz gerekiyor:"
    echo "  ./hizli_egitim.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Model bulundu: $MODEL_PATH${NC}"
echo ""

# Test seçenekleri
echo "Test yöntemini seçin:"
echo ""
echo "  1) Test seti üzerinde değerlendirme (mAP metrikleri)"
echo "  2) Test görüntüleri üzerinde tahmin"
echo "  3) Tek görüntü üzerinde tahmin"
echo "  4) Webcam ile canlı test"
echo "  5) Video dosyası üzerinde test"
echo "  6) Validation seti üzerinde değerlendirme"
echo "  7) Çıkış"
echo ""
read -p "Seçiminiz (1-7): " CHOICE

case $CHOICE in
    1)
        echo ""
        echo -e "${BLUE}📊 Test seti üzerinde değerlendirme yapılıyor...${NC}"
        echo "======================================================================"
        python train_yolo_model.py --mode test
        
        echo ""
        echo -e "${GREEN}✓ Test tamamlandı!${NC}"
        echo "Sonuçlar terminalde gösterildi."
        ;;
        
    2)
        echo ""
        read -p "Confidence threshold [varsayılan: 0.25]: " CONF
        CONF=${CONF:-0.25}
        
        echo ""
        echo -e "${BLUE}🔮 Test görüntüleri üzerinde tahmin yapılıyor...${NC}"
        echo "======================================================================"
        python train_yolo_model.py \
            --mode predict \
            --source test/images/ \
            --conf $CONF
        
        echo ""
        echo -e "${GREEN}✓ Tahminler tamamlandı!${NC}"
        echo "Sonuçlar: runs/detect/predict/"
        echo ""
        
        # Sonuçları göster
        if command -v xdg-open &> /dev/null; then
            read -p "Sonuçları açmak ister misiniz? (e/h) [h]: " OPEN_RESULTS
            if [ "$OPEN_RESULTS" = "e" ]; then
                xdg-open runs/detect/predict/ 2>/dev/null || nautilus runs/detect/predict/ 2>/dev/null || echo "Klasörü manuel olarak açın: runs/detect/predict/"
            fi
        fi
        ;;
        
    3)
        echo ""
        echo "Mevcut test görüntüleri:"
        ls -1 test/images/*.jpg 2>/dev/null | head -5
        echo "..."
        echo ""
        read -p "Görüntü yolu: " IMG_PATH
        
        if [ ! -f "$IMG_PATH" ]; then
            echo -e "${RED}❌ Görüntü bulunamadı: $IMG_PATH${NC}"
            exit 1
        fi
        
        read -p "Confidence threshold [varsayılan: 0.25]: " CONF
        CONF=${CONF:-0.25}
        
        echo ""
        echo -e "${BLUE}🔮 Tahmin yapılıyor...${NC}"
        echo "======================================================================"
        python train_yolo_model.py \
            --mode predict \
            --source "$IMG_PATH" \
            --conf $CONF
        
        echo ""
        echo -e "${GREEN}✓ Tahmin tamamlandı!${NC}"
        echo "Sonuç: runs/detect/predict/"
        ;;
        
    4)
        echo ""
        echo -e "${YELLOW}📹 Webcam testi başlıyor...${NC}"
        echo "Çıkmak için 'q' tuşuna basın"
        echo ""
        read -p "Confidence threshold [varsayılan: 0.25]: " CONF
        CONF=${CONF:-0.25}
        
        echo ""
        python train_yolo_model.py \
            --mode predict \
            --source 0 \
            --conf $CONF
        ;;
        
    5)
        echo ""
        read -p "Video dosyası yolu: " VIDEO_PATH
        
        if [ ! -f "$VIDEO_PATH" ]; then
            echo -e "${RED}❌ Video bulunamadı: $VIDEO_PATH${NC}"
            exit 1
        fi
        
        read -p "Confidence threshold [varsayılan: 0.25]: " CONF
        CONF=${CONF:-0.25}
        
        echo ""
        echo -e "${BLUE}🎬 Video işleniyor...${NC}"
        echo "======================================================================"
        python train_yolo_model.py \
            --mode predict \
            --source "$VIDEO_PATH" \
            --conf $CONF
        
        echo ""
        echo -e "${GREEN}✓ Video işleme tamamlandı!${NC}"
        echo "Sonuç: runs/detect/predict/"
        ;;
        
    6)
        echo ""
        echo -e "${BLUE}📊 Validation seti üzerinde değerlendirme yapılıyor...${NC}"
        echo "======================================================================"
        python train_yolo_model.py --mode val
        
        echo ""
        echo -e "${GREEN}✓ Validation tamamlandı!${NC}"
        ;;
        
    7)
        echo "Çıkılıyor..."
        exit 0
        ;;
        
    *)
        echo -e "${RED}Geçersiz seçim!${NC}"
        exit 1
        ;;
esac

echo ""
echo "======================================================================"
echo -e "${GREEN}🎉 Test işlemi tamamlandı!${NC}"
echo "======================================================================"
echo ""
echo "Diğer test komutları:"
echo ""
echo "• Test seti değerlendirme:"
echo "  python train_yolo_model.py --mode test"
echo ""
echo "• Görüntü tahmini:"
echo "  python train_yolo_model.py --mode predict --source test/images/"
echo ""
echo "• Model export (ONNX):"
echo "  python train_yolo_model.py --mode export --format onnx"
echo ""
