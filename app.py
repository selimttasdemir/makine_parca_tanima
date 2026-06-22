"""
Makine Parçası Tanıma Sistemi
Görüntü işleme ve yapay zeka kullanarak makine parçalarını tanıyan sistem
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import json
from pathlib import Path
import os
import warnings
import time

# PyTorch uyarılarını bastır
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*torch.classes.*')

# Lazy import - sadece gerektiğinde yükle
def lazy_import_torch():
    """PyTorch'u sadece gerektiğinde import et"""
    global torch, transforms, models
    if 'torch' not in globals():
        import torch
        from torchvision import transforms, models
    return torch, transforms, models

# Hibrit sistem için import
try:
    from hybrid_detector import HibritTanima
    HIBRIT_KULLANILABILIR = True
except ImportError:
    HIBRIT_KULLANILABILIR = False

try:
    from feature_matcher import FeatureMatchingTanima
    FEATURE_KULLANILABILIR = True
except ImportError:
    FEATURE_KULLANILABILIR = False

# YOLO için import
try:
    from ultralytics import YOLO
    YOLO_KULLANILABILIR = True
except ImportError:
    YOLO_KULLANILABILIR = False

# ESP32Cam için import
try:
    from esp32cam_handler import (
        ESP32CamHandler, ESP32CamBuffer, FrameProcessor, esp32_durum_kontrol
    )
    ESP32CAM_KULLANILABILIR = True
except ImportError:
    ESP32CAM_KULLANILABILIR = False

class MakineParcaTanima:
    def __init__(self):
        """Sistem başlatıcı"""
        self.model = None
        self.device = None
        self.transform = None
        self.parca_veritabani = self.veritabani_yukle()
        self.yolo_sinif_map = {
            'Bearing': 'rulman',
            'Bolt': 'vida',
            'Gear': 'disli',
            'Nut': 'somun'
        }
    
    def _init_torch(self):
        """PyTorch'u lazy init et"""
        if self.device is None:
            torch_lib, transforms_lib, _ = lazy_import_torch()
            self.device = torch_lib.device("cuda" if torch_lib.cuda.is_available() else "cpu")
            self.transform = transforms_lib.Compose([
                transforms_lib.Resize((224, 224)),
                transforms_lib.ToTensor(),
                transforms_lib.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        
    def veritabani_yukle(self):
        """Makine parçaları veritabanını yükle"""
        return {
            "vida": {
                "isim": "Vida",
                "tanim": "Dişli silindirik bağlantı elemanı",
                "kullanim_alanlari": [
                    "Mekanik parçaları birleştirme",
                    "Sabit bağlantılar oluşturma",
                    "Makine montajı",
                    "İnşaat ve mobilya"
                ],
                "ozellikler": [
                    "Farklı boyutlarda üretilebilir",
                    "Çelik, paslanmaz çelik, pirinç gibi malzemelerden yapılır",
                    "Standart dişler kullanır (M3, M4, M5, vb.)",
                    "Sökülüp takılabilir"
                ],
                "cesitleri": ["Altıköşe başlı", "Havşa başlı", "Yıldız başlı", "İmbus başlı"]
            },
            "somun": {
                "isim": "Somun",
                "tanim": "Vida ile birlikte kullanılan dişli delikli bağlantı elemanı",
                "kullanim_alanlari": [
                    "Vida ile birlikte bağlantı oluşturma",
                    "Cıvata bağlantıları",
                    "Mekanik montaj",
                    "Otomotiv endüstrisi"
                ],
                "ozellikler": [
                    "Genellikle altıgen şeklindedir",
                    "İç dişlidir",
                    "Vida standartlarına uyumludur",
                    "Farklı sıkıştırma kuvvetleri sağlar"
                ],
                "cesitleri": ["Altıköşe somun", "Kanal somun", "Kelebek somun", "Kayar somun"]
            },
            "rulman": {
                "isim": "Rulman",
                "tanim": "Dönen parçaların sürtünmesini azaltan bilyalı veya makaralı yataklama elemanı",
                "kullanim_alanlari": [
                    "Mil yataklama",
                    "Döner hareketlerde sürtünme azaltma",
                    "Elektrik motorları",
                    "Otomotiv (tekerlek rulmanları)",
                    "Pompa ve fanlar"
                ],
                "ozellikler": [
                    "Radyal veya eksenel yük taşır",
                    "Sürtünmeyi minimize eder",
                    "Yağlama gerektirir",
                    "Yüksek devirlerde çalışabilir"
                ],
                "cesitleri": ["Bilya rulman", "Makaralı rulman", "İğneli rulman", "Konik rulman"]
            },
            "kayis": {
                "isim": "Kayış",
                "tanim": "Güç aktarımı için kullanılan esnek bağlantı elemanı",
                "kullanim_alanlari": [
                    "Motor gücünü diğer parçalara iletme",
                    "Otomotiv (motor kayışı)",
                    "Konveyör sistemleri",
                    "Tarım makineleri"
                ],
                "ozellikler": [
                    "Esnek malzemeden yapılır",
                    "Farklı kasnak oranlarıyla hız değişimi sağlar",
                    "Düşük maliyetli",
                    "Gürültü azaltır"
                ],
                "cesitleri": ["V kayış", "Zımpara kayış", "Trapezoidal kayış", "Düz kayış"]
            },
            "disli": {
                "isim": "Dişli",
                "tanim": "Dişler aracılığıyla güç ve hareket ileten mekanik eleman",
                "kullanim_alanlari": [
                    "Hız ve tork değişimi",
                    "Güç aktarımı",
                    "Şanzıman sistemleri",
                    "Saat mekanizmaları",
                    "Redüktörler"
                ],
                "ozellikler": [
                    "Kesin hız oranı sağlar",
                    "Yüksek güç aktarımı",
                    "Uzun ömürlü",
                    "Hassas imalat gerektirir"
                ],
                "cesitleri": ["Düz dişli", "Konik dişli", "Helisel dişli", "Sonsuz vida"]
            },
            "piston": {
                "isim": "Piston",
                "tanim": "Silindirde ileri-geri hareket ederek güç üreten veya ileten parça",
                "kullanim_alanlari": [
                    "İçten yanmalı motorlar",
                    "Hidrolik sistemler",
                    "Pnömatik sistemler",
                    "Kompresörler",
                    "Pompalar"
                ],
                "ozellikler": [
                    "Silindir içinde sızdırmazlık sağlar",
                    "Yüksek sıcaklık ve basınca dayanıklı",
                    "Genellikle alüminyum alaşımından yapılır",
                    "Piston segmanları ile kullanılır"
                ],
                "cesitleri": ["Motor pistonu", "Hidrolik piston", "Kompresör pistonu"]
            },
            "supap": {
                "isim": "Supap (Valf)",
                "tanim": "Gaz veya sıvı akışını kontrol eden kapak mekanizması",
                "kullanim_alanlari": [
                    "Motor silindir başlığı (giriş/çıkış)",
                    "Hidrolik sistemler",
                    "Su ve gaz sistemleri",
                    "Basınç kontrolü"
                ],
                "ozellikler": [
                    "Hassas açılma-kapanma zamanlaması",
                    "Yüksek sıcaklığa dayanıklı",
                    "Sızdırmazlık sağlar",
                    "Yay mekanizması ile çalışır"
                ],
                "cesitleri": ["Emme supabı", "Egzoz supabı", "Kelebek valf", "Çek valf"]
            },
            "krank": {
                "isim": "Krank Mili",
                "tanim": "Pistonun ileri-geri hareketini döner harekete çeviren mil",
                "kullanim_alanlari": [
                    "Otomobil motorları",
                    "Kompresörler",
                    "Pompalar",
                    "Dizel jeneratörler"
                ],
                "ozellikler": [
                    "Çok yüksek mekanik dayanım",
                    "Rulmanlarla desteklenir",
                    "Dengelenmiş olmalı",
                    "Özel çelik alaşımlarından yapılır"
                ],
                "cesitleri": ["Tek silindirli", "Çok silindirli", "Offset krank"]
            },
            "yay": {
                "isim": "Yay",
                "tanim": "Esneklik özelliği ile enerji depolayan ve geri veren eleman",
                "kullanim_alanlari": [
                    "Süspansiyon sistemleri",
                    "Supap mekanizmaları",
                    "Kapı ve menteşeler",
                    "Saat mekanizmaları",
                    "Amortisörler"
                ],
                "ozellikler": [
                    "Elastik malzemeden yapılır",
                    "Enerji depolama kapasitesi",
                    "Tekrarlı yük altında çalışır",
                    "Farklı sertliklerde üretilir"
                ],
                "cesitleri": ["Helisel yay", "Yaprak yay", "Burulma yayı", "Disk yay"]
            },
            "kaynak": {
                "isim": "Kaynak Bağlantısı",
                "tanim": "Metal parçaları eritip birleştiren kalıcı bağlantı yöntemi",
                "kullanim_alanlari": [
                    "Çelik konstrüksiyonlar",
                    "Otomotiv şase üretimi",
                    "Boru hatları",
                    "Gemi ve uçak imalatı"
                ],
                "ozellikler": [
                    "Kalıcı bağlantı",
                    "Yüksek mukavemet",
                    "Sızdırmazlık sağlar",
                    "Farklı kaynak teknikleri"
                ],
                "cesitleri": ["Elektrik ark kaynağı", "TIG", "MIG/MAG", "Oxy-acetylene"]
            }
        }
    
    def goruntu_onisleme(self, image):
        """Görüntüyü ön işleme"""
        # PIL Image'e çevir
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Görüntü iyileştirme
        img_array = np.array(image)
        
        # Gri tonlamaya çevir
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Kontrast iyileştirme (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Gürültü azaltma
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # Kenar tespiti
        edges = cv2.Canny(denoised, 50, 150)
        
        # Renkli görüntüye geri çevir
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return {
            "orijinal": image,
            "gri": gray,
            "iyilestirilmis": enhanced,
            "kenarlar": edges,
            "renkli": img_rgb
        }
    
    def ozellik_cikarma(self, image):
        """Görüntüden özellik çıkar"""
        processed = self.goruntu_onisleme(image)
        
        # Şekil özellikleri
        edges = processed["kenarlar"]
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        ozellikler = {
            "kontur_sayisi": len(contours),
            "alan": 0,
            "cevre": 0,
            "sekil": "Bilinmiyor"
        }
        
        if contours:
            # En büyük konturu al
            largest_contour = max(contours, key=cv2.contourArea)
            ozellikler["alan"] = cv2.contourArea(largest_contour)
            ozellikler["cevre"] = cv2.arcLength(largest_contour, True)
            
            # Şekil tespiti
            approx = cv2.approxPolyDP(largest_contour, 0.04 * ozellikler["cevre"], True)
            koseler = len(approx)
            
            if koseler == 3:
                ozellikler["sekil"] = "Üçgen"
            elif koseler == 4:
                ozellikler["sekil"] = "Dikdörtgen/Kare"
            elif koseler > 4:
                ozellikler["sekil"] = "Daire/Elips"
        
        return ozellikler
    
    def parca_tanima_basit(self, ozellikler):
        """Basit kural tabanlı parça tanıma"""
        # Bu basit bir örnek - gerçek uygulamada ML modeli kullanılmalı
        sekil = ozellikler.get("sekil", "")
        alan = ozellikler.get("alan", 0)
        
        # Basit heuristikler
        if sekil == "Daire/Elips":
            if alan > 5000:
                return "rulman"
            else:
                return "vida"
        elif sekil == "Dikdörtgen/Kare":
            return "somun"
        
        # Varsayılan
        return "vida"
    
    def bilgi_getir(self, parca_adi):
        """Parça hakkında detaylı bilgi getir"""
        return self.parca_veritabani.get(parca_adi, {
            "isim": "Bilinmeyen Parça",
            "tanim": "Bu parça veritabanında bulunamadı",
            "kullanim_alanlari": [],
            "ozellikler": [],
            "cesitleri": []
        })
    
    def yolo_tahmin(self, image_path, model_path='runs/detect/train/weights/best.pt'):
        """YOLO modeli ile tahmin yap"""
        if not YOLO_KULLANILABILIR:
            return None
        
        if not Path(model_path).exists():
            return None
        
        try:
            # YOLO modelini yükle
            model = YOLO(model_path)
            
            # Tahmin yap
            results = model.predict(image_path, verbose=False, conf=0.25)
            
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                
                # Tüm tespit edilen nesneleri topla
                tespitler = []
                for box in boxes:
                    sinif_id = int(box.cls[0])
                    guven = float(box.conf[0])
                    sinif_adi = model.names[sinif_id]
                    
                    # Bounding box koordinatları (xyxy format)
                    xyxy = box.xyxy[0].cpu().numpy()
                    
                    tespitler.append({
                        'sinif_adi': sinif_adi,
                        'veritabani_adi': self.yolo_sinif_map.get(sinif_adi, sinif_adi.lower()),
                        'guven': guven,
                        'bbox': xyxy.tolist()
                    })
                
                # En yüksek güvenli tespiti döndür
                if tespitler:
                    en_iyi = max(tespitler, key=lambda x: x['guven'])
                    return {
                        'parca': en_iyi['veritabani_adi'],
                        'guven': en_iyi['guven'],
                        'sinif': en_iyi['sinif_adi'],
                        'tum_tespitler': tespitler,
                        'toplam_nesne': len(tespitler),
                        'sonuc_goruntu': results[0].plot()  # Çizilmiş görüntü
                    }
            
            return None
            
        except Exception as e:
            st.error(f"YOLO tahmin hatası: {e}")
            return None


def performans_sayfasi():
    """Model performans test sayfası"""
    st.title("📊 Model Performans Testi")
    st.markdown("""
    Bu sayfada eğitilmiş modelinizin test seti üzerindeki doğruluğunu ölçebilirsiniz.
    """)
    
    # Model seçimi
    model_path = st.text_input(
        "Model Dosyası Yolu:",
        value="runs/detect/train/weights/best.pt"
    )
    
    if not Path(model_path).exists():
        st.warning(f"⚠️ Model dosyası bulunamadı: {model_path}")
        st.info("Lütfen önce modeli eğitin veya doğru yolu girin.")
        return
    
    # Test limiti
    col1, col2 = st.columns(2)
    with col1:
        test_limiti = st.number_input(
            "Test Edilecek Görüntü Sayısı (0=Hepsi)",
            min_value=0,
            max_value=1000,
            value=50,
            step=10
        )
    
    with col2:
        test_klasoru = st.text_input(
            "Test Klasörü:",
            value="test"
        )
    
    # Test başlat butonu
    if st.button("🧪 Testi Başlat", type="primary"):
        try:
            from ultralytics import YOLO
            from test_dogruluk import ModelDogrulukTest
            
            with st.spinner("Model yükleniyor..."):
                model = YOLO(model_path)
            
            st.success("✅ Model yüklendi!")
            
            # Test seti analizi
            with st.spinner("Test seti analiz ediliyor..."):
                tester = ModelDogrulukTest(test_path=test_klasoru)
                analiz = tester.test_seti_analizi()
            
            if analiz:
                st.subheader("📁 Test Seti Bilgileri")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Toplam Görüntü", analiz['toplam_goruntu'])
                with col2:
                    st.metric("Toplam Nesne", analiz['toplam_nesne'])
                with col3:
                    st.metric("Ort. Nesne/Görüntü", f"{analiz['ortalama_nesne']:.2f}")
                
                # Sınıf dağılımı grafiği
                st.markdown("**Sınıf Dağılımı:**")
                import pandas as pd
                df_sinif = pd.DataFrame(
                    list(analiz['sinif_dagilimi'].items()),
                    columns=['Sınıf', 'Sayı']
                )
                st.bar_chart(df_sinif.set_index('Sınıf'))
            
            # Model testi
            st.divider()
            st.subheader("🔬 Model Test Ediliyor...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            limit = test_limiti if test_limiti > 0 else None
            
            with st.spinner(f"Test ediliyor... (Bu işlem biraz zaman alabilir)"):
                sonuclar = tester.model_test_et(model, limit=limit)
                progress_bar.progress(100)
            
            if sonuclar:
                status_text.success("✅ Test tamamlandı!")
                
                # Genel doğruluk
                st.divider()
                st.subheader("📈 Test Sonuçları")
                
                # Büyük metrik
                dogruluk_yuzde = sonuclar['genel_dogruluk'] * 100
                dogruluk_renk = "normal"
                if dogruluk_yuzde >= 90:
                    dogruluk_renk = "normal"
                    emoji = "🎯"
                elif dogruluk_yuzde >= 75:
                    emoji = "✅"
                elif dogruluk_yuzde >= 60:
                    emoji = "⚠️"
                else:
                    emoji = "❌"
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        f"{emoji} Genel Doğruluk",
                        f"%{dogruluk_yuzde:.2f}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "✅ Doğru Tahmin",
                        f"{sonuclar['toplam_dogru']}/{sonuclar['toplam_nesne']}"
                    )
                
                with col3:
                    st.metric(
                        "❌ Yanlış Tahmin",
                        f"{sonuclar['toplam_yanlis']}/{sonuclar['toplam_nesne']}"
                    )
                
                # Sınıf bazında doğruluk
                st.divider()
                st.subheader("📊 Sınıf Bazında Performans")
                
                # DataFrame oluştur
                sinif_data = []
                for sinif, dogruluk in sonuclar['sinif_dogruluk'].items():
                    stats = sonuclar['sinif_istatistik'][sinif]
                    sinif_data.append({
                        'Sınıf': sinif,
                        'Doğruluk (%)': f"{dogruluk*100:.2f}",
                        'Doğru': stats['dogru'],
                        'Yanlış': stats['yanlis'],
                        'Toplam': stats['toplam']
                    })
                
                df_sinif_perf = pd.DataFrame(sinif_data)
                df_sinif_perf = df_sinif_perf.sort_values('Doğruluk (%)', ascending=False)
                
                st.dataframe(df_sinif_perf, use_container_width=True, hide_index=True)
                
                # Sınıf doğruluk grafiği
                st.markdown("**Sınıf Doğruluk Grafiği:**")
                sinif_dogr_data = {k: v*100 for k, v in sonuclar['sinif_dogruluk'].items()}
                st.bar_chart(sinif_dogr_data)
                
                # Yanlış tahminler
                yanlis_tahminler = [s for s in sonuclar['detayli_sonuclar'] if not s['dogru']]
                
                if yanlis_tahminler:
                    st.divider()
                    st.subheader("❌ Yanlış Tahmin Örnekleri")
                    
                    goster_sayi = st.slider(
                        "Gösterilecek örnek sayısı:",
                        min_value=5,
                        max_value=min(50, len(yanlis_tahminler)),
                        value=min(10, len(yanlis_tahminler))
                    )
                    
                    # Tablo oluştur
                    yanlis_data = []
                    for yanlis in yanlis_tahminler[:goster_sayi]:
                        yanlis_data.append({
                            'Görüntü': yanlis['goruntu'],
                            'Gerçek Sınıf': yanlis['gercek'],
                            'Tahmin': yanlis['tahmin'],
                            'Güven (%)': f"{yanlis['guven']*100:.1f}"
                        })
                    
                    df_yanlis = pd.DataFrame(yanlis_data)
                    st.dataframe(df_yanlis, use_container_width=True, hide_index=True)
                
                # Sonuçları kaydet
                st.divider()
                if st.button("💾 Sonuçları Kaydet (JSON)"):
                    kayit_yolu = "test_sonuclari.json"
                    tester.sonuclari_kaydet(sonuclar, kayit_yolu)
                    st.success(f"✅ Sonuçlar kaydedildi: {kayit_yolu}")
                    
                    # İndirme butonu
                    with open(kayit_yolu, 'r', encoding='utf-8') as f:
                        json_str = f.read()
                    
                    st.download_button(
                        label="📥 JSON Dosyasını İndir",
                        data=json_str,
                        file_name=kayit_yolu,
                        mime="application/json"
                    )
                
        except ImportError as e:
            st.error(f"❌ Gerekli kütüphane bulunamadı: {e}")
            st.info("Lütfen şu komutu çalıştırın: pip install ultralytics")
        except Exception as e:
            st.error(f"❌ Hata oluştu: {e}")
            import traceback
            with st.expander("🔍 Hata Detayları"):
                st.code(traceback.format_exc())


def esp32_sayfasi():
    """ESP32Cam canlı kamera tanıma sayfası"""
    st.title("📹 ESP32Cam Canlı Kamera Tanıma")
    st.markdown("""
    Bu sayfada ESP32Cam modülünden alınan canlı görüntüler üzerinde gerçek zamanlı 
    makine parçası tanıması yapabilirsiniz.
    
    **Gereksiz kurulum:**
    - ESP32Cam modülü
    - MicroPython yazılımı
    - Web sunucusu (webrepl veya custom firmware)
    """)
    
    if not ESP32CAM_KULLANILABILIR:
        st.error("❌ ESP32Cam modülü yüklenmemiş. Lütfen şu komutu çalıştırın:")
        st.code("pip install requests")
        return
    
    # Sidebar ayarları
    with st.sidebar:
        st.header("⚙️ ESP32Cam Ayarları")
        
        # Bağlantı konfigürasyonu
        st.subheader("🔌 Bağlantı")
        esp32_ip = st.text_input(
            "ESP32 IP Adresi:",
            value=st.session_state.get("esp32_ip", "192.168.1.196"),
            placeholder="192.168.1.196"
        )
        
        esp32_port = st.number_input(
            "Port:",
            min_value=1,
            max_value=65535,
            value=st.session_state.get("esp32_port", 80),
            step=1
        )
        
        # Bağlantı durumu kontrol
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Bağlantı Kontrol", use_container_width=True):
                with st.spinner("Kontrol ediliyor..."):
                    durum = esp32_durum_kontrol(esp32_ip, esp32_port)
                    st.session_state['esp32_durum'] = durum
        
        with col2:
            if st.button("🔄 Yenile", use_container_width=True):
                st.rerun()
        
        # Bağlantı durumu göster
        if 'esp32_durum' in st.session_state:
            durum = st.session_state['esp32_durum']
            if "Online" in durum.get("durum", ""):
                st.success(f"✅ {durum['durum']}")
            else:
                st.warning(f"⚠️ {durum.get('durum', 'Bilinmiyor')}")
            
            if durum.get('error'):
                st.error(f"Hata: {durum['error']}")
    
    ESP32_GORUNTU_GENISLIK = 720
    ESP32_GORUNTU_YUKSEKLIK = 560
    
    # Session state başlat
    if 'esp32_handler' not in st.session_state:
        st.session_state.esp32_handler = None
    
    if 'esp32_streaming' not in st.session_state:
        st.session_state.esp32_streaming = False
    
    if 'esp32_frames' not in st.session_state:
        st.session_state.esp32_frames = []
    
    # IP adresini session'a kaydet
    st.session_state.esp32_ip = esp32_ip
    st.session_state.esp32_port = esp32_port
    
    col_main, col_settings = st.columns([3, 1])
    
    with col_settings:
        st.subheader("🎨 Filtreler")
        
        filter_type = st.radio(
            "Filtre Seçin:",
            ["Normal", "Gri Tonlama", "Kenar Tespiti", "Keskinleştirme", "Histogram Eşitleştir"],
            index=0
        )
    
    with col_main:
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            start_stream = st.button("▶️ Canlı Akışı Başlat", use_container_width=True)
        
        with col_btn2:
            stop_stream = st.button("⏹️ Akışı Durdur", use_container_width=True)
        
        with col_btn3:
            capture_snapshot = st.button("📸 Snapshot Al", use_container_width=True)
        
        stream_placeholder = st.empty()
        
        if start_stream and not st.session_state.esp32_streaming:
            with st.spinner("ESP32Cam'e bağlanılıyor..."):
                try:
                    st.session_state.esp32_handler = ESP32CamHandler(esp32_ip, esp32_port)
                    
                    if st.session_state.esp32_handler.is_connected:
                        st.session_state.esp32_handler.basla_stream()
                        st.session_state.esp32_streaming = True
                        st.success("✅ Canlı akış başlatıldı!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ ESP32Cam'e bağlanılamadı!")
                except Exception as e:
                    st.error(f"❌ Hata: {e}")
        
        if stop_stream and st.session_state.esp32_streaming:
            if st.session_state.esp32_handler:
                st.session_state.esp32_handler.durdur_stream()
            st.session_state.esp32_streaming = False
            st.info("⏹️ Akış durduruldu")
            time.sleep(0.3)
            st.rerun()
        
        if st.session_state.esp32_streaming and st.session_state.esp32_handler:
            handler = st.session_state.esp32_handler
            
            frame_update_interval = st.slider(
                "Frame Güncelleme (ms):",
                min_value=100,
                max_value=1000,
                value=500,
                step=100
            )
            
            if 'sistem' not in st.session_state:
                st.session_state.sistem = MakineParcaTanima()
            
            sistem = st.session_state.sistem
            
            yolo_model_path = "runs/detect/train/weights/best.pt"
            has_yolo_model = Path(yolo_model_path).exists() and YOLO_KULLANILABILIR
            
            col_proc1, col_proc2, col_proc3 = st.columns(3)
            
            with col_proc1:
                detect_objects = st.checkbox("🎯 YOLO Nesne Tespiti", value=has_yolo_model)
            
            with col_proc2:
                show_stats = st.checkbox("📊 İstatistik Göster", value=True)
            
            with col_proc3:
                record_frames = st.checkbox("💾 Frame'ler Kaydedilsin", value=False)
            
            st.divider()
            
            frame_count = 0
            start_time = time.time()
            detections_log = []
            
            while st.session_state.esp32_streaming and st.session_state.esp32_handler:
                try:
                    frame = handler.son_frame_al()
                    
                    if frame is None:
                        time.sleep(0.1)
                        continue
                    
                    display_frame = frame.copy()
                    display_frame = FrameProcessor.boyutlandir(
                        display_frame,
                        width=ESP32_GORUNTU_GENISLIK,
                        height=ESP32_GORUNTU_YUKSEKLIK
                    )
                    
                    if filter_type == "Gri Tonlama":
                        display_frame = FrameProcessor.gri_tonlama(display_frame)
                        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2BGR)
                    elif filter_type == "Kenar Tespiti":
                        display_frame = FrameProcessor.kenar_tespit(display_frame)
                        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2BGR)
                    elif filter_type == "Keskinleştirme":
                        display_frame = FrameProcessor.keskinlestir(display_frame)
                    elif filter_type == "Histogram Eşitleştir":
                        display_frame = FrameProcessor.histogram_esitlestir(display_frame)
                    
                    detection_info = None
                    if detect_objects and has_yolo_model:
                        try:
                            temp_path = "/tmp/esp32_frame.jpg"
                            cv2.imwrite(temp_path, display_frame)
                            
                            from ultralytics import YOLO
                            model = YOLO(yolo_model_path)
                            results = model(temp_path, verbose=False, conf=0.5)
                            
                            if results and len(results) > 0:
                                result = results[0]
                                
                                for box in result.boxes:
                                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                    conf = box.conf[0].cpu().numpy()
                                    cls = int(box.cls[0].cpu().numpy())
                                    
                                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                                    class_name = result.names[cls] if cls in result.names else f"Class {cls}"
                                    
                                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    label_text = f"{class_name}: {conf:.2f}"
                                    cv2.putText(
                                        display_frame,
                                        label_text,
                                        (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.7,
                                        (0, 255, 0),
                                        2
                                    )
                                    
                                    detections_log.append({
                                        "zaman": time.time(),
                                        "guven": float(conf),
                                        "sinif": class_name
                                    })
                            
                            if len(results[0].boxes) > 0:
                                detection_info = f"🎯 {len(results[0].boxes)} nesne tespit edildi"
                        except Exception as e:
                            detection_info = f"❌ Tespit hatası: {str(e)[:50]}"
                    
                    frame_count += 1
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    
                    if show_stats:
                        stats_text = f"FPS: {fps:.1f} | Frame: {frame_count}"
                        cv2.putText(
                            display_frame,
                            stats_text,
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2
                        )
                    
                    if detection_info:
                        cv2.putText(
                            display_frame,
                            detection_info,
                            (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 255),
                            2
                        )
                    
                    display_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    stream_placeholder.image(
                        display_frame_rgb,
                        width=ESP32_GORUNTU_GENISLIK,
                        caption=f"Canlı Görüntü ({ESP32_GORUNTU_GENISLIK}x{ESP32_GORUNTU_YUKSEKLIK})"
                    )
                    
                    if record_frames:
                        st.session_state.esp32_frames.append(display_frame.copy())
                    
                    time.sleep(frame_update_interval / 1000.0)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    st.error(f"❌ Akış hatası: {e}")
                    break
            
            if st.session_state.esp32_handler:
                st.session_state.esp32_handler.kapat()
            st.session_state.esp32_streaming = False
        
        else:
            with stream_placeholder.container():
                st.info("📹 Canlı akış başlatmak için ▶️ düğmesini tıklayın")
                placeholder_img = Image.new(
                    'RGB',
                    (ESP32_GORUNTU_GENISLIK, ESP32_GORUNTU_YUKSEKLIK),
                    color=(40, 40, 40)
                )
                st.image(
                    placeholder_img,
                    width=ESP32_GORUNTU_GENISLIK,
                    caption=f"Canlı Görüntü ({ESP32_GORUNTU_GENISLIK}x{ESP32_GORUNTU_YUKSEKLIK})"
                )
        
        if capture_snapshot and st.session_state.esp32_handler:
            with st.spinner("Snapshot alınıyor..."):
                snapshot = st.session_state.esp32_handler.snapshot_al()
                
                if snapshot is not None:
                    st.success("✅ Snapshot alındı!")
                    
                    snapshot_resized = cv2.resize(
                        snapshot,
                        (ESP32_GORUNTU_GENISLIK, ESP32_GORUNTU_YUKSEKLIK)
                    )
                    snapshot_rgb = cv2.cvtColor(snapshot_resized, cv2.COLOR_BGR2RGB)
                    st.image(
                        snapshot_rgb,
                        width=ESP32_GORUNTU_GENISLIK,
                        caption=f"Snapshot ({ESP32_GORUNTU_GENISLIK}x{ESP32_GORUNTU_YUKSEKLIK})"
                    )
                    
                    _, buffer = cv2.imencode('.jpg', snapshot)
                    jpg_data = buffer.tobytes()
                    
                    st.download_button(
                        label="📥 Snapshot İndir",
                        data=jpg_data,
                        file_name=f"esp32_snapshot_{int(time.time())}.jpg",
                        mime="image/jpeg"
                    )
    
    # Kamera kontrol paneli
    if st.session_state.esp32_handler and st.session_state.esp32_streaming:
        with st.expander("🎨 Kamera Kontrolleri"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                brightness = st.slider("Parlaklık:", -2, 2, 0)
                if st.button("Uygula", key="brightness"):
                    st.session_state.esp32_handler.parlaklik_ayarla(brightness)
                    st.success("✅ Parlaklık ayarlandı")
            
            with col2:
                contrast = st.slider("Kontrast:", -2, 2, 0)
                if st.button("Uygula", key="contrast"):
                    st.session_state.esp32_handler.kontrast_ayarla(contrast)
                    st.success("✅ Kontrast ayarlandı")
            
            with col3:
                saturation = st.slider("Doygunluk:", -2, 2, 0)
                if st.button("Uygula", key="saturation"):
                    st.session_state.esp32_handler.doygunluk_ayarla(saturation)
                    st.success("✅ Doygunluk ayarlandı")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Dikey Çevir", use_container_width=True):
                    st.session_state.esp32_handler.cevir_dikey(True)
                    st.success("✅ Uygulandı")
            
            with col2:
                if st.button("↔️ Yatay Çevir", use_container_width=True):
                    st.session_state.esp32_handler.cevir_yatay(True)
                    st.success("✅ Uygulandı")
            
            with col3:
                if st.button("🌙 Gece Modu", use_container_width=True):
                    st.session_state.esp32_handler.parlaklik_ayarla(2)
                    st.session_state.esp32_handler.kontrast_ayarla(1)


def main():
    """Ana Streamlit uygulaması"""
    st.set_page_config(
        page_title="Makine Parçası Tanıma Sistemi",
        page_icon="🔧",
        layout="wide"
    )
    
    # Sidebar - Sayfa seçimi
    with st.sidebar:
        st.title("🔧 Menü")
        sayfa = st.radio(
            "Sayfa Seçin:",
            ["🏠 Ana Sayfa - Parça Tanıma", "� ESP32Cam Canlı Kamera", "📊 Model Performans Testi"],
            index=0
        )
    
    # Sayfa yönlendirmesi
    if "ESP32Cam" in sayfa:
        esp32_sayfasi()
        return
    
    if "Model Performans" in sayfa:
        performans_sayfasi()
        return
    
    # Ana sayfa
    st.title("🔧 Makine Parçası Tanıma Sistemi")
    st.markdown("""
    Bu sistem görüntü işleme teknolojisi kullanarak makine parçalarını tanır ve 
    onlar hakkında detaylı bilgi verir.
    """)
    
    # Sistem başlat
    if 'sistem' not in st.session_state:
        st.session_state.sistem = MakineParcaTanima()
    
    sistem = st.session_state.sistem
    
    # Hibrit sistem kontrolü
    hibrit_sistem = None
    if HIBRIT_KULLANILABILIR:
        if 'hibrit_sistem' not in st.session_state:
            # Hibrit sistem başlat
            model_path = 'best_model.pth' if Path('best_model.pth').exists() else None
            referans_path = 'referans_gorseller' if Path('referans_gorseller').exists() else None
            
            if model_path or referans_path:
                st.session_state.hibrit_sistem = HibritTanima(
                    model_path=model_path,
                    referans_klasor=referans_path,
                    mod='auto',
                    guven_esik=0.7
                )
        
        hibrit_sistem = st.session_state.get('hibrit_sistem')
    
    # Sidebar - Bilgi
    with st.sidebar:
        st.header("ℹ️ Kullanım Kılavuzu")
        st.markdown("""
        1. Bir görüntü yükleyin
        2. Tanıma yöntemini seçin
        3. Sistem otomatik olarak analiz edecek
        4. Parça bilgilerini görüntüleyin
        
        **Desteklenen Formatlar:**
        - JPG, JPEG, PNG
        
        **Tanınabilir Parçalar:**
        - Vida, Somun
        - Rulman
        - Kayış, Dişli
        - Piston, Supap
        - Krank Mili
        - Yay
        """)
        
        st.divider()
        
        # Tanıma yöntemi seçimi
        st.header("🔧 Tanıma Yöntemi")
        
        yontemler = ["Kural Tabanlı (Basit)"]
        
        # YOLO model kontrolü
        yolo_model_path = "runs/detect/train/weights/best.pt"  # Varsayılan değer
        if YOLO_KULLANILABILIR:
            yolo_model_path = st.text_input(
                "YOLO Model Yolu:",
                value=yolo_model_path,
                help="Eğitilmiş YOLO model dosyasının yolu"
            )
            if Path(yolo_model_path).exists():
                yontemler.insert(0, "🎯 YOLO (Eğitilmiş Model)")
                st.success("✅ YOLO modeli bulundu!")
            else:
                st.warning("⚠️ YOLO modeli bulunamadı")
        
        if hibrit_sistem:
            if hibrit_sistem.dl_kullanilabilir:
                yontemler.append("Deep Learning")
            if hibrit_sistem.feature_kullanilabilir:
                yontemler.append("Feature Matching")
            if hibrit_sistem.dl_kullanilabilir or hibrit_sistem.feature_kullanilabilir:
                yontemler.append("Hibrit (Otomatik)")
                yontemler.append("Ensemble (İkisini Birleştir)")
        
        secili_yontem = st.selectbox(
            "Yöntem seçin:",
            yontemler,
            index=0 if "YOLO" in yontemler[0] else (len(yontemler)-1 if len(yontemler) > 1 else 0)
        )
        
        if hibrit_sistem:
            st.info(f"""
            **Aktif Sistemler:**
            - DL Model: {'✅' if hibrit_sistem.dl_kullanilabilir else '❌'}
            - Feature Match: {'✅' if hibrit_sistem.feature_kullanilabilir else '❌'}
            """)
        
        st.divider()
        
        st.header("📚 Veritabanı")
        st.write(f"Toplam {len(sistem.parca_veritabani)} parça tanımlanmış")
        
        if st.checkbox("Tüm parçaları göster"):
            for parca_id, bilgi in sistem.parca_veritabani.items():
                st.markdown(f"**{bilgi['isim']}**")
    
    # Ana içerik
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📸 Görüntü Yükleme")
        
        # Dosya yükleme
        uploaded_file = st.file_uploader(
            "Makine parçası görüntüsü seçin",
            type=['jpg', 'jpeg', 'png']
        )
        
        # Temizle butonu
        if st.button("🗑️ Sonuçları Temizle"):
            if 'sonuc' in st.session_state:
                del st.session_state.sonuc
                st.rerun()
        
        # Örnek parçalar
        st.subheader("veya örnek bir parça seçin:")
        ornek_parca = st.selectbox(
            "Örnek Parçalar",
            ["Seçiniz...", "Vida", "Somun", "Rulman", "Dişli", "Piston"]
        )
        
        if uploaded_file is not None:
            # Görüntüyü yükle
            image = Image.open(uploaded_file)
            # PIL Image'i RGB'ye dönüştür (format problemlerini önlemek için)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            # Görüntüyü 720x560 standardında göster
            img_array = np.array(image)
            # OpenCV BGR formatını bekler, PIL RGB döndürür - BGR'ye çevir
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = img_array  # Zaten doğru formatta veya gri tonlama
            img_resized = cv2.resize(img_bgr, (720, 560))
            # Gösterim için RGB'ye geri çevir
            if len(img_resized.shape) == 3 and img_resized.shape[2] == 3:
                img_display = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            else:
                img_display = img_resized
            st.image(img_display, caption="Yüklenen Görüntü (720x560)", use_container_width=True)
            
            # Analiz et butonu
            if st.button("🔍 Analiz Et", type="primary"):
                with st.spinner("Görüntü analiz ediliyor..."):
                    # Görüntüyü geçici olarak kaydet (resize edilmiş versyon)
                    temp_path = "temp_upload.jpg"
                    cv2.imwrite(temp_path, img_resized)
                    
                    # Görüntü işleme (numpy array üzerinde)
                    processed = sistem.goruntu_onisleme(img_resized)
                    ozellikler = sistem.ozellik_cikarma(img_resized)
                    
                    # Şekil analizi yap
                    from image_utils import GorselIslemci
                    img_cv = cv2.imread(temp_path)
                    sekiller = GorselIslemci.sekil_analizi(img_cv)
                    
                    # Seçilen yönteme göre tanıma
                    if secili_yontem == "🎯 YOLO (Eğitilmiş Model)":
                        # YOLO ile tahmin
                        yolo_sonuc = sistem.yolo_tahmin(temp_path, model_path=yolo_model_path)
                        
                        if yolo_sonuc:
                            parca_adi = yolo_sonuc['parca']
                            yontem_bilgi = {
                                "yontem": "YOLO v8",
                                "guven": yolo_sonuc['guven'],
                                "detay": f"YOLOv8 Object Detection - {yolo_sonuc['toplam_nesne']} nesne tespit edildi",
                                "tum_tespitler": yolo_sonuc['tum_tespitler'],
                                "sonuc_goruntu": yolo_sonuc['sonuc_goruntu']
                            }
                        else:
                            # Tespit başarısız, fallback
                            parca_adi = sistem.parca_tanima_basit(ozellikler)
                            yontem_bilgi = {
                                "yontem": "YOLO (Tespit Yok)",
                                "guven": 0.3,
                                "detay": "YOLO hiçbir nesne tespit edemedi, basit yönteme geçildi"
                            }
                    
                    elif secili_yontem == "Kural Tabanlı (Basit)":
                        parca_adi = sistem.parca_tanima_basit(ozellikler)
                        yontem_bilgi = {
                            "yontem": "Kural Tabanlı",
                            "guven": 0.5,  # Sabit değer
                            "detay": "Şekil ve özellik tabanlı basit tanıma"
                        }
                    
                    elif hibrit_sistem and secili_yontem == "Deep Learning":
                        hibrit_sistem.mod = 'dl_only'
                        sonuc = hibrit_sistem.tanima_yap(temp_path)
                        parca_adi = sonuc['parca']
                        yontem_bilgi = {
                            "yontem": "Deep Learning",
                            "guven": sonuc['guven'],
                            "detay": f"Neural Network tabanlı tanıma",
                            "olasiliklar": sonuc.get('olasiliklar', {})
                        }
                    
                    elif hibrit_sistem and secili_yontem == "Feature Matching":
                        hibrit_sistem.mod = 'feature_only'
                        sonuc = hibrit_sistem.tanima_yap(temp_path)
                        parca_adi = sonuc['parca']
                        yontem_bilgi = {
                            "yontem": "Feature Matching",
                            "guven": sonuc['guven'],
                            "detay": f"SIFT + Histogram + Hu Moments",
                            "sift": sonuc.get('sift_skor', 0),
                            "histogram": sonuc.get('histogram_skor', 0),
                            "hu": sonuc.get('hu_skor', 0)
                        }
                    
                    elif hibrit_sistem and secili_yontem == "Hibrit (Otomatik)":
                        hibrit_sistem.mod = 'auto'
                        sonuc = hibrit_sistem.tanima_yap(temp_path)
                        parca_adi = sonuc['parca']
                        yontem_bilgi = {
                            "yontem": "Hibrit Otomatik",
                            "guven": sonuc['guven'],
                            "detay": f"Kullanılan: {sonuc['method']}",
                            "tam_sonuc": sonuc
                        }
                    
                    elif hibrit_sistem and secili_yontem == "Ensemble (İkisini Birleştir)":
                        hibrit_sistem.mod = 'ensemble'
                        sonuc = hibrit_sistem.tanima_yap(temp_path)
                        parca_adi = sonuc['parca']
                        yontem_bilgi = {
                            "yontem": "Ensemble",
                            "guven": sonuc['guven'],
                            "detay": "DL + Feature Matching birleşimi",
                            "tam_sonuc": sonuc
                        }
                    
                    else:
                        # Fallback
                        parca_adi = sistem.parca_tanima_basit(ozellikler)
                        yontem_bilgi = {
                            "yontem": "Kural Tabanlı (Fallback)",
                            "guven": 0.5,
                            "detay": "Varsayılan basit tanıma"
                        }
                    
                    # Geçici dosyayı sil
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    # Sonuçları session'a kaydet
                    st.session_state.sonuc = {
                        "parca_adi": parca_adi,
                        "ozellikler": ozellikler,
                        "processed": processed,
                        "yontem_bilgi": yontem_bilgi,
                        "sekiller": sekiller
                    }
        
        elif ornek_parca != "Seçiniz...":
            st.info(f"'{ornek_parca}' için bilgiler gösteriliyor...")
            st.session_state.sonuc = {
                "parca_adi": ornek_parca.lower(),
                "ozellikler": {"sekil": "Örnek"},
                "processed": None
            }
    
    with col2:
        st.header("📊 Analiz Sonuçları")
        
        if 'sonuc' in st.session_state:
            sonuc = st.session_state.sonuc
            parca_bilgi = sistem.bilgi_getir(sonuc["parca_adi"])
            yontem_bilgi = sonuc.get("yontem_bilgi", {})
            
            # Tanıma sonucu
            st.success(f"✅ Tespit Edilen Parça: **{parca_bilgi['isim']}**")
            
            # YOLO tespit sonucu görselini göster
            if yontem_bilgi.get('sonuc_goruntu') is not None:
                try:
                    st.subheader("🎯 YOLO Tespit Sonucu")
                    sonuc_img = yontem_bilgi['sonuc_goruntu']
                    # BGR to RGB dönüşümü
                    sonuc_img_rgb = cv2.cvtColor(sonuc_img, cv2.COLOR_BGR2RGB)
                    st.image(sonuc_img_rgb, caption="Tespit Edilen Nesneler (Bounding Box)", use_container_width=True)
                    
                    # Tüm tespitleri göster
                    if yontem_bilgi.get('tum_tespitler'):
                        st.markdown("**🔍 Tespit Edilen Tüm Nesneler:**")
                        for i, tespit in enumerate(yontem_bilgi['tum_tespitler'], 1):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            with col1:
                                st.write(f"**{i}. {tespit['sinif_adi']}**")
                            with col2:
                                st.write(f"Türkçe: *{sistem.parca_veritabani.get(tespit['veritabani_adi'], {}).get('isim', tespit['sinif_adi'])}*")
                            with col3:
                                st.write(f"🎯 %{tespit['guven']*100:.1f}")
                    
                    st.divider()
                except Exception as e:
                    st.warning(f"⚠️ Tespit görseli gösterilemiyor: {str(e)}")
                    st.divider()
            
            # Yöntem bilgisi
            yontem_bilgi = sonuc.get("yontem_bilgi", {})
            if yontem_bilgi:
                guven_renk = "🟢" if yontem_bilgi['guven'] > 0.7 else "🟡" if yontem_bilgi['guven'] > 0.5 else "🔴"
                st.metric(
                    label=f"Yöntem: {yontem_bilgi['yontem']}",
                    value=f"{guven_renk} %{yontem_bilgi['guven']*100:.1f} Güven"
                )
                
                # Detaylı bilgi
                with st.expander("🔍 Tanıma Detayları"):
                    st.write(yontem_bilgi['detay'])
                    
                    # Olasılıklar varsa göster
                    if 'olasiliklar' in yontem_bilgi:
                        st.markdown("**Sınıf Olasılıkları:**")
                        olasiliklar = sorted(
                            yontem_bilgi['olasiliklar'].items(),
                            key=lambda x: x[1],
                            reverse=True
                        )
                        for sinif, olasilik in olasiliklar[:5]:
                            st.progress(olasilik, text=f"{sinif}: %{olasilik*100:.1f}")
                    
                    # Feature matching skorları
                    if 'sift' in yontem_bilgi:
                        col1, col2, col3 = st.columns(3)
                        col1.metric("SIFT", f"{yontem_bilgi['sift']:.3f}")
                        col2.metric("Histogram", f"{yontem_bilgi['histogram']:.3f}")
                        col3.metric("Hu Moments", f"{yontem_bilgi['hu']:.3f}")
                    
                    # Ensemble detayları
                    if 'tam_sonuc' in yontem_bilgi:
                        st.json(yontem_bilgi['tam_sonuc'])
            
            # Parça tanımı
            st.markdown("### 📝 Tanım")
            st.info(parca_bilgi['tanim'])
            
            # Kullanım alanları
            if parca_bilgi.get('kullanim_alanlari'):
                st.markdown("### 🔨 Kullanım Alanları")
                for alan in parca_bilgi['kullanim_alanlari']:
                    st.markdown(f"- {alan}")
            
            # Özellikler
            if parca_bilgi.get('ozellikler'):
                st.markdown("### ⚙️ Teknik Özellikler")
                for ozellik in parca_bilgi['ozellikler']:
                    st.markdown(f"- {ozellik}")
            
            # Çeşitleri
            if parca_bilgi.get('cesitleri'):
                st.markdown("### 📦 Çeşitleri")
                cesit_cols = st.columns(2)
                for idx, cesit in enumerate(parca_bilgi['cesitleri']):
                    with cesit_cols[idx % 2]:
                        st.markdown(f"- {cesit}")
            
            # Görüntü işleme sonuçları
            if sonuc.get("processed"):
                with st.expander("🔬 Görüntü İşleme Detayları"):
                    proc_cols = st.columns(2)
                    
                    with proc_cols[0]:
                        st.image(sonuc["processed"]["gri"], 
                                caption="Gri Tonlama", 
                                use_container_width=True)
                    
                    with proc_cols[1]:
                        st.image(sonuc["processed"]["kenarlar"], 
                                caption="Kenar Tespiti", 
                                use_container_width=True)
                    
                    # Şekil analizi sonuçları
                    if sonuc.get("sekiller"):
                        st.markdown("**🔷 Şekil Analizi Sonuçları:**")
                        for i, sekil in enumerate(sonuc["sekiller"], 1):
                            # Dairesellik bazlı öneri
                            oneri = ""
                            if sekil['dairesellik'] > 0.75:
                                oneri = "🔴 (Daire/Elips → **Rulman** veya **Dişli** olabilir)"
                            elif sekil['dairesellik'] > 0.6:
                                oneri = "🟡 (Yuvarlağa yakın şekil)"
                            
                            st.markdown(f"""
                            **Şekil {i}:**
                            - Tip: **{sekil.get('tip', sekil['sekil'])}** 
                            - Şekil: **{sekil['sekil']}**
                            - Dairesellik: {sekil['dairesellik']:.3f} {oneri}
                            - Alan: {sekil['alan']:.0f} px²
                            - Köşe Sayısı: {sekil['koseler']}
                            """)
                            if i >= 3:  # İlk 3 şekli göster
                                break
                    
                    # Özellikler
                    st.markdown("**Çıkarılan Özellikler:**")
                    st.json(sonuc["ozellikler"])
        else:
            st.info("👆 Lütfen bir görüntü yükleyin veya örnek parça seçin")
    
    # Alt bilgi
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    <small>
    Makine Parçası Tanıma Sistemi v1.0 | 
    Görüntü İşleme & Yapay Zeka Tabanlı | 
    Python + OpenCV + PyTorch
    </small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
