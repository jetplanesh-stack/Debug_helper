import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="🎓 웹앱 디버거 - 버전 선택",
    page_icon="🎓",
    layout="centered"
)

# API 키 및 설정 검증
api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")

# 설정 오류 체크
config_errors = []

if not api_key:
    config_errors.append("❌ ANTHROPIC_API_KEY가 없습니다")
elif not api_key.startswith(("sk-", "sk_")):
    config_errors.append("⚠️ API 키 형식이 잘못되었습니다 (sk-로 시작해야 함)")

if base_url and "pickle" in base_url.lower():
    config_errors.append("❌ BASE_URL이 잘못되었습니다: https://api.pickle.ac")
    config_errors.append("   → 올바른 URL: https://api.anthropic.com")

if base_url and not base_url.startswith("https://"):
    config_errors.append("⚠️ BASE_URL은 https://로 시작해야 합니다")

if config_errors:
    st.error("**⚙️ 설정 오류 감지됨:**")
    for error in config_errors:
        st.write(error)

    st.markdown("---")
    st.warning("""
    **⚠️ API 키 확인 중요:**

    API 키가 너무 짧으면 유효하지 않습니다!
    (현재 키 길이: %d자)

    올바른 형식:
    - 길이: 40자 이상
    - 시작: `sk-ant-` 또는 `sk-`
    - 예: `sk-ant-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

    **해결 방법:**

    1. https://console.anthropic.com/ 접속
    2. 새 API 키 생성 (전체 키 복사)
    3. `.env` 파일에 붙여넣기:
    ```
    ANTHROPIC_API_KEY=sk-ant-v1-xxxxxxxxxxxx
    ANTHROPIC_BASE_URL=https://api.anthropic.com
    ```

    4. 파일 저장 후 앱 재시작
    """ % len(api_key) if api_key else 0)
    st.stop()

st.title("🎓 웹앱 디버거")
st.markdown("---")

st.markdown("""
## 📌 버전을 선택하세요

다음 명령어를 터미널에서 실행하세요:

### 🎓 학생용 버전 (추천)
```bash
streamlit run app_student.py
```
- 초보자 친화적 인터페이스
- 한국어로 된 설명
- 학습 팁 포함
- 쉬운 오류 이해

### 🔧 전문가용 버전
```bash
streamlit run app_professional.py
```
- 고급 기능 포함
- 보안 분석
- 성능 측정
- 접근성 검사

---

## 🚀 빠른 시작

**Windows 사용자:**
```bash
run.bat
```

**Mac/Linux 사용자:**
```bash
streamlit run app_student.py
```
""")

st.markdown("---")
st.info("💡 처음 사용하시는 경우 **학생용 버전**을 추천합니다!")
