# 🎯 Web'de YOLO Model ile Görüntü Testi

## Hızlı Başlangıç

### 1. Web Uygulamasını Başlat

```bash
./web_test.sh
```

veya

```bash
streamlit run app.py
```

Tarayıcınızda otomatik açılacak: `http://localhost:8501`

---

## 📸 Yüklediğiniz Fotoğrafı Test Etme

### Adım 1: Ana Sayfaya Git
- Sol menüden **"🏠 Ana Sayfa - Parça Tanıma"** seçin

### Adım 2: YOLO Modelini Seç

Sol kenar çubuğunda:
1. **YOLO Model Yolu** alanını kontrol edin
   - Varsayılan: `runs/detect/train/weights/best.pt`
   - Farklı bir model varsa yolunu girin

2. Model bulunursa **"✅ YOLO modeli bulundu!"** mesajını göreceksiniz

3. **Tanıma Yöntemi** dropdown'ından seçin:
   - **"🎯 YOLO (Eğitilmiş Model)"** ← Bu seçeneği seçin!

### Adım 3: Fotoğraf Yükle

Ana ekranda:
1. **"Browse files"** butonuna tıklayın
2. Bilgisayarınızdan bir makine parçası fotoğrafı seçin
   - Desteklenen formatlar: JPG, JPEG, PNG

### Adım 4: Analiz Et

1. Fotoğraf yüklendikten sonra **"🔍 Analiz Et"** butonuna tıklayın
2. Sistem birkaç saniye içinde analiz edecek

### Adım 5: Sonuçları İncele

Sağ tarafta görecekleriniz:

#### 🎯 YOLO Tespit Sonucu
- **Bounding box'larla işaretlenmiş görüntü**
- Her tespit edilen nesne üzerinde:
  - Sınıf adı (İngilizce: Bearing, Bolt, Gear, Nut)
  - Güven skoru (örn: 0.87)
  - Renkli dikdörtgen çerçeve

#### 🔍 Tespit Edilen Nesneler Listesi
Her tespit için:
- **Sınıf adı** (İngilizce)
- **Türkçe karşılığı** (Rulman, Vida, Dişli, Somun)
- **Güven skoru** (yüzde olarak)

#### 📊 Detaylı Bilgiler
- **Tespit Edilen Parça:** En yüksek güvenli tespit
- **Güven Skoru:** %0-100 arası
  - 🟢 %70+ → Mükemmel
  - 🟡 %50-70 → İyi
  - 🔴 %50↓ → Düşük güven

#### 📝 Parça Bilgileri
- Tanım ve açıklama
- Kullanım alanları
- Teknik özellikler
- Çeşitleri

---

## 💡 Örnek Kullanım Senaryosu

### Senaryo: Rulman Tespiti

1. ✅ Web uygulamasını başlat
2. ✅ Sol menüden YOLO seç
3. ✅ Rulman fotoğrafı yükle
4. ✅ "Analiz Et" tıkla

**Beklenen Sonuç:**
```
🎯 YOLO Tespit Sonucu
┌─────────────────────────────┐
│  [Bearing 0.92]             │
│     ┌──────────┐            │
│     │  Rulman  │            │
│     └──────────┘            │
└─────────────────────────────┘

🔍 Tespit Edilen Tüm Nesneler:
1. Bearing  →  Rulman  🎯 %92.3

✅ Tespit Edilen Parça: Rulman
🟢 %92.3 Güven

📝 Tanım:
Dönen parçaların sürtünmesini azaltan bilyalı veya 
makaralı yataklama elemanı...
```

---

## 🎨 Görsel Özellikler

### Bounding Box Renkleri
YOLO otomatik olarak her sınıf için farklı renk atar:
- Bearing (Rulman) → Genellikle mavi/yeşil
- Bolt (Vida) → Genellikle kırmızı/turuncu
- Gear (Dişli) → Genellikle sarı/pembe
- Nut (Somun) → Genellikle mor/cyan

### Etiket Formatı
Her tespit üzerinde:
```
Sınıf_Adı Güven_Skoru
   ┌──────────┐
   │          │  ← Bounding box
   └──────────┘
```

---

## 🔧 Ayarlar ve Özelleştirme

### Model Yolunu Değiştirme

Sol kenar çubuğunda:
```
YOLO Model Yolu:
[runs/detect/train/weights/best.pt]
```

Farklı bir model kullanmak için:
```
# Örnek alternatif yollar
runs/detect/train2/weights/best.pt
models/yolo_v8n.pt
/tam/yol/model.pt
```

### Güven Eşiği

YOLO varsayılan olarak **%25** güven eşiği kullanır.
- %25'ten düşük tespitler gösterilmez
- Daha yüksek eşik için kodu değiştirin (yolo_tahmin fonksiyonu, conf parametresi)

---

## 📊 Çoklu Nesne Tespiti

Bir fotoğrafta birden fazla parça varsa:

**Örnek:** 2 vida, 1 somun içeren görüntü

```
🎯 YOLO Tespit Sonucu
┌─────────────────────────────┐
│  [Bolt 0.89]  [Bolt 0.85]   │
│                              │
│         [Nut 0.91]           │
└─────────────────────────────┘

🔍 Tespit Edilen Tüm Nesneler:
1. Nut   →  Somun  🎯 %91.2  ← En yüksek güven
2. Bolt  →  Vida   🎯 %89.3
3. Bolt  →  Vida   🎯 %85.1

✅ Tespit Edilen Parça: Somun
(En yüksek güvenli tespit seçilir)
```

---

## ❓ Sık Sorulan Sorular

### S: Model bulunamadı hatası alıyorum?
**C:** 
```bash
# Önce modeli eğitin
python train_yolo_model.py --mode train --epochs 50 --batch 8

# Veya doğru yolu girin
ls runs/detect/train/weights/best.pt
```

### S: Hiçbir nesne tespit edilmedi?
**C:**
- Fotoğraf kalitesini kontrol edin (bulanık değil mi?)
- Parça görüntüde net görünüyor mu?
- Model bu sınıfı öğrendi mi? (test/val sonuçlarını kontrol edin)
- Güven eşiği çok yüksek olabilir

### S: Yanlış tespit yapıyor?
**C:**
- Modelin doğruluğunu kontrol edin: "📊 Model Performans Testi"
- Daha fazla eğitim verisi ekleyin
- Daha uzun süre eğitin (daha fazla epoch)
- Benzer sınıflar karışıyor olabilir (vida-somun gibi)

### S: Tespit çok yavaş?
**C:**
- GPU kullanıyor musunuz? CPU'da daha yavaş
- Görüntü boyutu çok mu büyük? (resize otomatik yapılır ama yine de)
- Model boyutu: YOLOv8n en hızlı, YOLOv8x en yavaş ama en doğru

### S: Güven skoru neden düşük (%50-60)?
**C:**
- Model daha fazla eğitime ihtiyaç duyabilir
- Test görüntüsü eğitim setinden çok farklı olabilir
- Aydınlatma, açı, arka plan farklılıkları
- Veri artırma (augmentation) uygulayın

---

## 🚀 Performans İpuçları

### Hızlı Tespit İçin
1. **YOLOv8n** kullanın (en hafif model)
2. **GPU** kullanın (CUDA)
3. Görüntüleri **800x800** altında tutun

### Yüksek Doğruluk İçin
1. **YOLOv8m veya YOLOv8l** kullanın
2. **Daha uzun eğitim** (100+ epoch)
3. **Daha fazla veri** toplayın
4. **Veri artırma** uygulayın

---

## 🎯 Sonuç Yorumlama

| Güven Skoru | Anlamı | Öneri |
|-------------|--------|-------|
| **%90+** | 🎯 Çok Yüksek | Güvenle kullanılabilir |
| **%80-90** | ✅ Yüksek | İyi tespit, kullanılabilir |
| **%70-80** | 👍 İyi | Kabul edilebilir |
| **%60-70** | ⚠️ Orta | Dikkatli kullanın |
| **%50-60** | ⚠️ Düşük | Manuel kontrol gerekli |
| **%50↓** | ❌ Çok Düşük | Güvenilmez |

---

## 📝 Karşılaştırma: YOLO vs Diğer Yöntemler

| Özellik | YOLO | Kural Tabanlı | Hibrit |
|---------|------|---------------|--------|
| **Hız** | Hızlı (~1s) | Çok Hızlı (<0.1s) | Orta (~2s) |
| **Doğruluk** | Çok Yüksek | Düşük | Yüksek |
| **Çoklu Nesne** | ✅ Evet | ❌ Hayır | ⚠️ Sınırlı |
| **Eğitim Gerekli** | ✅ Evet | ❌ Hayır | ✅ Evet |
| **GPU Gerekli** | İsteğe bağlı | Hayır | İsteğe bağlı |

**Öneri:** Eğitilmiş modeliniz varsa **YOLO** kullanın!

---

## 🔄 Alternatif Kullanım

### Komut Satırından Test
```bash
# Tek görüntü
python train_yolo_model.py --mode predict --source foto.jpg

# Klasör
python train_yolo_model.py --mode predict --source test/images/

# Webcam
python train_yolo_model.py --mode predict --source 0
```

### Python Scripti
```python
from ultralytics import YOLO

# Model yükle
model = YOLO('runs/detect/train/weights/best.pt')

# Tahmin yap
results = model.predict('foto.jpg', conf=0.25)

# Sonuçları göster
results[0].show()
```

---

## 📚 Ek Kaynaklar

- **Model Eğitimi:** `YOLO_EGITIM_REHBERI.md`
- **Performans Testi:** `WEB_DOGRULUK_TESTI.md`
- **GPU Sorunları:** `GPU_BELLEK_COZUM.md`
- **Genel Bilgi:** `README.md`

---

**Kolay gelsin! 🚀 İyi testler!**

## 🎓 Video Rehber (Adım Adım)

1. **Web'i aç** → `./web_test.sh`
2. **YOLO seç** → Dropdown'dan "🎯 YOLO"
3. **Foto yükle** → Browse files
4. **Analiz et** → Tek tık
5. **Sonuçları gör** → Bounding box + bilgiler

**Bu kadar! 3 dakikada test edebilirsiniz!** ✨
