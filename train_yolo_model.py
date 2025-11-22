"""
YOLOv8 ile Makine Parçası Tespit Modeli Eğitimi
YOLO formatındaki train, val, test klasörleriyle uyumlu eğitim scripti
"""

from ultralytics import YOLO
import yaml
from pathlib import Path
import torch
import os


def train_yolo_model(
    data_yaml='mech_parts_data.yaml',
    model_size='n',  # n, s, m, l, x (nano, small, medium, large, xlarge)
    epochs=100,
    batch_size=8,  # 8GB GPU için güvenli değer
    imgsz=640,
    device='',  # boş string: otomatik, '0' veya 'cpu'
    patience=50,
    save_dir='runs/detect',
    pretrained=True
):
    """
    YOLOv8 modelini eğitir
    
    Args:
        data_yaml: Dataset konfigürasyon dosyası yolu
        model_size: Model boyutu (n, s, m, l, x)
        epochs: Epoch sayısı
        batch_size: Batch boyutu
        imgsz: Görüntü boyutu
        device: Cihaz ('', '0', 'cpu', '0,1,2,3')
        patience: Early stopping patience
        save_dir: Model kayıt dizini
        pretrained: Pretrained ağırlık kullan
    """
    
    # Data YAML dosyasını kontrol et
    data_path = Path(data_yaml)
    if not data_path.exists():
        raise FileNotFoundError(f"Data YAML dosyası bulunamadı: {data_yaml}")
    
    # YAML içeriğini oku ve doğrula
    with open(data_yaml, 'r') as f:
        data_config = yaml.safe_load(f)
    
    print("=" * 70)
    print("YOLOv8 Makine Parçası Tespit Modeli Eğitimi")
    print("=" * 70)
    print(f"\n📊 Dataset Bilgileri:")
    print(f"   - Sınıf Sayısı: {data_config.get('nc', 'Belirtilmemiş')}")
    print(f"   - Sınıflar: {data_config.get('names', 'Belirtilmemiş')}")
    print(f"   - Train Path: {data_config.get('train', 'Belirtilmemiş')}")
    print(f"   - Val Path: {data_config.get('val', 'Belirtilmemiş')}")
    print(f"   - Test Path: {data_config.get('test', 'Belirtilmemiş')}")
    
    # Cihaz kontrolü
    if device == '':
        device_info = 'CUDA' if torch.cuda.is_available() else 'CPU'
        print(f"\n💻 Cihaz: {device_info}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"   GPU Bellek: {gpu_memory:.1f} GB")
            if gpu_memory < 12 and batch_size > 8:
                print(f"   ⚠️  Uyarı: {gpu_memory:.0f}GB GPU için batch_size={batch_size} çok büyük olabilir")
                print(f"   Önerilen: batch_size=8 veya daha küçük")
    else:
        print(f"\n💻 Cihaz: {device}")
    
    # Model oluştur
    model_name = f'yolov8{model_size}.pt' if pretrained else f'yolov8{model_size}.yaml'
    print(f"\n🔧 Model: YOLOv8{model_size.upper()}")
    print(f"   Pretrained: {'Evet' if pretrained else 'Hayır'}")
    
    try:
        model = YOLO(model_name)
    except Exception as e:
        print(f"\n⚠️  Model yüklenemedi: {e}")
        print("Otomatik olarak indiriliyor...")
        model = YOLO(model_name)
    
    # Eğitim parametreleri
    print(f"\n⚙️  Eğitim Parametreleri:")
    print(f"   - Epochs: {epochs}")
    print(f"   - Batch Size: {batch_size}")
    print(f"   - Image Size: {imgsz}")
    print(f"   - Patience: {patience}")
    print(f"   - Workers: 4 (optimized)")
    print(f"   - Cache: False (RAM tasarrufu)")
    print(f"   - Mixed Precision: True")
    print(f"   - Save Dir: {save_dir}")
    
    print("\n" + "=" * 70)
    print("🚀 Eğitim Başlıyor...")
    print("=" * 70 + "\n")
    
    # GPU bellek optimizasyonu
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        # Bellek fragmantasyonunu azalt
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
        print("✓ GPU bellek cache temizlendi")
        print("✓ Bellek optimizasyonu aktif\n")
    
    # Eğitimi başlat
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=device,
        patience=patience,
        workers=4,  # Bellek optimizasyonu için azaltıldı
        cache=False,  # RAM kullanımını azaltır
        save=True,
        project=save_dir,
        name='train',
        exist_ok=True,
        pretrained=pretrained,
        optimizer='auto',
        verbose=True,
        seed=0,
        deterministic=True,
        single_cls=False,
        rect=False,
        cos_lr=False,
        close_mosaic=10,
        resume=False,
        amp=True,
        fraction=1.0,
        profile=False,
        overlap_mask=True,
        mask_ratio=4,
        dropout=0.0,
        val=True,
        split='val',
        save_json=False,
        save_hybrid=False,
        conf=None,
        iou=0.7,
        max_det=300,
        half=False,
        dnn=False,
        plots=True,
        source=None,
        show=False,
        save_txt=False,
        save_conf=False,
        save_crop=False,
        show_labels=True,
        show_conf=True,
        vid_stride=1,
        line_thickness=3,
        visualize=False,
        augment=False,
        agnostic_nms=False,
        classes=None,
        retina_masks=False,
        boxes=True,
    )
    
    print("\n" + "=" * 70)
    print("✅ Eğitim Tamamlandı!")
    print("=" * 70)
    
    # Sonuçları göster
    print(f"\n📈 En İyi Model: {model.trainer.best}")
    print(f"📁 Modeller kaydedildi: {model.trainer.save_dir}")
    
    return model, results


def validate_model(model_path='runs/detect/train/weights/best.pt', data_yaml='mech_parts_data.yaml'):
    """
    Eğitilmiş modeli validation seti üzerinde test et
    
    Args:
        model_path: Model dosyası yolu
        data_yaml: Dataset konfigürasyon dosyası
    """
    print("\n" + "=" * 70)
    print("🔍 Model Validasyonu")
    print("=" * 70)
    
    model = YOLO(model_path)
    
    # Validation
    results = model.val(
        data=data_yaml,
        split='val',
        batch=16,
        imgsz=640,
        save_json=True,
        save_hybrid=False,
        conf=0.001,
        iou=0.6,
        max_det=300,
        half=False,
        device='',
        dnn=False,
        plots=True,
        rect=False,
        verbose=True,
    )
    
    print(f"\n📊 Validation Sonuçları:")
    print(f"   - mAP50: {results.box.map50:.4f}")
    print(f"   - mAP50-95: {results.box.map:.4f}")
    
    # Sınıf başına metrikler
    if hasattr(results.box, 'ap_class_index'):
        print(f"\n📋 Sınıf Başına Performans:")
        for idx, ap in zip(results.box.ap_class_index, results.box.ap50):
            print(f"   - Sınıf {idx}: mAP50 = {ap:.4f}")
    
    return results


def test_model(model_path='runs/detect/train/weights/best.pt', data_yaml='mech_parts_data.yaml'):
    """
    Eğitilmiş modeli test seti üzerinde test et
    
    Args:
        model_path: Model dosyası yolu
        data_yaml: Dataset konfigürasyon dosyası
    """
    print("\n" + "=" * 70)
    print("🧪 Model Testi (Test Set)")
    print("=" * 70)
    
    model = YOLO(model_path)
    
    # Test
    results = model.val(
        data=data_yaml,
        split='test',
        batch=16,
        imgsz=640,
        save_json=True,
        save_hybrid=False,
        conf=0.001,
        iou=0.6,
        max_det=300,
        half=False,
        device='',
        dnn=False,
        plots=True,
        rect=False,
        verbose=True,
    )
    
    print(f"\n📊 Test Sonuçları:")
    print(f"   - mAP50: {results.box.map50:.4f}")
    print(f"   - mAP50-95: {results.box.map:.4f}")
    
    return results


def predict_image(model_path='runs/detect/train/weights/best.pt', image_path='test/images/', conf=0.25):
    """
    Tek bir görüntü veya klasör üzerinde tahmin yap
    
    Args:
        model_path: Model dosyası yolu
        image_path: Görüntü veya klasör yolu
        conf: Confidence threshold
    """
    print("\n" + "=" * 70)
    print("🔮 Tahmin Yapılıyor")
    print("=" * 70)
    
    model = YOLO(model_path)
    
    # Tahmin yap
    results = model.predict(
        source=image_path,
        conf=conf,
        iou=0.7,
        imgsz=640,
        device='',
        max_det=300,
        vid_stride=1,
        stream_buffer=False,
        visualize=False,
        augment=False,
        agnostic_nms=False,
        classes=None,
        retina_masks=False,
        boxes=True,
        save=True,
        save_frames=False,
        save_txt=False,
        save_conf=False,
        save_crop=False,
        show=False,
        show_labels=True,
        show_conf=True,
        show_boxes=True,
        line_thickness=2,
    )
    
    print(f"\n✅ Tahminler kaydedildi: runs/detect/predict/")
    
    # Sonuçları göster
    for i, result in enumerate(results):
        print(f"\n📸 Görüntü {i+1}:")
        if len(result.boxes) > 0:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                cls_name = result.names[cls_id]
                print(f"   - {cls_name}: {conf:.2f}")
        else:
            print("   - Tespit yok")
    
    return results


def export_model(model_path='runs/detect/train/weights/best.pt', format='onnx'):
    """
    Modeli farklı formatlara export et
    
    Args:
        model_path: Model dosyası yolu
        format: Export formatı (onnx, torchscript, tensorflow, tflite, etc.)
    """
    print("\n" + "=" * 70)
    print(f"📦 Model Export Ediliyor ({format.upper()})")
    print("=" * 70)
    
    model = YOLO(model_path)
    
    # Export
    model.export(format=format, imgsz=640, half=False, int8=False, dynamic=False, simplify=False, opset=None)
    
    print(f"\n✅ Model export edildi!")
    
    return model


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='YOLOv8 Makine Parçası Tespit Modeli Eğitimi')
    parser.add_argument('--mode', type=str, default='train', 
                       choices=['train', 'val', 'test', 'predict', 'export'],
                       help='Mod: train, val, test, predict veya export')
    parser.add_argument('--data', type=str, default='mech_parts_data.yaml',
                       help='Dataset YAML dosyası')
    parser.add_argument('--model', type=str, default='runs/detect/train/weights/best.pt',
                       help='Model dosyası (val, test, predict için)')
    parser.add_argument('--size', type=str, default='n',
                       choices=['n', 's', 'm', 'l', 'x'],
                       help='Model boyutu (train için)')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Epoch sayısı')
    parser.add_argument('--batch', type=int, default=8,
                       help='Batch size (8GB GPU için 8 önerilir)')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='Görüntü boyutu')
    parser.add_argument('--device', type=str, default='',
                       help='Cihaz (boş=otomatik, 0, cpu, 0,1,2,3)')
    parser.add_argument('--patience', type=int, default=50,
                       help='Early stopping patience')
    parser.add_argument('--source', type=str, default='test/images/',
                       help='Tahmin için görüntü/klasör yolu')
    parser.add_argument('--conf', type=float, default=0.25,
                       help='Confidence threshold')
    parser.add_argument('--format', type=str, default='onnx',
                       choices=['onnx', 'torchscript', 'tensorflow', 'tflite', 'coreml'],
                       help='Export formatı')
    parser.add_argument('--pretrained', action='store_true', default=True,
                       help='Pretrained ağırlık kullan')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        print("\n🎯 Eğitim modu seçildi")
        model, results = train_yolo_model(
            data_yaml=args.data,
            model_size=args.size,
            epochs=args.epochs,
            batch_size=args.batch,
            imgsz=args.imgsz,
            device=args.device,
            patience=args.patience,
            pretrained=args.pretrained
        )
        
    elif args.mode == 'val':
        print("\n🎯 Validation modu seçildi")
        results = validate_model(
            model_path=args.model,
            data_yaml=args.data
        )
        
    elif args.mode == 'test':
        print("\n🎯 Test modu seçildi")
        results = test_model(
            model_path=args.model,
            data_yaml=args.data
        )
        
    elif args.mode == 'predict':
        print("\n🎯 Tahmin modu seçildi")
        results = predict_image(
            model_path=args.model,
            image_path=args.source,
            conf=args.conf
        )
        
    elif args.mode == 'export':
        print("\n🎯 Export modu seçildi")
        export_model(
            model_path=args.model,
            format=args.format
        )
    
    print("\n" + "=" * 70)
    print("🏁 İşlem Tamamlandı!")
    print("=" * 70 + "\n")
