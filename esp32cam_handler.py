"""
ESP32Cam Canlı Kamera Yöneticisi
ESP32Cam modülünden canlı görüntü alarak makine parçası tanımasını yapan modül
"""

import cv2
import numpy as np
import threading
import time
import requests
from urllib.parse import urlparse
from PIL import Image
import io
import logging
from typing import Optional, Dict, Tuple
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ESP32CamHandler:
    """ESP32Cam canlı akışını işleyen sınıf"""
    
    def __init__(self, esp32_ip: str, port: int = 80, timeout: int = 5):
        """
        ESP32Cam bağlantısını başlat
        
        Args:
            esp32_ip: ESP32 cihazının IP adresi (ör: 192.168.1.100)
            port: ESP32 web sunucusu portu (varsayılan 80)
            timeout: Bağlantı zaman aşımı (saniye)
        """
        self.esp32_ip = esp32_ip
        self.port = port
        self.timeout = timeout
        
        # URL oluştur
        if not esp32_ip.startswith("http://") and not esp32_ip.startswith("https://"):
            self.base_url = f"http://{esp32_ip}:{port}"
        else:
            self.base_url = esp32_ip
        
        # Stream ve kontrol URLs
        self.stream_url = f"{self.base_url}/stream"
        self.capture_url = f"{self.base_url}/capture"
        self.control_url = f"{self.base_url}/control"
        
        # Bağlantı durumu
        self.is_connected = False
        self.is_streaming = False
        self.stream_thread = None
        self.frame_buffer = deque(maxlen=2)  # Son 2 frame'i sakla
        self.lock = threading.Lock()
        
        # İstatistikler
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        self.frame_times = deque(maxlen=30)
        
        # Test bağlantı
        self.test_baglanti()
    
    def test_baglanti(self) -> bool:
        """ESP32'ye bağlantı testi yap"""
        try:
            response = requests.get(
                f"{self.base_url}/status",
                timeout=self.timeout
            )
            if response.status_code == 200:
                self.is_connected = True
                logger.info(f"✅ ESP32Cam'e başarıyla bağlandı: {self.esp32_ip}")
                return True
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ ESP32Cam'e bağlanılamadı: {e}")
        
        self.is_connected = False
        return False
    
    def basla_stream(self):
        """Canlı akışı başlat"""
        if not self.is_connected:
            logger.error("❌ ESP32Cam'e bağlı değilsiniz")
            return False
        
        if self.is_streaming:
            logger.warning("⚠️ Akış zaten başlamış")
            return True
        
        self.is_streaming = True
        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()
        logger.info("✅ Canlı akış başlatıldı")
        return True
    
    def durdur_stream(self):
        """Canlı akışı durdur"""
        self.is_streaming = False
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=2)
        logger.info("⏹️ Canlı akış durduruldu")
    
    def _stream_loop(self):
        """Akış döngüsü"""
        try:
            response = requests.get(
                self.stream_url,
                stream=True,
                timeout=self.timeout
            )
            
            bytes_data = b''
            
            for chunk in response.iter_content(chunk_size=1024):
                if not self.is_streaming:
                    break
                
                bytes_data += chunk
                
                # JPEG sınırlarını bul
                a = bytes_data.find(b'\xff\xd8')  # JPEG başlangıcı
                b = bytes_data.find(b'\xff\xd9')  # JPEG sonu
                
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    # Frame'i decode et
                    frame = cv2.imdecode(
                        np.frombuffer(jpg, dtype=np.uint8),
                        cv2.IMREAD_COLOR
                    )
                    
                    if frame is not None:
                        # Buffer'a ekle
                        with self.lock:
                            self.frame_buffer.append(frame)
                            self.frame_count += 1
                        
                        # FPS hesapla
                        self._update_fps()
        
        except Exception as e:
            logger.error(f"❌ Stream döngüsünde hata: {e}")
        finally:
            self.is_streaming = False
    
    def _update_fps(self):
        """FPS hesapla"""
        current_time = time.time()
        self.frame_times.append(current_time)
        
        if len(self.frame_times) > 1:
            time_diff = self.frame_times[-1] - self.frame_times[0]
            if time_diff > 0:
                self.fps = len(self.frame_times) / time_diff
    
    def son_frame_al(self) -> Optional[np.ndarray]:
        """Son yakalanan frame'i al"""
        with self.lock:
            if self.frame_buffer:
                return self.frame_buffer[-1].copy()
        return None
    
    def snapshot_al(self) -> Optional[np.ndarray]:
        """Tek bir snapshot al"""
        try:
            response = requests.get(
                self.capture_url,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                frame = cv2.imdecode(
                    np.frombuffer(response.content, dtype=np.uint8),
                    cv2.IMREAD_COLOR
                )
                return frame
        except Exception as e:
            logger.error(f"❌ Snapshot alınamadı: {e}")
        
        return None
    
    def kamera_ayarla(self, setting: str, value: int) -> bool:
        """
        ESP32 kamera ayarlarını değiştir
        
        Args:
            setting: Ayar adı (brightness, contrast, saturation, vb.)
            value: Yeni değer
        """
        try:
            response = requests.post(
                f"{self.control_url}?var={setting}&val={value}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Kamera ayarı güncellendi: {setting}={value}")
                return True
        except Exception as e:
            logger.error(f"❌ Kamera ayarı değiştirilemedi: {e}")
        
        return False
    
    def parlaklik_ayarla(self, value: int) -> bool:
        """Parlaklığı ayarla (-2 to 2)"""
        return self.kamera_ayarla("brightness", value)
    
    def kontrast_ayarla(self, value: int) -> bool:
        """Kontrastı ayarla (-2 to 2)"""
        return self.kamera_ayarla("contrast", value)
    
    def doygunluk_ayarla(self, value: int) -> bool:
        """Doygunluğu ayarla (-2 to 2)"""
        return self.kamera_ayarla("saturation", value)
    
    def otomatik_beyaz_balansi_ac(self) -> bool:
        """Otomatik beyaz balansı aç"""
        return self.kamera_ayarla("awb", 1)
    
    def otomatik_beyaz_balansi_kapat(self) -> bool:
        """Otomatik beyaz balansı kapat"""
        return self.kamera_ayarla("awb", 0)
    
    def cevir_dikey(self, ac: bool = True) -> bool:
        """Görüntüyü dikey çevir"""
        return self.kamera_ayarla("vflip", 1 if ac else 0)
    
    def cevir_yatay(self, ac: bool = True) -> bool:
        """Görüntüyü yatay çevir"""
        return self.kamera_ayarla("hflip", 1 if ac else 0)
    
    def istatistikler_al(self) -> Dict:
        """İstatistikleri al"""
        return {
            "baglanti": self.is_connected,
            "akis": self.is_streaming,
            "toplam_frame": self.frame_count,
            "fps": round(self.fps, 2),
            "buffer_boyutu": len(self.frame_buffer)
        }
    
    def kapat(self):
        """Bağlantıyı kapat"""
        self.durdur_stream()
        self.is_connected = False
        logger.info("🔌 ESP32Cam bağlantısı kapatıldı")


class ESP32CamBuffer:
    """ESP32Cam frame buffer yöneticisi"""
    
    def __init__(self, buffer_size: int = 30):
        """
        Buffer'ı başlat
        
        Args:
            buffer_size: Buffer boyutu (frame sayısı)
        """
        self.buffer = deque(maxlen=buffer_size)
        self.timestamps = deque(maxlen=buffer_size)
        self.lock = threading.Lock()
    
    def frame_ekle(self, frame: np.ndarray):
        """Frame ekle"""
        with self.lock:
            self.buffer.append(frame.copy())
            self.timestamps.append(time.time())
    
    def son_frame_al(self) -> Optional[np.ndarray]:
        """Son frame'i al"""
        with self.lock:
            if self.buffer:
                return self.buffer[-1].copy()
        return None
    
    def tum_frameler_al(self) -> list:
        """Tüm frame'leri al"""
        with self.lock:
            return list(self.buffer)
    
    def temizle(self):
        """Buffer'ı temizle"""
        with self.lock:
            self.buffer.clear()
            self.timestamps.clear()


class FrameProcessor:
    """ESP32Cam frame'lerini işleme"""
    
    @staticmethod
    def boyutlandir(frame: np.ndarray, width: int = 720, height: int = 560) -> np.ndarray:
        """Frame'i boyutlandır"""
        return cv2.resize(frame, (width, height))
    
    @staticmethod
    def gri_tonlama(frame: np.ndarray) -> np.ndarray:
        """Gri tonlamaya çevir"""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def bulaniklastir(frame: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """Gaussian bulanıklığı uygula"""
        return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    
    @staticmethod
    def keskinlestir(frame: np.ndarray) -> np.ndarray:
        """Keskinleştirme filtresi uygula"""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(frame, -1, kernel)
    
    @staticmethod
    def kenar_tespit(frame: np.ndarray, threshold1: int = 50, 
                     threshold2: int = 150) -> np.ndarray:
        """Canny kenar tespiti"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.Canny(gray, threshold1, threshold2)
    
    @staticmethod
    def histogram_esitlestir(frame: np.ndarray) -> np.ndarray:
        """Histogram eşitleştirme (kontrast iyileştirme)"""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.equalizeHist(l)
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    @staticmethod
    def metni_ekle(frame: np.ndarray, text: str, pos: Tuple = (10, 30),
                   font_size: float = 1, color: Tuple = (0, 255, 0),
                   thickness: int = 2) -> np.ndarray:
        """Frame'e metin ekle"""
        return cv2.putText(
            frame,
            text,
            pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_size,
            color,
            thickness
        )
    
    @staticmethod
    def dikdortgen_ciz(frame: np.ndarray, pt1: Tuple, pt2: Tuple,
                       color: Tuple = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """Frame'e dikdörtgen çiz"""
        return cv2.rectangle(frame, pt1, pt2, color, thickness)


def esp32_durum_kontrol(esp32_ip: str, port: int = 80) -> Dict:
    """
    ESP32 cihazının durumunu kontrol et
    
    Args:
        esp32_ip: ESP32 IP adresi
        port: Port numarası
    
    Returns:
        Durum bilgileri
    """
    base_url = f"http://{esp32_ip}:{port}"
    
    sonuc = {
        "durum": "Offline",
        "ip": esp32_ip,
        "port": port,
        "error": None
    }
    
    try:
        response = requests.get(f"{base_url}/status", timeout=3)
        if response.status_code == 200:
            sonuc["durum"] = "Online ✅"
            try:
                sonuc["bilgi"] = response.json()
            except:
                sonuc["bilgi"] = response.text
    except requests.exceptions.ConnectionError:
        sonuc["error"] = "Bağlantı başarısız"
    except requests.exceptions.Timeout:
        sonuc["error"] = "Zaman aşımı"
    except Exception as e:
        sonuc["error"] = str(e)
    
    return sonuc


if __name__ == "__main__":
    # Test kodu
    esp32 = ESP32CamHandler("192.168.1.100")
    
    if esp32.is_connected:
        esp32.basla_stream()
        time.sleep(2)
        frame = esp32.son_frame_al()
        if frame is not None:
            cv2.imshow("ESP32Cam", frame)
            cv2.waitKey(1000)
        esp32.durdur_stream()
    
    esp32.kapat()
