# ⚡ HIZLI BAŞLANGIÇ - 15 Dakikada İlk Model

## 🎯 Hedef
15-20 dakikada ilk 30 görüntü ile sistemi çalıştırabilir hale getirin.

---

## 📝 Adım Adım (3 Parça x 10 Görüntü = 30 Toplam)

### 1️⃣ VIDA (5 dakika)

**Google'da ara:**
```
hex bolt
```

**Yapılacaklar:**
1. Google Görseller'e girin
2. "hex bolt" yazın ve ara
3. 10 görüntüye sağ tık → "Resmi farklı kaydet"
4. Kayıt yeri: `training_data/vida/`
5. İsimler: `vida_01.jpg`, `vida_02.jpg`, ... `vida_10.jpg`

✅ **10 vida görüntüsü indirildi!**

---

### 2️⃣ SOMUN (5 dakika)

**Google'da ara:**
```
hex nut
```

**Yapılacaklar:**
1. "hex nut" ara
2. 10 görüntü indir
3. Kayıt yeri: `training_data/somun/`
4. İsimler: `somun_01.jpg`, `somun_02.jpg`, ... `somun_10.jpg`

✅ **10 somun görüntüsü indirildi!**

---

### 3️⃣ RULMAN (5 dakika)

**Google'da ara:**
```
ball bearing
```

**Yapılacaklar:**
1. "ball bearing" ara
2. 10 görüntü indir
3. Kayıt yeri: `training_data/rulman/`
4. İsimler: `rulman_01.jpg`, `rulman_02.jpg`, ... `rulman_10.jpg`

✅ **10 rulman görüntüsü indirildi!**

---

## ✅ Kontrol Edin

```bash
python check_training_data.py
```

**Beklenen çıktı:**
```
vida:    10 görüntü  ✅
somun:   10 görüntü  ✅
rulman:  10 görüntü  ✅
TOPLAM:  30 görüntü
```

---

## 🚀 İlk Eğitimi Yapın

```bash
python train_model.py --mode train --data_dir ./training_data --epochs 10
```

**Süre:** ~2-5 dakika (CPU'da)

**Sonuç:** `best_model.pth` dosyası oluşacak

---

## 🎉 Test Edin

```bash
streamlit run app.py
```

1. Tarayıcıda `http://localhost:8501` açılacak
2. Bir vida/somun/rulman görüntüsü yükleyin
3. "Deep Learning" yöntemini seçin
4. "🔍 Analiz Et" butonuna basın

**Sonuç:** Sistem artık 3 parçayı tanıyabilir! 🎊

---

## 📈 Sonraki Adımlar

### Aynı Gün (30 dakika)
- [ ] 3 parça daha ekleyin (dişli, kayış, piston)
- [ ] Her biri için 10 görüntü
- [ ] Toplam: 60 görüntü
- [ ] Yeniden eğitin (20 epoch)

### Bu Hafta
- [ ] 10 parçanın tamamını ekleyin
- [ ] Her parça için 20-30 görüntü
- [ ] Toplam: 200-300 görüntü
- [ ] 30 epoch eğitim

### Bu Ay
- [ ] Her parça için 100+ görüntü
- [ ] Veri artırma uygulayın
- [ ] 50 epoch profesyonel eğitim
- [ ] %90+ doğruluk

---

## 🔍 İyi Görüntü Seçme İpuçları

### ✅ İyi
- Tek renkli arka plan (beyaz/gri)
- Net ve keskin
- Parça görünür
- 500x500 px veya daha büyük

### ❌ Kötü
- Karışık arka plan
- Bulanık
- Çok küçük
- Watermark/logo var

---

## 💡 Hızlı Püf Noktalar

1. **Toplu indirme:**
   - Google Görseller'de bir sekme açın
   - 10 görüntüyü bulun
   - Hepsine aynı anda sağ tık → İndir
   - Toplu seç → training_data/[klasör]/ taşı

2. **Dosya isimlendirme:**
   - Otomatik: Tarayıcı `vida (1).jpg`, `vida (2).jpg` diye kaydeder
   - Manuel rename gerekmez, sistem tüm .jpg dosyalarını okur

3. **Hızlı test:**
   - İlk 30 görüntü ile test edin
   - Çalıştığını görünce daha fazla ekleyin
   - Yavaş yavaş ilerleyin

---

## 🆘 Sorun Giderme

### Sorun: "No such file or directory"
**Çözüm:**
```bash
# Klasörleri kontrol edin
ls training_data/vida/
# Boşsa, görüntüleri doğru klasöre koymadınız
```

### Sorun: "Insufficient data"
**Çözüm:**
```bash
# En az 10 görüntü gerekli
python check_training_data.py
# Eksik parçalara görüntü ekleyin
```

### Sorun: Eğitim çok yavaş
**Çözüm:**
```bash
# GPU yoksa epoch sayısını azaltın
python train_model.py --mode train --data_dir ./training_data --epochs 5
```

---

## 🎯 15 Dakika Özet

```
1. Google Görseller → "hex bolt"     → 10 görüntü indir → training_data/vida/     (5 dk)
2. Google Görseller → "hex nut"      → 10 görüntü indir → training_data/somun/    (5 dk)
3. Google Görseller → "ball bearing" → 10 görüntü indir → training_data/rulman/   (5 dk)
4. python check_training_data.py                                                  (10 sn)
5. python train_model.py --mode train --data_dir ./training_data --epochs 10      (3 dk)
6. streamlit run app.py                                                           (10 sn)
7. Test edin! 🎉
```

**Toplam:** ~15-20 dakika

---

**🚀 Başarılar! Sisteminiz artık çalışıyor!**
