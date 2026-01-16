@echo off
chcp 65001 >nul
title Makine Parçası Tanıma Sistemi - Kurulum ve Çalıştırma
color 0A

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║     MAKİNE PARÇASI TANIMA SİSTEMİ                        ║
echo ║     Kurulum ve Çalıştırma                                ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Python kontrolü
echo [1/5] Python kontrolü yapılıyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [HATA] Python bulunamadı!
    echo.
    echo Python'u yüklemek için:
    echo 1. https://www.python.org/downloads/ adresine gidin
    echo 2. Son sürümü indirin
    echo 3. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python bulundu
echo.

REM Pip kontrolü
echo [2/5] Pip kontrolü yapılıyor...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Pip bulunamadı!
    echo Python'u yeniden yükleyin
    pause
    exit /b 1
)
echo [OK] Pip bulundu
echo.

REM requirements.txt kontrolü
echo [3/5] Gerekli paketler kontrol ediliyor...
if exist requirements.txt (
    echo requirements.txt dosyası bulundu
    echo.
    echo Paketler yükleniyor/güncelleniyor...
    echo (Bu işlem birkaç dakika sürebilir)
    echo.
    pip install -r requirements.txt --quiet
    if %errorlevel% equ 0 (
        echo [OK] Tüm paketler yüklendi
    ) else (
        echo [UYARI] Bazı paketler yüklenemedi, devam ediliyor...
    )
) else (
    echo [UYARI] requirements.txt bulunamadı
    echo Temel paketler yükleniyor...
    pip install streamlit torch torchvision ultralytics opencv-python pillow numpy pandas --quiet
)
echo.

REM Klasör yapısı kontrolü
echo [4/5] Klasör yapısı kontrol ediliyor...
if not exist "training_data" mkdir training_data
if not exist "referans_gorseller" mkdir referans_gorseller
if not exist "test" mkdir test
if not exist "train" mkdir train
if not exist "val" mkdir val
echo [OK] Klasörler hazır
echo.

REM Uygulama kontrolü
echo [5/5] Uygulama dosyası kontrol ediliyor...
if not exist "app.py" (
    echo [HATA] app.py dosyası bulunamadı!
    echo Lütfen doğru klasörde olduğunuzdan emin olun.
    pause
    exit /b 1
)
echo [OK] app.py bulundu
echo.

echo ╔═══════════════════════════════════════════════════════════╗
echo ║     KURULUM TAMAMLANDI!                                  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo Web uygulaması başlatılıyor...
echo.
echo Tarayıcınızda otomatik olarak açılacak:
echo   ^> http://localhost:8501
echo.
echo Kullanım:
echo   - Sol menüden tanıma yöntemini seçin
echo   - Fotoğraf yükleyin
echo   - Analiz Et butonuna tıklayın
echo.
echo Uygulamayı durdurmak için: Ctrl+C
echo.
echo ═══════════════════════════════════════════════════════════
echo.

timeout /t 3 /nobreak >nul

streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Uygulama başlatılamadı!
    echo.
    pause
)
