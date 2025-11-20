"""
Otomatik Görüntü İndirici
Google Images'dan parça görüntülerini otomatik indirir
"""

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlencode
import time
from pathlib import Path


def google_image_search(query, num_images=10, output_dir='referans_gorseller'):
    """
    Google'dan görüntü ara ve indir
    
    NOT: google-images-download paketi artık çalışmıyor,
    bu basit alternatif yöntemdir.
    """
    
    # Output klasörünü oluştur
    os.makedirs(output_dir, exist_ok=True)
    
    # User agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Google Images URL
    params = {
        'q': query,
        'tbm': 'isch',
        'ijn': '0'
    }
    
    url = f"https://www.google.com/search?{urlencode(params)}"
    
    print(f"🔍 Aranıyor: {query}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Görüntü URL'lerini bul
        img_tags = soup.find_all('img')
        
        downloaded = 0
        for i, img in enumerate(img_tags[:num_images + 5]):  # Biraz fazla dene
            if downloaded >= num_images:
                break
                
            try:
                img_url = img.get('src') or img.get('data-src')
                
                if not img_url or img_url.startswith('data:'):
                    continue
                
                # Görüntüyü indir
                img_response = requests.get(img_url, timeout=10)
                
                if img_response.status_code == 200:
                    filename = os.path.join(output_dir, f"{query.replace(' ', '_')}_{downloaded+1}.jpg")
                    
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f"   ✓ İndirildi: {filename}")
                    downloaded += 1
                    
                    time.sleep(0.5)  # Rate limiting
                    
            except Exception as e:
                continue
        
        print(f"✅ {downloaded} görüntü indirildi\n")
        return downloaded
        
    except Exception as e:
        print(f"❌ Hata: {e}\n")
        return 0


def bulk_download(parcalar, images_per_parca=10):
    """Toplu indirme"""
    
    print("=" * 60)
    print("📥 TOPLU GÖRÜNTÜ İNDİRME BAŞLIYOR")
    print("=" * 60 + "\n")
    
    toplam = 0
    
    for parca in parcalar:
        # Klasör oluştur
        parca_dir = os.path.join('referans_gorseller', parca)
        os.makedirs(parca_dir, exist_ok=True)
        
        # İngilizce arama terimleri ekle
        queries = [
            f"makine {parca}",
            f"mechanical {parca}",
            f"{parca} part"
        ]
        
        parca_toplam = 0
        
        for query in queries:
            count = google_image_search(
                query, 
                num_images=images_per_parca // len(queries), 
                output_dir=parca_dir
            )
            parca_toplam += count
            
            if parca_toplam >= images_per_parca:
                break
        
        toplam += parca_toplam
        print(f"📊 {parca}: {parca_toplam} görüntü\n")
    
    print("=" * 60)
    print(f"✅ TOPLAM {toplam} GÖRÜNTÜ İNDİRİLDİ")
    print("=" * 60)


def alternatif_yontem():
    """
    Alternatif: Manuel indirme talimatları
    """
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  🖼️  MANUEL GÖRÜNTÜ İNDİRME REHBERİ                        ║
    ╚══════════════════════════════════════════════════════════════╝
    
    YÖNTEM 1: Google Görseller (En Kolay)
    ────────────────────────────────────────
    1. Google'da "makine vida" ara
    2. "Görseller" sekmesine tıkla
    3. Her görüntüye sağ tık → "Resmi farklı kaydet"
    4. referans_gorseller/vida/ klasörüne kaydet
    5. 5-10 farklı görüntü indir
    
    YÖNTEM 2: Ücretsiz Stok Fotoğraf Siteleri
    ────────────────────────────────────────
    • Unsplash.com - search "mechanical parts"
    • Pexels.com - search "machine parts"
    • Pixabay.com - search "screw bolt nut"
    • Freepik.com - bazı ücretsiz
    
    YÖNTEM 3: Ürün Katalogları
    ────────────────────────────────────────
    • McMaster-Carr (mcmaster.com)
    • Grainger (grainger.com)
    • RS Components (rs-online.com)
    
    YÖNTEM 4: Telefon Kameranız
    ────────────────────────────────────────
    1. Beyaz kağıt üzerine parçayı koy
    2. İyi aydınlatma altında çek
    3. 3-5 farklı açıdan
    4. Bilgisayara aktar
    
    ╔══════════════════════════════════════════════════════════════╗
    ║  📁 HEDEF KLASÖR YAPISI                                      ║
    ╚══════════════════════════════════════════════════════════════╝
    
    referans_gorseller/
    ├── vida/
    │   ├── vida1.jpg
    │   ├── vida2.jpg
    │   ├── vida3.jpg
    │   ├── vida4.jpg
    │   └── vida5.jpg
    ├── somun/
    │   ├── somun1.jpg
    │   └── ...
    └── ...
    
    ✅ HER PARÇA İÇİN EN AZ 5 GÖRÜNTÜ HEDEF!
    """)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  📥 GÖRÜNTÜ İNDİRME ARACI                                   ║
    ╚══════════════════════════════════════════════════════════════╝
    
    UYARI: Otomatik web scraping bazı sitelerde engellenir!
    En güvenilir yöntem manuel indirmedir.
    
    Seçenekler:
    1. Otomatik indirme dene (basit yöntem)
    2. Manuel indirme talimatlarını göster
    """)
    
    secim = input("\nSeçiminiz (1/2): ").strip()
    
    if secim == "1":
        parcalar = ['vida', 'somun', 'rulman', 'kayış', 'dişli', 
                   'piston', 'supap', 'krank mili', 'yay']
        
        print("\n⚠️  NOT: Bu basit scraper sınırlı çalışır.")
        print("Daha iyi sonuçlar için manuel indirme önerilir!\n")
        
        devam = input("Devam edilsin mi? (e/h): ").strip().lower()
        
        if devam == 'e':
            bulk_download(parcalar, images_per_parca=5)
        else:
            print("İptal edildi.")
    
    elif secim == "2":
        alternatif_yontem()
    
    else:
        print("Geçersiz seçim!")
    
    print("\n✅ İşlem tamamlandı!")
    print("Sonraki adım: python test_system.py ile kontrol edin")
