"""
Sistem Testi ve Demo
Tüm özellikleri test eden demo script
"""

import os
from pathlib import Path


def print_banner(text):
    """Güzel banner yazdır"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def test_kurulum():
    """Kurulumu test et"""
    print_banner("📦 KURULUM KONTROLÜ")
    
    # Gerekli dosyalar
    gerekli_dosyalar = [
        'app.py',
        'feature_matcher.py',
        'hybrid_detector.py',
        'train_model.py',
        'image_utils.py',
        'requirements.txt'
    ]
    
    for dosya in gerekli_dosyalar:
        if Path(dosya).exists():
            print(f"✅ {dosya}")
        else:
            print(f"❌ {dosya} - EKSİK!")
    
    # Gerekli klasörler
    gerekli_klasorler = [
        'referans_gorseller',
        'test_images',
        'training_data'
    ]
    
    print()
    for klasor in gerekli_klasorler:
        if Path(klasor).exists():
            # Alt klasörleri say
            alt_klasorler = len(list(Path(klasor).iterdir()))
            print(f"✅ {klasor}/ ({alt_klasorler} alt klasör)")
        else:
            print(f"❌ {klasor}/ - EKSİK!")


def test_import():
    """Import kontrolü"""
    print_banner("🔧 MODÜL KONTROLÜ")
    
    moduller = {
        'streamlit': 'Web arayüzü',
        'cv2': 'OpenCV - Görüntü işleme',
        'torch': 'PyTorch - Deep learning',
        'torchvision': 'PyTorch vision',
        'numpy': 'Numerik hesaplamalar',
        'PIL': 'Görüntü işleme',
    }
    
    for modul, aciklama in moduller.items():
        try:
            __import__(modul)
            print(f"✅ {modul:20s} - {aciklama}")
        except ImportError:
            print(f"❌ {modul:20s} - YÜKLÜ DEĞİL! ({aciklama})")


def test_feature_matching():
    """Feature matching test"""
    print_banner("🔍 FEATURE MATCHING TESTİ")
    
    try:
        from feature_matcher import FeatureMatchingTanima
        
        # Referans klasörü var mı?
        if not Path('referans_gorseller').exists():
            print("⚠️  referans_gorseller/ klasörü bulunamadı")
            print("   Önce: ./setup_folders.sh çalıştırın")
            return
        
        # Matcher oluştur
        matcher = FeatureMatchingTanima('./referans_gorseller')
        
        ref_sayisi = len(matcher.referans_veritabani)
        print(f"✅ Feature Matcher başlatıldı")
        print(f"   Yüklenen referans: {ref_sayisi} görüntü")
        
        if ref_sayisi == 0:
            print("\n⚠️  Hiç referans görüntü yok!")
            print("   referans_gorseller/vida/ klasörüne örnek görüntüler ekleyin")
        else:
            print("\n🎉 Feature matching sistemi hazır!")
            
    except Exception as e:
        print(f"❌ Hata: {e}")


def test_deep_learning():
    """Deep learning model kontrolü"""
    print_banner("🧠 DEEP LEARNING KONTROLÜ")
    
    model_path = 'best_model.pth'
    
    if Path(model_path).exists():
        print(f"✅ Model bulundu: {model_path}")
        
        try:
            import torch
            checkpoint = torch.load(model_path, map_location='cpu')
            siniflar = checkpoint.get('classes', [])
            epoch = checkpoint.get('epoch', 'bilinmiyor')
            val_acc = checkpoint.get('val_acc', 'bilinmiyor')
            
            print(f"   Sınıf sayısı: {len(siniflar)}")
            print(f"   Epoch: {epoch}")
            print(f"   Val Accuracy: {val_acc}")
            print(f"   Sınıflar: {', '.join(siniflar)}")
            
        except Exception as e:
            print(f"⚠️  Model yüklenirken hata: {e}")
    else:
        print(f"ℹ️  Model bulunamadı: {model_path}")
        print("   Model eğitmek için:")
        print("   python train_model.py --mode train --data_dir ./training_data")


def test_hibrit_sistem():
    """Hibrit sistem kontrolü"""
    print_banner("🚀 HİBRİT SİSTEM KONTROLÜ")
    
    try:
        from hybrid_detector import HibritTanima
        
        model_path = 'best_model.pth' if Path('best_model.pth').exists() else None
        referans_path = 'referans_gorseller' if Path('referans_gorseller').exists() else None
        
        sistem = HibritTanima(
            model_path=model_path,
            referans_klasor=referans_path,
            mod='auto'
        )
        
        print("Sistem Durumu:")
        print(f"  Deep Learning: {'✅ Aktif' if sistem.dl_kullanilabilir else '❌ Pasif'}")
        print(f"  Feature Matching: {'✅ Aktif' if sistem.feature_kullanilabilir else '❌ Pasif'}")
        
        if sistem.dl_kullanilabilir and sistem.feature_kullanilabilir:
            print("\n🎉 Hibrit sistem TAM DONANIM!")
        elif sistem.dl_kullanilabilir or sistem.feature_kullanilabilir:
            print("\n⚠️  Hibrit sistem kısmen aktif")
            if not sistem.dl_kullanilabilir:
                print("   → Model eğitin: python train_model.py")
            if not sistem.feature_kullanilabilir:
                print("   → Referans görüntüler ekleyin")
        else:
            print("\n❌ Hibrit sistem pasif")
            print("   Hem model hem de referans görüntüler gerekli")
            
    except Exception as e:
        print(f"❌ Hata: {e}")


def test_dosyalar():
    """Veri dosyalarını kontrol et"""
    print_banner("📁 VERİ DOSYALARI KONTROLÜ")
    
    # Referans görüntüler
    print("Referans Görüntüler:")
    if Path('referans_gorseller').exists():
        parcalar = list(Path('referans_gorseller').iterdir())
        toplam = 0
        for parca in parcalar:
            if parca.is_dir():
                goruntuler = list(parca.glob('*.jpg')) + list(parca.glob('*.png'))
                sayi = len(goruntuler)
                toplam += sayi
                emoji = "✅" if sayi >= 5 else "⚠️ " if sayi > 0 else "❌"
                print(f"  {emoji} {parca.name:15s}: {sayi} görüntü")
        
        print(f"\n  Toplam: {toplam} referans görüntü")
        
        if toplam == 0:
            print("\n  💡 İpucu: Her parça için 5-10 örnek görüntü ekleyin")
    else:
        print("  ❌ referans_gorseller/ klasörü bulunamadı")
    
    # Test görüntüleri
    print("\nTest Görüntüleri:")
    if Path('test_images').exists():
        test_imgs = list(Path('test_images').glob('*.jpg')) + list(Path('test_images').glob('*.png'))
        print(f"  {len(test_imgs)} test görüntüsü")
        for img in test_imgs[:5]:
            print(f"    - {img.name}")
    else:
        print("  ❌ test_images/ klasörü bulunamadı")
    
    # Training data
    print("\nEğitim Verileri:")
    if Path('training_data').exists():
        parcalar = list(Path('training_data').iterdir())
        toplam = 0
        for parca in parcalar:
            if parca.is_dir():
                goruntuler = list(parca.glob('*.jpg')) + list(parca.glob('*.png'))
                sayi = len(goruntuler)
                toplam += sayi
                if sayi > 0:
                    emoji = "✅" if sayi >= 100 else "⚠️ "
                    print(f"  {emoji} {parca.name:15s}: {sayi} görüntü")
        
        print(f"\n  Toplam: {toplam} eğitim görüntüsü")
        
        if toplam > 0 and toplam < 500:
            print("  💡 İpucu: İyi sonuçlar için sınıf başına 100+ görüntü ekleyin")
    else:
        print("  ❌ training_data/ klasörü bulunamadı")


def ozet():
    """Genel özet"""
    print_banner("📊 GENEL ÖZET VE ÖNERİLER")
    
    # Durum değerlendirmesi
    durum = {
        'dosyalar': Path('app.py').exists(),
        'moduller': True,  # Basitleştirilmiş
        'referans': len(list(Path('referans_gorseller').glob('*/*.jpg'))) > 0 if Path('referans_gorseller').exists() else False,
        'model': Path('best_model.pth').exists(),
    }
    
    print("Sistem Durumu:")
    for anahtar, deger in durum.items():
        emoji = "✅" if deger else "❌"
        print(f"  {emoji} {anahtar.title()}")
    
    print("\nÖnerilen Adımlar:")
    
    if not durum['referans']:
        print("\n1️⃣  REFERANS GÖRÜNTÜLER EKLE (ÖNCELİKLİ)")
        print("   └─ Her parça için 5-10 örnek görüntü")
        print("   └─ referans_gorseller/vida/vida1.jpg")
        print("   └─ Feature matching için yeterli!")
    
    if durum['referans'] and not durum['model']:
        print("\n2️⃣  MODEL EĞİT (İSTEĞE BAĞLI)")
        print("   └─ Daha yüksek doğruluk için")
        print("   └─ python train_model.py --mode train --data_dir ./training_data")
    
    print("\n3️⃣  SİSTEMİ KULLAN")
    print("   └─ streamlit run app.py")
    print("   └─ http://localhost:8501")
    
    print("\n📚 Daha Fazla Bilgi:")
    print("   QUICKSTART.md          - Hızlı başlangıç")
    print("   YONTEM_KARSILASTIRMA.md - Yöntem detayları")
    print("   EXAMPLES.md            - Kod örnekleri")
    print("   PROJE_OZETI.md         - Genel özet")


def main():
    """Ana test fonksiyonu"""
    print("\n" + "🔧" * 35)
    print("   MAKİNE PARÇASI TANIMA SİSTEMİ - SİSTEM TESTİ")
    print("🔧" * 35)
    
    test_kurulum()
    test_import()
    test_dosyalar()
    test_feature_matching()
    test_deep_learning()
    test_hibrit_sistem()
    ozet()
    
    print("\n" + "🔧" * 35)
    print("   TEST TAMAMLANDI!")
    print("🔧" * 35 + "\n")


if __name__ == "__main__":
    main()
