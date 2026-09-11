@echo off
title MyDTU Auto-Login Server (ddddocr)
color 0A

echo [1/2] Dang kiem tra va cai dat thu vien ddddocr (Neu chua co)...
py -3 -m pip install ddddocr --upgrade

echo ===============================================================
echo      🚀 KHOI DONG TRAM TRUNG CHUYEN GIAI MA CAPTCHA MyDTU 🚀
echo ===============================================================
echo.
echo De cua so nay chay ngam, Extension tren Chrome se tu dong 
echo ket noi vao day de giai ma Captcha sieu toc!
echo.
echo ===============================================================

py -3 server.py

echo.
echo [!] Server da bi tat hoac bi loi.
pause
