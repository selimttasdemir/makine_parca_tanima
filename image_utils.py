"""
Görüntü İşleme Yardımcı Fonksiyonlar
"""

import cv2
import numpy as np
from PIL import Image


class GorselIslemci:
    """Gelişmiş görüntü işleme araçları"""
    
    @staticmethod
    def kenar_tespit(image, method='canny'):
        """
        Farklı yöntemlerle kenar tespiti
        
        Args:
            image: Giriş görüntüsü (numpy array)
            method: 'canny', 'sobel', 'laplacian'
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        if method == 'canny':
            edges = cv2.Canny(gray, 50, 150)
        elif method == 'sobel':
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
            edges = np.sqrt(sobelx**2 + sobely**2)
            edges = np.uint8(edges / edges.max() * 255)
        elif method == 'laplacian':
            edges = cv2.Laplacian(gray, cv2.CV_64F)
            edges = np.uint8(np.absolute(edges))
        else:
            raise ValueError(f"Bilinmeyen method: {method}")
        
        return edges
    
    @staticmethod
    def sekil_analizi(image):
        """Görüntüdeki şekilleri analiz et"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Binary threshold
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Konturları bul
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        sonuclar = []
        
        for contour in contours:
            # Alan hesapla
            area = cv2.contourArea(contour)
            if area < 100:  # Çok küçük alanları atla
                continue
            
            # Çevre hesapla
            perimeter = cv2.arcLength(contour, True)
            
            # Şekil yaklaşımı
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            
            # Merkez nokta
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = 0, 0
            
            # Sınırlayıcı dikdörtgen
            x, y, w, h = cv2.boundingRect(contour)
            
            # Dairesellik (circularity)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
            else:
                circularity = 0
            
            # Şekil sınıflandırması
            vertices = len(approx)
            if vertices == 3:
                shape = "Üçgen"
            elif vertices == 4:
                aspect_ratio = float(w) / h
                if 0.95 <= aspect_ratio <= 1.05:
                    shape = "Kare"
                else:
                    shape = "Dikdörtgen"
            elif vertices > 4:
                if circularity > 0.8:
                    shape = "Daire"
                else:
                    shape = "Elips/Çokgen"
            else:
                shape = "Belirsiz"
            
            sonuclar.append({
                'sekil': shape,
                'alan': area,
                'cevre': perimeter,
                'merkez': (cx, cy),
                'sinir': (x, y, w, h),
                'koseler': vertices,
                'dairesellik': circularity,
                'kontur': contour
            })
        
        return sonuclar
    
    @staticmethod
    def renk_analizi(image):
        """Renk dağılımını analiz et"""
        if len(image.shape) != 3:
            return None
        
        # RGB histogramları
        colors = ('r', 'g', 'b')
        histograms = {}
        
        for i, color in enumerate(colors):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            histograms[color] = hist.flatten()
        
        # Dominant rengi bul
        avg_color = np.mean(image, axis=(0, 1))
        
        # HSV'ye çevir
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        avg_hsv = np.mean(hsv, axis=(0, 1))
        
        return {
            'rgb_ortalama': avg_color,
            'hsv_ortalama': avg_hsv,
            'histogramlar': histograms
        }
    
    @staticmethod
    def govde_cikarma(image, background=None):
        """Arka planı çıkar, sadece nesneyi al"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Otsu thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morfolojik işlemler
        kernel = np.ones((5, 5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Mask oluştur
        if len(image.shape) == 3:
            mask = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
            result = cv2.bitwise_and(image, mask)
        else:
            result = cv2.bitwise_and(image, binary)
        
        return result, binary
    
    @staticmethod
    def doku_analizi(image):
        """Doku özelliklerini çıkar (GLCM benzeri)"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Gradyan hesapla
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Gradyan büyüklüğü ve yönü
        magnitude = np.sqrt(gx**2 + gy**2)
        direction = np.arctan2(gy, gx)
        
        # İstatistikler
        doku_ozellikleri = {
            'ortalama': np.mean(gray),
            'standart_sapma': np.std(gray),
            'min': np.min(gray),
            'max': np.max(gray),
            'gradyan_ortalama': np.mean(magnitude),
            'gradyan_std': np.std(magnitude),
            'entropi': -np.sum((gray / 255.0) * np.log2((gray / 255.0) + 1e-10))
        }
        
        return doku_ozellikleri
    
    @staticmethod
    def perspektif_duzeltme(image, points):
        """
        4 nokta kullanarak perspektif düzeltme
        
        Args:
            image: Giriş görüntüsü
            points: 4 köşe noktası [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
        """
        pts1 = np.float32(points)
        
        # Hedef dikdörtgen boyutlarını hesapla
        widthA = np.sqrt(((points[2][0] - points[3][0]) ** 2) + 
                        ((points[2][1] - points[3][1]) ** 2))
        widthB = np.sqrt(((points[1][0] - points[0][0]) ** 2) + 
                        ((points[1][1] - points[0][1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((points[1][0] - points[2][0]) ** 2) + 
                         ((points[1][1] - points[2][1]) ** 2))
        heightB = np.sqrt(((points[0][0] - points[3][0]) ** 2) + 
                         ((points[0][1] - points[3][1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        pts2 = np.float32([[0, 0], [maxWidth, 0], 
                          [maxWidth, maxHeight], [0, maxHeight]])
        
        # Perspektif dönüşümü
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        result = cv2.warpPerspective(image, matrix, (maxWidth, maxHeight))
        
        return result


# Kullanım örnekleri
if __name__ == "__main__":
    print("Görüntü İşleme Modülü")
    print("Bu modül app.py tarafından kullanılır")
