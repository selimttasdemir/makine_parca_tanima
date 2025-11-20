"""
Hibrit Parça Tanıma Sistemi
Hem Deep Learning hem de Feature Matching kullanan akıllı sistem
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import json
import warnings

# PyTorch uyarılarını bastır
warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', message='.*torch.*')

# Lazy imports
def lazy_import_torch():
    """Sadece gerektiğinde torch import et"""
    import torch
    import torch.nn as nn
    from torchvision import transforms
    from PIL import Image
    return torch, nn, transforms, Image

try:
    from feature_matcher import FeatureMatchingTanima
    FEATURE_AVAILABLE = True
except ImportError:
    FEATURE_AVAILABLE = False
    print("⚠️  Feature matcher yüklenemedi")


class HibritTanima:
    """
    İki yöntemi birleştiren akıllı tanıma sistemi:
    1. Deep Learning model varsa kullan (yüksek doğruluk)
    2. Model yoksa veya güven düşükse Feature Matching kullan
    3. Her iki sonucu birleştir (ensemble)
    """
    
    def __init__(
        self, 
        model_path=None,
        referans_klasor=None,
        guven_esik=0.7,
        mod='auto'
    ):
        """
        Args:
            model_path: Eğitilmiş DL model yolu
            referans_klasor: Referans görüntüler klasörü
            guven_esik: Bu değerin altında feature matching devreye girer
            mod: 'dl_only', 'feature_only', 'auto', 'ensemble'
        """
        self.guven_esik = guven_esik
        self.mod = mod
        
        # Deep Learning modeli
        self.dl_model = None
        self.dl_siniflar = None
        self.dl_kullanilabilir = False
        
        if model_path and Path(model_path).exists():
            self._dl_model_yukle(model_path)
        
        # Feature Matching sistemi
        self.feature_matcher = None
        self.feature_kullanilabilir = False
        
        if FEATURE_AVAILABLE and referans_klasor and Path(referans_klasor).exists():
            self.feature_matcher = FeatureMatchingTanima(referans_klasor)
            self.feature_kullanilabilir = len(self.feature_matcher.referans_veritabani) > 0
        
        # Transform lazy olacak
        self.transform = None
        
        self._sistem_durumu()
    
    def _dl_model_yukle(self, model_path):
        """Deep Learning modelini yükle"""
        try:
            torch, nn, transforms_lib, Image_lib = lazy_import_torch()
            from train_model import MakineParcaModel
            
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
            self.dl_siniflar = checkpoint['classes']
            
            self.dl_model = MakineParcaModel(
                num_classes=len(self.dl_siniflar),
                pretrained=False
            )
            self.dl_model.load_state_dict(checkpoint['model_state_dict'])
            self.dl_model.eval()
            
            self.dl_kullanilabilir = True
            print(f"✅ DL Model yüklendi: {len(self.dl_siniflar)} sınıf")
            
        except Exception as e:
            print(f"⚠️  DL Model yüklenemedi: {e}")
            self.dl_kullanilabilir = False
    
    def _sistem_durumu(self):
        """Sistem durumunu göster"""
        print("\n" + "=" * 60)
        print("🤖 Hibrit Tanıma Sistemi Durumu")
        print("=" * 60)
        
        if self.dl_kullanilabilir:
            print(f"✅ Deep Learning: Aktif ({len(self.dl_siniflar)} sınıf)")
        else:
            print("❌ Deep Learning: Pasif")
        
        if self.feature_kullanilabilir:
            ref_sayisi = len(self.feature_matcher.referans_veritabani)
            print(f"✅ Feature Matching: Aktif ({ref_sayisi} referans)")
        else:
            print("❌ Feature Matching: Pasif")
        
        print(f"⚙️  Mod: {self.mod}")
        print(f"📊 Güven Eşiği: {self.guven_esik}")
        print("=" * 60 + "\n")
    
    def _dl_tahmin(self, goruntu_path: str) -> Dict:
        """Deep Learning ile tahmin"""
        torch, nn, transforms_lib, Image_lib = lazy_import_torch()
        
        # Transform oluştur
        transform = transforms_lib.Compose([
            transforms_lib.Resize((224, 224)),
            transforms_lib.ToTensor(),
            transforms_lib.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        image = Image_lib.open(goruntu_path).convert('RGB')
        image_tensor = transform(image).unsqueeze(0)
        
        with torch.no_grad():
            outputs = self.dl_model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = probabilities.max(1)
        
        predicted_class = self.dl_siniflar[predicted.item()]
        confidence_score = confidence.item()
        
        # Tüm sınıf olasılıkları
        all_probs = {}
        for i, sinif in enumerate(self.dl_siniflar):
            all_probs[sinif] = probabilities[0][i].item()
        
        return {
            'method': 'deep_learning',
            'parca': predicted_class,
            'guven': confidence_score,
            'olasiliklar': all_probs
        }
    
    def _feature_tahmin(self, goruntu_path: str) -> Dict:
        """Feature Matching ile tahmin (Şekil analizi dahil)"""
        # Şekil analizi ile tanıma yap
        sonuclar = self.feature_matcher.tanima_yap(
            goruntu_path, 
            method='hybrid',
            sekil_analizi_kullan=True  # Şekil analizini aktifleştir
        )
        
        if not sonuclar:
            return {
                'method': 'feature_matching',
                'parca': 'bilinmiyor',
                'guven': 0.0,
                'detaylar': []
            }
        
        en_iyi = sonuclar[0]
        
        return {
            'method': 'feature_matching',
            'parca': en_iyi['parca_adi'],
            'guven': en_iyi['skor'],
            'base_skor': en_iyi.get('base_skor', en_iyi['skor']),
            'sekil_bonusu': en_iyi.get('sekil_bonusu', 0),
            'detaylar': sonuclar[:3],  # En iyi 3
            'sift_skor': en_iyi['sift_skor'],
            'histogram_skor': en_iyi['histogram_skor'],
            'hu_skor': en_iyi['hu_skor']
        }
    
    def _ensemble_tahmin(self, dl_sonuc: Dict, feature_sonuc: Dict) -> Dict:
        """İki yöntemi birleştir"""
        # Ağırlıklı birleştirme
        dl_agirlik = 0.7  # DL daha güvenilir
        feature_agirlik = 0.3
        
        # Her parça için toplam skor hesapla
        parca_skorlari = {}
        
        # DL skorları
        if dl_sonuc:
            for parca, olasilik in dl_sonuc.get('olasiliklar', {}).items():
                parca_skorlari[parca] = dl_agirlik * olasilik
        
        # Feature matching skorları
        if feature_sonuc and feature_sonuc.get('detaylar'):
            for detay in feature_sonuc['detaylar']:
                parca = detay['parca_adi']
                skor = detay['skor']
                
                if parca in parca_skorlari:
                    parca_skorlari[parca] += feature_agirlik * skor
                else:
                    parca_skorlari[parca] = feature_agirlik * skor
        
        # En yüksek skoru bul
        if parca_skorlari:
            en_iyi_parca = max(parca_skorlari.items(), key=lambda x: x[1])
            
            return {
                'method': 'ensemble',
                'parca': en_iyi_parca[0],
                'guven': en_iyi_parca[1],
                'dl_sonuc': dl_sonuc,
                'feature_sonuc': feature_sonuc,
                'tum_skorlar': parca_skorlari
            }
        
        # Fallback
        if dl_sonuc:
            return dl_sonuc
        elif feature_sonuc:
            return feature_sonuc
        else:
            return {'method': 'none', 'parca': 'bilinmiyor', 'guven': 0.0}
    
    def tanima_yap(self, goruntu_path: str) -> Dict:
        """
        Akıllı tanıma yap
        
        Strateji:
        - auto: DL önce, güven düşükse feature matching ekle
        - ensemble: Her ikisini de kullan ve birleştir
        - dl_only: Sadece deep learning
        - feature_only: Sadece feature matching
        """
        if not Path(goruntu_path).exists():
            raise FileNotFoundError(f"Görüntü bulunamadı: {goruntu_path}")
        
        print(f"\n🔍 Görüntü analiz ediliyor: {goruntu_path}")
        print("-" * 60)
        
        dl_sonuc = None
        feature_sonuc = None
        
        # Mod'a göre işle
        if self.mod == 'dl_only':
            if not self.dl_kullanilabilir:
                raise ValueError("DL model yüklü değil!")
            dl_sonuc = self._dl_tahmin(goruntu_path)
            final_sonuc = dl_sonuc
            
        elif self.mod == 'feature_only':
            if not self.feature_kullanilabilir:
                raise ValueError("Feature matching sistemi yüklü değil!")
            feature_sonuc = self._feature_tahmin(goruntu_path)
            final_sonuc = feature_sonuc
            
        elif self.mod == 'ensemble':
            if self.dl_kullanilabilir:
                dl_sonuc = self._dl_tahmin(goruntu_path)
                print(f"  DL: {dl_sonuc['parca']} (güven: {dl_sonuc['guven']:.3f})")
            
            if self.feature_kullanilabilir:
                feature_sonuc = self._feature_tahmin(goruntu_path)
                print(f"  FM: {feature_sonuc['parca']} (güven: {feature_sonuc['guven']:.3f})")
            
            final_sonuc = self._ensemble_tahmin(dl_sonuc, feature_sonuc)
            
        else:  # auto
            # Önce DL dene
            if self.dl_kullanilabilir:
                dl_sonuc = self._dl_tahmin(goruntu_path)
                print(f"  DL: {dl_sonuc['parca']} (güven: {dl_sonuc['guven']:.3f})")
                
                if dl_sonuc['guven'] >= self.guven_esik:
                    # Yeterince güvenli
                    final_sonuc = dl_sonuc
                else:
                    # Güven düşük, feature matching ekle
                    if self.feature_kullanilabilir:
                        print("  ⚠️  DL güveni düşük, Feature Matching ekleniyor...")
                        feature_sonuc = self._feature_tahmin(goruntu_path)
                        print(f"  FM: {feature_sonuc['parca']} (güven: {feature_sonuc['guven']:.3f})")
                        final_sonuc = self._ensemble_tahmin(dl_sonuc, feature_sonuc)
                    else:
                        final_sonuc = dl_sonuc
            
            elif self.feature_kullanilabilir:
                # DL yok, sadece feature matching
                feature_sonuc = self._feature_tahmin(goruntu_path)
                final_sonuc = feature_sonuc
            
            else:
                raise ValueError("Hiçbir tanıma yöntemi aktif değil!")
        
        print("-" * 60)
        print(f"✅ Sonuç: {final_sonuc['parca'].upper()} "
              f"(güven: {final_sonuc['guven']:.3f}, "
              f"yöntem: {final_sonuc['method']})\n")
        
        return final_sonuc
    
    def toplu_test(self, test_klasor: str) -> List[Dict]:
        """Bir klasördeki tüm görüntüleri test et"""
        test_path = Path(test_klasor)
        sonuclar = []
        
        for img_path in test_path.glob('*.jpg'):
            try:
                sonuc = self.tanima_yap(str(img_path))
                sonuclar.append({
                    'dosya': img_path.name,
                    **sonuc
                })
            except Exception as e:
                print(f"❌ Hata ({img_path.name}): {e}")
        
        for img_path in test_path.glob('*.png'):
            try:
                sonuc = self.tanima_yap(str(img_path))
                sonuclar.append({
                    'dosya': img_path.name,
                    **sonuc
                })
            except Exception as e:
                print(f"❌ Hata ({img_path.name}): {e}")
        
        return sonuclar


def karsilastirma_testi():
    """İki yöntemi karşılaştırmalı test et"""
    print("\n" + "=" * 70)
    print("🔬 HİBRİT SİSTEM KARŞILAŞTIRMALI TEST")
    print("=" * 70)
    
    # Test görüntüsü
    test_img = './test_images/vida1.jpg'
    
    if not Path(test_img).exists():
        print(f"⚠️  Test görüntüsü bulunamadı: {test_img}")
        print("\nÖnce test_images/ klasörüne örnek görüntüler ekleyin!")
        return
    
    # 1. Sadece Feature Matching
    print("\n1️⃣  FEATURE MATCHING ONLY")
    print("-" * 70)
    try:
        sistem1 = HibritTanima(
            referans_klasor='./referans_gorseller',
            mod='feature_only'
        )
        sonuc1 = sistem1.tanima_yap(test_img)
    except Exception as e:
        print(f"❌ Feature Matching hatası: {e}")
        sonuc1 = None
    
    # 2. Sadece Deep Learning (varsa)
    print("\n2️⃣  DEEP LEARNING ONLY")
    print("-" * 70)
    try:
        sistem2 = HibritTanima(
            model_path='best_model.pth',
            mod='dl_only'
        )
        sonuc2 = sistem2.tanima_yap(test_img)
    except Exception as e:
        print(f"❌ Deep Learning hatası: {e}")
        sonuc2 = None
    
    # 3. Hibrit (Auto)
    print("\n3️⃣  HYBRID (AUTO)")
    print("-" * 70)
    try:
        sistem3 = HibritTanima(
            model_path='best_model.pth',
            referans_klasor='./referans_gorseller',
            mod='auto',
            guven_esik=0.7
        )
        sonuc3 = sistem3.tanima_yap(test_img)
    except Exception as e:
        print(f"❌ Hibrit hatası: {e}")
        sonuc3 = None
    
    # 4. Ensemble
    print("\n4️⃣  ENSEMBLE")
    print("-" * 70)
    try:
        sistem4 = HibritTanima(
            model_path='best_model.pth',
            referans_klasor='./referans_gorseller',
            mod='ensemble'
        )
        sonuc4 = sistem4.tanima_yap(test_img)
    except Exception as e:
        print(f"❌ Ensemble hatası: {e}")
        sonuc4 = None
    
    # Karşılaştırma
    print("\n" + "=" * 70)
    print("📊 KARŞILAŞTIRMA SONUÇLARI")
    print("=" * 70)
    
    sonuclar = [
        ("Feature Matching", sonuc1),
        ("Deep Learning", sonuc2),
        ("Hybrid Auto", sonuc3),
        ("Ensemble", sonuc4)
    ]
    
    for yontem, sonuc in sonuclar:
        if sonuc:
            print(f"\n{yontem}:")
            print(f"  Parça: {sonuc['parca']}")
            print(f"  Güven: {sonuc['guven']:.3f}")
        else:
            print(f"\n{yontem}: Kullanılamadı")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    karsilastirma_testi()
