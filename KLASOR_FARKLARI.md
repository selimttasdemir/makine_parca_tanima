# 📂 Training Data vs Referans Görseller - Fark Nedir?

## 🤔 Sorunuz

> "train data kısmına ne eklemem gerekiyor boş klasörler var sanırım oraya ilgili klasör adına uygun görseller ekleyeceğim doğru mu"

**CEVAP:** ✅ Evet, kesinlikle doğru! Ama iki farklı klasör var ve farklı amaçları var.

---

## 📁 İKİ FARKLI KLASÖR

### 1️⃣ `referans_gorseller/` (Feature Matching için)

```
referans_gorseller/
├── vida/      ← 5-10 görüntü yeterli
├── somun/     ← 5-10 görüntü yeterli
├── rulman/    ← 5-10 görüntü yeterli
└── ...
```

**Amaç:** SIFT, Histogram, Hu Moments ile benzerlik karşılaştırması

**Nasıl Çalışır:**
- Test görüntüsü gelir
- Referans görüntülerle karşılaştırılır
- En benzer olanı bulur
- ❌ Eğitim yapmaz, sadece karşılaştırır

**Avantajlar:**
- ✅ Hızlı (eğitim gerekmez)
- ✅ Az veri yeterli (5-10 görüntü/parça)
- ✅ Anında kullanılabilir

**Dezavantajlar:**
- ❌ Düşük doğruluk (%60-75)
- ❌ Farklı açılardan zorlanır

---

### 2️⃣ `training_data/` (Deep Learning için)

```
training_data/
├── vida/      ← 100-200 görüntü ideal
├── somun/     ← 100-200 görüntü ideal
├── rulman/    ← 100-200 görüntü ideal
└── ...
```

**Amaç:** ResNet50 neural network'ünü eğitmek

**Nasıl Çalışır:**
- Görüntüleri öğrenir
- Kalıpları/özellikleri çıkarır
- Model oluşturur (best_model.pth)
- Bu modeli kullanarak tahmin yapar

**Avantajlar:**
- ✅ Yüksek doğruluk (%85-95)
- ✅ Farklı açılardan tanır
- ✅ Genelleme yapabilir

**Dezavantajlar:**
- ❌ Çok veri gerekir (100+ görüntü/parça)
- ❌ Eğitim süresi (2-10 saat)
- ❌ GPU tercih edilir

---

## 🆚 YAN YANA KARŞILAŞTIRMA

| Özellik | referans_gorseller/ | training_data/ |
|---------|---------------------|----------------|
| **Amaç** | Benzerlik karşılaştırma | Model eğitimi |
| **Yöntem** | Feature Matching | Deep Learning |
| **Veri miktarı** | 5-10 görüntü/parça | 100-200 görüntü/parça |
| **Eğitim** | Gerekmiyor | Gerekli (2-10 saat) |
| **Doğruluk** | %60-75 | %85-95 |
| **Hız** | Çok hızlı (50ms) | Hızlı (100ms) |
| **Kullanım** | Hızlı prototip | Üretim sistemi |

---

## 🎯 HANGİSİNİ KULLANMALISINIZ?

### Senaryo 1: Hızlı Test İstiyorum (1 saat)
**Kullanın:** `referans_gorseller/`

```bash
# Her parça için 5-10 görüntü ekleyin
referans_gorseller/vida/vida_01.jpg ... vida_10.jpg

# Test edin
streamlit run app.py
# "Feature Matching" seçin
```

### Senaryo 2: Gerçek Proje (1 hafta-1 ay)
**Kullanın:** `training_data/`

```bash
# Her parça için 50-200 görüntü ekleyin
training_data/vida/vida_001.jpg ... vida_200.jpg

# Model eğitin
python train_model.py --mode train --data_dir ./training_data --epochs 30

# Test edin
streamlit run app.py
# "Deep Learning" seçin
```

### Senaryo 3: En İyi Sonuç (ÖNERİLEN)
**Kullanın:** **İKİSİNİ BİRLİKTE** (Hibrit)

```bash
# 1. Hızlı başlangıç için referans ekleyin
referans_gorseller/*/  # 10 görüntü/parça

# 2. Zamanla training data artırın
training_data/*/       # 100+ görüntü/parça

# 3. Hibrit modu kullanın
streamlit run app.py
# "Hibrit (Otomatik)" seçin
```

**Sonuç:** %90-99 doğruluk! 🎉

---

## 📊 NASIL DOLDURULUR?

### ADIM 1: Boş Durumu Kontrol Edin

```bash
python check_training_data.py
```

**Çıktı:**
```
training_data/vida:    0 görüntü  ❌ BOŞ
training_data/somun:   0 görüntü  ❌ BOŞ
...
```

### ADIM 2: Görüntü Toplamaya Başlayın

#### Yöntem A: Manuel İndirme (ÖNERİLEN)

```
1. Google → "hex bolt" ara
2. Görseller sekmesi
3. Sağ tık → "Resmi farklı kaydet"
4. training_data/vida/ klasörüne kaydet
5. 10-20 kez tekrarla
```

#### Yöntem B: Hızlı Başlangıç Scripti

```bash
./baslangic_rehberi.sh
```

Bu script size adım adım ne yapacağınızı gösterecek.

#### Yöntem C: Telefon Kamerası

```
1. Beyaz kağıt üzerine parçayı koyun
2. İyi ışıkta fotoğraf çekin (5-10 farklı açı)
3. Bilgisayara aktarın
4. training_data/[parca]/ klasörüne kopyalayın
```

### ADIM 3: Tekrar Kontrol Edin

```bash
python check_training_data.py
```

**Çıktı:**
```
training_data/vida:    10 görüntü  🟡 YETERSIZ (50+ öneririz)
training_data/somun:   10 görüntü  🟡 YETERSIZ
training_data/rulman:  10 görüntü  🟡 YETERSIZ
TOPLAM: 30 görüntü
```

### ADIM 4: Model Eğitimi

```bash
# İlk test (10-20 görüntü/parça varsa)
python train_model.py --mode train --data_dir ./training_data --epochs 10

# Sonuç: best_model.pth dosyası oluşur
```

### ADIM 5: Streamlit'te Test

```bash
streamlit run app.py
```

1. "Deep Learning" seçin
2. Görüntü yükleyin
3. "Analiz Et" butonuna basın

---

## 📈 AŞAMALI YAKLAŞIM

### Hafta 1: Hızlı Test (10 görüntü/parça)
```
Hedef: Sistemin çalıştığını görmek
```
- Google'dan 3 parça x 10 görüntü = 30 toplam
- 10 epoch eğitim
- Doğruluk: ~%70

### Hafta 2-3: Kullanılabilir Sistem (50 görüntü/parça)
```
Hedef: Gerçek kullanım için hazırlamak
```
- 10 parça x 50 görüntü = 500 toplam
- 30 epoch eğitim
- Doğruluk: ~%80-85

### Ay 1: Profesyonel Sistem (100+ görüntü/parça)
```
Hedef: Üretim kalitesi
```
- 10 parça x 100-200 görüntü = 1000-2000 toplam
- 50 epoch eğitim
- Veri artırma uygula
- Doğruluk: ~%90-95

---

## 🎯 HIZLI BAŞLANGIÇ ÖNERİSİ

**15 dakikada başlayın:**

```bash
# 1. Script çalıştır (yol gösterir)
./baslangic_rehberi.sh

# 2. Veya manuel:
# Google'dan vida, somun, rulman için 10'ar görüntü indir
# training_data/ klasörlerine at

# 3. Kontrol
python check_training_data.py

# 4. Eğit
python train_model.py --mode train --data_dir ./training_data --epochs 10

# 5. Test
streamlit run app.py
```

---

## 📚 Ek Kaynaklar

- **Hızlı başlangıç:** `15_DAKIKA_HIZLI_BASLANGIC.md`
- **Detaylı rehber:** `TRAINING_DATA_REHBER.md`
- **Veri yol haritası:** `VERİ_TOPLAMA_YOL_HARİTASI.md`
- **Durum kontrolü:** `python check_training_data.py`
- **Interaktif rehber:** `./baslangic_rehberi.sh`

---

## ❓ SSS

### S: Hangi formatta olmalı?
**C:** JPG, JPEG veya PNG. Tercihen JPG.

### S: Boyut ne olmalı?
**C:** 500x500 ile 2000x2000 piksel arası ideal.

### S: Aynı görüntüyü her iki klasöre de koymalı mıyım?
**C:** Hayır, gerek yok. İsterseniz:
- `referans_gorseller/`: En iyi 5-10 görüntü
- `training_data/`: Tüm görüntüler (100+)

### S: İki klasöre de veri eklersem ne olur?
**C:** Hibrit sistem her ikisini de kullanır, daha iyi sonuç verir!

### S: Önce hangisini doldurmalıyım?
**C:** 
1. **Hızlı test için:** `referans_gorseller/` (5-10 görüntü)
2. **Gerçek proje için:** `training_data/` (100+ görüntü)
3. **En iyi sonuç için:** İkisi birden

---

**✅ ÖZET:** Evet, `training_data/` klasörlerini doldurmanız gerekiyor. Her parça klasörüne en az 10-20 (ideal: 100+) görüntü ekleyin!

**🚀 Başarılar!**
