import os
import time
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from urllib.parse import urlparse

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

load_dotenv()

client = Anthropic(
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

st.set_page_config(
    page_title="웹앱 디버거",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 웹앱 자동 테스트 & 디버깅 매크로")
st.markdown("---")

def ask_ai(prompt):
    res = client.messages.create(
        model="claude-haiku",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return res.content[0].text

def test_web_app(url):
    """웹앱을 자동으로 테스트하고 분석"""
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
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        results["url"] = url

        progress_placeholder = st.empty()
        progress_placeholder.info("🌐 웹사이트 접속 중...")

        response = requests.get(url, timeout=10)
        results["load_time"] = time.time() - start_time
        results["http_status"] = response.status_code

        if response.status_code != 200:
            results["errors"].append(f"HTTP {response.status_code}")

        progress_placeholder.info("📄 HTML 구조 분석 중...")

        if BeautifulSoup:
            soup = BeautifulSoup(response.content, 'html.parser')

            results["html_analysis"] = {
                "title": soup.title.string if soup.title else "없음",
                "links_count": len(soup.find_all('a')),
                "images_count": len(soup.find_all('img')),
                "forms_count": len(soup.find_all('form')),
                "buttons_count": len(soup.find_all('button')),
                "inputs_count": len(soup.find_all('input')),
                "scripts_count": len(soup.find_all('script')),
                "stylesheets_count": len(soup.find_all('link', rel='stylesheet')),
            }

            broken_links = []
            for link in soup.find_all('a', href=True)[:10]:
                href = link['href']
                if href.startswith(('http://', 'https://')):
                    try:
                        r = requests.head(href, timeout=5)
                        if r.status_code >= 400:
                            broken_links.append(f"{href} ({r.status_code})")
                    except:
                        broken_links.append(f"{href} (연결 실패)")

            if broken_links:
                results["html_analysis"]["broken_links"] = broken_links

        results["status"] = "success"
        progress_placeholder.success("✅ 테스트 완료!")

    except requests.exceptions.Timeout:
        results["errors"].append("요청 타임아웃")
        results["status"] = "error"
    except requests.exceptions.ConnectionError:
        results["errors"].append("연결 실패")
        results["status"] = "error"
    except Exception as e:
        results["errors"].append(str(e))
        results["status"] = "error"

    return results

def ai_analyze_results(results):
    """AI가 테스트 결과를 분석하고 문제점 파악"""
    prompt = f"""
다음은 웹앱 자동 테스트 결과입니다:

URL: {results['url']}
HTTP 상태코드: {results['http_status']}
페이지 로딩시간: {results['load_time']:.2f}초
페이지 분석:
  - 제목: {results['html_analysis'].get('title', 'N/A')}
  - 링크: {results['html_analysis'].get('links_count', 0)}개
  - 이미지: {results['html_analysis'].get('images_count', 0)}개
  - 폼: {results['html_analysis'].get('forms_count', 0)}개
  - 버튼: {results['html_analysis'].get('buttons_count', 0)}개
  - 입력필드: {results['html_analysis'].get('inputs_count', 0)}개
  - 스크립트: {results['html_analysis'].get('scripts_count', 0)}개
  - 스타일시트: {results['html_analysis'].get('stylesheets_count', 0)}개

오류: {', '.join(results['errors']) if results['errors'] else '없음'}

이 웹앱의 문제점과 개선 사항을 요약해주세요:
1. 성능 이슈
2. 구조적 문제
3. 보안 관련 우려사항
4. 개선 권고사항
"""

    return ask_ai(prompt)

# 사이드바
with st.sidebar:
    st.subheader("⚙️ 설정")
    st.markdown("---")

    show_details = st.checkbox("상세 분석 결과 표시", value=True)
    show_ai_analysis = st.checkbox("AI 분석 결과 표시", value=True)

# 메인 콘텐츠
col1, col2 = st.columns([3, 1])

with col1:
    url_input = st.text_input(
        "🌐 테스트할 웹앱 URL을 입력하세요",
        placeholder="예: google.com 또는 https://example.com",
        help="웹사이트 주소를 입력하면 자동으로 테스트합니다."
    )

with col2:
    test_button = st.button("🚀 테스트 시작", use_container_width=True)

st.markdown("---")

if test_button:
    if not url_input.strip():
        st.error("❌ URL을 입력해주세요.")
    else:
        st.info("⏳ 테스트를 시작합니다...")

        test_results = test_web_app(url_input)

        # 기본 결과 표시
        st.subheader("📊 테스트 결과")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("상태", "✅ 성공" if test_results['status'] == 'success' else "❌ 오류")
        with col2:
            st.metric("HTTP 코드", test_results['http_status'])
        with col3:
            st.metric("로딩시간", f"{test_results['load_time']:.2f}초")
        with col4:
            st.metric("오류수", len(test_results['errors']))

        if test_results['errors']:
            st.warning(f"⚠️ 감지된 오류: {', '.join(test_results['errors'])}")

        # HTML 분석 결과
        if show_details and test_results['html_analysis']:
            st.subheader("📄 HTML 구조 분석")

            col1, col2, col3, col4, col5, col6 = st.columns(6)
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
            with col6:
                st.metric("스크립트", test_results['html_analysis'].get('scripts_count', 0))

            st.write(f"**페이지 제목**: {test_results['html_analysis'].get('title', 'N/A')}")

            if test_results['html_analysis'].get('broken_links'):
                with st.expander("🔗 깨진 링크 목록"):
                    for link in test_results['html_analysis']['broken_links']:
                        st.code(link, language="text")

        # AI 분석
        if show_ai_analysis:
            st.subheader("🤖 AI 분석 결과")

            with st.spinner("AI가 분석 중입니다..."):
                ai_analysis = ai_analyze_results(test_results)

            st.markdown(ai_analysis)

        # 보고서 생성 및 다운로드
        st.subheader("📋 디버깅 보고서")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""
╔════════════════════════════════════════════════════════════╗
║           웹앱 자동 테스트 & 디버깅 보고서                   ║
╚════════════════════════════════════════════════════════════╝

📋 기본 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 생성일시: {timestamp}
 테스트 URL: {test_results['url']}
 처리시간: {test_results['load_time']:.2f}초

🔍 HTTP 테스트 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 상태코드: {test_results['http_status']}
 로딩시간: {test_results['load_time']:.2f}초
 상태: {'✅ 정상' if test_results['status'] == 'success' else '❌ 오류'}
"""

        if test_results['errors']:
            report += f"""
 오류 발생:
   {chr(10).join(['   - ' + e for e in test_results['errors']])}
"""

        if test_results['html_analysis']:
            report += f"""
📄 HTML 구조 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 페이지 제목: {test_results['html_analysis'].get('title', 'N/A')}
 링크 수: {test_results['html_analysis'].get('links_count', 0)}개
 이미지 수: {test_results['html_analysis'].get('images_count', 0)}개
 폼 수: {test_results['html_analysis'].get('forms_count', 0)}개
 버튼 수: {test_results['html_analysis'].get('buttons_count', 0)}개
 입력필드 수: {test_results['html_analysis'].get('inputs_count', 0)}개
 스크립트 수: {test_results['html_analysis'].get('scripts_count', 0)}개
 스타일시트 수: {test_results['html_analysis'].get('stylesheets_count', 0)}개
"""

            if test_results['html_analysis'].get('broken_links'):
                report += f"""
 ⚠️ 깨진 링크 감지:
{chr(10).join(['   - ' + link for link in test_results['html_analysis']['broken_links']])}
"""

        report += f"""
🤖 AI 분석 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{ai_analysis if show_ai_analysis else '(표시하지 않음)'}

════════════════════════════════════════════════════════════
"""

        st.text_area("보고서 내용", value=report, height=300, disabled=True)

        domain = urlparse(test_results['url']).netloc.replace('.', '_')
        filename = f"debug_report_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        st.download_button(
            label="📥 보고서 다운로드",
            data=report,
            file_name=filename,
            mime="text/plain",
            use_container_width=True
        )

st.markdown("---")
st.markdown("""
### 💡 사용 방법
1. 상단에 테스트할 웹사이트 URL 입력
2. "🚀 테스트 시작" 버튼 클릭
3. 자동 테스트 및 AI 분석 결과 확인
4. 📥 버튼으로 보고서 다운로드

### ✨ 주요 기능
- **웹앱 자동 테스트**: HTTP 상태코드, 로딩시간, 페이지 구조 분석
- **HTML 분석**: 링크, 이미지, 폼, 버튼, 스크립트 등 통계
- **깨진 링크 감지**: 외부 링크 자동 확인
- **AI 분석**: Claude AI가 문제점과 개선사항 제시
- **상세 보고서**: 모든 결과를 한 파일에 정리
""")
