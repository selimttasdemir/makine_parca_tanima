@echo off
chcp 65001 >nul
echo ========================================
echo   Makine Parçası Tanıma Sistemi
echo ========================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadı!
    echo Lütfen Python'u yükleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python bulundu
echo.

REM Streamlit kontrolü
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [UYARI] Streamlit bulunamadı, yükleniyor...
    pip install streamlit
)

echo.
echo ========================================
echo   Web uygulaması başlatılıyor...
echo ========================================
echo.
echo Tarayıcınızda otomatik açılacak:
echo   http://localhost:8501
echo.
echo Uygulamayı durdurmak için: Ctrl+C
echo ========================================
echo.

streamlit run app.py

pause
