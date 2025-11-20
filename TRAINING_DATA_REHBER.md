# 📚 Training Data Klasörü Kullanım Rehberi

## 🎯 Ne Yapmalısınız?

`training_data/` klasörüne **her parça türü için en az 100-200 görüntü** eklemelisiniz. Bu görüntüler Deep Learning modelini eğitmek için kullanılacak.

---

## 📁 Klasör Yapısı

```
training_data/
├── vida/          ← Vida görüntüleri buraya (100-200 adet)
├── somun/         ← Somun görüntüleri buraya (100-200 adet)
├── rulman/        ← Rulman görüntüleri buraya (100-200 adet)
├── kayis/         ← Kayış görüntüleri buraya (100-200 adet)
├── disli/         ← Dişli görüntüleri buraya (100-200 adet)
├── piston/        ← Piston görüntüleri buraya (100-200 adet)
├── supap/         ← Supap görüntüleri buraya (100-200 adet)
├── krank/         ← Krank mili görüntüleri buraya (100-200 adet)
├── yay/           ← Yay görüntüleri buraya (100-200 adet)
└── kaynak/        ← Kaynak görüntüleri buraya (100-200 adet)
```

---

## 🆚 İki Klasör Arasındaki Fark

### 1️⃣ `referans_gorseller/` (Feature Matching için)
- **Amaç:** Hızlı benzerlik karşılaştırması
- **Gerekli miktar:** Her parça için **5-10 görüntü** yeterli
- **Kullanım:** SIFT, Histogram, Hu Moments ile eşleştirme
- **Doğruluk:** ~%60-75

### 2️⃣ `training_data/` (Deep Learning için)
- **Amaç:** Neural network eğitimi
- **Gerekli miktar:** Her parça için **100-200+ görüntü**
- **Kullanım:** ResNet50 modelini eğitme
- **Doğruluk:** ~%85-95

---

## 🚀 HIZLI BAŞLANGIÇ (İlk 1 Saat)

### Seçenek 1: Manuel İndirme (ÖNERİLEN)

1. **Google Görseller'den indirin:**
   ```
   1. Google'da arayın: "M8 vida", "hex bolt", "screw"
   2. Görseller sekmesine gidin
   3. Sağ tık → "Resmi farklı kaydet"
   4. training_data/vida/ klasörüne kaydedin
   5. Her parça için tekrarlayın (önce 10'ar tane ile başlayın)
   ```

2. **Unsplash.com'dan yüksek kaliteli görseller:**
   ```
   - unsplash.com → Arama: "bolt", "bearing", "gear"
   - Ücretsiz, yüksek çözünürlüklü
   - İndir → training_data/ilgili_klasor/
   ```

3. **Telefon kameranızla çekin:**
   ```
   📸 İpuçları:
   - Beyaz/gri arka plan kullanın
   - İyi ışık altında çekin
   - Farklı açılardan (yukarı, yan, 45°)
   - Her parçadan 5-10 fotoğraf
   ```

### Seçenek 2: Otomatik İndirme Scripti

```bash
# Hazır scripti kullanın
python download_images.py
```

Bu script size arama terimleri önerecek ve manuel indirme talimatları verecek.

---

## 📊 AŞAMALI YAKLAŞIM

### 🥉 Minimum Başlangıç (1-2 saat)
**Hedef:** Sistemi test etmek
```
Her parça için: 10-20 görüntü
Toplam: ~100-200 görüntü
Beklenen doğruluk: %70-80
```

**Nasıl:**
1. Her parça için Google'dan 10 görüntü indirin
2. `training_data/` klasörlerine atın
3. Model eğitimi yapın:
   ```bash
   python train_model.py --mode train --data_dir ./training_data --epochs 10
   ```

### 🥈 Orta Seviye (1 hafta)
**Hedef:** Kullanılabilir sistem
```
Her parça için: 50-100 görüntü
Toplam: ~500-1000 görüntü
Beklenen doğruluk: %80-85
```

**Nasıl:**
1. Web'den 30-50 görüntü toplayın
2. Kendiniz 10-20 fotoğraf çekin
3. Veri artırma (augmentation) uygulayın
4. Model eğitimi:
   ```bash
   python train_model.py --mode train --data_dir ./training_data --epochs 30
   ```

### 🥇 Profesyonel Seviye (1 ay)
**Hedef:** Üretim kalitesi sistem
```
Her parça için: 200-500 görüntü
Toplam: 2000-5000 görüntü
Beklenen doğruluk: %90-95+
```

**Nasıl:**
1. Çeşitli kaynaklardan veri toplayın
2. Farklı arka planlar, aydınlatmalar
3. Farklı açılar ve uzaklıklar
4. Veri artırma ile 5-10x çoğaltın
5. Model eğitimi:
   ```bash
   python train_model.py --mode train --data_dir ./training_data --epochs 50 --batch_size 32
   ```

---

## 🖼️ Görüntü Gereksinimleri

### ✅ İDEAL Görüntü Özellikleri

```
✓ Format: JPG, JPEG, PNG
✓ Boyut: 500x500 - 2000x2000 piksel
✓ Dosya boyutu: 100KB - 5MB
✓ Arka plan: Tek renkli (beyaz/gri) veya düz
✓ Aydınlatma: İyi, gölgesiz
✓ Netlik: Keskin, bulanık değil
✓ Çeşitlilik: Farklı açılar, uzaklıklar, parça tipleri
```

### ❌ Kaçınılması Gerekenler

```
✗ Çok küçük görüntüler (<200x200 px)
✗ Karmaşık arka planlar
✗ Bulanık/bozuk görüntüler
✗ Çok fazla gölge
✗ Aşırı yakın/uzak çekimler
✗ Watermark/logo içeren görseller
✗ Aynı görüntünün kopyaları
```

---

## 🔍 Görüntü Bulma Kaynakları

### 1. Ücretsiz Stok Fotoğraf Siteleri
```
🌐 Unsplash.com       - Yüksek kaliteli, ücretsiz
🌐 Pexels.com         - Geniş koleksiyon
🌐 Pixabay.com        - Çeşitli içerik
🌐 Freepik.com        - Bazı ücretsiz görseller
```

### 2. Teknik/Endüstriyel Kaynaklar
```
🔧 McMaster-Carr      - Teknik parça fotoğrafları
🔧 Grainger.com       - Endüstriyel katalog
🔧 RS Components      - Elektronik parçalar
🔧 Alibaba            - Ürün görüntüleri
```

### 3. Veri Setleri
```
📊 ImageNet           - Genel nesneler
📊 Kaggle Datasets    - Makine öğrenmesi veri setleri
📊 Google Dataset Search - Arama motoru
```

### 4. Kendi Kaynaklarınız
```
📸 Telefon kamerası
📸 Workshop/atölye
📸 Arkadaşlardan ödünç
📸 Yerel donanım mağazası (izinle)
```

---

## 🛠️ Adım Adım: İlk 10 Görüntü Ekleyelim

### Örnek: Vida için görüntü toplama

```bash
# 1. Google Görseller'de ara
Arama terimleri:
- "M8 hex bolt"
- "machine screw"
- "threaded fastener"
- "vida makine parçası"

# 2. 10 görüntü indir
training_data/vida/vida_01.jpg
training_data/vida/vida_02.jpg
...
training_data/vida/vida_10.jpg

# 3. Kontrol et
ls training_data/vida/ | wc -l
# Çıktı: 10

# 4. Tüm parçalar için tekrarla
```

### Hızlı Test Script'i

Bir scriptle görüntü sayılarını kontrol edin:

```bash
# Görüntü sayılarını say
for dir in training_data/*/; do
    count=$(find "$dir" -type f \( -name "*.jpg" -o -name "*.png" \) | wc -l)
    echo "$(basename $dir): $count görüntü"
done
```

---

## 🤖 Veri Artırma (Data Augmentation)

Az görüntünüz varsa, veri artırma ile çoğaltabilirsiniz:

### Script Oluşturun: `augment_data.py`

```python
from PIL import Image
import os
from pathlib import Path

def augment_image(img_path, output_dir):
    """Bir görüntüyü çeşitli şekillerde dönüştür"""
    img = Image.open(img_path)
    base_name = Path(img_path).stem
    
    # 1. Orijinal
    img.save(f"{output_dir}/{base_name}_original.jpg")
    
    # 2. 90° döndürülmüş
    img.rotate(90).save(f"{output_dir}/{base_name}_rot90.jpg")
    
    # 3. 180° döndürülmüş
    img.rotate(180).save(f"{output_dir}/{base_name}_rot180.jpg")
    
    # 4. Yatay çevrilmiş
    img.transpose(Image.FLIP_LEFT_RIGHT).save(
        f"{output_dir}/{base_name}_flip.jpg"
    )
    
    # 5. Parlaklık artırılmış
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Brightness(img)
    enhancer.enhance(1.3).save(f"{output_dir}/{base_name}_bright.jpg")

# Kullanım
for parca_dir in Path('training_data').iterdir():
    if parca_dir.is_dir():
        for img in parca_dir.glob('*.jpg'):
            augment_image(img, parca_dir)
```

**Sonuç:** 10 görüntü → 50 görüntü (5x artış)

---

## 📈 Model Eğitimi

Görüntüleri ekledikten sonra:

### 1. Veri Miktarını Kontrol Edin
```bash
python test_system.py
```

### 2. Model Eğitin
```bash
# Küçük veri seti için (10-50 görüntü/sınıf)
python train_model.py --mode train --data_dir ./training_data --epochs 20

# Orta veri seti için (50-100 görüntü/sınıf)
python train_model.py --mode train --data_dir ./training_data --epochs 30 --batch_size 16

# Büyük veri seti için (100+ görüntü/sınıf)
python train_model.py --mode train --data_dir ./training_data --epochs 50 --batch_size 32
```

### 3. Model Test Edin
```bash
python train_model.py --mode test --model_path best_model.pth --image test_images/test_vida.jpg
```

### 4. Streamlit'te Kullanın
```bash
streamlit run app.py
# "Deep Learning" veya "Hibrit" modunu seçin
```

---

## ✅ Checklist: Başlamadan Önce

- [ ] `training_data/` klasörlerinin var olduğunu kontrol ettim
- [ ] Her parça için en az 10 görüntü hedefi belirledim
- [ ] Görüntü kaynaklarını araştırdım
- [ ] İlk parça için 5-10 görüntü indirdim
- [ ] Görüntülerin doğru klasöre gittiğini doğruladım
- [ ] `test_system.py` ile kontrol ettim
- [ ] Model eğitimi için hazırım

---

## 🎯 Hızlı Başlangıç Planı (ÖNERİLEN)

### Bugün (1-2 saat)
1. ✅ 3 parça seçin (vida, somun, rulman)
2. ✅ Her biri için 10 görüntü toplayın (Google'dan)
3. ✅ `training_data/` klasörlerine koyun
4. ✅ İlk eğitimi yapın (10 epoch)

### Bu Hafta
1. ✅ 6 parçaya çıkarın
2. ✅ Her biri için 30 görüntü
3. ✅ Veri artırma uygulayın
4. ✅ 30 epoch eğitim

### Bu Ay
1. ✅ Tüm 10 parça
2. ✅ Her biri için 100+ görüntü
3. ✅ Profesyonel model eğitimi
4. ✅ Gerçek dünya testleri

---

## 🆘 Sık Sorulan Sorular

### S: Kaç görüntü yeterli?
**C:** 
- Minimum: 10-20 (test için)
- İyi: 50-100 (kullanılabilir)
- Mükemmel: 200+ (profesyonel)

### S: Görüntüler birbirine çok mu benzemeli?
**C:** HAYIR! Çeşitlilik önemli:
- Farklı açılar
- Farklı arka planlar
- Farklı aydınlatma
- Farklı parça tipleri (M6, M8, M10 vidalar)

### S: Renkli mi gri tonlamalı mı?
**C:** Renkli (RGB) tercih edin. Sistem otomatik dönüştürür.

### S: Boyut önemli mi?
**C:** 500x500 ile 2000x2000 arası ideal. Çok küçük veya çok büyük resimlerden kaçının.

### S: İnternetten aldığım görüntüleri kullanabilir miyim?
**C:** Evet, ancak:
- Telif hakkına dikkat edin
- Ticari kullanım için lisans kontrol edin
- Eğitim/araştırma için genelde sorun olmaz

---

## 📞 Yardım

Sorun yaşarsanız:

```bash
# Görüntü sayısını kontrol
python test_system.py

# Görüntü formatını kontrol
file training_data/vida/*.jpg

# Klasör yapısını kontrol
tree training_data/
```

---

**🎉 İYİ ŞANSLAR!** İlk 10 görüntü ile başlayın, sistem çalışmaya başladığında daha fazla eklersiniz!
