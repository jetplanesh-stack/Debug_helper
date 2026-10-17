import os
import time
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

load_dotenv()

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
    st.info("""
    **해결 방법:**

    1. `.env` 파일 수정:
    ```
    ANTHROPIC_API_KEY=sk-xxxxxxxxxxxx
    ANTHROPIC_BASE_URL=https://api.anthropic.com
    ```

    2. 파일 저장 후 앱 재시작

    3. API 키가 없으면: https://console.anthropic.com/ 에서 생성
    """)
    st.stop()

client = Anthropic(
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    api_key=api_key
)

st.set_page_config(
    page_title="🎓 웹앱 디버거 - 학생용",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 웹앱 디버깅 학습 도구")
st.markdown("웹사이트를 테스트하고 AI가 문제점을 알려줍니다!")
st.markdown("---")

def ask_ai(prompt):
    """AI에게 분석 요청"""
    try:
        res = client.messages.create(
            model="claude-haiku",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.content[0].text
    except Exception as e:
        return f"❌ AI 분석 중 오류 발생: {str(e)}"

def test_web_app(url):
    """웹앱을 테스트하고 상태 확인"""
    start_time = time.time()
    results = {
        "url": url,
        "status": None,
        "load_time": 0,
        "http_status": None,
        "html_analysis": {},
        "errors": [],
        "ai_analysis": None
    }

    try:
        # URL 형식 자동 수정
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        results["url"] = url

        progress_placeholder = st.empty()
        progress_placeholder.info("🌐 1단계: 웹사이트에 접속 중...")

        # 웹사이트 접속
        response = requests.get(url, timeout=10)
        results["load_time"] = time.time() - start_time
        results["http_status"] = response.status_code

        if response.status_code != 200:
            results["errors"].append(f"HTTP 상태코드 오류: {response.status_code}")

        progress_placeholder.info("📄 2단계: HTML 구조 분석 중...")

        # HTML 분석
        if BeautifulSoup:
            soup = BeautifulSoup(response.content, 'html.parser')

            results["html_analysis"] = {
                "title": soup.title.string if soup.title else "제목 없음",
                "links_count": len(soup.find_all('a')),
                "images_count": len(soup.find_all('img')),
                "forms_count": len(soup.find_all('form')),
                "buttons_count": len(soup.find_all('button')),
                "inputs_count": len(soup.find_all('input')),
                "scripts_count": len(soup.find_all('script')),
                "stylesheets_count": len(soup.find_all('link', rel='stylesheet')),
            }

            # 깨진 링크 확인 (최대 5개만)
            broken_links = []
            link_count = 0
            for link in soup.find_all('a', href=True)[:5]:
                href = link['href']
                if href.startswith(('http://', 'https://')):
                    try:
                        r = requests.head(href, timeout=5)
                        if r.status_code >= 400:
                            broken_links.append(f"{href} (오류: {r.status_code})")
                            link_count += 1
                    except requests.exceptions.Timeout:
                        broken_links.append(f"{href} (연결 시간 초과)")
                        link_count += 1
                    except Exception:
                        broken_links.append(f"{href} (연결 실패)")
                        link_count += 1

            if broken_links:
                results["html_analysis"]["broken_links"] = broken_links

        results["status"] = "success"
        progress_placeholder.success("✅ 테스트 완료!")

    except requests.exceptions.Timeout:
        results["errors"].append("⏱️ 요청 타임아웃: 웹사이트 응답이 너무 느립니다")
        results["status"] = "error"
    except requests.exceptions.ConnectionError:
        results["errors"].append("🔗 연결 실패: 인터넷 연결을 확인해주세요")
        results["status"] = "error"
    except Exception as e:
        results["errors"].append(f"❌ 오류 발생: {str(e)}")
        results["status"] = "error"

    return results

def ai_analyze_results(results):
    """AI가 테스트 결과를 분석"""
    prompt = f"""
다음은 웹앱 테스트 결과입니다. 학생을 위해 쉽고 친절하게 설명해주세요.

📊 테스트 정보
- URL: {results['url']}
- HTTP 상태코드: {results['http_status']}
- 로딩시간: {results['load_time']:.2f}초

📄 페이지 구조
- 제목: {results['html_analysis'].get('title', 'N/A')}
- 링크: {results['html_analysis'].get('links_count', 0)}개
- 이미지: {results['html_analysis'].get('images_count', 0)}개
- 폼: {results['html_analysis'].get('forms_count', 0)}개
- 버튼: {results['html_analysis'].get('buttons_count', 0)}개
- 입력필드: {results['html_analysis'].get('inputs_count', 0)}개
- 스크립트: {results['html_analysis'].get('scripts_count', 0)}개

⚠️ 발견된 오류: {', '.join(results['errors']) if results['errors'] else '없음'}

다음을 쉬운 말로 설명해주세요:
1. 이 웹사이트는 정상인가요?
2. 로딩 속도는 빠른가요?
3. 어떤 문제점이 있나요?
4. 어떻게 개선하면 좋을까요?
"""

    return ask_ai(prompt)

# 사이드바
with st.sidebar:
    st.subheader("⚙️ 설정")
    st.markdown("---")

    show_details = st.checkbox("📊 상세 분석 보기", value=True)
    show_ai_analysis = st.checkbox("🤖 AI 분석 결과 보기", value=True)

    st.markdown("---")
    st.info("💡 **학습 팁**: 여러 웹사이트를 테스트해보고 결과를 비교해보세요!")

# 메인 콘텐츠
st.markdown("### 테스트할 웹사이트 URL 입력")
col1, col2 = st.columns([3, 1])

with col1:
    url_input = st.text_input(
        "URL을 입력하세요",
        placeholder="예: google.com 또는 https://example.com",
        label_visibility="collapsed"
    )

with col2:
    test_button = st.button("🚀 테스트 시작", use_container_width=True, key="student_test")

st.markdown("---")

if test_button:
    if not url_input.strip():
        st.error("❌ URL을 입력해주세요!")
    else:
        st.info("⏳ 테스트를 시작합니다...")

        test_results = test_web_app(url_input)

        # 기본 결과 표시
        st.subheader("📊 테스트 결과")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_text = "✅ 성공" if test_results['status'] == 'success' else "❌ 오류"
            st.metric("상태", status_text)
        with col2:
            st.metric("HTTP 코드", test_results['http_status'] or "N/A")
        with col3:
            st.metric("로딩시간", f"{test_results['load_time']:.2f}초")
        with col4:
            st.metric("오류 수", len(test_results['errors']))

        if test_results['errors']:
            st.warning("⚠️ 발견된 문제점:")
            for error in test_results['errors']:
                st.write(f"• {error}")

        # HTML 분석 결과
        if show_details and test_results['html_analysis']:
            st.subheader("📄 페이지 구조 분석")

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("링크", test_results['html_analysis'].get('links_count', 0))
            with col2:
                st.metric("이미지", test_results['html_analysis'].get('images_count', 0))
            with col3:
                st.metric("폼", test_results['html_analysis'].get('forms_count', 0))
            with col4:
                st.metric("버튼", test_results['html_analysis'].get('buttons_count', 0))
            with col5:
                st.metric("입력필드", test_results['html_analysis'].get('inputs_count', 0))

            st.write(f"**📌 페이지 제목**: {test_results['html_analysis'].get('title', 'N/A')}")

            if test_results['html_analysis'].get('broken_links'):
                with st.expander("🔗 깨진 링크 (클릭해서 보기)"):
                    st.warning("다음 링크가 작동하지 않습니다:")
                    for link in test_results['html_analysis']['broken_links']:
                        st.write(f"• {link}")

        # AI 분석
        if show_ai_analysis:
            st.subheader("🤖 AI 분석 및 조언")

            with st.spinner("AI가 분석 중입니다..."):
                ai_analysis = ai_analyze_results(test_results)

            st.markdown(ai_analysis)

        # 보고서 생성
        st.subheader("📋 테스트 보고서")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""
╔════════════════════════════════════════════════════════════╗
║         🎓 웹앱 디버깅 테스트 보고서 (학생용)                ║
╚════════════════════════════════════════════════════════════╝

📋 기본 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
생성일시: {timestamp}
테스트 URL: {test_results['url']}
테스트 시간: {test_results['load_time']:.2f}초

🔍 테스트 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
상태: {'✅ 정상 작동' if test_results['status'] == 'success' else '❌ 오류 발생'}
HTTP 코드: {test_results['http_status']}
로딩시간: {test_results['load_time']:.2f}초
"""

        if test_results['errors']:
            report += f"""
발견된 문제점:
{chr(10).join(['  • ' + e for e in test_results['errors']])}
"""

        if test_results['html_analysis']:
            report += f"""
📄 페이지 구조 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
페이지 제목: {test_results['html_analysis'].get('title', 'N/A')}
링크 수: {test_results['html_analysis'].get('links_count', 0)}개
이미지 수: {test_results['html_analysis'].get('images_count', 0)}개
폼 수: {test_results['html_analysis'].get('forms_count', 0)}개
버튼 수: {test_results['html_analysis'].get('buttons_count', 0)}개
입력필드 수: {test_results['html_analysis'].get('inputs_count', 0)}개
스크립트 수: {test_results['html_analysis'].get('scripts_count', 0)}개
"""

            if test_results['html_analysis'].get('broken_links'):
                report += f"""
⚠️ 깨진 링크:
{chr(10).join(['  • ' + link for link in test_results['html_analysis']['broken_links']])}
"""

        if show_ai_analysis:
            report += f"""
🤖 AI 분석 및 조언
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{ai_analysis}
"""

        report += """
════════════════════════════════════════════════════════════
"""

        st.text_area("보고서 내용", value=report, height=250, disabled=True)

        filename = f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        st.download_button(
            label="📥 보고서 다운로드",
            data=report,
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
            key="student_download"
        )

st.markdown("---")
st.markdown("""
## 💡 사용 방법

1. **URL 입력**: 테스트하고 싶은 웹사이트 주소 입력
2. **테스트 시작**: "🚀 테스트 시작" 버튼 클릭
3. **결과 확인**:
   - HTTP 상태코드와 로딩시간 확인
   - 페이지 구조 분석 결과 보기
   - AI가 제시하는 조언 읽기
4. **보고서 다운로드**: 📥 버튼으로 결과 저장

## ✨ 학습 포인트

- **HTTP 상태코드**: 200은 정상, 404는 페이지 없음, 500은 서버 오류
- **로딩시간**: 일반적으로 3초 이내가 빠른 속도
- **HTML 구조**: 링크, 이미지, 폼 등의 요소 개수 파악
- **깨진 링크**: 클릭할 수 없는 링크 자동 감지

## 🎓 도움말

- 여러 웹사이트를 테스트해서 비교해보세요
- AI 분석 결과를 읽고 웹 개발에 대해 배워보세요
- 자신이 만든 웹사이트도 테스트해볼 수 있습니다!
""")
