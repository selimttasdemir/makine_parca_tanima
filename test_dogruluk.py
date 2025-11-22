"""
Web uygulaması için model doğruluğu test scriptı
Test seti üzerinde detaylı performans analizi yapar
"""

import os
import cv2
import numpy as np
from pathlib import Path
import yaml
from collections import defaultdict
import json

class ModelDogrulukTest:
    def __init__(self, test_path='test', yaml_path='mech_parts_data.yaml'):
        self.test_path = Path(test_path)
        self.yaml_path = yaml_path
        self.sinif_isimleri = self.yaml_yukle()
        self.sonuclar = defaultdict(lambda: {'dogru': 0, 'yanlis': 0, 'toplam': 0})
        
    def yaml_yukle(self):
        """YAML dosyasından sınıf isimlerini yükle"""
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data['names']
    
    def etiket_oku(self, etiket_path):
        """YOLO formatındaki etiket dosyasını oku"""
        if not etiket_path.exists():
            return []
        
        etiketler = []
        with open(etiket_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    sinif_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                    etiketler.append({
                        'sinif_id': sinif_id,
                        'sinif_adi': self.sinif_isimleri[sinif_id],
                        'bbox': [x_center, y_center, width, height]
                    })
        return etiketler
    
    def test_seti_analizi(self):
        """Test setindeki tüm görüntüleri analiz et"""
        images_path = self.test_path / 'images'
        labels_path = self.test_path / 'labels'
        
        if not images_path.exists():
            return None
        
        # Tüm görüntüleri al
        image_files = list(images_path.glob('*.jpg')) + \
                     list(images_path.glob('*.jpeg')) + \
                     list(images_path.glob('*.png'))
        
        toplam_nesne = 0
        sinif_dagilimi = defaultdict(int)
        
        for img_file in image_files:
            # Karşılık gelen etiket dosyasını bul
            label_file = labels_path / f"{img_file.stem}.txt"
            
            etiketler = self.etiket_oku(label_file)
            toplam_nesne += len(etiketler)
            
            for etiket in etiketler:
                sinif_dagilimi[etiket['sinif_adi']] += 1
        
        return {
            'toplam_goruntu': len(image_files),
            'toplam_nesne': toplam_nesne,
            'sinif_dagilimi': dict(sinif_dagilimi),
            'ortalama_nesne': toplam_nesne / len(image_files) if image_files else 0
        }
    
    def model_test_et(self, model, limit=None):
        """
        Model ile test seti üzerinde tahmin yap ve doğruluğu hesapla
        
        Args:
            model: YOLO modeli (ultralytics YOLO objesi)
            limit: Test edilecek maksimum görüntü sayısı (None = hepsi)
        """
        images_path = self.test_path / 'images'
        labels_path = self.test_path / 'labels'
        
        if not images_path.exists():
            return None
        
        image_files = list(images_path.glob('*.jpg')) + \
                     list(images_path.glob('*.jpeg')) + \
                     list(images_path.glob('*.png'))
        
        if limit:
            image_files = image_files[:limit]
        
        toplam_dogru = 0
        toplam_yanlis = 0
        toplam_nesne = 0
        
        detayli_sonuclar = []
        
        for img_file in image_files:
            # Gerçek etiketleri oku
            label_file = labels_path / f"{img_file.stem}.txt"
            gercek_etiketler = self.etiket_oku(label_file)
            
            # Model tahmini yap
            results = model.predict(str(img_file), verbose=False)
            
            if len(results) > 0 and results[0].boxes is not None:
                tahminler = []
                boxes = results[0].boxes
                
                for box in boxes:
                    sinif_id = int(box.cls[0])
                    guven = float(box.conf[0])
                    tahminler.append({
                        'sinif_id': sinif_id,
                        'sinif_adi': self.sinif_isimleri[sinif_id],
                        'guven': guven
                    })
                
                # Her nesne için doğruluğu kontrol et
                for gercek in gercek_etiketler:
                    toplam_nesne += 1
                    gercek_sinif = gercek['sinif_adi']
                    
                    # En yüksek güvenli tahmin
                    if tahminler:
                        en_iyi_tahmin = max(tahminler, key=lambda x: x['guven'])
                        tahmin_sinif = en_iyi_tahmin['sinif_adi']
                        guven = en_iyi_tahmin['guven']
                        
                        if tahmin_sinif == gercek_sinif:
                            toplam_dogru += 1
                            self.sonuclar[gercek_sinif]['dogru'] += 1
                        else:
                            toplam_yanlis += 1
                            self.sonuclar[gercek_sinif]['yanlis'] += 1
                        
                        self.sonuclar[gercek_sinif]['toplam'] += 1
                        
                        detayli_sonuclar.append({
                            'goruntu': img_file.name,
                            'gercek': gercek_sinif,
                            'tahmin': tahmin_sinif,
                            'guven': guven,
                            'dogru': tahmin_sinif == gercek_sinif
                        })
                    else:
                        toplam_yanlis += 1
                        self.sonuclar[gercek_sinif]['yanlis'] += 1
                        self.sonuclar[gercek_sinif]['toplam'] += 1
            else:
                # Tahmin yapılamadı
                for gercek in gercek_etiketler:
                    toplam_yanlis += 1
                    gercek_sinif = gercek['sinif_adi']
                    self.sonuclar[gercek_sinif]['yanlis'] += 1
                    self.sonuclar[gercek_sinif]['toplam'] += 1
        
        # Genel doğruluk
        genel_dogruluk = toplam_dogru / toplam_nesne if toplam_nesne > 0 else 0
        
        # Sınıf bazında doğruluk
        sinif_dogruluk = {}
        for sinif, stats in self.sonuclar.items():
            if stats['toplam'] > 0:
                sinif_dogruluk[sinif] = stats['dogru'] / stats['toplam']
        
        return {
            'genel_dogruluk': genel_dogruluk,
            'toplam_dogru': toplam_dogru,
            'toplam_yanlis': toplam_yanlis,
            'toplam_nesne': toplam_nesne,
            'test_edilen_goruntu': len(image_files),
            'sinif_dogruluk': sinif_dogruluk,
            'sinif_istatistik': dict(self.sonuclar),
            'detayli_sonuclar': detayli_sonuclar
        }
    
    def sonuclari_kaydet(self, sonuclar, kayit_yolu='test_sonuclari.json'):
        """Test sonuçlarını JSON dosyasına kaydet"""
        with open(kayit_yolu, 'w', encoding='utf-8') as f:
            json.dump(sonuclar, f, ensure_ascii=False, indent=2)
        print(f"✅ Sonuçlar kaydedildi: {kayit_yolu}")


def main():
    """Örnek kullanım"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Model doğruluk testi')
    parser.add_argument('--model', type=str, default='runs/detect/train/weights/best.pt',
                       help='Model dosyası yolu')
    parser.add_argument('--test', type=str, default='test',
                       help='Test klasörü yolu')
    parser.add_argument('--limit', type=int, default=None,
                       help='Test edilecek maksimum görüntü sayısı')
    parser.add_argument('--save', type=str, default='test_sonuclari.json',
                       help='Sonuçların kaydedileceği dosya')
    
    args = parser.parse_args()
    
    print("🔍 Model Doğruluk Testi Başlatılıyor...")
    print(f"Model: {args.model}")
    print(f"Test Klasörü: {args.test}")
    
    # Test sınıfını oluştur
    tester = ModelDogrulukTest(test_path=args.test)
    
    # Önce test setini analiz et
    print("\n📊 Test Seti Analizi:")
    analiz = tester.test_seti_analizi()
    if analiz:
        print(f"  Toplam Görüntü: {analiz['toplam_goruntu']}")
        print(f"  Toplam Nesne: {analiz['toplam_nesne']}")
        print(f"  Ortalama Nesne/Görüntü: {analiz['ortalama_nesne']:.2f}")
        print(f"\n  Sınıf Dağılımı:")
        for sinif, sayi in analiz['sinif_dagilimi'].items():
            print(f"    - {sinif}: {sayi}")
    
    # Modeli yükle ve test et
    try:
        from ultralytics import YOLO
        
        if not Path(args.model).exists():
            print(f"\n❌ Model dosyası bulunamadı: {args.model}")
            print("   Lütfen önce modeli eğitin: python train_yolo_model.py --mode train")
            return
        
        print(f"\n📦 Model Yükleniyor: {args.model}")
        model = YOLO(args.model)
        
        print("\n🧪 Test Ediliyor...")
        if args.limit:
            print(f"   (İlk {args.limit} görüntü test edilecek)")
        
        sonuclar = tester.model_test_et(model, limit=args.limit)
        
        if sonuclar:
            print("\n" + "="*60)
            print("📈 TEST SONUÇLARI")
            print("="*60)
            print(f"\n✅ Genel Doğruluk: %{sonuclar['genel_dogruluk']*100:.2f}")
            print(f"   Doğru: {sonuclar['toplam_dogru']}/{sonuclar['toplam_nesne']}")
            print(f"   Yanlış: {sonuclar['toplam_yanlis']}/{sonuclar['toplam_nesne']}")
            print(f"   Test Edilen Görüntü: {sonuclar['test_edilen_goruntu']}")
            
            print(f"\n📊 Sınıf Bazında Doğruluk:")
            for sinif, dogruluk in sorted(sonuclar['sinif_dogruluk'].items(), 
                                         key=lambda x: x[1], reverse=True):
                stats = sonuclar['sinif_istatistik'][sinif]
                print(f"   {sinif:12s}: %{dogruluk*100:5.2f} "
                      f"({stats['dogru']}/{stats['toplam']} doğru)")
            
            # En kötü tahminler
            yanlis_tahminler = [s for s in sonuclar['detayli_sonuclar'] if not s['dogru']]
            if yanlis_tahminler:
                print(f"\n❌ Yanlış Tahmin Örnekleri (İlk 5):")
                for i, yanlis in enumerate(yanlis_tahminler[:5], 1):
                    print(f"   {i}. {yanlis['goruntu']}")
                    print(f"      Gerçek: {yanlis['gercek']} | "
                          f"Tahmin: {yanlis['tahmin']} (Güven: %{yanlis['guven']*100:.1f})")
            
            # Sonuçları kaydet
            tester.sonuclari_kaydet(sonuclar, args.save)
            print(f"\n💾 Detaylı sonuçlar kaydedildi: {args.save}")
            
    except ImportError:
        print("\n❌ Ultralytics kütüphanesi bulunamadı!")
        print("   Yüklemek için: pip install ultralytics")
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")


if __name__ == "__main__":
    main()
