@echo off
title Slime Client 26.2 Yerel Derleyici
color 0A
echo ==================================================
echo   SLIME CLIENT 26.2 - OTOMATIK DERLEME ARACI
echo ==================================================
echo.

cd /d "%~dp0"
mkdir release 2>nul

echo [1/3] Fabric 26.2 Modu derleniyor (Gradle)...
cd mod
call gradle build --no-daemon
if exist "build\libs\SlimeClient-26.2-1.0.0.jar" (
    copy /Y "build\libs\SlimeClient-26.2-1.0.0.jar" "..\launcher\SlimeClient-26.2.jar" >nul
    copy /Y "build\libs\SlimeClient-26.2-1.0.0.jar" "..\release\SlimeClient-26.2.jar" >nul
    echo [+] Mod basariyla derlendi!
) else (
    echo [!] Mod derlenemedi (Java 21/Gradle eksik olabilir), sadece Launcher derlenecek.
)
cd ..

echo.
echo [2/3] Python kutuphaneleri kontrol ediliyor...
cd launcher
pip install -r requirements.txt pyinstaller

echo.
echo [3/3] SlimeLauncher.exe ve SlimeClient-Setup.exe olusturuluyor...
pyinstaller --noconfirm --onefile --windowed --name "SlimeLauncher" slime_launcher.py

if exist "SlimeClient-26.2.jar" (
    pyinstaller --noconfirm --onefile --windowed --name "SlimeClient-Setup" --add-data "dist\SlimeLauncher.exe;." --add-data "SlimeClient-26.2.jar;." slime_setup_wizard.py
) else (
    pyinstaller --noconfirm --onefile --windowed --name "SlimeClient-Setup" --add-data "dist\SlimeLauncher.exe;." slime_setup_wizard.py
)

copy /Y "dist\SlimeLauncher.exe" "..\release\" >nul
copy /Y "dist\SlimeClient-Setup.exe" "..\release\" >nul
cd ..

echo.
echo ==================================================
echo   TAMAMLANDI! Dosyalar 'release' klasorunde hazir.
echo ==================================================
pause
