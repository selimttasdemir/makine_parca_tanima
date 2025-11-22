#!/bin/bash

# Hızlı YOLOv8 Eğitim Scripti
# Makine Parçası Tespit Modeli

echo "======================================================================"
echo "YOLOv8 Makine Parçası Tespit Modeli - Hızlı Eğitim"
echo "======================================================================"
echo ""

# Renk kodları
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Gerekli kütüphaneleri kontrol et
echo -e "${BLUE}[1/5]${NC} Gerekli kütüphaneler kontrol ediliyor..."
if python3 -c "import ultralytics" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} ultralytics yüklü"
else
    echo -e "${YELLOW}⚠${NC} ultralytics yüklenmiş değil. Yükleniyor..."
    pip install ultralytics pyyaml
fi

if python3 -c "import torch" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} PyTorch yüklü"
else
    echo -e "${YELLOW}⚠${NC} PyTorch yüklenmiş değil. Yükleniyor..."
    pip install torch torchvision
fi
echo ""

# 2. Veri yapısını kontrol et
echo -e "${BLUE}[2/5]${NC} Veri yapısı kontrol ediliyor..."
if [ -d "train/images" ] && [ -d "train/labels" ]; then
    TRAIN_IMG_COUNT=$(ls train/images/*.jpg 2>/dev/null | wc -l)
    TRAIN_LBL_COUNT=$(ls train/labels/*.txt 2>/dev/null | wc -l)
    echo -e "${GREEN}✓${NC} Train klasörü: ${TRAIN_IMG_COUNT} görüntü, ${TRAIN_LBL_COUNT} etiket"
else
    echo -e "${RED}✗${NC} Train klasörü bulunamadı!"
    exit 1
fi

if [ -d "val/images" ] && [ -d "val/labels" ]; then
    VAL_IMG_COUNT=$(ls val/images/*.jpg 2>/dev/null | wc -l)
    VAL_LBL_COUNT=$(ls val/labels/*.txt 2>/dev/null | wc -l)
    echo -e "${GREEN}✓${NC} Val klasörü: ${VAL_IMG_COUNT} görüntü, ${VAL_LBL_COUNT} etiket"
else
    echo -e "${YELLOW}⚠${NC} Val klasörü bulunamadı!"
fi

if [ -f "mech_parts_data.yaml" ]; then
    echo -e "${GREEN}✓${NC} Dataset YAML dosyası mevcut"
else
    echo -e "${RED}✗${NC} mech_parts_data.yaml bulunamadı!"
    exit 1
fi
echo ""

# 3. GPU/CPU kontrolü
echo -e "${BLUE}[3/5]${NC} Donanım kontrol ediliyor..."
if python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null | grep -q "True"; then
    GPU_NAME=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
    echo -e "${GREEN}✓${NC} GPU bulundu: ${GPU_NAME}"
    DEVICE="0"
else
    echo -e "${YELLOW}⚠${NC} GPU bulunamadı, CPU kullanılacak"
    DEVICE="cpu"
fi
echo ""

# 4. Kullanıcıdan eğitim parametrelerini al
echo -e "${BLUE}[4/5]${NC} Eğitim parametrelerini seçin:"
echo ""
echo "Model boyutu seçin:"
echo "  1) Nano (n)    - En hızlı, düşük doğruluk (önerilen: test için)"
echo "  2) Small (s)   - Hızlı, orta doğruluk (önerilen: genel kullanım)"
echo "  3) Medium (m)  - Orta hız, yüksek doğruluk"
echo "  4) Large (l)   - Yavaş, çok yüksek doğruluk"
echo "  5) XLarge (x)  - En yavaş, en yüksek doğruluk"
echo ""
read -p "Seçiminiz (1-5) [varsayılan: 2]: " MODEL_CHOICE
MODEL_CHOICE=${MODEL_CHOICE:-2}

case $MODEL_CHOICE in
    1) MODEL_SIZE="n" ;;
    2) MODEL_SIZE="s" ;;
    3) MODEL_SIZE="m" ;;
    4) MODEL_SIZE="l" ;;
    5) MODEL_SIZE="x" ;;
    *) MODEL_SIZE="s" ;;
esac

echo ""
read -p "Epoch sayısı [varsayılan: 100]: " EPOCHS
EPOCHS=${EPOCHS:-100}

# GPU varsa batch size 8, CPU varsa 4 (8GB GPU için optimize edildi)
if [ "$DEVICE" = "cpu" ]; then
    DEFAULT_BATCH=4
else
    DEFAULT_BATCH=8
fi

read -p "Batch size [varsayılan: $DEFAULT_BATCH]: " BATCH
BATCH=${BATCH:-$DEFAULT_BATCH}

read -p "Görüntü boyutu [varsayılan: 640]: " IMGSZ
IMGSZ=${IMGSZ:-640}

echo ""
echo -e "${GREEN}Seçilen Parametreler:${NC}"
echo "  - Model: YOLOv8${MODEL_SIZE}"
echo "  - Epochs: ${EPOCHS}"
echo "  - Batch Size: ${BATCH}"
echo "  - Image Size: ${IMGSZ}"
echo "  - Device: ${DEVICE}"
echo ""
echo -e "${YELLOW}💡 Not:${NC} 8GB GPU için batch size 8 optimize edilmiştir."
echo "   Bellek hatası alırsanız batch size'ı 4'e düşürün."
echo ""

read -p "Eğitime başlamak için ENTER'a basın (çıkmak için Ctrl+C)..."
echo ""

# 5. Eğitimi başlat
echo -e "${BLUE}[5/5]${NC} Eğitim başlıyor..."
echo "======================================================================"
echo ""

python3 train_yolo_model.py \
    --mode train \
    --size ${MODEL_SIZE} \
    --epochs ${EPOCHS} \
    --batch ${BATCH} \
    --imgsz ${IMGSZ} \
    --device ${DEVICE} \
    --patience 50

# Eğitim sonucu kontrolü
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo -e "${GREEN}✓ Eğitim başarıyla tamamlandı!${NC}"
    echo "======================================================================"
    echo ""
    echo "Sonuçlar:"
    echo "  📁 Model: runs/detect/train/weights/best.pt"
    echo "  📊 Grafikler: runs/detect/train/"
    echo ""
    echo "Şimdi ne yapabilirsiniz:"
    echo ""
    echo "1. Modeli test edin:"
    echo "   python3 train_yolo_model.py --mode test"
    echo ""
    echo "2. Tahmin yapın:"
    echo "   python3 train_yolo_model.py --mode predict --source test/images/"
    echo ""
    echo "3. Validation yapın:"
    echo "   python3 train_yolo_model.py --mode val"
    echo ""
    echo "4. Export edin (ONNX):"
    echo "   python3 train_yolo_model.py --mode export --format onnx"
    echo ""
else
    echo ""
    echo "======================================================================"
    echo -e "${RED}✗ Eğitim sırasında hata oluştu!${NC}"
    echo "======================================================================"
    echo ""
    echo "Sorun giderme önerileri:"
    echo "  1. Veri yapısını kontrol edin (train/val/test klasörleri)"
    echo "  2. mech_parts_data.yaml dosyasını kontrol edin"
    echo "  3. Bellek yetersizse batch size'ı azaltın"
    echo "  4. YOLO_EGITIM_REHBERI.md dosyasına bakın"
    echo ""
fi
