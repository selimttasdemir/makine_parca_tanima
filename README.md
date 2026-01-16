# 🔧 Makine Parçası Tanıma ve Tespit Sistemi

Görüntü işleme, derin öğrenme (ResNet50) ve YOLO tabanlı nesne tespiti ile makine parçalarını sınıflandıran ve tespit eden kapsamlı Python projesi.

## 📋 İçindekiler
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Proje Yapısı](#-proje-yapısı)
- [Kurulum](#-kurulum)
- [Veri Toplama](#-veri-toplama-ve-hazırlık)
- [Model Eğitimi](#-model-eğitimi)
  - [ResNet50 Sınıflandırma](#1-resnet50-sınıflandırma)
  - [YOLO Nesne Tespiti](#2-yolo-nesne-tespiti)
- [Web Uygulaması](#-web-uygulaması-kullanımı)
- [Model Performans Testi](#-model-performans-testi)
- [GPU ve Performans](#-gpu-bellek-yönetimi)
- [Sorun Giderme](#-sorun-giderme)

## 🚀 Hızlı Başlangıç

### Temel Kurulum
```bash
# Gerekli paketleri kur
pip install -r requirements.txt

# Klasör yapısını oluştur
chmod +x setup_folders.sh && ./setup_folders.sh

# Web uygulamasını başlat
./web_test.sh
# veya
streamlit run app.py
```

### Hızlı Eğitim
```bash
# 1. Veri topla
python download_images.py --classes vida somun rulman disli --per-class 40 --out training_data

# 2. Sınıflandırma modeli eğit
python train_model.py --mode train --data_dir ./training_data --epochs 25

# 3. YOLO modeli eğit (hızlı)
./hizli_egitim.sh
```

## 📁 Proje Yapısı
```
makine_parca_tanima/
├── app.py                      # Streamlit web arayüzü (ana uygulama)
├── train_model.py              # ResNet50 transfer learning eğitimi
├── hybrid_detector.py          # DL + feature matching hibrit sistem
├── feature_matcher.py          # SIFT/histogram/hu tabanlı hızlı tanıma
├── download_images.py          # DuckDuckGo ile görsel indirme
├── train_yolo_model.py         # YOLOv8 eğitim/val/test/predict/export
├── test_dogruluk.py            # Model doğruluk testi
├── hizli_egitim.sh             # YOLO hızlı eğitim scripti
├── web_test.sh                 # Web uygulaması başlatma scripti
├── web_durum_kontrol.sh        # Sistem durum kontrolü
├── mech_parts_data.yaml        # YOLO dataset tanımı
├── requirements.txt            # Gerekli Python paketleri
├── training_data/              # Sınıflandırma verisi (klasör başına sınıf)
│   ├── civata/
│   ├── disli/
│   ├── kayis/
│   ├── krank/
│   ├── pim/
│   ├── piston/
│   ├── rulman/
│   ├── somun/
│   ├── vida/
│   └── yay/
├── referans_gorseller/         # Feature matching için referans görseller
├── train/                      # YOLO eğitim verisi
│   ├── images/
│   └── labels/
├── val/                        # YOLO doğrulama verisi
│   ├── images/
│   └── labels/
├── test/                       # YOLO test verisi
│   ├── images/
│   └── labels/
└── runs/                       # Eğitim sonuçları ve modeller
    └── detect/
        └── train/
            └── weights/
                └── best.pt     # Eğitilmiş YOLO modeli
```

## 📦 Kurulum

### Gereksinimler
- Python 3.8+
- CUDA (GPU kullanımı için önerilir)
- 8GB+ RAM (16GB önerilir)

### Paket Kurulumu
```bash
# Tüm gerekli paketleri kur
pip install -r requirements.txt

# Manuel kurulum (gerekirse)
pip install torch torchvision
pip install ultralytics opencv-python
pip install streamlit pillow numpy pandas
pip install scikit-learn matplotlib seaborn
```

### Klasör Yapısını Oluşturma
```bash
chmod +x setup_folders.sh
./setup_folders.sh
```

## 📥 Veri Toplama ve Hazırlık

### Otomatik Veri İndirme
```bash
# Birden fazla sınıf için otomatik indirme
python download_images.py --classes vida somun rulman disli piston --per-class 40 --out training_data

# Özel parametrelerle
python download_images.py --classes civata kayis --per-class 100 --out ./my_data
```

### Manuel Veri Toplama
Her sınıf için minimum 10-15 görsel önerilir:
```bash
training_data/
  ├── vida/        # 10+ görsel
  ├── somun/       # 10+ görsel
  ├── rulman/      # 10+ görsel
  └── disli/       # 10+ görsel
```

### Veri Kontrolü
```bash
# Eğitim verisini kontrol et
python check_training_data.py

# YOLO dataset kontrolü
python check_dataset.py
```

## 🧠 Model Eğitimi

### 1. ResNet50 Sınıflandırma

#### Temel Eğitim
```bash
# Varsayılan parametrelerle eğitim
python train_model.py --mode train --data_dir ./training_data --epochs 25

# Gelişmiş parametrelerle
python train_model.py \
  --mode train \
  --data_dir ./training_data \
  --epochs 50 \
  --batch_size 32 \
  --lr 0.001 \
  --patience 10
```

**Minimum Gereksinimler:**
- En az 2 farklı sınıf
- Toplam 2+ görüntü
- Otomatik veri kontrolü entegre

#### Model Testi
```bash
# Tek görsel testi
python train_model.py --mode test --model_path best_model.pth --test_image ./test.jpg

# Test seti üzerinde değerlendirme
python train_model.py --mode evaluate --model_path best_model.pth --test_dir ./test_images
```

#### Python Kodu ile Kullanım
```python
from hybrid_detector import HibritTanima

# Model yükle
sistem = HibritTanima(
    model_path='best_model.pth',
    referans_klasor='./referans_gorseller',
    mod='auto'  # veya 'dl', 'feature'
)

# Tahmin yap
sonuc = sistem.tanima_yap('test.jpg')
print(f"Parça: {sonuc['parca']}")
print(f"Güven: {sonuc['guven']:.2%}")
```

### 2. YOLO Nesne Tespiti

#### Hızlı Eğitim (Önerilen)
```bash
# İnteraktif script (model boyutu, epoch, batch otomatik seçilir)
./hizli_egitim.sh
```

#### Manuel Eğitim
```bash
# Nano model (en hızlı, 8GB GPU için ideal)
python train_yolo_model.py \
  --mode train \
  --size n \
  --epochs 100 \
  --batch 16 \
  --imgsz 640 \
  --data mech_parts_data.yaml

# Medium model (daha yüksek doğruluk)
python train_yolo_model.py \
  --mode train \
  --size m \
  --epochs 150 \
  --batch 8 \
  --imgsz 640

# CPU eğitimi (GPU yoksa)
python train_yolo_model.py \
  --mode train \
  --size n \
  --epochs 50 \
  --batch 4 \
  --device cpu
```

#### Model Boyutları
| Model | Hız | Doğruluk | GPU Bellek | Önerilen Batch |
|-------|-----|----------|------------|----------------|
| YOLOv8n | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | ~2GB | 16 |
| YOLOv8s | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | ~4GB | 12 |
| YOLOv8m | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ~6GB | 8 |
| YOLOv8l | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~8GB | 4 |
| YOLOv8x | ⚡ | ⭐⭐⭐⭐⭐⭐ | ~12GB | 2 |

#### Doğrulama ve Test
```bash
# Doğrulama (validation)
python train_yolo_model.py --mode val

# Test seti değerlendirme
python train_yolo_model.py --mode test

# Tahmin (prediction)
python train_yolo_model.py \
  --mode predict \
  --source test/images/ \
  --conf 0.25

# Model export (ONNX, TensorRT vb.)
python train_yolo_model.py --mode export --format onnx
```

#### YOLO Dataset Yapısı
```yaml
# mech_parts_data.yaml
train: ./train/images
val: ./val/images
test: ./test/images

nc: 4  # Sınıf sayısı
names: ['Bearing', 'Bolt', 'Gear', 'Nut']  # Sınıf isimleri
```

**Label formatı (YOLO format):**
```
# train/labels/image1.txt
0 0.5 0.5 0.3 0.4  # class_id center_x center_y width height (normalize)
```

## 🌐 Web Uygulaması Kullanımı

### Başlatma
```bash
# Otomatik başlatma (önerilen)
./web_test.sh

# Manuel başlatma
streamlit run app.py

# Durum kontrolü
./web_durum_kontrol.sh
```

Uygulama otomatik olarak tarayıcınızda açılacak: `http://localhost:8501`

### Ana Sayfa - Parça Tanıma

#### 1. Tanıma Yöntemi Seçimi
Sol kenar çubuğundan seçim yapın:
- **🎯 YOLO (Eğitilmiş Model)** - En yüksek doğruluk, çoklu nesne tespiti
- **🧠 Deep Learning (ResNet50)** - Tek nesne sınıflandırma
- **🔍 Feature Matching** - Hızlı, referans tabanlı
- **⚡ Hibrit (Otomatik)** - DL + Feature matching kombinasyonu

#### 2. YOLO Kullanımı
```
Adım 1: YOLO Model Yolu
  └─ runs/detect/train/weights/best.pt (varsayılan)

Adım 2: Tanıma Yöntemi
  └─ 🎯 YOLO seçin

Adım 3: Fotoğraf Yükle
  └─ Browse files → Görsel seç

Adım 4: Analiz Et
  └─ 🔍 Analiz Et butonuna tıkla

Adım 5: Sonuçları İncele
  ├─ Bounding box'lı görsel
  ├─ Tespit edilen nesneler listesi
  ├─ Güven skorları
  └─ Parça bilgileri
```

#### 3. Sonuçları Temizleme
Yeni bir analiz yapmadan önce:
```bash
🗑️ Sonuçları Temizle  # Butona tıklayın
```

### Örnek Kullanım Senaryoları

#### Senaryo 1: Rulman Tespiti
```
✅ YOLO seç
✅ Rulman fotoğrafı yükle
✅ Analiz Et

Sonuç:
🎯 YOLO Tespit Sonucu
   [Bearing 0.92]
   
🔍 Tespit Edilen Nesneler:
   1. Bearing → Rulman 🎯 %92.3

✅ Tespit Edilen Parça: Rulman
🟢 %92.3 Güven
```

#### Senaryo 2: Çoklu Nesne Tespiti
```
Fotoğrafta: 2 vida, 1 somun

Sonuç:
🎯 YOLO Tespit Sonucu
   [Bolt 0.89] [Bolt 0.85]
   [Nut 0.91]

🔍 Tespit Edilen Tüm Nesneler:
   1. Nut → Somun 🎯 %91.2
   2. Bolt → Vida 🎯 %89.3
   3. Bolt → Vida 🎯 %85.1
```

### Güven Skoru Yorumlama

| Güven Skoru | Anlamı | Durum |
|-------------|--------|-------|
| **90%+** | 🎯 Çok Yüksek | Güvenle kullanılabilir |
| **80-90%** | ✅ Yüksek | İyi tespit |
| **70-80%** | 👍 İyi | Kabul edilebilir |
| **60-70%** | ⚠️ Orta | Dikkatli kullanın |
| **50-60%** | ⚠️ Düşük | Manuel kontrol gerekli |
| **<50%** | ❌ Çok Düşük | Güvenilmez |

### Bounding Box Özellikleri
- Her sınıf için farklı renk
- Sınıf adı + güven skoru etiketi
- Çoklu nesne desteği
- Otomatik güven eşiği filtreleme (%25)

## 📊 Model Performans Testi

### Web Arayüzü ile Test

#### Adım 1: Test Sayfasına Git
Sol menüden **"📊 Model Performans Testi"** seçin

#### Adım 2: Test Ayarları
```
Model Yolu: runs/detect/train/weights/best.pt
Test Görüntü Sayısı: 50 (0 = hepsi)
Test Klasörü: test
```

#### Adım 3: Testi Başlat
**"🧪 Testi Başlat"** butonuna tıklayın

#### Adım 4: Sonuçları İncele
- ✅ Genel doğruluk oranı
- 📊 Sınıf bazında performans
- ❌ Yanlış tahmin örnekleri
- 📈 İnteraktif grafikler

#### Adım 5: Sonuçları Kaydet
```
💾 Sonuçları Kaydet (JSON)
  └─ 📥 JSON Dosyasını İndir
```

### Komut Satırı ile Test

#### Tam Test (Tüm Görüntüler)
```bash
python test_dogruluk.py --model runs/detect/train/weights/best.pt
```

#### Hızlı Test (İlk 50)
```bash
python test_dogruluk.py --model runs/detect/train/weights/best.pt --limit 50
```

#### Özel Parametrelerle
```bash
python test_dogruluk.py \
  --model runs/detect/train/weights/best.pt \
  --test test \
  --limit 100 \
  --save sonuclarim.json
```

### Örnek Test Çıktısı
```
============================================================
📈 TEST SONUÇLARI
============================================================

✅ Genel Doğruluk: %87.45
   Doğru: 962/1100
   Yanlış: 138/1100
   Test Edilen Görüntü: 225

📊 Sınıf Bazında Doğruluk:
   Bearing (Rulman): %91.27 (251/275 doğru)
   Gear (Dişli)    : %88.93 (257/289 doğru)
   Bolt (Vida)     : %86.22 (269/312 doğru)
   Nut (Somun)     : %82.59 (185/224 doğru)

❌ Yanlış Tahmin Örnekleri (İlk 5):
   1. image_252.jpg
      Gerçek: Nut | Tahmin: Bolt (Güven: %73.2)
   2. image_288.jpg
      Gerçek: Gear | Tahmin: Bearing (Güven: %68.5)
   ...

💾 Detaylı sonuçlar kaydedildi: test_sonuclari.json
```

### Doğruluk Skorlarını Yorumlama

| Genel Doğruluk | Değerlendirme | Öneriler |
|----------------|---------------|----------|
| **90%+** | 🎯 Mükemmel | Model üretime hazır |
| **75-90%** | ✅ İyi | Kullanılabilir, iyileştirilebilir |
| **60-75%** | ⚠️ Orta | Daha fazla eğitim gerekli |
| **<60%** | ❌ Zayıf | Model/veri gözden geçirilmeli |

### Performans İyileştirme İpuçları

Bir sınıf düşük performans gösteriyorsa:
1. **Daha Fazla Veri:** O sınıftan daha fazla örnek toplayın
2. **Veri Artırma:** Augmentation teknikleri uygulayın
3. **Etiket Kontrolü:** Yanlış etiketleri düzeltin
4. **Uzun Eğitim:** Daha fazla epoch ile eğitin
5. **Büyük Model:** YOLOv8n yerine YOLOv8m/l kullanın

## ⚡ GPU Bellek Yönetimi

### 8GB GPU için Öneriler
```bash
# YOLOv8n veya YOLOv8s kullanın
python train_yolo_model.py --size n --batch 16 --imgsz 640

# Bellek hatası alırsanız
python train_yolo_model.py --size n --batch 8 --imgsz 640

# Son çare
python train_yolo_model.py --size n --batch 4 --imgsz 416
```

### Bellek Hatası Çözümleri

#### CUDA Out of Memory
1. **Batch size küçült:**
   ```bash
   --batch 8  # 16'dan 8'e
   --batch 4  # 8'den 4'e
   ```

2. **Görüntü boyutu küçült:**
   ```bash
   --imgsz 416  # 640'tan 416'ya
   ```

3. **Daha küçük model:**
   ```bash
   --size n  # m veya l yerine
   ```

4. **CPU kullan (son çare):**
   ```bash
   --device cpu --batch 4
   ```

### GPU vs CPU Karşılaştırması

| Özellik | GPU (8GB) | CPU |
|---------|-----------|-----|
| **Hız** | 100 epoch → 20-30 dk | 100 epoch → 5-8 saat |
| **Batch Size** | 16 (n), 8 (m) | 4 |
| **Önerilen** | YOLOv8n/s/m | YOLOv8n |
| **Kullanım** | Üretim | Test/Geliştirme |

### Hızlı Test Eğitimi
```bash
# GPU ile
python train_yolo_model.py --mode train --size n --epochs 30 --batch 16 --imgsz 640

# CPU ile
python train_yolo_model.py --mode train --size n --epochs 10 --batch 4 --imgsz 416 --device cpu
```

## 🔧 Sorun Giderme

### Veri İle İlgili Sorunlar

#### Veri Eksik veya Boş
```
❌ Sorun: Eğitim verisi bulunamadı
```
**Çözüm:**
```bash
# Veri sayısını kontrol et
python check_training_data.py

# Her sınıfa minimum 10 görüntü ekle
# training_data/<sınıf_adı>/ klasörüne görsel ekleyin
```

#### YOLO Dataset Hatası
```
❌ Sorun: train/images veya train/labels bulunamadı
```
**Çözüm:**
```bash
# Klasör yapısını kontrol et
ls train/images/
ls train/labels/

# Dataset kontrolü
python check_dataset.py
```

### Model İle İlgili Sorunlar

#### Model Dosyası Bulunamadı
```
❌ Sorun: best_model.pth veya best.pt bulunamadı
```
**Çözüm:**
```bash
# ResNet50 için
python train_model.py --mode train --epochs 25

# YOLO için
python train_yolo_model.py --mode train --epochs 50
```

#### CPU'da Model Yükleme Hatası
```
❌ Sorun: CUDA model loading error on CPU
```
**Çözüm:**
Model otomatik olarak CPU'ya maplenir. Eğer hata alırsanız:
```python
# train_model.py içinde
model.load_state_dict(torch.load('best_model.pth', map_location='cpu'))
```

### Web Uygulaması Sorunları

#### Streamlit Bulunamadı
```
❌ streamlit: command not found
```
**Çözüm:**
```bash
pip install streamlit
```

#### OpenCV (cv2) Import Hatası
```
❌ NameError: name 'cv2' is not defined
```
**Çözüm:**
Bu hata düzeltildi! Ama emin olmak için:
```bash
pip install opencv-python
```

#### YOLO Tespit Görseli Gösterilemiyor
Web arayüzünde uyarı mesajı göreceksiniz. Sorun devam ederse:
```bash
./web_durum_kontrol.sh
pip install --upgrade opencv-python Pillow
```

### Referans Veritabanı Sorunları

#### Feature Matching Başarısız
```
❌ Sorun: Referans veritabanı boş
```
**Çözüm:**
```bash
# Her parça için referans görseller ekle
referans_gorseller/
  ├── vida/     # min 5 görsel
  ├── somun/    # min 5 görsel
  ├── rulman/   # min 5 görsel
  └── disli/    # min 5 görsel
```

### Paket Kurulum Sorunları

#### PyTorch CUDA Uyumsuzluğu
```bash
# CUDA 11.8 için
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1 için
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# CPU only
pip install torch torchvision
```

#### Ultralytics Bulunamadı
```bash
pip install ultralytics
```

## 📚 Ek Bilgiler

### Desteklenen Parça Sınıfları
- **Civata** (Bolt)
- **Dişli** (Gear)
- **Kayış** (Belt)
- **Krank** (Crankshaft)
- **Pim** (Pin)
- **Piston** (Piston)
- **Rulman** (Bearing)
- **Somun** (Nut)
- **Vida** (Screw/Bolt)
- **Yay** (Spring)

### Model Karşılaştırması

| Özellik | YOLO | ResNet50 | Feature Matching | Hibrit |
|---------|------|----------|------------------|--------|
| **Hız** | ⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡⚡⚡ | ⚡⚡ |
| **Doğruluk** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Çoklu Nesne** | ✅ Evet | ❌ Hayır | ❌ Hayır | ⚠️ Sınırlı |
| **Eğitim Gerekli** | ✅ Evet | ✅ Evet | ❌ Hayır | ✅ Evet |
| **GPU Gerekli** | İsteğe bağlı | İsteğe bağlı | Hayır | İsteğe bağlı |
| **Kullanım** | Üretim | Geliştirme | Prototip | Üretim |

### Faydalı Komutlar

```bash
# Sistem durumu kontrolü
./web_durum_kontrol.sh

# Web uygulaması başlat
./web_test.sh

# Hızlı YOLO eğitimi
./hizli_egitim.sh

# Model test scripti
./test_model.sh

# Dataset kontrolü
python check_dataset.py
python check_training_data.py

# Veri indirme
python download_images.py --classes vida somun --per-class 50

# YOLO doğruluk testi
python test_dogruluk.py --limit 50

# Sistem bilgileri
python quick_test.py
```

## 🎓 Öğreticiler ve Kaynaklar

### Video Rehberleri
1. **Kurulum ve İlk Eğitim** → `baslangic_rehberi.sh` çalıştır
2. **Web Kullanımı** → Yukarıdaki Web Uygulaması bölümüne bakın
3. **Model Testi** → Model Performans Testi bölümüne bakın

### Kod Örnekleri

#### Python ile YOLO Kullanımı
```python
from ultralytics import YOLO

# Model yükle
model = YOLO('runs/detect/train/weights/best.pt')

# Tahmin yap
results = model.predict('foto.jpg', conf=0.25)

# Sonuçları göster
results[0].show()

# Sonuçları kaydet
results[0].save('sonuc.jpg')
```

#### ResNet50 ile Sınıflandırma
```python
from hybrid_detector import HibritTanima

sistem = HibritTanima(
    model_path='best_model.pth',
    mod='dl'  # Sadece deep learning
)

sonuc = sistem.tanima_yap('test.jpg')
print(f"Parça: {sonuc['parca']} ({sonuc['guven']:.1%})")
```

## 📞 Destek ve Katkı

### Hata Bildirimi
Hata bulduğunuzda:
1. `./web_durum_kontrol.sh` çalıştırın
2. Hata mesajını ve sistem bilgilerini kaydedin
3. GitHub Issues'da bildirin

### Katkıda Bulunma
1. Projeyi fork edin
2. Yeni branch oluşturun
3. Değişikliklerinizi yapın
4. Pull request gönderin

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

**Kolay gelsin! 🚀 İyi çalışmalar!**

Son güncelleme: 16 Ocak 2026
