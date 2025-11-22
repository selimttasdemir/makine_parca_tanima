# Web Uygulamasında Model Doğruluk Testi

## 🎯 Genel Bakış

Web uygulamanıza model performans testi sayfası eklendi. Bu sayfa sayesinde eğitilmiş modelinizin test seti üzerindeki doğruluğunu kolayca ölçebilirsiniz.

## 🚀 Hızlı Başlangıç

### 1. Web Uygulamasını Başlatma

**Otomatik (Önerilen):**
```bash
./web_test.sh
```

**Manuel:**
```bash
streamlit run app.py
```

Uygulama otomatik olarak tarayıcınızda açılacak: `http://localhost:8501`

### 2. Model Performans Testi Yapma

1. **Sol menüden** "📊 Model Performans Testi" seçeneğini tıklayın

2. **Model ayarlarını yapın:**
   - Model dosyası yolu: `runs/detect/train/weights/best.pt` (varsayılan)
   - Test edilecek görüntü sayısı: `50` (0 = hepsi)
   - Test klasörü: `test` (varsayılan)

3. **"🧪 Testi Başlat"** butonuna tıklayın

4. **Sonuçları inceleyin:**
   - Genel doğruluk oranı
   - Sınıf bazında performans
   - Yanlış tahmin örnekleri

## 📊 Sonuçlar

### Test Sonucu Metrikleri

Web arayüzünde göreceğiniz metrikler:

#### 1. Genel Metrikler
- **Genel Doğruluk**: Toplam doğru tahmin yüzdesi
- **Doğru Tahmin**: Kaç nesne doğru tahmin edildi
- **Yanlış Tahmin**: Kaç nesne yanlış tahmin edildi

#### 2. Sınıf Bazında Performans
Her sınıf için ayrı ayrı:
- Doğruluk oranı (%)
- Doğru tahmin sayısı
- Yanlış tahmin sayısı
- Toplam nesne sayısı

#### 3. Yanlış Tahmin Analizi
Hangi görüntülerde hatalar yapıldığını görün:
- Görüntü adı
- Gerçek sınıf
- Tahmin edilen sınıf
- Güven skoru

### Sonuçları Kaydetme

Web arayüzünden:
1. **"💾 Sonuçları Kaydet (JSON)"** butonuna tıklayın
2. **"📥 JSON Dosyasını İndir"** ile bilgisayarınıza indirin

JSON dosyası şunları içerir:
- Detaylı test sonuçları
- Tüm tahminler ve doğruluk skorları
- Sınıf bazında istatistikler

## 💻 Komut Satırı Testi (Alternatif)

Web arayüzü yerine terminal üzerinden test etmek isterseniz:

### Tam Test (Tüm Test Seti)
```bash
python test_dogruluk.py --model runs/detect/train/weights/best.pt
```

### Hızlı Test (İlk 50 Görüntü)
```bash
python test_dogruluk.py --model runs/detect/train/weights/best.pt --limit 50
```

### Özel Ayarlarla Test
```bash
python test_dogruluk.py \
    --model runs/detect/train/weights/best.pt \
    --test test \
    --limit 100 \
    --save sonuclarim.json
```

### Parametreler

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `--model` | Model dosyası yolu | `runs/detect/train/weights/best.pt` |
| `--test` | Test klasörü yolu | `test` |
| `--limit` | Maksimum test görüntüsü | `None` (hepsi) |
| `--save` | Sonuç kayıt dosyası | `test_sonuclari.json` |

## 📈 Örnek Çıktı

### Terminal Çıktısı
```
🔍 Model Doğruluk Testi Başlatılıyor...
Model: runs/detect/train/weights/best.pt
Test Klasörü: test

📊 Test Seti Analizi:
  Toplam Görüntü: 225
  Toplam Nesne: 1100
  Ortalama Nesne/Görüntü: 4.89

  Sınıf Dağılımı:
    - Bearing: 275
    - Bolt: 312
    - Gear: 289
    - Nut: 224

📦 Model Yükleniyor: runs/detect/train/weights/best.pt

🧪 Test Ediliyor...

============================================================
📈 TEST SONUÇLARI
============================================================

✅ Genel Doğruluk: %87.45
   Doğru: 962/1100
   Yanlış: 138/1100
   Test Edilen Görüntü: 225

📊 Sınıf Bazında Doğruluk:
   Bearing     : %91.27 (251/275 doğru)
   Gear        : %88.93 (257/289 doğru)
   Bolt        : %86.22 (269/312 doğru)
   Nut         : %82.59 (185/224 doğru)

❌ Yanlış Tahmin Örnekleri (İlk 5):
   1. 252_jpg.rf.2860da11dfb0f41fb0012f7f49dbe4f4.jpg
      Gerçek: Nut | Tahmin: Bolt (Güven: %73.2)
   2. 288_jpg.rf.2789171d3932854442bdfc457b106853.jpg
      Gerçek: Gear | Tahmin: Bearing (Güven: %68.5)
   ...

💾 Detaylı sonuçlar kaydedildi: test_sonuclari.json
```

### Web Arayüzü Görünümü

Web arayüzünde görecekleriniz:

1. **Test Seti Bilgileri Kartı**
   - 3 metrik kutucuğu (Toplam Görüntü, Nesne, Ortalama)
   - Sınıf dağılımı bar grafiği

2. **Test Sonuçları Kartı**
   - Genel doğruluk (büyük, renkli)
   - Doğru/Yanlış tahmin sayıları
   - Sınıf bazında doğruluk tablosu
   - İnteraktif bar grafiği

3. **Yanlış Tahminler Tablosu**
   - Filtrelenebilir
   - Sıralanabilir
   - İndirillebilir

## 🎯 Doğruluk Skorlarını Yorumlama

### Genel Doğruluk Seviyeleri

| Doğruluk | Değerlendirme | Öneriler |
|----------|---------------|----------|
| **90%+** | 🎯 Mükemmel | Model üretime hazır |
| **75-90%** | ✅ İyi | Kullanılabilir, iyileştirilebilir |
| **60-75%** | ⚠️ Orta | Daha fazla eğitim gerekli |
| **<60%** | ❌ Zayıf | Model/veri gözden geçirilmeli |

### Sınıf Bazında Analiz

Eğer bir sınıf diğerlerinden düşük performans gösteriyorsa:

**Olası Nedenler:**
- ❌ O sınıftan yeterli eğitim verisi yok
- ❌ Görüntü kalitesi düşük
- ❌ Diğer sınıflarla çok benzer (karışıklık)
- ❌ Etiketleme hataları

**Çözüm Önerileri:**
1. O sınıftan daha fazla veri toplayın
2. Veri artırma (augmentation) uygulayın
3. Etiketleri gözden geçirin
4. Benzer sınıfları ayırt etmek için modeli daha uzun eğitin

## 🔧 Sorun Giderme

### Model Dosyası Bulunamadı
```
⚠️ Model dosyası bulunamadı: runs/detect/train/weights/best.pt
```

**Çözüm:**
```bash
# Önce modeli eğitin
python train_yolo_model.py --mode train --epochs 50 --batch 8

# Veya farklı bir model yolu belirtin
```

### Test Klasörü Boş
```
❌ Test klasörü bulunamadı veya boş
```

**Çözüm:**
Test klasörünün şu yapıda olduğundan emin olun:
```
test/
  images/          # Test görüntüleri
  labels/          # Test etiketleri (.txt)
```

### Ultralytics Bulunamadı
```
❌ Ultralytics kütüphanesi bulunamadı!
```

**Çözüm:**
```bash
pip install ultralytics
```

### Streamlit Bulunamadı
```
❌ streamlit: command not found
```

**Çözüm:**
```bash
pip install streamlit
```

## 📝 İpuçları

### Hızlı Test
- İlk deneme için `limit=50` kullanın (5-10 saniye)
- Tam test için `limit=0` veya boş bırakın (1-2 dakika)

### Detaylı Analiz
- Yanlış tahminleri inceleyin
- Hangi sınıfların karıştırıldığını görün
- JSON dosyasını indirerek Excel'de analiz edin

### Karşılaştırma
- Her eğitim sonrası test sonuçlarını kaydedin
- Farklı modelleri karşılaştırın:
  ```bash
  # Model 1
  python test_dogruluk.py --model runs/detect/train1/weights/best.pt --save model1_test.json
  
  # Model 2
  python test_dogruluk.py --model runs/detect/train2/weights/best.pt --save model2_test.json
  ```

### Performans İyileştirme
1. **Veri Artırma**: Daha fazla çeşitlilik
2. **Uzun Eğitim**: Daha fazla epoch
3. **Daha Büyük Model**: YOLOv8n yerine YOLOv8m
4. **Veri Temizleme**: Hatalı etiketleri düzeltin

## 🌐 Web vs Terminal

| Özellik | Web Arayüzü | Terminal |
|---------|-------------|----------|
| **Kullanım** | Görsel, kolay | Kod tabanlı |
| **Hız** | Orta | Hızlı |
| **Grafikler** | İnteraktif | Yok |
| **Sonuç İndirme** | Kolay | JSON dosyası |
| **Toplu Test** | Sınırlı | Esnek |
| **Otomasyon** | Hayır | Evet (script) |

**Öneri:** İlk kez test yapıyorsanız web arayüzünü kullanın. Toplu testler veya otomasyon için terminal kullanın.

## 📚 Ek Kaynaklar

### İlgili Dosyalar
- `app.py` - Ana web uygulaması
- `test_dogruluk.py` - Test scripti
- `train_yolo_model.py` - Model eğitimi
- `web_test.sh` - Web başlatma scripti

### Dokümantasyon
- `YOLO_EGITIM_REHBERI.md` - Eğitim rehberi
- `GPU_BELLEK_COZUM.md` - GPU sorunları
- `README.md` - Genel proje bilgisi

---

## ❓ Sık Sorulan Sorular

**S: Test süresi ne kadar?**
A: 50 görüntü için ~30 saniye, 225 görüntü için ~2 dakika (GPU ile daha hızlı)

**S: Minimum kaç görüntü test etmeliyim?**
A: En az 50, güvenilir sonuç için tüm test seti (225)

**S: Hangi metriklere bakmalıyım?**
A: İlk olarak genel doğruluğa, sonra sınıf bazında dengesiz performans var mı kontrol edin

**S: %100 doğruluk normal mi?**
A: Hayır, genellikle overfitting işareti. %85-95 arası ideal.

**S: Test sonuçlarını Excel'de açabilir miyim?**
A: Evet, JSON dosyasını indirip Excel'de JSON import edin veya pandas ile CSV'ye çevirin.

---

**Kolay gelsin! 🚀**
