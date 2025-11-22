# Makine Parçası Tanıma ve Tespit Sistemi

Görüntü işleme, derin öğrenme ve YOLO tabanlı nesne tespiti ile makine parçalarını sınıflandıran ve tespit eden Python projesi.

## İçindekiler
- [Hızlı Başlangıç (Özet)](#hızlı-başlangıç-özet)
- [Proje Yapısı](#proje-yapısı)
- [Kurulum](#kurulum)
- [Veri Toplama ve Etiketli Görsel İndirme](#veri-toplama-ve-etiketli-görsel-indirme)
- [2B Sınıflandırma (ResNet50 + Hibrit)](#2b-sınıflandırma-resnet50--hibrit)
- [YOLOv8 Nesne Tespiti](#yolov8-nesne-tespiti)
- [GPU Bellek İpuçları](#gpu-bellek-ipuçları)
- [Sorun Giderme](#sorun-giderme)

## Hızlı Başlangıç (Özet)
```bash
pip install -r requirements.txt
chmod +x setup_folders.sh && ./setup_folders.sh
# Etiketli görsel indir (sınıf başına 40, örnek sınıflar)
python image_dataset_downloader.py --classes vida somun rulman disli piston --per-class 40 --out training_data
# Kısa eğitim
python train_model.py --mode train --data_dir ./training_data --epochs 10
# Arayüz
streamlit run app.py
```

## Proje Yapısı
```
makine_parca_tanima/
├── app.py                    # Streamlit arayüz (hibrit sınıflandırma)
├── train_model.py            # ResNet50 transfer learning eğitimi
├── hybrid_detector.py        # DL + feature matching hibrit sistem
├── feature_matcher.py        # SIFT/histogram/hu tabanlı hızlı tanıma
├── image_dataset_downloader.py # DuckDuckGo ile etiketli görsel indirme
├── train_yolo_model.py       # YOLOv8 eğitim/val/test/predict/export
├── hizli_egitim.sh           # YOLO hızlı etkileşimli eğitim scripti
├── mech_parts_data.yaml      # YOLO dataset tanımı (hazırsa)
├── training_data/            # Sınıflandırma verisi (klasör=etiket)
├── referans_gorseller/       # Feature matching referansları
├── train/ val/ test/         # YOLO veri klasörleri (images/labels)
└── README.md                 # Bu dosya
```

## Kurulum
```bash
pip install -r requirements.txt
# YOLO için ek paket (kurulu değilse)
pip install ultralytics pyyaml
```

## Veri Toplama ve Etiketli Görsel İndirme
- Otomatik (etiket klasörü oluşturur):
  ```bash
  python image_dataset_downloader.py --classes vida somun rulman --per-class 40 --out training_data
  ```
- Manuel hızlı rehber (3x10 görüntü):
  - `training_data/vida/` → 10 görüntü
  - `training_data/somun/` → 10 görüntü
  - `training_data/rulman/` → 10 görüntü
- Kontrol:
  ```bash
  python check_training_data.py
  ```

## 2B Sınıflandırma (ResNet50 + Hibrit)
- Arayüz: `streamlit run app.py` → sol panelden “Hibrit (Otomatik)” seç, görsel yükle.
- Kütüphane kullanımı:
  ```python
  from hybrid_detector import HibritTanima
  sistem = HibritTanima(model_path='best_model.pth', referans_klasor='./referans_gorseller', mod='auto')
  sonuc = sistem.tanima_yap('test.jpg')
  print(sonuc['parca'], sonuc['guven'])
  ```
- Eğitim:
  ```bash
  python train_model.py --mode train --data_dir ./training_data --epochs 25 --batch_size 32 --lr 0.001
  ```
  - Minimum veri kontrolü entegre: en az 2 sınıf ve toplam 2+ görüntü gerekir.
- Test:
  ```bash
  python train_model.py --mode test --model_path best_model.pth --test_image ./test_images/vida1.jpg
  ```

## YOLOv8 Nesne Tespiti
- Veri yapısı:
  ```
  train/images/*.jpg|png   train/labels/*.txt
  val/images/...           val/labels/...
  test/images/...          test/labels/...
  mech_parts_data.yaml
  ```
- Hızlı script: `./hizli_egitim.sh` (model boyutu/epoch/batch interaktif seçer, 8GB GPU için varsayılan batch=8).
- Manuel:
  ```bash
  python train_yolo_model.py --mode train --size n --epochs 100 --batch 16 --imgsz 640 --data mech_parts_data.yaml
  python train_yolo_model.py --mode val
  python train_yolo_model.py --mode test
  python train_yolo_model.py --mode predict --source test/images/ --conf 0.25
  python train_yolo_model.py --mode export --format onnx
  ```
- Model boyutları: n (en hızlı) → s → m → l → x (en yavaş/en yüksek doğruluk).

## GPU Bellek İpuçları
- 8GB GPU için öneri: `--batch 8 --size n|s`, `--imgsz 640`. Bellek hatasında batch’i 4’e veya imgsz’yi 416’ya düşür.
- CPU kullanımı (zorunluysa): `--device cpu --batch 4`.
- Hızlı test: `python train_yolo_model.py --mode train --size n --epochs 30 --batch 4 --imgsz 416`.

## Sorun Giderme
- **Veri eksik/boş**: `check_training_data.py` ile sayıları kontrol edin; her sınıfa min 10 görüntü ekleyin.
- **DL model yüklenmiyor**: `best_model.pth` yoksa önce eğitim yapın; CPU’da test için `--model_path best_model.pth` yüklendiğinde otomatik CPU’ya maplenir.
- **GPU bellek hatası (YOLO)**: Batch küçült, görüntü boyutunu düşür, gerekirse CPU’ya geç.
- **Referans veritabanı boş (Feature Matching)**: `referans_gorseller/<parca>/` içine en az 5 görüntü ekleyin.
