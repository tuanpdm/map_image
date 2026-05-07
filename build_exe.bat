@echo off
chcp 65001 >nul
echo ========================================
echo  Build file .exe co giao dien GUI
echo ========================================
echo.

echo [1/3] Cai dat thu vien can thiet...
python -m pip install pyinstaller pandas openpyxl
if %errorlevel% neq 0 (
    echo.
    echo [LOI] Cai dat thu vien that bai!
    echo Kiem tra lai Python da duoc cai dat va co ket noi mang khong.
    pause
    exit /b 1
)
echo.

echo [2/3] Dang build .exe (co the mat 1-2 phut)...
python -m PyInstaller --onefile --windowed --name "MapAnhSinhVien" "%~dp0map_anh.py"
if %errorlevel% neq 0 (
    echo.
    echo [LOI] Build that bai! Xem thong bao loi phia tren.
    pause
    exit /b 1
)
echo.

echo [3/3] Hoan thanh!
echo.
echo >>> File .exe nam tai: %~dp0dist\MapAnhSinhVien.exe
echo.
pause