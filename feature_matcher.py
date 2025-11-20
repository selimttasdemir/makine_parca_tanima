"""
Görüntü Benzerlik Tabanlı Parça Tanıma Sistemi
Feature matching ve görsel benzerlik kullanarak tanıma yapar
"""

import cv2
import numpy as np
from pathlib import Path
import pickle
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
from image_utils import GorselIslemci


@dataclass
class ReferansGoruntu:
    """Referans görüntü bilgisi"""
    parca_adi: str
    goruntu_path: str
    keypoints: List
    descriptors: np.ndarray
    histogram: np.ndarray
    hu_moments: np.ndarray
    
    
class FeatureMatchingTanima:
    """
    Görüntü benzerlik tabanlı tanıma sistemi
    - SIFT/ORB feature matching
    - Histogram karşılaştırma
    - Hu moments
    - SSIM (Structural Similarity)
    """
    
    def __init__(self, referans_klasor=None):
        """
        Args:
            referans_klasor: Referans görüntülerin bulunduğu klasör
                Yapı: referans_klasor/parca_adi/goruntu.jpg
        """
        self.referans_klasor = referans_klasor
        self.referans_veritabani = []
        
        # Feature detectors
        self.sift = cv2.SIFT_create()
        self.orb = cv2.ORB_create(nfeatures=1000)
        
        # Feature matcher
        self.bf_matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        
        if referans_klasor and Path(referans_klasor).exists():
            self.referans_yukle()
    
    def referans_yukle(self):
        """Referans görüntüleri yükle ve özelliklerini çıkar"""
        print("📚 Referans veritabanı yükleniyor...")
        
        referans_path = Path(self.referans_klasor)
        
        for parca_klasor in referans_path.iterdir():
            if not parca_klasor.is_dir():
                continue
            
            parca_adi = parca_klasor.name
            print(f"  → {parca_adi} parçası işleniyor...")
            
            for img_path in parca_klasor.glob('*.jpg'):
                self._referans_ekle(str(img_path), parca_adi)
            
            for img_path in parca_klasor.glob('*.png'):
                self._referans_ekle(str(img_path), parca_adi)
        
        print(f"✅ {len(self.referans_veritabani)} referans görüntü yüklendi\n")
    
    def _referans_ekle(self, img_path: str, parca_adi: str):
        """Tek bir referans görüntü ekle"""
        img = cv2.imread(img_path)
        if img is None:
            return
        
        # Özellik çıkarma
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # SIFT features
        keypoints, descriptors = self.sift.detectAndCompute(gray, None)
        
        if descriptors is None:
            return
        
        # Renk histogramı
        histogram = self._histogram_hesapla(img)
        
        # Hu moments (şekil özellikleri)
        moments = cv2.moments(gray)
        hu_moments = cv2.HuMoments(moments).flatten()
        
        # Veritabanına ekle
        referans = ReferansGoruntu(
            parca_adi=parca_adi,
            goruntu_path=img_path,
            keypoints=keypoints,
            descriptors=descriptors,
            histogram=histogram,
            hu_moments=hu_moments
        )
        
        self.referans_veritabani.append(referans)
    
    def _histogram_hesapla(self, img: np.ndarray) -> np.ndarray:
        """RGB histogram hesapla"""
        histograms = []
        for i in range(3):
            hist = cv2.calcHist([img], [i], None, [64], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            histograms.append(hist)
        return np.concatenate(histograms)
    
    def _sift_eslestir(self, desc1: np.ndarray, desc2: np.ndarray) -> float:
        """SIFT descriptor eşleştirme skoru"""
        if desc1 is None or desc2 is None:
            return 0.0
        
        # KNN matching
        matches = self.bf_matcher.knnMatch(desc1, desc2, k=2)
        
        # Lowe's ratio test
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)
        
        # Normalize by descriptor count
        score = len(good_matches) / max(len(desc1), len(desc2))
        return score
    
    def _histogram_benzerlik(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """Histogram benzerlik skoru (0-1)"""
        # Chi-square distance kullan
        similarity = cv2.compareHist(
            hist1.astype(np.float32), 
            hist2.astype(np.float32), 
            cv2.HISTCMP_CORREL
        )
        return max(0, similarity)  # -1 ile 1 arası, negatif değerleri 0 yap
    
    def _hu_benzerlik(self, hu1: np.ndarray, hu2: np.ndarray) -> float:
        """Hu moments benzerlik skoru"""
        # Log-scale Hu moments
        hu1_log = -np.sign(hu1) * np.log10(np.abs(hu1) + 1e-10)
        hu2_log = -np.sign(hu2) * np.log10(np.abs(hu2) + 1e-10)
        
        # Euclidean distance
        distance = np.linalg.norm(hu1_log - hu2_log)
        
        # Convert to similarity (0-1)
        similarity = np.exp(-distance / 10)
        return similarity
    
    def _sekil_tabani_oncelik(self, sekiller: List[Dict]) -> Dict[str, float]:
        """
        Şekil analizi sonuçlarına göre parça öncelikleri belirle
        
        Returns:
            Dict[parca_adi, bonus_skor] - Her parça için bonus puan
        """
        oncelikler = {}
        
        if not sekiller:
            return oncelikler
        
        # En büyük şekli bul (genelde ana parça)
        en_buyuk_sekil = max(sekiller, key=lambda x: x['alan'])
        sekil_adi = en_buyuk_sekil['sekil']
        dairesellik = en_buyuk_sekil['dairesellik']
        
        # Şekil-Parça eşleştirmeleri
        if sekil_adi == "Daire" or (dairesellik > 0.75):
            # Daire/Elips -> Rulman, Somun
            oncelikler['rulman'] = 0.3
            oncelikler['somun'] = 0.15
            print(f"   🔍 Şekil analizi: Daire tespit edildi (dairesellik: {dairesellik:.2f}) -> Rulman/Somun öncelikli")
        
        elif sekil_adi == "Elips/Çokgen":
            if dairesellik > 0.6:
                # Oval şekil -> Rulman, Kayış
                oncelikler['rulman'] = 0.25
                oncelikler['kayis'] = 0.2
                print(f"   🔍 Şekil analizi: Elips tespit edildi -> Rulman/Kayış öncelikli")
            else:
                # Çokgen -> Dişli, Somun
                oncelikler['disli'] = 0.25
                oncelikler['somun'] = 0.15
                print(f"   🔍 Şekil analizi: Çokgen tespit edildi -> Dişli/Somun öncelikli")
        
        elif sekil_adi == "Dikdörtgen":
            # Uzun ince -> Vida, Yay, Krank
            aspect_ratio = en_buyuk_sekil['sinir'][2] / max(en_buyuk_sekil['sinir'][3], 1)
            if aspect_ratio > 3 or aspect_ratio < 0.33:  # Çok uzun veya çok dar
                oncelikler['vida'] = 0.25
                oncelikler['yay'] = 0.2
                oncelikler['krank'] = 0.15
                print(f"   🔍 Şekil analizi: Uzun dikdörtgen tespit edildi -> Vida/Yay öncelikli")
            else:
                # Kısa dikdörtgen -> Piston, Supap
                oncelikler['piston'] = 0.2
                oncelikler['supap'] = 0.15
                print(f"   🔍 Şekil analizi: Dikdörtgen tespit edildi -> Piston/Supap öncelikli")
        
        elif sekil_adi == "Kare":
            # Kare -> Somun, Vida başı
            oncelikler['somun'] = 0.25
            oncelikler['vida'] = 0.1
            print(f"   🔍 Şekil analizi: Kare tespit edildi -> Somun öncelikli")
        
        return oncelikler
    
    def tanima_yap(self, goruntu_path: str, method='hybrid', sekil_analizi_kullan=True) -> List[Dict]:
        """
        Görüntü tanıma yap
        
        Args:
            goruntu_path: Test görüntü yolu
            method: 'sift', 'histogram', 'hu', 'hybrid'
            sekil_analizi_kullan: Şekil analizi ile tahmin iyileştir
        
        Returns:
            Liste of {parca_adi, skor, method_skorlari}
        """
        # Test görüntüsünü yükle
        img = cv2.imread(goruntu_path)
        if img is None:
            raise ValueError(f"Görüntü yüklenemedi: {goruntu_path}")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Test görüntü özellikleri
        test_keypoints, test_descriptors = self.sift.detectAndCompute(gray, None)
        test_histogram = self._histogram_hesapla(img)
        moments = cv2.moments(gray)
        test_hu = cv2.HuMoments(moments).flatten()
        
        # Şekil analizi yap
        sekil_bonuslari = {}
        if sekil_analizi_kullan:
            try:
                sekiller = GorselIslemci.sekil_analizi(img)
                sekil_bonuslari = self._sekil_tabani_oncelik(sekiller)
            except Exception as e:
                print(f"   ⚠️  Şekil analizi hatası: {e}")
        
        # Her referans ile karşılaştır
        sonuclar = {}
        
        for referans in self.referans_veritabani:
            parca = referans.parca_adi
            
            # SIFT matching skoru
            sift_skor = self._sift_eslestir(test_descriptors, referans.descriptors)
            
            # Histogram benzerlik
            hist_skor = self._histogram_benzerlik(test_histogram, referans.histogram)
            
            # Hu moments benzerlik
            hu_skor = self._hu_benzerlik(test_hu, referans.hu_moments)
            
            # Hibrit skor (ağırlıklı ortalama)
            if method == 'sift':
                base_skor = sift_skor
            elif method == 'histogram':
                base_skor = hist_skor
            elif method == 'hu':
                base_skor = hu_skor
            else:  # hybrid
                base_skor = (
                    0.5 * sift_skor +
                    0.3 * hist_skor +
                    0.2 * hu_skor
                )
            
            # Şekil bonusunu ekle
            bonus = sekil_bonuslari.get(parca, 0)
            final_skor = min(1.0, base_skor + bonus)  # Max 1.0
            
            # Parça başına en yüksek skoru tut
            if parca not in sonuclar or final_skor > sonuclar[parca]['skor']:
                sonuclar[parca] = {
                    'parca_adi': parca,
                    'skor': final_skor,
                    'base_skor': base_skor,
                    'sekil_bonusu': bonus,
                    'sift_skor': sift_skor,
                    'histogram_skor': hist_skor,
                    'hu_skor': hu_skor,
                    'referans_goruntu': referans.goruntu_path
                }
        
        # Skora göre sırala
        sonuc_listesi = sorted(
            sonuclar.values(), 
            key=lambda x: x['skor'], 
            reverse=True
        )
        
        return sonuc_listesi
    
    def veritabani_kaydet(self, dosya_adi='referans_veritabani.pkl'):
        """Veritabanını dosyaya kaydet"""
        # Keypoints pickle edilemez, sadece koordinatları sakla
        kayit_verisi = []
        
        for ref in self.referans_veritabani:
            kayit_verisi.append({
                'parca_adi': ref.parca_adi,
                'goruntu_path': ref.goruntu_path,
                'descriptors': ref.descriptors,
                'histogram': ref.histogram,
                'hu_moments': ref.hu_moments
            })
        
        with open(dosya_adi, 'wb') as f:
            pickle.dump(kayit_verisi, f)
        
        print(f"✅ Veritabanı kaydedildi: {dosya_adi}")
    
    def veritabani_yukle_dosya(self, dosya_adi='referans_veritabani.pkl'):
        """Veritabanını dosyadan yükle"""
        with open(dosya_adi, 'rb') as f:
            kayit_verisi = pickle.load(f)
        
        self.referans_veritabani = []
        
        for veri in kayit_verisi:
            referans = ReferansGoruntu(
                parca_adi=veri['parca_adi'],
                goruntu_path=veri['goruntu_path'],
                keypoints=[],  # Yeniden hesaplanabilir
                descriptors=veri['descriptors'],
                histogram=veri['histogram'],
                hu_moments=veri['hu_moments']
            )
            self.referans_veritabani.append(referans)
        
        print(f"✅ {len(self.referans_veritabani)} referans yüklendi")


def test_sistem():
    """Test fonksiyonu"""
    print("=" * 60)
    print("Feature Matching Tabanlı Tanıma Sistemi - Test")
    print("=" * 60)
    
    # Örnek kullanım
    matcher = FeatureMatchingTanima(referans_klasor='./referans_gorseller')
    
    # Test görüntüsü
    test_img = './test_images/test_vida.jpg'
    
    if Path(test_img).exists():
        sonuclar = matcher.tanima_yap(test_img, method='hybrid')
        
        print("\n🎯 Tanıma Sonuçları (En İyi 3):\n")
        for i, sonuc in enumerate(sonuclar[:3], 1):
            print(f"{i}. {sonuc['parca_adi'].upper()}")
            print(f"   Genel Skor: {sonuc['skor']:.3f}")
            print(f"   SIFT: {sonuc['sift_skor']:.3f} | "
                  f"Histogram: {sonuc['histogram_skor']:.3f} | "
                  f"Hu: {sonuc['hu_skor']:.3f}")
            print(f"   Referans: {sonuc['referans_goruntu']}")
            print()
    else:
        print(f"⚠️  Test görüntüsü bulunamadı: {test_img}")
        print("Önce referans görüntüler ekleyin!")


if __name__ == "__main__":
    test_sistem()
