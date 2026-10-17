@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════╗
echo ║      🎓 웹앱 디버거 - 학생용 ^& 전문가용                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 📦 필수 패키지 확인 중...
pip install -q streamlit anthropic python-dotenv requests beautifulsoup4

echo ✅ 패키지 준비 완료!
echo.

echo 어떤 버전을 실행하시겠습니까?
echo.
echo 1️⃣  학생용 버전 (추천 - 초보자)
echo.
echo 2️⃣  전문가용 버전 (고급)
echo.
echo 3️⃣  종료
echo.

set /p choice="선택 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 🎓 학생용 버전을 실행합니다...
    echo 🌐 브라우저가 자동으로 열립니다.
    echo.
    streamlit run app_student.py
) else if "%choice%"=="2" (
    echo.
    echo 🔧 전문가용 버전을 실행합니다...
    echo 🌐 브라우저가 자동으로 열립니다.
    echo.
    streamlit run app_professional.py
) else if "%choice%"=="3" (
    echo.
    echo 👋 프로그램을 종료합니다.
    exit /b 0
) else (
    echo.
    echo ❌ 잘못된 선택입니다. 1, 2, 3 중 하나를 입력해주세요.
    exit /b 1
)
