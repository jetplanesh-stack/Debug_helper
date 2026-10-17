# 🚀 빠른 시작 가이드

5분 안에 시작할 수 있습니다!

## 1️⃣ 설치 (2분)

### Windows 사용자

#### 옵션 A: 배치 파일 (가장 쉬움)
1. 폴더를 탐색기로 열기
2. `run.bat` 파일 더블클릭
3. 원하는 버전 선택 (1 또는 2)

#### 옵션 B: PowerShell
```powershell
# PowerShell 실행 권한 설정 (첫 시간만)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 스크립트 실행
.\run.ps1
```

#### 옵션 C: 명령어 실행
```bash
pip install -r requirements.txt
streamlit run app_student.py
```

### Mac/Linux 사용자

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 학생용 버전 실행
streamlit run app_student.py

# 또는 전문가용 버전 실행
streamlit run app_professional.py
```

## 2️⃣ API 키 설정 (1분)

### 단계 1: Anthropic API 키 얻기
1. https://console.anthropic.com/ 방문
2. 회원가입 또는 로그인
3. API 키 생성 및 복사

### 단계 2: .env 파일 만들기
1. `.env.example` 파일을 `.env`로 이름 변경
2. 또는 새 파일 `.env` 생성

### 단계 3: API 키 입력
```
ANTHROPIC_API_KEY=sk-ant-v1-xxxxx...
```

💡 **팁**: 키를 절대 공개하지 마세요!

## 3️⃣ 첫 테스트 (2분)

### 1단계: 앱 실행
```bash
streamlit run app_student.py
```

자동으로 브라우저가 열립니다.

### 2단계: 웹사이트 입력
```
google.com
```

### 3단계: 테스트 시작
"🚀 테스트 시작" 버튼 클릭

### 4단계: 결과 확인
- 상태, 로딩시간, 오류 수 확인
- AI 분석 결과 읽기

### 5단계: 보고서 다운로드 (선택)
"📥 보고서 다운로드" 버튼 클릭

## ✅ 완료!

축하합니다! 🎉 이제 웹사이트를 테스트할 수 있습니다.

---

## 🎯 다음 단계

### 학습 용도
1. 여러 웹사이트 비교하기
   - Google vs Naver
   - 개인 블로그 vs 포털 사이트
2. AI 분석 읽고 학습하기
3. 개선 사항 직접 구현해보기

### 실무 용도
1. 자신의 웹사이트 정기적으로 테스트
2. 보안 헤더 설정하기
3. 성능 최적화하기

---

## 🆘 문제 해결

### "API 키가 설정되지 않았습니다"
```
해결: .env 파일 생성하고 API 키 입력
```

### "pip: command not found"
```
해결: Python 재설치 (python.org)
```

### "streamlit: command not found"
```bash
해결: pip install streamlit
```

### "연결 실패"
```
해결: 인터넷 연결 확인
```

### "모듈을 찾을 수 없습니다"
```bash
해결: pip install -r requirements.txt
```

---

## 📚 도움말

- **README.md**: 상세한 사용법
- **COMPARISON.md**: 학생용 vs 전문가용 비교
- **GitHub Issues**: 문제 보고

---

## 🎓 학습 자료

### 초급 (웹 기초)
- HTML 구조 이해하기
- HTTP 상태코드 학습
- 웹 성능 개념 이해

### 중급 (웹 개발)
- CSS 최적화
- JavaScript 성능
- 캐싱 전략

### 고급 (보안)
- 보안 헤더 이해
- HTTPS/SSL
- 웹 취약점 학습

---

## 💡 팁

✅ **첫 번째 테스트 추천**: google.com
- 가장 최적화된 웹사이트
- 모든 최신 기술 적용
- 우수한 사례 학습 가능

✅ **비교 추천**
- 개인 블로그 vs 포털 사이트
- 작은 스타트업 vs 대기업 사이트
- 국내 vs 국제 사이트

✅ **학습 팁**
- 한 사이트씩 여러 번 테스트
- AI 분석 결과 꼼꼼히 읽기
- 개선 사항 실제로 적용해보기

---

## 🚀 시작하세요!

1. `run.bat` 또는 `run.ps1` 실행
2. 버전 선택 (1 = 학생용)
3. 웹사이트 입력
4. 결과 확인

**행운을 빕니다! Happy debugging! 🎉**
