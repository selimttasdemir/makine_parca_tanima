# Makine Parçası Tanıma Sistemi - Kullanım Örnekleri

## 1. Temel Kullanım

### Web Arayüzü ile Kullanım

```bash
# Uygulamayı başlat
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresine gidin ve:
1. Bir makine parçası görüntüsü yükleyin
2. "Analiz Et" butonuna tıklayın
3. Sonuçları görüntüleyin

## 2. Kendi Modelinizi Eğitme

### Veri Hazırlama

Önce verilerinizi şu yapıda organize edin:

```
data/
├── vida/
│   ├── img1.jpg
│   ├── img2.jpg
│   └── ...
├── somun/
│   ├── img1.jpg
│   ├── img2.jpg
│   └── ...
├── rulman/
│   ├── img1.jpg
│   └── ...
└── ...
```

### Model Eğitimi

```bash
# Basit eğitim
python train_model.py --mode train --data_dir ./data

# Gelişmiş parametrelerle
python train_model.py --mode train \
    --data_dir ./data \
    --epochs 50 \
    --batch_size 16 \
    --lr 0.0001
```

### Model Test Etme

```bash
python train_model.py --mode test \
    --model_path best_model.pth \
    --test_image ./test_images/vida1.jpg
```

## 3. Python Kodu ile Kullanım

### Basit Kullanım

```python
from app import MakineParcaTanima
from PIL import Image

# Sistem başlat
sistem = MakineParcaTanima()

# Görüntü yükle
image = Image.open("parca.jpg")

# Analiz et
processed = sistem.goruntu_onisleme(image)
ozellikler = sistem.ozellik_cikarma(image)
parca_adi = sistem.parca_tanima_basit(ozellikler)

# Bilgi al
bilgi = sistem.bilgi_getir(parca_adi)
print(f"Parça: {bilgi['isim']}")
print(f"Tanım: {bilgi['tanim']}")
```

### Görüntü İşleme Araçları

```python
from image_utils import GorselIslemci
import cv2

# Görüntü yükle
img = cv2.imread("parca.jpg")

# Kenar tespiti
edges = GorselIslemci.kenar_tespit(img, method='canny')

# Şekil analizi
shapes = GorselIslemci.sekil_analizi(img)
for shape in shapes:
    print(f"Şekil: {shape['sekil']}, Alan: {shape['alan']}")

# Renk analizi
colors = GorselIslemci.renk_analizi(img)
print(f"Ortalama RGB: {colors['rgb_ortalama']}")

# Doku analizi
texture = GorselIslemci.doku_analizi(img)
print(f"Ortalama: {texture['ortalama']}")
```

## 4. Batch İşleme

### Çoklu Görüntü Analizi

```python
import os
from app import MakineParcaTanima
from PIL import Image

sistem = MakineParcaTanima()
image_folder = "./images"

results = []

for filename in os.listdir(image_folder):
    if filename.endswith(('.jpg', '.png', '.jpeg')):
        img_path = os.path.join(image_folder, filename)
        image = Image.open(img_path)
        
        ozellikler = sistem.ozellik_cikarma(image)
        parca_adi = sistem.parca_tanima_basit(ozellikler)
        
        results.append({
            'dosya': filename,
            'parca': parca_adi,
            'alan': ozellikler['alan']
        })

# Sonuçları kaydet
import json
with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
```

## 5. API Kullanımı (İleride Eklenebilir)

### Flask API Örneği

```python
# api.py
from flask import Flask, request, jsonify
from app import MakineParcaTanima
from PIL import Image
import io

app = Flask(__name__)
sistem = MakineParcaTanima()

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    image = Image.open(io.BytesIO(file.read()))
    
    ozellikler = sistem.ozellik_cikarma(image)
    parca_adi = sistem.parca_tanima_basit(ozellikler)
    bilgi = sistem.bilgi_getir(parca_adi)
    
    return jsonify({
        'parca': bilgi['isim'],
        'tanim': bilgi['tanim'],
        'kullanim_alanlari': bilgi['kullanim_alanlari']
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### API'ye İstek Gönderme

```python
import requests

url = 'http://localhost:5000/analyze'
files = {'image': open('parca.jpg', 'rb')}

response = requests.post(url, files=files)
print(response.json())
```

## 6. Komut Satırı Kullanımı

### CLI Script Örneği

```python
# cli.py
import argparse
from app import MakineParcaTanima
from PIL import Image

def main():
    parser = argparse.ArgumentParser(description='Makine Parçası Tanıma CLI')
    parser.add_argument('image', help='Görüntü dosyası yolu')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Detaylı çıktı')
    
    args = parser.parse_args()
    
    sistem = MakineParcaTanima()
    image = Image.open(args.image)
    
    ozellikler = sistem.ozellik_cikarma(image)
    parca_adi = sistem.parca_tanima_basit(ozellikler)
    bilgi = sistem.bilgi_getir(parca_adi)
    
    print(f"\n{'='*50}")
    print(f"Parça: {bilgi['isim']}")
    print(f"{'='*50}")
    print(f"\nTanım: {bilgi['tanim']}")
    
    if args.verbose:
        print(f"\nÖzellikler:")
        print(f"  - Şekil: {ozellikler.get('sekil', 'N/A')}")
        print(f"  - Alan: {ozellikler.get('alan', 'N/A')}")
        print(f"  - Çevre: {ozellikler.get('cevre', 'N/A')}")
        
        print(f"\nKullanım Alanları:")
        for alan in bilgi.get('kullanim_alanlari', []):
            print(f"  • {alan}")

if __name__ == '__main__':
    main()
```

Kullanımı:
```bash
python cli.py parca.jpg
python cli.py parca.jpg --verbose
```

## 7. Jupyter Notebook ile Kullanım

```python
# notebook.ipynb
import matplotlib.pyplot as plt
from app import MakineParcaTanima
from PIL import Image
import numpy as np

# Sistem başlat
sistem = MakineParcaTanima()

# Görüntü yükle
image = Image.open("parca.jpg")

# İşle
processed = sistem.goruntu_onisleme(image)

# Görselleştir
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

axes[0, 0].imshow(processed['orijinal'])
axes[0, 0].set_title('Orijinal')

axes[0, 1].imshow(processed['gri'], cmap='gray')
axes[0, 1].set_title('Gri Tonlama')

axes[1, 0].imshow(processed['iyilestirilmis'], cmap='gray')
axes[1, 0].set_title('İyileştirilmiş')

axes[1, 1].imshow(processed['kenarlar'], cmap='gray')
axes[1, 1].set_title('Kenarlar')

plt.tight_layout()
plt.show()

# Analiz sonucu
ozellikler = sistem.ozellik_cikarma(image)
parca_adi = sistem.parca_tanima_basit(ozellikler)
bilgi = sistem.bilgi_getir(parca_adi)

print(f"Tespit Edilen Parça: {bilgi['isim']}")
print(f"Tanım: {bilgi['tanim']}")
```

## 8. Veri Artırma (Data Augmentation)

```python
from torchvision import transforms
from PIL import Image

# Veri artırma pipeline'ı
augmentation = transforms.Compose([
    transforms.RandomRotation(30),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.3, contrast=0.3),
    transforms.RandomResizedCrop(224),
])

# Uygula
image = Image.open("parca.jpg")
augmented_images = [augmentation(image) for _ in range(5)]

# Kaydet
for i, aug_img in enumerate(augmented_images):
    aug_img.save(f"augmented_{i}.jpg")
```

## 9. Performans İyileştirme

### GPU Kullanımı

```python
import torch

# GPU kontrolü
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    device = torch.device("cuda")
else:
    print("CPU kullanılıyor")
    device = torch.device("cpu")
```

### Batch İşleme Optimizasyonu

```python
from torch.utils.data import DataLoader
import torch

# Batch processing
images_batch = torch.stack([transform(img) for img in images])
with torch.no_grad():
    predictions = model(images_batch.to(device))
```

## 10. Hata Ayıklama

```python
import logging

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Kullan
logger.info("Görüntü işleme başladı")
logger.warning("Düşük güvenilirlik skoru")
logger.error("Görüntü yüklenemedi")
```
