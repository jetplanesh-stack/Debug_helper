# 웹앱 디버거 실행 스크립트

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      🎓 웹앱 디버거 - 학생용 & 전문가용                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 필수 패키지 확인 및 설치
Write-Host "📦 필수 패키지 확인 중..." -ForegroundColor Yellow
$packages = @("streamlit", "anthropic", "python-dotenv", "requests", "beautifulsoup4")

foreach ($package in $packages) {
    $installed = pip show $package 2>$null
    if (-not $installed) {
        Write-Host "⚠️  $package 설치 중..." -ForegroundColor Yellow
        pip install $package -q
    }
}

Write-Host "✅ 패키지 준비 완료!" -ForegroundColor Green
Write-Host ""

# 버전 선택
Write-Host "어떤 버전을 실행하시겠습니까?" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  학생용 버전 (추천 - 초보자)" -ForegroundColor Green
Write-Host "   • 쉬운 인터페이스" -ForegroundColor Gray
Write-Host "   • 명확한 오류 메시지" -ForegroundColor Gray
Write-Host "   • 학습 팁 포함" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  전문가용 버전 (고급)" -ForegroundColor Yellow
Write-Host "   • 상세한 분석" -ForegroundColor Gray
Write-Host "   • 보안/성능 분석" -ForegroundColor Gray
Write-Host "   • 접근성 검사" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  종료" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "선택 (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🎓 학생용 버전을 실행합니다..." -ForegroundColor Green
        Write-Host "🌐 브라우저가 자동으로 열립니다. (기다려주세요...)" -ForegroundColor Cyan
        Write-Host ""

        streamlit run app_student.py
    }
    "2" {
        Write-Host ""
        Write-Host "🔧 전문가용 버전을 실행합니다..." -ForegroundColor Yellow
        Write-Host "🌐 브라우저가 자동으로 열립니다. (기다려주세요...)" -ForegroundColor Cyan
        Write-Host ""

        streamlit run app_professional.py
    }
    "3" {
        Write-Host ""
        Write-Host "👋 프로그램을 종료합니다." -ForegroundColor Gray
        exit
    }
    default {
        Write-Host ""
        Write-Host "❌ 잘못된 선택입니다. 1, 2, 3 중 하나를 입력해주세요." -ForegroundColor Red
        exit
    }
}
