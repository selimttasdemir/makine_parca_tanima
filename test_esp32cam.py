#!/usr/bin/env python3
"""
ESP32Cam Bağlantı Test Aracı
ESP32Cam modülüne bağlantıyı test etmek ve canlı kameraları görüntülemek için kullanılır.
"""

import cv2
import sys
import argparse
from pathlib import Path
from esp32cam_handler import (
    ESP32CamHandler, ESP32CamBuffer, FrameProcessor, esp32_durum_kontrol
)


def test_baglanti(ip_address: str, port: int = 80, timeout: int = 5):
    """
    ESP32Cam'e bağlantı testi yap
    
    Args:
        ip_address: ESP32 IP adresi
        port: Port numarası
        timeout: Zaman aşımı (saniye)
    """
    print(f"🔍 {ip_address}:{port} adresine bağlantı test ediliyor...")
    
    durum = esp32_durum_kontrol(ip_address, port)
    
    print(f"\n📊 Bağlantı Sonucu:")
    print(f"   Durum: {durum['durum']}")
    if durum.get('error'):
        print(f"   Hata: {durum['error']}")
        return False
    else:
        print("   ✅ Bağlantı Başarılı!")
        return True


def snapshot_al(ip_address: str, port: int = 80, kaydet_dosya: str = None):
    """
    ESP32Cam'den snapshot al
    
    Args:
        ip_address: ESP32 IP adresi
        port: Port numarası
        kaydet_dosya: Snapshot'ı kaydedilecek dosya yolu
    """
    print(f"\n📸 Snapshot alınıyor...")
    
    try:
        handler = ESP32CamHandler(ip_address, port)
        
        if not handler.is_connected:
            print("❌ ESP32Cam'e bağlanılamadı!")
            return False
        
        snapshot = handler.snapshot_al()
        
        if snapshot is not None:
            print("✅ Snapshot alındı!")
            
            # Görüntüle
            cv2.imshow("ESP32Cam Snapshot", snapshot)
            print("   Kapatmak için herhangi bir tuşa basın...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            # Kaydet
            if kaydet_dosya:
                cv2.imwrite(kaydet_dosya, snapshot)
                print(f"   Dosya kaydedildi: {kaydet_dosya}")
            
            handler.kapat()
            return True
        else:
            print("❌ Snapshot alınamadı!")
            return False
    
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


def canli_stream(ip_address: str, port: int = 80, sure: int = 30, 
                 filtre: str = "Normal", yolo: bool = False):
    """
    ESP32Cam'den canlı akışı izle
    
    Args:
        ip_address: ESP32 IP adresi
        port: Port numarası
        sure: İzleme süresi (saniye)
        filtre: Uygulanacak filtre (Normal, GriTonlama, KeyarTespiti, vb.)
        yolo: YOLO tespiti etkinleştir
    """
    print(f"\n▶️ Canlı akış başlatılıyor (Süre: {sure}s)...")
    print("   Kapatmak için ESC tuşuna basın")
    
    try:
        handler = ESP32CamHandler(ip_address, port)
        
        if not handler.is_connected:
            print("❌ ESP32Cam'e bağlanılamadı!")
            return False
        
        print("✅ Bağlantı başarılı!")
        print("   Canlı akış başlatılıyor...")
        
        handler.basla_stream()
        
        import time
        start_time = time.time()
        frame_count = 0
        
        while (time.time() - start_time) < sure:
            frame = handler.son_frame_al()
            
            if frame is None:
                continue
            
            # Filtre uygula
            if filtre == "GriTonlama":
                processed = FrameProcessor.gri_tonlama(frame)
                processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            elif filtre == "KeyarTespiti":
                processed = FrameProcessor.kenar_tespit(frame)
                processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            elif filtre == "Keskinleştirme":
                processed = FrameProcessor.keskinlestir(frame)
            elif filtre == "Histogram":
                processed = FrameProcessor.histogram_esitlestir(frame)
            else:
                processed = frame
            
            # FPS ve bilgi
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            frame_count += 1
            
            info_text = f"FPS: {fps:.1f} | Frame: {frame_count} | Filtre: {filtre}"
            cv2.putText(
                processed, info_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2
            )
            
            # Göster
            cv2.imshow("ESP32Cam Canlı Akış", processed)
            
            # ESC tuşu kontrolü
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("\n   Kullanıcı tarafından kapatıldı")
                break
        
        handler.durdur_stream()
        handler.kapat()
        cv2.destroyAllWindows()
        
        print(f"✅ İşlem tamamlandı! (Toplam: {frame_count} frame)")
        return True
    
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


def kamera_ayar_test(ip_address: str, port: int = 80):
    """
    Kamera ayarlarını test et
    
    Args:
        ip_address: ESP32 IP adresi
        port: Port numarası
    """
    print(f"\n🎨 Kamera ayarları test ediliyor...")
    
    try:
        handler = ESP32CamHandler(ip_address, port)
        
        if not handler.is_connected:
            print("❌ ESP32Cam'e bağlanılamadı!")
            return False
        
        print("✅ Bağlantı başarılı!\n")
        
        # Test ayarları
        ayarlar = [
            ("Parlaklık", lambda h, v: h.parlaklik_ayarla(v), 2),
            ("Kontrast", lambda h, v: h.kontrast_ayarla(v), 2),
            ("Doygunluk", lambda h, v: h.doygunluk_ayarla(v), 2),
            ("Otomatik Beyaz Balans (Aç)", lambda h, v: h.otomatik_beyaz_balansi_ac(), None),
            ("Dikey Çevir", lambda h, v: h.cevir_dikey(True), None),
            ("Yatay Çevir", lambda h, v: h.cevir_yatay(True), None),
        ]
        
        for ayar_adi, ayar_func, value in ayarlar:
            try:
                if value is not None:
                    sonuc = ayar_func(handler, value)
                else:
                    sonuc = ayar_func(handler, None)
                
                status = "✅" if sonuc else "❌"
                print(f"   {status} {ayar_adi}")
            except Exception as e:
                print(f"   ❌ {ayar_adi}: {e}")
        
        handler.kapat()
        return True
    
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="ESP32Cam Bağlantı ve Fonksiyon Test Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python3 test_esp32cam.py -i 192.168.1.100 test-connection
  python3 test_esp32cam.py -i 192.168.1.100 snapshot -o snapshot.jpg
  python3 test_esp32cam.py -i 192.168.1.100 stream -d 30 -f GriTonlama
  python3 test_esp32cam.py -i 192.168.1.100 camera-settings
        """
    )
    
    parser.add_argument(
        "-i", "--ip",
        required=True,
        help="ESP32 IP adresi (ör: 192.168.1.100)"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=80,
        help="Port numarası (varsayılan: 80)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Komut seçin")
    
    # Test bağlantı komutu
    subparsers.add_parser(
        "test-connection",
        help="Bağlantı testini çalıştır"
    )
    
    # Snapshot komutu
    snap_parser = subparsers.add_parser(
        "snapshot",
        help="Snapshot al"
    )
    snap_parser.add_argument(
        "-o", "--output",
        default=None,
        help="Çıktı dosya yolu"
    )
    
    # Stream komutu
    stream_parser = subparsers.add_parser(
        "stream",
        help="Canlı akışı izle"
    )
    stream_parser.add_argument(
        "-d", "--duration",
        type=int,
        default=30,
        help="İzleme süresi saniye (varsayılan: 30)"
    )
    stream_parser.add_argument(
        "-f", "--filter",
        default="Normal",
        choices=["Normal", "GriTonlama", "KeyarTespiti", "Keskinleştirme", "Histogram"],
        help="Uygulanacak filtre"
    )
    stream_parser.add_argument(
        "--yolo",
        action="store_true",
        help="YOLO tespiti etkinleştir"
    )
    
    # Kamera ayarları komutu
    subparsers.add_parser(
        "camera-settings",
        help="Kamera ayarlarını test et"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("="*60)
    print("🔧 ESP32Cam Test Aracı")
    print("="*60)
    
    try:
        if args.command == "test-connection":
            test_baglanti(args.ip, args.port)
        
        elif args.command == "snapshot":
            snapshot_al(args.ip, args.port, args.output)
        
        elif args.command == "stream":
            canli_stream(
                args.ip, args.port,
                sure=args.duration,
                filtre=args.filter,
                yolo=args.yolo
            )
        
        elif args.command == "camera-settings":
            kamera_ayar_test(args.ip, args.port)
    
    except KeyboardInterrupt:
        print("\n\n⏹️ İşlem iptal edildi")
    except Exception as e:
        print(f"\n❌ Beklenmedik hata: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
