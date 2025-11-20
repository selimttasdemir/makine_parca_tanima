#!/usr/bin/env python3
"""
Training Data Durum Kontrolü ve Yardımcı Script
Her klasörde kaç görüntü olduğunu gösterir ve öneriler sunar
"""

import os
from pathlib import Path
from collections import defaultdict

# ANSI renk kodları
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


def check_training_data():
    """Training data klasörlerini kontrol et"""
    
    print("=" * 70)
    print(f"{BOLD}📊 TRAINING DATA DURUMU{RESET}")
    print("=" * 70)
    
    training_dir = Path('./training_data')
    
    if not training_dir.exists():
        print(f"{RED}❌ training_data/ klasörü bulunamadı!{RESET}")
        return
    
    # Her parça için görüntü sayısı
    parca_sayilari = {}
    desteklenen_formatlar = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    
    for parca_klasor in sorted(training_dir.iterdir()):
        if not parca_klasor.is_dir():
            continue
        
        parca_adi = parca_klasor.name
        
        # Görüntü dosyalarını say
        goruntu_sayisi = 0
        for ext in desteklenen_formatlar:
            goruntu_sayisi += len(list(parca_klasor.glob(f'*{ext}')))
        
        parca_sayilari[parca_adi] = goruntu_sayisi
    
    # Sonuçları göster
    print(f"\n{BOLD}Parça                Görüntü Sayısı    Durum{RESET}")
    print("-" * 70)
    
    toplam_goruntu = 0
    
    for parca, sayi in sorted(parca_sayilari.items()):
        toplam_goruntu += sayi
        
        # Durum göstergesi
        if sayi == 0:
            durum = f"{RED}❌ BOŞ - Acil: Görüntü ekleyin!{RESET}"
            renk = RED
        elif sayi < 10:
            durum = f"{RED}⚠️  ÇOK AZ - Min 10 olmalı{RESET}"
            renk = RED
        elif sayi < 50:
            durum = f"{YELLOW}🟡 YETERSIZ - 50+ öneririz{RESET}"
            renk = YELLOW
        elif sayi < 100:
            durum = f"{BLUE}🔵 İYİ - Kullanılabilir{RESET}"
            renk = BLUE
        else:
            durum = f"{GREEN}✅ MÜKEMMEL - Eğitime hazır{RESET}"
            renk = GREEN
        
        print(f"{parca:<20} {renk}{sayi:>3}{RESET} görüntü      {durum}")
    
    print("-" * 70)
    print(f"{BOLD}TOPLAM:{RESET} {toplam_goruntu} görüntü")
    
    # Genel değerlendirme
    print("\n" + "=" * 70)
    print(f"{BOLD}📋 GENEL DEĞERLENDİRME{RESET}")
    print("=" * 70)
    
    bos_klasorler = [p for p, s in parca_sayilari.items() if s == 0]
    az_klasorler = [p for p, s in parca_sayilari.items() if 0 < s < 50]
    iyi_klasorler = [p for p, s in parca_sayilari.items() if 50 <= s < 100]
    mukemmel_klasorler = [p for p, s in parca_sayilari.items() if s >= 100]
    
    if toplam_goruntu == 0:
        print(f"\n{RED}{BOLD}🚨 HİÇBİR GÖRÜNTÜ YOK!{RESET}")
        print(f"\n{YELLOW}➡️  İlk adım: Her parça için 10 görüntü ekleyin{RESET}")
        print(f"   Örnek: training_data/vida/vida_01.jpg")
        print(f"\n   Kaynak önerileri:")
        print(f"   • Google Görseller: 'M8 vida' ara, sağ tık → kaydet")
        print(f"   • Unsplash.com: 'bolt' 'screw' ara")
        print(f"   • Telefon kameranız ile çekin")
    
    elif toplam_goruntu < 100:
        print(f"\n{YELLOW}{BOLD}⚠️  VERİ ÇOK AZ - Henüz model eğitimine hazır değil{RESET}")
        print(f"\n   Minimum hedef: 100 görüntü (10 parça x 10 görüntü)")
        print(f"   Şu an: {toplam_goruntu} görüntü")
        print(f"   Eksik: {100 - toplam_goruntu} görüntü")
        
        if bos_klasorler:
            print(f"\n   {RED}Boş klasörler:{RESET} {', '.join(bos_klasorler)}")
            print(f"   ➡️  Bu klasörlere öncelik verin!")
    
    elif toplam_goruntu < 500:
        print(f"\n{BLUE}{BOLD}🔵 TEST İÇİN YETERLİ - Basit eğitim yapılabilir{RESET}")
        print(f"\n   Mevcut: {toplam_goruntu} görüntü")
        print(f"   Önerilen: 500+ görüntü (50 görüntü/parça)")
        print(f"   Eksik: ~{500 - toplam_goruntu} görüntü")
        
        if az_klasorler:
            print(f"\n   {YELLOW}Az veri olan parçalar:{RESET} {', '.join(az_klasorler)}")
            print(f"   ➡️  Bu parçalara daha fazla örnek ekleyin")
    
    else:
        print(f"\n{GREEN}{BOLD}✅ MODEL EĞİTİMİNE HAZIR!{RESET}")
        print(f"\n   Toplam: {toplam_goruntu} görüntü")
        print(f"   Parça başına ortalama: {toplam_goruntu // len(parca_sayilari)}")
        
        if bos_klasorler or az_klasorler:
            print(f"\n   {YELLOW}Geliştirilebilir:{RESET}")
            if bos_klasorler:
                print(f"   • Boş: {', '.join(bos_klasorler)}")
            if az_klasorler:
                print(f"   • Az: {', '.join(az_klasorler)}")
        else:
            print(f"\n   {GREEN}Tüm parçalar yeterli veri içeriyor! 🎉{RESET}")
    
    # Öneriler
    print("\n" + "=" * 70)
    print(f"{BOLD}💡 ÖNERİLER{RESET}")
    print("=" * 70)
    
    if toplam_goruntu == 0:
        print(f"""
{BOLD}1. İlk 30 görüntü ile başlayın (3 parça x 10 görüntü):{RESET}
   
   cd training_data/vida
   # Google'dan 10 vida görüntüsü indirin
   # vida_01.jpg, vida_02.jpg, ... vida_10.jpg
   
   cd ../somun
   # 10 somun görüntüsü
   
   cd ../rulman
   # 10 rulman görüntüsü

{BOLD}2. Kontrol edin:{RESET}
   python check_training_data.py
   
{BOLD}3. İlk eğitimi yapın:{RESET}
   python train_model.py --mode train --data_dir ./training_data --epochs 10
""")
    
    elif toplam_goruntu < 100:
        eksik_sayi = 100 - toplam_goruntu
        print(f"""
{BOLD}Sonraki adım: {eksik_sayi} görüntü daha ekleyin{RESET}

• Boş klasörlere öncelik verin: {', '.join(bos_klasorler) if bos_klasorler else 'Yok'}
• Az olan parçaları güçlendirin: {', '.join(az_klasorler) if az_klasorler else 'Yok'}

{BOLD}Hızlı yöntem:{RESET}
1. Her parça için 10 görüntü hedefleyin
2. Google Görseller'den manuel indirme yapın
3. 1-2 saatte bitirebilirsiniz
""")
    
    elif toplam_goruntu < 500:
        print(f"""
{BOLD}Model eğitimine geçebilirsiniz!{RESET}

{YELLOW}Küçük veri seti eğitimi:{RESET}
   python train_model.py --mode train --data_dir ./training_data --epochs 20

{BLUE}Daha iyi sonuç için:{RESET}
• Veri artırma (augmentation) uygulayın
• Her parça için 50+ görüntü hedefleyin
• Çeşitlilik artırın (farklı açılar, arka planlar)
""")
    
    else:
        print(f"""
{GREEN}{BOLD}Profesyonel eğitime başlayabilirsiniz!{RESET}

{BOLD}Önerilen eğitim komutu:{RESET}
   python train_model.py --mode train \\
       --data_dir ./training_data \\
       --epochs 50 \\
       --batch_size 32

{BOLD}Eğitim sonrası:{RESET}
   streamlit run app.py
   # "Deep Learning" veya "Hibrit" modunu seçin
""")
    
    # Detaylı durum tablosu
    print("\n" + "=" * 70)
    print(f"{BOLD}📈 HEDEF KARŞILAŞTIRMASI{RESET}")
    print("=" * 70)
    print(f"""
{'Seviye':<20} {'Hedef':<15} {'Mevcut':<15} {'Durum':<15}
{'-'*70}
Minimum (Test)       100 görüntü     {toplam_goruntu:<15} {get_status(toplam_goruntu, 100)}
İyi (Kullanılabilir) 500 görüntü     {toplam_goruntu:<15} {get_status(toplam_goruntu, 500)}
Mükemmel (Pro)       1000 görüntü    {toplam_goruntu:<15} {get_status(toplam_goruntu, 1000)}
""")
    
    print("=" * 70)


def get_status(current, target):
    """Durum göstergesi döndür"""
    if current >= target:
        return f"{GREEN}✅ Tamamlandı{RESET}"
    elif current >= target * 0.7:
        return f"{YELLOW}🟡 Yakın ({int(current/target*100)}%){RESET}"
    elif current > 0:
        return f"{YELLOW}⚠️  Devam ({int(current/target*100)}%){RESET}"
    else:
        return f"{RED}❌ Başlanmadı{RESET}"


def check_referans_data():
    """Referans görüntüleri de kontrol et"""
    print("\n" + "=" * 70)
    print(f"{BOLD}📚 REFERANS GÖRSELLER DURUMU (Feature Matching için){RESET}")
    print("=" * 70)
    
    referans_dir = Path('./referans_gorseller')
    
    if not referans_dir.exists():
        print(f"{RED}❌ referans_gorseller/ klasörü bulunamadı!{RESET}")
        return
    
    toplam = 0
    desteklenen_formatlar = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    
    print(f"\n{BOLD}Parça                Görüntü Sayısı{RESET}")
    print("-" * 70)
    
    for parca_klasor in sorted(referans_dir.iterdir()):
        if not parca_klasor.is_dir():
            continue
        
        parca_adi = parca_klasor.name
        sayi = 0
        for ext in desteklenen_formatlar:
            sayi += len(list(parca_klasor.glob(f'*{ext}')))
        
        toplam += sayi
        
        if sayi == 0:
            print(f"{parca_adi:<20} {RED}{sayi:>3} görüntü  ❌ Boş{RESET}")
        elif sayi < 5:
            print(f"{parca_adi:<20} {YELLOW}{sayi:>3} görüntü  ⚠️  Az (min 5){RESET}")
        else:
            print(f"{parca_adi:<20} {GREEN}{sayi:>3} görüntü  ✅ Yeterli{RESET}")
    
    print("-" * 70)
    print(f"{BOLD}TOPLAM:{RESET} {toplam} görüntü")
    
    if toplam == 0:
        print(f"\n{YELLOW}💡 Feature Matching için her parçaya 5-10 görüntü ekleyin{RESET}")
    elif toplam >= 50:
        print(f"\n{GREEN}✅ Feature Matching aktif olabilir!{RESET}")


def main():
    """Ana fonksiyon"""
    print(f"\n{BOLD}{BLUE}🔍 Makine Parçası Tanıma - Veri Durumu Kontrolü{RESET}\n")
    
    # Training data kontrolü
    check_training_data()
    
    # Referans data kontrolü
    check_referans_data()
    
    print("\n" + "=" * 70)
    print(f"{BOLD}📖 Detaylı rehber için:{RESET} TRAINING_DATA_REHBER.md")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
