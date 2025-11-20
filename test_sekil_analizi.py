#!/usr/bin/env python3
"""
Şekil Analizi Sistemi Test Scripti
Yuvarlak/daire şekillerin rulman olarak tanınması testi
"""

import cv2
import numpy as np
from pathlib import Path
from image_utils import GorselIslemci
from feature_matcher import FeatureMatchingTanima


def test_goruntu_olustur():
    """Test için basit şekiller içeren görüntü oluştur"""
    
    # 1. Daire şekli (Rulman benzeri)
    img_daire = np.ones((400, 400, 3), dtype=np.uint8) * 255
    cv2.circle(img_daire, (200, 200), 150, (100, 100, 100), -1)
    cv2.imwrite('test_images/test_daire.jpg', img_daire)
    print("✅ Daire şekli oluşturuldu: test_images/test_daire.jpg")
    
    # 2. Dikdörtgen şekli (Vida benzeri)
    img_dikdortgen = np.ones((400, 400, 3), dtype=np.uint8) * 255
    cv2.rectangle(img_dikdortgen, (150, 50), (250, 350), (100, 100, 100), -1)
    cv2.imwrite('test_images/test_dikdortgen.jpg', img_dikdortgen)
    print("✅ Dikdörtgen şekli oluşturuldu: test_images/test_dikdortgen.jpg")
    
    # 3. Altıgen (Somun benzeri)
    img_altigen = np.ones((400, 400, 3), dtype=np.uint8) * 255
    pts = np.array([
        [200, 50], [300, 125], [300, 275], 
        [200, 350], [100, 275], [100, 125]
    ], np.int32)
    cv2.fillPoly(img_altigen, [pts], (100, 100, 100))
    cv2.imwrite('test_images/test_altigen.jpg', img_altigen)
    print("✅ Altıgen şekli oluşturuldu: test_images/test_altigen.jpg")


def test_sekil_analizi():
    """Şekil analizi fonksiyonunu test et"""
    print("\n" + "="*60)
    print("🔬 Şekil Analizi Testi")
    print("="*60)
    
    test_dosyalar = [
        ('test_images/test_daire.jpg', 'Daire (Rulman bekleniyor)'),
        ('test_images/test_dikdortgen.jpg', 'Dikdörtgen (Vida bekleniyor)'),
        ('test_images/test_altigen.jpg', 'Altıgen (Somun bekleniyor)')
    ]
    
    for dosya, aciklama in test_dosyalar:
        if not Path(dosya).exists():
            print(f"⚠️  Dosya bulunamadı: {dosya}")
            continue
        
        print(f"\n📸 Test: {aciklama}")
        print(f"   Dosya: {dosya}")
        
        img = cv2.imread(dosya)
        sekiller = GorselIslemci.sekil_analizi(img)
        
        if sekiller:
            print(f"\n   ✅ {len(sekiller)} şekil tespit edildi:")
            for i, sekil in enumerate(sekiller, 1):
                print(f"\n   Şekil {i}:")
                print(f"      • Tip: {sekil['sekil']}")
                print(f"      • Dairesellik: {sekil['dairesellik']:.3f}")
                print(f"      • Alan: {sekil['alan']:.0f} px²")
                print(f"      • Köşe: {sekil['koseler']}")
                print(f"      • Merkez: {sekil['merkez']}")
                
                # Değerlendirme
                if sekil['dairesellik'] > 0.8:
                    print(f"      ✅ Sonuç: YÜKSEK DAİRESELLİK → Rulman/Somun olabilir")
                elif sekil['dairesellik'] > 0.6:
                    print(f"      🟡 Sonuç: ORTA DAİRESELLİK → Elips/Kayış olabilir")
                else:
                    print(f"      🔵 Sonuç: DÜŞÜK DAİRESELLİK → Çokgen/Dikdörtgen")
        else:
            print("   ❌ Şekil tespit edilemedi")


def test_bonus_sistemi():
    """Şekil bonus sistemini test et (referans görseller varsa)"""
    print("\n" + "="*60)
    print("🎯 Şekil Bonus Sistemi Testi")
    print("="*60)
    
    referans_klasor = Path('./referans_gorseller')
    
    # Referans görüntü sayısını kontrol et
    toplam_referans = sum(1 for _ in referans_klasor.rglob('*.jpg'))
    toplam_referans += sum(1 for _ in referans_klasor.rglob('*.png'))
    
    if toplam_referans == 0:
        print("\n⚠️  Referans görüntü bulunamadı!")
        print("   Şekil bonus sistemi test edilemiyor.")
        print("   Lütfen önce referans görüntüler ekleyin:")
        print("   referans_gorseller/rulman/rulman1.jpg")
        print("   referans_gorseller/vida/vida1.jpg")
        print("   vb...")
        return
    
    print(f"\n✅ {toplam_referans} referans görüntü bulundu")
    
    matcher = FeatureMatchingTanima(referans_klasor='./referans_gorseller')
    
    test_dosyalar = [
        'test_images/test_daire.jpg',
        'test_images/test_dikdortgen.jpg',
        'test_images/test_altigen.jpg'
    ]
    
    for dosya in test_dosyalar:
        if not Path(dosya).exists():
            continue
        
        print(f"\n📸 Test: {dosya}")
        
        try:
            # Şekil analizi KAPALI
            print("\n   [1] Şekil Analizi KAPALI:")
            sonuclar_off = matcher.tanima_yap(dosya, sekil_analizi_kullan=False)
            if sonuclar_off:
                for i, s in enumerate(sonuclar_off[:3], 1):
                    print(f"      {i}. {s['parca_adi']}: {s['skor']:.3f}")
            
            # Şekil analizi AÇIK
            print("\n   [2] Şekil Analizi AÇIK:")
            sonuclar_on = matcher.tanima_yap(dosya, sekil_analizi_kullan=True)
            if sonuclar_on:
                for i, s in enumerate(sonuclar_on[:3], 1):
                    bonus_info = f" (+{s['sekil_bonusu']:.2f} bonus)" if s.get('sekil_bonusu', 0) > 0 else ""
                    print(f"      {i}. {s['parca_adi']}: {s['skor']:.3f}{bonus_info}")
            
            # Farkı göster
            if sonuclar_off and sonuclar_on:
                print("\n   📊 FARK:")
                if sonuclar_off[0]['parca_adi'] != sonuclar_on[0]['parca_adi']:
                    print(f"      ✅ TAHMİN DEĞİŞTİ!")
                    print(f"         Önceki: {sonuclar_off[0]['parca_adi']}")
                    print(f"         Yeni: {sonuclar_on[0]['parca_adi']}")
                else:
                    print(f"      📌 Tahmin aynı kaldı: {sonuclar_on[0]['parca_adi']}")
                    if sonuclar_on[0].get('sekil_bonusu', 0) > 0:
                        print(f"         Ama güven arttı: {sonuclar_off[0]['skor']:.3f} → {sonuclar_on[0]['skor']:.3f}")
        
        except Exception as e:
            print(f"   ❌ Hata: {e}")


def main():
    """Ana test fonksiyonu"""
    print("="*60)
    print("🔷 Şekil Analizi ve Bonus Sistemi - Kapsamlı Test")
    print("="*60)
    
    # 1. Test görüntüleri oluştur
    print("\n[1/3] Test görüntüleri oluşturuluyor...")
    test_goruntu_olustur()
    
    # 2. Şekil analizi test
    print("\n[2/3] Şekil analizi testi yapılıyor...")
    test_sekil_analizi()
    
    # 3. Bonus sistemi test
    print("\n[3/3] Bonus sistemi testi yapılıyor...")
    test_bonus_sistemi()
    
    print("\n" + "="*60)
    print("✅ Tüm testler tamamlandı!")
    print("="*60)
    
    print("\n💡 Sonraki Adımlar:")
    print("   1. Referans görüntüler ekleyin: referans_gorseller/")
    print("   2. Streamlit uygulamasını çalıştırın: streamlit run app.py")
    print("   3. Test görüntülerini yükleyip sonuçları karşılaştırın")


if __name__ == "__main__":
    main()
