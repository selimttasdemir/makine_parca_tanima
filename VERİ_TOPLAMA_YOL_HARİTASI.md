# 🗺️ VERİ TOPLAMA YOL HARİTASI

Makine parçası tanıma sisteminiz için kapsamlı bir bilgi tabanı oluşturma rehberi.

---

## 📅 AŞAMA 1: HIZLI PROTOTIP (1-3 GÜN)

### Hedef: Sistemin çalıştığını görmek

#### Adım 1.1: Temel Referans Görüntüler (2 saat)
```bash
# Her parça için 3-5 örnek görüntü
referans_gorseller/
├── vida/         (3-5 görüntü)
├── somun/        (3-5 görüntü)
├── rulman/       (3-5 görüntü)
└── ...
```

**Nereden Bulabilirsiniz:**
1. **Google Görseller**: "M8 vida", "altıgen somun", vb.
   - Sağ tık → Resmi farklı kaydet
   - Her parça için 3-5 farklı açıdan
   
2. **Ücretsiz Stok Fotoğraf Siteleri**:
   - Unsplash.com
   - Pexels.com
   - Pixabay.com
   - Freepik.com (bazı ücretsiz)

3. **Telefon Kameranız**:
   - Beyaz/gri arka plan
   - İyi aydınlatma
   - Farklı açılar

#### Adım 1.2: Test (10 dakika)
```bash
python test_system.py
streamlit run app.py
```

**Beklenen Sonuç:**
- ✅ Feature matching aktif
- 📊 %60-70 doğruluk (yeterli başlangıç için)

#### Adım 1.3: İlk Geri Bildirim (1 gün)
- Arkadaşlara test ettirin
- Hangi parçalar karışıyor?
- Hangi açılar zor?

---

## 📅 AŞAMA 2: VERİ GENİŞLETME (1-2 HAFTA)

### Hedef: Her parça için 20-30 görüntü

#### Adım 2.1: Web Scraping (Otomatik) - 1 gün

**Script ile toplu indirme:**
```python
# web_scraper.py dosyası oluşturun
from google_images_download import google_images_download

parcalar = ['vida', 'somun', 'rulman', 'kayış', 'dişli']
response = google_images_download.googleimagesdownload()

for parca in parcalar:
    arguments = {
        "keywords": f"makine {parca}, mechanical {parca}",
        "limit": 30,
        "format": "jpg",
        "output_directory": "referans_gorseller",
        "image_directory": parca,
        "size": "medium",
        "aspect_ratio": "square"
    }
    paths = response.download(arguments)
    print(f"{parca}: İndirildi")
```

**Kurulum:**
```bash
pip install google_images_download
python web_scraper.py
```

#### Adım 2.2: Online Kataloglar - 2 saat
**Önerilen Kaynaklar:**
1. **Grainger.com** - Endüstriyel parça katalogları
2. **McMaster-Carr** - Teknik çizimler ve fotoğraflar
3. **RS Components** - Elektronik ve mekanik parçalar
4. **Digikey** - Elektronik komponentler
5. **Alibaba/AliExpress** - Ürün fotoğrafları

#### Adım 2.3: Manuel Fotoğraf Çekimi - 1-2 saat
**Profesyonel Fotoğraf İpuçları:**
```
SETUP:
├── Beyaz A4 kağıt (arka plan)
├── LED lamba (gölgesiz aydınlatma)
├── Telefon kamerası (en az 8MP)
└── Tripod (sabit çekim)

AÇILAR:
├── Üstten (90°)
├── Yan (45°)
├── Çapraz (30°)
├── Yakın plan
└── Uzak plan
```

**Örnek Çekim Listesi:**
```
vida_001.jpg - Üstten, düz
vida_002.jpg - 45° açı
vida_003.jpg - Yan görünüm
vida_004.jpg - Yakın plan (dişler)
vida_005.jpg - 3-4 vida bir arada
```

---

## 📅 AŞAMA 3: KALİTE KONTROL (2-3 GÜN)

### Hedef: Kalitesiz görüntüleri temizlemek

#### Adım 3.1: Otomatik Filtreleme
```python
# image_quality_check.py
from PIL import Image
import os

def check_image_quality(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(('.jpg', '.png')):
                img_path = os.path.join(root, file)
                img = Image.open(img_path)
                
                # Boyut kontrolü
                if img.width < 200 or img.height < 200:
                    print(f"❌ Küçük: {img_path}")
                    
                # Aspect ratio kontrolü
                ratio = img.width / img.height
                if ratio > 3 or ratio < 0.33:
                    print(f"⚠️  Orantısız: {img_path}")
                
                # Dosya boyutu
                size_kb = os.path.getsize(img_path) / 1024
                if size_kb < 10:
                    print(f"❌ Çok küçük dosya: {img_path}")

check_image_quality('referans_gorseller')
```

#### Adım 3.2: Manuel İnceleme (1 saat)
Şunları kontrol edin:
- ✅ Parça net görünüyor mu?
- ✅ Arka plan temiz mi?
- ✅ Doğru etiketlenmiş mi?
- ❌ Filigran/logo var mı?

#### Adım 3.3: Temizleme
```bash
# Küçük görüntüleri sil
find referans_gorseller -type f -size -10k -delete

# Duplicate kontrol
pip install imagededup
```

---

## 📅 AŞAMA 4: VERİ ARTIRMA (1 GÜN)

### Hedef: 20 görüntüyü 100'e çıkarmak

#### Script ile Otomatik Augmentation:
```python
# data_augmentation.py
from torchvision import transforms
from PIL import Image
import os

augmentation = transforms.Compose([
    transforms.RandomRotation(30),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ColorJitter(brightness=0.3, contrast=0.3),
    transforms.RandomPerspective(distortion_scale=0.2, p=0.5),
    transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
])

def augment_folder(input_folder, output_folder, count=5):
    os.makedirs(output_folder, exist_ok=True)
    
    for img_file in os.listdir(input_folder):
        if not img_file.endswith(('.jpg', '.png')):
            continue
            
        img_path = os.path.join(input_folder, img_file)
        img = Image.open(img_path)
        
        # Orijinali kopyala
        img.save(os.path.join(output_folder, img_file))
        
        # Augmented versiyonlar
        for i in range(count):
            aug_img = augmentation(img)
            name, ext = os.path.splitext(img_file)
            aug_img.save(os.path.join(output_folder, f"{name}_aug{i}{ext}"))
        
        print(f"✓ {img_file}: 1 + {count} = {count+1} görüntü")

# Kullanım
augment_folder('referans_gorseller/vida', 'training_data/vida', count=5)
```

**Çalıştır:**
```bash
python data_augmentation.py
```

**Sonuç:**
- 20 gerçek görüntü → 120 toplam görüntü (20 + 100 augmented)

---

## 📅 AŞAMA 5: ETİKETLEME VE ORGANİZASYON (1-2 GÜN)

### Adım 5.1: Klasör Yapısını Düzenle
```
training_data/
├── vida/
│   ├── m3_vida_001.jpg
│   ├── m3_vida_002.jpg
│   ├── m8_vida_001.jpg
│   └── ...
├── somun/
│   ├── altigen_somun_001.jpg
│   └── ...
└── rulman/
    ├── 608_rulman_001.jpg
    └── ...
```

### Adım 5.2: Metadata Oluştur
```python
# create_metadata.py
import json
import os
from PIL import Image

metadata = {}

for parca in os.listdir('training_data'):
    parca_path = os.path.join('training_data', parca)
    if not os.path.isdir(parca_path):
        continue
    
    images = []
    for img_file in os.listdir(parca_path):
        if img_file.endswith(('.jpg', '.png')):
            img_path = os.path.join(parca_path, img_file)
            img = Image.open(img_path)
            
            images.append({
                'filename': img_file,
                'width': img.width,
                'height': img.height,
                'size_kb': os.path.getsize(img_path) / 1024
            })
    
    metadata[parca] = {
        'count': len(images),
        'images': images
    }

with open('dataset_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("Metadata oluşturuldu!")
```

---

## 📅 AŞAMA 6: MODEL EĞİTİMİ (1-2 GÜN)

### Adım 6.1: Veri Setini Böl
```python
# split_dataset.py
import os
import shutil
import random

def split_dataset(source, train_ratio=0.8):
    for parca in os.listdir(source):
        parca_path = os.path.join(source, parca)
        if not os.path.isdir(parca_path):
            continue
        
        images = [f for f in os.listdir(parca_path) if f.endswith(('.jpg', '.png'))]
        random.shuffle(images)
        
        split_idx = int(len(images) * train_ratio)
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]
        
        # Train klasörü
        train_dir = f'dataset/train/{parca}'
        os.makedirs(train_dir, exist_ok=True)
        
        # Val klasörü
        val_dir = f'dataset/val/{parca}'
        os.makedirs(val_dir, exist_ok=True)
        
        for img in train_imgs:
            shutil.copy(
                os.path.join(parca_path, img),
                os.path.join(train_dir, img)
            )
        
        for img in val_imgs:
            shutil.copy(
                os.path.join(parca_path, img),
                os.path.join(val_dir, img)
            )
        
        print(f"{parca}: {len(train_imgs)} train, {len(val_imgs)} val")

split_dataset('training_data')
```

### Adım 6.2: Model Eğit
```bash
python train_model.py \
    --mode train \
    --data_dir ./dataset/train \
    --epochs 50 \
    --batch_size 32 \
    --lr 0.001
```

### Adım 6.3: Model Değerlendir
```bash
python train_model.py \
    --mode test \
    --model_path best_model.pth \
    --test_image ./dataset/val/vida/test1.jpg
```

---

## 📅 AŞAMA 7: KULLANICI GERİ BİLDİRİMİ (SÜREKLİ)

### Feedback Sistemi Kur
```python
# app.py içine ekleyin
if st.button("❌ Yanlış Tanıma"):
    feedback = {
        'image': uploaded_file.name,
        'predicted': parca_adi,
        'user_says': st.selectbox("Doğrusu ne?", sistem.parca_veritabani.keys())
    }
    
    # CSV'ye kaydet
    import csv
    with open('feedback.csv', 'a') as f:
        writer = csv.DictWriter(f, fieldnames=['image', 'predicted', 'user_says'])
        writer.writerow(feedback)
    
    st.success("Geri bildirim kaydedildi!")
```

### Aylık İyileştirme Döngüsü
```bash
# 1. Feedback topla (30 gün)
# 2. Yanlış tanımaları analiz et
# 3. O parçalar için daha fazla veri topla
# 4. Yeniden eğit
# 5. Deploy et
```

---

## 📊 HEDEF VERİ MİKTARLARI

| Aşama | Görüntü/Sınıf | Toplam (10 sınıf) | Doğruluk Beklentisi |
|-------|---------------|-------------------|---------------------|
| **Prototip** | 3-5 | 30-50 | %60-70 (FM) |
| **Beta** | 20-30 | 200-300 | %70-80 (FM) |
| **Production v1** | 50-100 | 500-1000 | %85-90 (DL) |
| **Production v2** | 100-200 | 1000-2000 | %90-95 (Hibrit) |
| **Enterprise** | 200-500 | 2000-5000 | %95-98 (Ensemble) |

---

## 🛠️ ARAÇLAR VE KAYNAKLAR

### Görüntü Toplama
- **google-images-download**: Otomatik indirme
- **Selenium**: Web scraping
- **Beautiful Soup**: HTML parsing
- **Scrapy**: Profesyonel scraping

### Etiketleme
- **Labelbox**: Web tabanlı (ücretsiz plan)
- **LabelImg**: Desktop app
- **CVAT**: Açık kaynak
- **Roboflow**: Veri yönetimi + etiketleme

### Veri Artırma
- **Albumentations**: Gelişmiş augmentation
- **imgaug**: Çeşitli augmentation
- **Torchvision transforms**: Basit augmentation

### Kalite Kontrol
- **ImageMagick**: Batch işlemler
- **ImageDedupe**: Duplicate silme
- **PIL/Pillow**: Python ile kontrol

---

## 📅 ZAMAN ÇİZELGESİ ÖZETİ

```
┌─────────────────────────────────────────────┐
│  GÜN 1-3: Hızlı Prototip                   │
│  └─ 3-5 görüntü/sınıf                       │
│  └─ Feature matching test                   │
│  Çıktı: Çalışan demo                        │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│  HAFTA 1-2: Veri Toplama                   │
│  └─ Web scraping                            │
│  └─ Manuel fotoğraf                          │
│  └─ 20-30 görüntü/sınıf                     │
│  Çıktı: 200-300 toplam görüntü              │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│  HAFTA 2-3: Kalite & Artırma               │
│  └─ Filtreleme ve temizleme                 │
│  └─ Data augmentation                        │
│  └─ 100+ görüntü/sınıf                      │
│  Çıktı: 1000+ eğitim verisi                 │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│  HAFTA 4: Model Eğitimi                    │
│  └─ Transfer learning                        │
│  └─ Validation ve test                       │
│  Çıktı: best_model.pth (%85-90)             │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│  SÜREKLİ: İyileştirme                      │
│  └─ Kullanıcı feedback                       │
│  └─ Aylık yeniden eğitim                     │
│  Çıktı: %95+ doğruluk                       │
└─────────────────────────────────────────────┘
```

---

## 💰 MALİYET TAHMİNİ

### Ücretsiz Yöntem:
- ✅ Google Görseller (manuel)
- ✅ Kendi fotoğraflarınız
- ✅ Açık kaynak araçlar
- **Toplam: 0 TL**

### Yarı-Otomatik:
- ✅ Web scraping (ücretsiz)
- ✅ Labelbox ücretsiz plan
- ✅ Roboflow ücretsiz tier
- **Toplam: 0-500 TL**

### Profesyonel:
- 💰 Mechanical Turk (etiketleme): ~1000 TL
- 💰 Shutterstock/Getty: ~2000 TL
- 💰 GPU Cloud (eğitim): ~500 TL/ay
- **Toplam: 3500-5000 TL**

---

## ✅ KONTROL LİSTESİ

### Hafta 1
- [ ] 5 farklı parça seçildi
- [ ] Parça başına 10 görüntü toplandı
- [ ] Feature matching test edildi
- [ ] İlk demo hazır

### Hafta 2
- [ ] Web scraping scripti çalışıyor
- [ ] 300+ görüntü toplandı
- [ ] Kalite kontrol yapıldı
- [ ] Augmentation test edildi

### Hafta 3
- [ ] 1000+ eğitim verisi hazır
- [ ] Train/val/test split yapıldı
- [ ] Metadata oluşturuldu

### Hafta 4
- [ ] Model eğitimi tamamlandı
- [ ] %85+ validation accuracy
- [ ] Hibrit sistem test edildi
- [ ] Production'a deploy edildi

---

**BAŞARILAR! 🚀**

Sorularınız için: Issues açabilir veya doğrudan sorabilirsiniz!
