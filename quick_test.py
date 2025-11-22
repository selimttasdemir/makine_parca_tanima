"""
Hızlı Model Test ve Görselleştirme Scripti
Eğitilmiş YOLOv8 modelini kolayca test edin
"""

from ultralytics import YOLO
import cv2
from pathlib import Path
import random


def quick_test(model_path='runs/detect/train/weights/best.pt', num_samples=5):
    """
    Test setinden rastgele görüntüler seçip tahmin yap
    
    Args:
        model_path: Eğitilmiş model yolu
        num_samples: Test edilecek görüntü sayısı
    """
    print("=" * 70)
    print("🧪 Hızlı Model Testi")
    print("=" * 70)
    
    # Model yükle
    if not Path(model_path).exists():
        print(f"❌ Model bulunamadı: {model_path}")
        print("Önce modeli eğitmeniz gerekiyor!")
        return
    
    print(f"\n📦 Model yükleniyor: {model_path}")
    model = YOLO(model_path)
    
    # Test görüntülerini bul
    test_img_dir = Path('test/images')
    if not test_img_dir.exists():
        print(f"❌ Test klasörü bulunamadı: {test_img_dir}")
        return
    
    images = list(test_img_dir.glob('*.jpg')) + list(test_img_dir.glob('*.png'))
    
    if not images:
        print("❌ Test görüntüsü bulunamadı!")
        return
    
    print(f"✓ {len(images)} test görüntüsü bulundu")
    
    # Rastgele örnekler seç
    num_samples = min(num_samples, len(images))
    sample_images = random.sample(images, num_samples)
    
    print(f"\n🔮 {num_samples} görüntü üzerinde tahmin yapılıyor...\n")
    
    # Tahminleri yap
    results = model.predict(
        source=sample_images,
        conf=0.25,
        save=True,
        project='runs/detect',
        name='quick_test'
    )
    
    # Sonuçları göster
    print("-" * 70)
    print("📊 Tahmin Sonuçları:")
    print("-" * 70)
    
    for i, (img_path, result) in enumerate(zip(sample_images, results), 1):
        print(f"\n📸 Görüntü {i}: {img_path.name}")
        
        if len(result.boxes) > 0:
            detections = {}
            for box in result.boxes:
                cls_id = int(box.cls[0])
                cls_name = result.names[cls_id]
                conf = float(box.conf[0])
                
                if cls_name not in detections:
                    detections[cls_name] = []
                detections[cls_name].append(conf)
            
            for cls_name, confs in detections.items():
                avg_conf = sum(confs) / len(confs)
                print(f"   • {cls_name}: {len(confs)} adet (ortalama güven: {avg_conf:.2f})")
        else:
            print("   • Tespit yok")
    
    print("\n" + "=" * 70)
    print("✅ Test tamamlandı!")
    print("=" * 70)
    print(f"\n📁 Sonuçlar kaydedildi: runs/detect/quick_test/")
    print("   Görüntüleri kontrol edin!\n")


def interactive_test():
    """İnteraktif test modu"""
    
    print("=" * 70)
    print("🎯 İnteraktif Model Test")
    print("=" * 70)
    print()
    
    model_path = input("Model yolu [runs/detect/train/weights/best.pt]: ").strip()
    if not model_path:
        model_path = 'runs/detect/train/weights/best.pt'
    
    if not Path(model_path).exists():
        print(f"❌ Model bulunamadı: {model_path}")
        return
    
    print(f"\n📦 Model yükleniyor...")
    model = YOLO(model_path)
    print("✓ Model yüklendi!")
    
    while True:
        print("\n" + "=" * 70)
        print("Seçenekler:")
        print("  1) Test setinden rastgele örnekler")
        print("  2) Belirli bir görüntü")
        print("  3) Test klasörünün tamamı")
        print("  4) Webcam")
        print("  5) Çıkış")
        print()
        
        choice = input("Seçiminiz (1-5): ").strip()
        
        if choice == '1':
            num = input("Kaç örnek? [5]: ").strip()
            num = int(num) if num else 5
            quick_test(model_path, num)
            
        elif choice == '2':
            img_path = input("Görüntü yolu: ").strip()
            if Path(img_path).exists():
                conf = input("Confidence threshold [0.25]: ").strip()
                conf = float(conf) if conf else 0.25
                
                print(f"\n🔮 Tahmin yapılıyor...")
                results = model.predict(img_path, conf=conf, save=True)
                
                for result in results:
                    print(f"\n📊 Tespit edilen nesneler:")
                    if len(result.boxes) > 0:
                        for box in result.boxes:
                            cls_name = result.names[int(box.cls[0])]
                            conf_score = float(box.conf[0])
                            print(f"   • {cls_name}: {conf_score:.2f}")
                    else:
                        print("   • Tespit yok")
                
                print(f"\n✓ Sonuç kaydedildi: runs/detect/predict/")
            else:
                print(f"❌ Görüntü bulunamadı: {img_path}")
        
        elif choice == '3':
            conf = input("Confidence threshold [0.25]: ").strip()
            conf = float(conf) if conf else 0.25
            
            print(f"\n🔮 Test klasörü işleniyor...")
            model.predict('test/images/', conf=conf, save=True)
            print(f"\n✓ Tamamlandı: runs/detect/predict/")
        
        elif choice == '4':
            conf = input("Confidence threshold [0.25]: ").strip()
            conf = float(conf) if conf else 0.25
            
            print(f"\n📹 Webcam başlatılıyor... (Çıkmak için 'q')")
            model.predict(0, conf=conf, show=True)
        
        elif choice == '5':
            print("\nÇıkılıyor...")
            break
        
        else:
            print("❌ Geçersiz seçim!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--interactive' or sys.argv[1] == '-i':
            interactive_test()
        elif sys.argv[1] == '--quick' or sys.argv[1] == '-q':
            num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            quick_test(num_samples=num_samples)
        else:
            print("Kullanım:")
            print("  python quick_test.py                    # Hızlı test (5 örnek)")
            print("  python quick_test.py -q 10              # 10 örnek test")
            print("  python quick_test.py -i                 # İnteraktif mod")
    else:
        # Varsayılan: hızlı test
        quick_test()
