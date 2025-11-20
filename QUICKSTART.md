# 🚀 Hızlı Başlangıç Kılavuzu

Sisteminizi 3 adımda çalıştırın!

## Adım 1: Klasörleri Oluştur

```bash
chmod +x setup_folders.sh
./setup_folders.sh
```

veya manuel:
```bash
mkdir -p referans_gorseller/{vida,somun,rulman,kayis,disli,piston}
mkdir -p test_images
mkdir -p training_data/{vida,somun,rulman}
```

## Adım 2: Referans Görüntüler Ekle

Her parça için **5-10 örnek görüntü** ekleyin:

```
referans_gorseller/
├── vida/
│   ├── vida1.jpg
│   ├── vida2.jpg
│   └── vida3.jpg
├── somun/
│   ├── somun1.jpg
│   └── somun2.jpg
└── ...
```

💡 **Nereden bulabilirsiniz?**
- Google Görseller
- Telefon kameranız ile çekin
- Online parça katalogları
- 3D modelleme yazılımından screenshot

## Adım 3: Sistemi Kullanın

### A) Web Arayüzü (En Kolay)

```bash
streamlit run app.py
```

Tarayıcıda açılan arayüzde:
1. Görüntü yükleyin
2. Yöntemi seçin: **"Hibrit (Otomatik)"**
3. Analiz Et'e tıklayın

### B) Komut Satırı (Feature Matching)

```python
from feature_matcher import FeatureMatchingTanima

# Sistem başlat
matcher = FeatureMatchingTanima('./referans_gorseller')

# Test et
sonuclar = matcher.tanima_yap('./test_images/test_vida.jpg')

# Sonuçları göster
for i, sonuc in enumerate(sonuclar[:3], 1):
    print(f"{i}. {sonuc['parca_adi']} - Skor: {sonuc['skor']:.3f}")
```

### C) Hibrit Sistem (En İyi Sonuç)

```python
from hybrid_detector import HibritTanima

# Sistem başlat
sistem = HibritTanima(
    referans_klasor='./referans_gorseller',
    mod='auto'
)

# Test et
sonuc = sistem.tanima_yap('./test_images/test_vida.jpg')

print(f"Parça: {sonuc['parca']}")
print(f"Güven: {sonuc['guven']:.2%}")
print(f"Yöntem: {sonuc['method']}")
```

## İleri Seviye: Model Eğitimi

Daha yüksek doğruluk için kendi modelinizi eğitin:

### 1. Veri Toplama

Her parça için **100+ görüntü** toplayın:

```
training_data/
├── vida/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   ├── ... (100+ görüntü)
├── somun/
│   ├── img_001.jpg
│   └── ... (100+ görüntü)
```

### 2. Model Eğitimi

```bash
python train_model.py \
    --mode train \
    --data_dir ./training_data \
    --epochs 25 \
    --batch_size 32 \
    --lr 0.001
```

Eğitim tamamlandığında `best_model.pth` dosyası oluşacak.

### 3. Model Test

```bash
python train_model.py \
    --mode test \
    --model_path best_model.pth \
    --test_image ./test_images/vida1.jpg
```

### 4. Hibrit Sistemde Kullan

Model eğitildikten sonra hibrit sistem otomatik olarak kullanacak:

```python
sistem = HibritTanima(
    model_path='best_model.pth',           # ✅ DL model
    referans_klasor='./referans_gorseller', # ✅ Feature matching
    mod='auto'                              # ✅ Akıllı mod
)
```

## 🎯 Hangi Yöntemi Kullanmalıyım?

| Durum | Önerilen Yöntem | Komut |
|-------|----------------|-------|
| Hızlı prototip | Feature Matching | `mod='feature_only'` |
| Az veri var (< 50/sınıf) | Feature Matching | `mod='feature_only'` |
| Çok veri var (100+/sınıf) | Deep Learning | `mod='dl_only'` |
| Production ortam | Hibrit Auto | `mod='auto'` |
| Kritik uygulama | Ensemble | `mod='ensemble'` |

## 📊 Performans Beklentileri

### Feature Matching
- ⚡ Hız: ~50ms
- 📊 Doğruluk: %60-75
- 💾 Veri: 5-10/sınıf
- 🎓 Eğitim: Yok

### Deep Learning
- ⚡ Hız: ~100ms
- 📊 Doğruluk: %85-98
- 💾 Veri: 100+/sınıf
- 🎓 Eğitim: 2-10 saat

### Hibrit (Auto)
- ⚡ Hız: ~120ms
- 📊 Doğruluk: %90-99
- 💾 Veri: 50+/sınıf
- 🎓 Eğitim: 2-10 saat

## 🔧 Sorun Giderme

### "Referans veritabanı boş"
```bash
# Referans görüntüler eklediniz mi?
ls -la referans_gorseller/vida/

# En az 1 görüntü olmalı!
```

### "DL model yüklenemedi"
```bash
# Model eğittiniz mi?
ls -la best_model.pth

# Eğitmediyseniz feature_only modunu kullanın
```

### "Düşük doğruluk"
1. Daha fazla referans görüntü ekleyin
2. Farklı açılardan çekin
3. İyi aydınlatma kullanın
4. Arka planı temiz tutun

## 💡 İpuçları

1. **Kaliteli Görüntüler**: Net, iyi aydınlatılmış görüntüler kullanın
2. **Farklı Açılar**: Her parça için farklı açılardan çekin
3. **Temiz Arka Plan**: Mümkünse beyaz/gri arka plan kullanın
4. **Tutarlı Boyut**: Benzer boyutlarda görüntüler daha iyi sonuç verir
5. **Veri Augmentation**: Az veriniz varsa augmentation kullanın

## 📞 Yardım

Sorun yaşarsanız:
1. `YONTEM_KARSILASTIRMA.md` dosyasını okuyun
2. `EXAMPLES.md` dosyasındaki örneklere bakın
3. Hata mesajlarını dikkatlice okuyun
4. GitHub Issues'da sorun açın

---

**Başarılar! 🎉**
