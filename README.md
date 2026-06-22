# Makine Parçası Tanıma ve Tespit Sistemi

Görüntü işleme, derin öğrenme ve YOLO tabanlı nesne tespiti ile makine parçalarını tanıyan Python projesi. Sistem; tek görsel analizi, YOLO ile çoklu nesne tespiti, ResNet50 sınıflandırma, feature matching, hibrit tanıma ve ESP32Cam üzerinden canlı kamera desteği sunar.

![Makine parçası tanıma demosu](makine_parca_tanima.gif)

## İçindekiler

- [Özellikler](#özellikler)
- [Demo ve Ekran Görüntüleri](#demo-ve-ekran-görüntüleri)
- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Proje Yapısı](#proje-yapısı)
- [Veri Hazırlama](#veri-hazırlama)
- [Model Eğitimi](#model-eğitimi)
- [Web Uygulaması](#web-uygulaması)
- [ESP32Cam Canlı Kamera](#esp32cam-canlı-kamera)
- [Test ve Değerlendirme](#test-ve-değerlendirme)
- [Sorun Giderme](#sorun-giderme)
- [Lisans](#lisans)

## Özellikler

- YOLO ile çoklu makine parçası tespiti ve bounding box gösterimi.
- ResNet50 transfer learning ile tek nesne sınıflandırma.
- SIFT, histogram ve Hu moment tabanlı feature matching.
- Hibrit mod ile deep learning ve feature matching sonuçlarını birlikte kullanma.
- Streamlit web arayüzü ile görsel yükleme, örnek seçme ve analiz.
- Model performans testi, sınıf bazlı doğruluk ve sonuç kaydetme.
- ESP32Cam ile canlı MJPEG akışı, filtreleme, snapshot ve gerçek zamanlı YOLO tespiti.

Desteklenen temel sınıflar:

| Türkçe | Model Etiketi | Açıklama |
|---|---|---|
| Rulman | Bearing | Döner sistemlerde yataklama elemanı |
| Vida / Civata | Bolt | Bağlantı elemanı |
| Dişli | Gear | Güç ve hareket aktarma elemanı |
| Somun | Nut | Vidalı bağlantı elemanı |
| Kayış | Belt | Hareket aktarımı |
| Krank mili | Crankshaft | Dönel hareket elemanı |
| Pim | Pin | Konumlama ve sabitleme elemanı |
| Piston | Piston | Motor ve kompresör parçası |
| Yay | Spring | Esnek mekanik eleman |

## Demo ve Ekran Görüntüleri

### Web Arayüzü ile YOLO Analizi

![Görsel yükleme ve YOLO analiz sonucu](<Ekran Görüntüsü - 2026-06-21 18-19-15.png>)

Yüklenen dişli görseli YOLO modeliyle analiz edilir, parça sınıfı ve güven skoru arayüzde gösterilir.

### Parça Bilgisi ve Güven Skoru

![Parça tanımı ve güven skoru](<Ekran Görüntüsü - 2026-06-21 18-19-41.png>)

Tanıma sonucundan sonra parça açıklaması, kullanım alanları, teknik özellikler ve alt tür bilgileri görüntülenir.

### Görüntü İşleme Detayları

![Gri tonlama ve kenar tespiti](<Ekran Görüntüsü - 2026-06-21 18-19-51.png>)

Gri tonlama, kenar tespiti ve şekil analizi çıktıları görsel işleme detaylarında incelenebilir.

### ESP32Cam Canlı Tespit

![ESP32Cam canlı YOLO tespit ekranı](<Ekran Görüntüsü - 2026-06-21 18-17-34.png>)

ESP32Cam akışında YOLO modeli gerçek zamanlı nesne tespiti yapar ve sonuçları canlı görüntü üzerine çizer.

### Dataset İstatistikleri

![Dataset istatistikleri](dataset_statistics.png)

`check_dataset.py` çalıştırıldığında eğitim, doğrulama ve test verilerinin sınıf dağılımı `dataset_statistics.png` olarak kaydedilir.

## Hızlı Başlangıç

### Kurulum

```bash
pip install -r requirements.txt
chmod +x setup_folders.sh
./setup_folders.sh
```

### Web Uygulamasını Başlatma

```bash
./web_test.sh
```

Alternatif olarak:

```bash
streamlit run app.py
```

Uygulama varsayılan olarak `http://localhost:8501` adresinde açılır.

### Hızlı Eğitim Akışı

```bash
python download_images.py --classes vida somun rulman disli --per-class 40 --out training_data
python train_model.py --mode train --data_dir ./training_data --epochs 25
./hizli_egitim.sh
```

## Proje Yapısı

```text
makine_parca_tanima/
├── app.py                    # Streamlit web arayüzü
├── train_model.py            # ResNet50 sınıflandırma eğitimi
├── train_yolo_model.py       # YOLO train/val/test/predict/export aracı
├── hybrid_detector.py        # Hibrit tanıma sistemi
├── feature_matcher.py        # Referans tabanlı feature matching
├── esp32cam_handler.py       # ESP32Cam bağlantı ve frame işleme modülü
├── test_esp32cam.py          # ESP32Cam komut satırı test aracı
├── test_dogruluk.py          # YOLO doğruluk testi
├── check_dataset.py          # YOLO dataset kontrolü ve istatistik üretimi
├── check_training_data.py    # Sınıflandırma veri kontrolü
├── download_images.py        # Görsel indirme aracı
├── mech_parts_data.yaml      # YOLO dataset tanımı
├── requirements.txt          # Python bağımlılıkları
├── training_data/            # ResNet50 sınıflandırma verisi
├── train/                    # YOLO eğitim verisi
├── val/                      # YOLO doğrulama verisi
├── test/                     # YOLO test verisi
└── runs/                     # Eğitim çıktıları ve model ağırlıkları
```

## Veri Hazırlama

### Otomatik Görsel İndirme

```bash
python download_images.py --classes vida somun rulman disli piston --per-class 40 --out training_data
python download_images.py --classes civata kayis --per-class 100 --out ./my_data
```

### Sınıflandırma Verisi

ResNet50 eğitimi için klasör adı sınıf adı olarak kullanılır:

```text
training_data/
├── vida/
├── somun/
├── rulman/
├── disli/
├── kayis/
└── yay/
```

Her sınıf için en az 10-15 görsel ile başlanabilir. Daha kararlı sonuçlar için sınıf başına 50+ görsel önerilir.

### YOLO Dataset Yapısı

`mech_parts_data.yaml` dosyası YOLO veri yollarını ve sınıfları tanımlar:

```yaml
train: ./train/images
val: ./val/images
test: ./test/images

nc: 4
names: ['Bearing', 'Bolt', 'Gear', 'Nut']
```

YOLO etiket formatı:

```text
class_id center_x center_y width height
```

Tüm koordinatlar normalize edilmelidir.

### Veri Kontrolü

```bash
python check_training_data.py
python check_dataset.py
```

## Model Eğitimi

### ResNet50 Sınıflandırma

Temel eğitim:

```bash
python train_model.py --mode train --data_dir ./training_data --epochs 25
```

Gelişmiş parametrelerle eğitim:

```bash
python train_model.py \
  --mode train \
  --data_dir ./training_data \
  --epochs 50 \
  --batch_size 32 \
  --lr 0.001 \
  --patience 10
```

Tek görsel testi:

```bash
python train_model.py --mode test --model_path best_model.pth --test_image ./test.jpg
```

Python API örneği:

```python
from hybrid_detector import HibritTanima

sistem = HibritTanima(
    model_path="best_model.pth",
    referans_klasor="./referans_gorseller",
    mod="auto",
)

sonuc = sistem.tanima_yap("test.jpg")
print(f"Parça: {sonuc['parca']}")
print(f"Güven: {sonuc['guven']:.2%}")
```

### YOLO Nesne Tespiti

İnteraktif hızlı eğitim:

```bash
./hizli_egitim.sh
```

Manuel eğitim:

```bash
python train_yolo_model.py \
  --mode train \
  --size n \
  --epochs 100 \
  --batch 16 \
  --imgsz 640 \
  --data mech_parts_data.yaml
```

CPU eğitimi:

```bash
python train_yolo_model.py \
  --mode train \
  --size n \
  --epochs 50 \
  --batch 4 \
  --device cpu
```

Model işlemleri:

```bash
python train_yolo_model.py --mode val
python train_yolo_model.py --mode test
python train_yolo_model.py --mode predict --source test/images/ --conf 0.25
python train_yolo_model.py --mode export --format onnx
```

Model boyutu seçimi:

| Model | Hız | Doğruluk | Yaklaşık GPU Belleği | Önerilen Batch |
|---|---:|---:|---:|---:|
| YOLOv8n | Çok yüksek | Orta | 2 GB | 16 |
| YOLOv8s | Yüksek | İyi | 4 GB | 12 |
| YOLOv8m | Orta | Yüksek | 6 GB | 8 |
| YOLOv8l | Düşük | Çok yüksek | 8 GB | 4 |
| YOLOv8x | Çok düşük | En yüksek | 12 GB | 2 |

## Web Uygulaması

Web arayüzünde üç ana sayfa bulunur:

- Ana Sayfa - Parça Tanıma
- ESP32Cam Canlı Kamera
- Model Performans Testi

### Parça Tanıma Akışı

1. Sol menüden tanıma yöntemini seçin.
2. YOLO model yolunu kontrol edin: `runs/detect/train/weights/best.pt`.
3. Bir görsel yükleyin veya örnek parça seçin.
4. Analizi başlatın.
5. Bounding box, güven skoru, parça bilgisi ve görüntü işleme detaylarını inceleyin.

Kullanılabilir tanıma yöntemleri:

| Yöntem | Kullanım |
|---|---|
| YOLO | Çoklu nesne tespiti ve üretim senaryoları |
| Deep Learning | Tek nesne sınıflandırma |
| Feature Matching | Referans görsellerle hızlı prototip |
| Hibrit | DL ve feature matching sonuçlarını birlikte değerlendirme |

### Güven Skoru Yorumu

| Güven Skoru | Anlamı |
|---|---|
| 90%+ | Çok yüksek, güvenle kullanılabilir |
| 80-90% | Yüksek, iyi tespit |
| 70-80% | Kabul edilebilir |
| 60-70% | Orta, manuel kontrol önerilir |
| 50-60% | Düşük |
| <50% | Güvenilmez |

## ESP32Cam Canlı Kamera

ESP32Cam desteği, yerel ağdaki ESP32Cam modülünden MJPEG akışı alır ve Streamlit arayüzünde canlı görüntü işler. YOLO modeli etkinse her frame üzerinde gerçek zamanlı parça tespiti yapılabilir.

### Hazırlık

ESP32Cam tarafında firmware yüklenmiş, WiFi bağlantısı yapılmış ve IP adresi biliniyor olmalıdır. Python tarafında gerekli paketler `requirements.txt` içinde yer alır:

```bash
pip install -r requirements.txt
```

Ek olarak yalnızca ESP32Cam testleri için:

```bash
pip install requests opencv-python pillow
```

### Streamlit Üzerinden Kullanım

1. `streamlit run app.py` komutuyla uygulamayı başlatın.
2. Sol menüden `ESP32Cam Canlı Kamera` sayfasını açın.
3. ESP32 IP adresini girin, örneğin `192.168.1.100`.
4. Portu girin, varsayılan değer `80`.
5. Bağlantı kontrolü yapın.
6. Canlı akışı başlatın.
7. İsteğe bağlı olarak YOLO tespiti, istatistik ve frame kaydetme seçeneklerini etkinleştirin.

### ESP32Cam Özellikleri

- Canlı MJPEG video akışı.
- YOLO ile gerçek zamanlı nesne tespiti.
- FPS ve frame sayacı.
- Snapshot alma ve indirme.
- Frame kaydı.
- Normal, gri tonlama, kenar tespiti, keskinleştirme ve histogram eşitleştirme filtreleri.
- Parlaklık, kontrast, doygunluk, dikey/yatay çevirme ve gece modu kontrolleri.

### Kamera Ayarı Önerileri

| Senaryo | Öneri |
|---|---|
| Canlı tespit | Frame güncelleme 500 ms, filtre Normal, YOLO açık |
| İzleme | Frame güncelleme 1000 ms, YOLO kapalı |
| Kayıt | Frame güncelleme 200 ms, frame kaydı açık |
| Gece ortamı | Parlaklık +2, kontrast +1, doygunluk -1 |

### Komut Satırı Test Aracı

```bash
python3 test_esp32cam.py -i 192.168.1.100 test-connection
python3 test_esp32cam.py -i 192.168.1.100 snapshot -o test.jpg
python3 test_esp32cam.py -i 192.168.1.100 stream -d 30
python3 test_esp32cam.py -i 192.168.1.100 stream -f KeyarTespiti -d 20
python3 test_esp32cam.py -i 192.168.1.100 camera-settings
```

### Python API Örneği

```python
from esp32cam_handler import ESP32CamHandler, FrameProcessor

esp32 = ESP32CamHandler("192.168.1.100", port=80)

if esp32.is_connected:
    esp32.basla_stream()
    frame = esp32.son_frame_al()

    if frame is not None:
        gray = FrameProcessor.gri_tonlama(frame)
        edges = FrameProcessor.kenar_tespit(frame)

    esp32.durdur_stream()
    esp32.kapat()
```

### Mimari

```text
ESP32Cam
  -> HTTP/MJPEG
esp32cam_handler.py
  -> Threading ve frame buffer
app.py
  -> OpenCV + YOLO + Streamlit
Tespit sonuçları
```

### Bilinen Sınırlamalar ve Güvenlik

- Kararlı WiFi bağlantısı gerekir.
- Yüksek çözünürlük ve düşük frame aralığı bant genişliği tüketimini artırır.
- WiFi gecikmesi genellikle 100-300 ms aralığındadır.
- PSRAM'li ESP32Cam modelleri daha kararlı çalışır.
- Üretim ortamında HTTPS ve yerel ağ izolasyonu önerilir.
- Modem üzerinden port yönlendirmesi yapılmamalıdır.

### Sonraki Adımlar

- Video kaydı.
- WebRTC ile düşük gecikmeli yayın.
- Çoklu kamera desteği.
- Cloud upload.
- Mobil uygulama entegrasyonu.

## Test ve Değerlendirme

### Web Arayüzü ile Model Testi

1. Sol menüden `Model Performans Testi` sayfasını açın.
2. Model yolunu girin: `runs/detect/train/weights/best.pt`.
3. Test klasörünü seçin.
4. Test edilecek görüntü sayısını belirleyin.
5. Testi başlatın ve genel doğruluk, sınıf bazlı performans ve yanlış tahminleri inceleyin.

### Komut Satırı Testleri

```bash
python test_dogruluk.py --model runs/detect/train/weights/best.pt
python test_dogruluk.py --model runs/detect/train/weights/best.pt --limit 50
python test_dogruluk.py --model runs/detect/train/weights/best.pt --test test --limit 100 --save sonuclarim.json
```

### Hızlı Sistem Kontrolleri

```bash
./web_durum_kontrol.sh
./test_model.sh
python quick_test.py
python check_dataset.py
python check_training_data.py
```

### Doğruluk Yorumu

| Genel Doğruluk | Değerlendirme | Öneri |
|---|---|---|
| 90%+ | Çok iyi | Üretime yakın |
| 75-90% | İyi | Kullanılabilir, iyileştirilebilir |
| 60-75% | Orta | Daha fazla veri ve eğitim gerekli |
| <60% | Zayıf | Veri ve etiketler gözden geçirilmeli |

## Sorun Giderme

### Eğitim Verisi Bulunamadı

```bash
python check_training_data.py
```

`training_data/<sinif_adi>/` klasörlerine görsel ekleyin. Her sınıf için en az 10 görsel önerilir.

### YOLO Dataset Hatası

```bash
ls train/images/
ls train/labels/
python check_dataset.py
```

Görsel ve etiket dosyalarının aynı ada sahip olduğundan emin olun.

### Model Dosyası Bulunamadı

ResNet50 için:

```bash
python train_model.py --mode train --epochs 25
```

YOLO için:

```bash
python train_yolo_model.py --mode train --epochs 50
```

### CUDA Bellek Hatası

Batch boyutunu veya görüntü boyutunu düşürün:

```bash
python train_yolo_model.py --size n --batch 8 --imgsz 640
python train_yolo_model.py --size n --batch 4 --imgsz 416
```

GPU yoksa CPU kullanın:

```bash
python train_yolo_model.py --size n --batch 4 --device cpu
```

### Streamlit veya OpenCV Bulunamadı

```bash
pip install streamlit opencv-python
```

### Feature Matching Referans Veritabanı Boş

Her parça için referans görseller ekleyin:

```text
referans_gorseller/
├── vida/
├── somun/
├── rulman/
└── disli/
```

### ESP32Cam Bağlantısı Başarısız

```bash
ping 192.168.1.100
curl http://192.168.1.100/status
python3 test_esp32cam.py -i 192.168.1.100 test-connection
```

Kontrol edilmesi gerekenler:

- ESP32Cam ve bilgisayar aynı WiFi ağında olmalı.
- IP adresi Arduino Serial Monitor çıktısıyla eşleşmeli.
- Firewall yerel bağlantıyı engellememeli.
- Akış kesiliyorsa frame güncelleme süresi artırılmalı veya YOLO tespiti kapatılmalıdır.

## Faydalı Komutlar

```bash
./web_test.sh
./web_durum_kontrol.sh
./hizli_egitim.sh
./test_model.sh
python test_dogruluk.py --limit 50
python download_images.py --classes vida somun --per-class 50
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

Son güncelleme: 22 Haziran 2026
