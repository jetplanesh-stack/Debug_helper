import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# API 키 검증
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    st.error("❌ API 키가 설정되지 않았습니다. .env 파일에 ANTHROPIC_API_KEY를 추가해주세요.")
    st.stop()

st.set_page_config(
    page_title="🎓 웹앱 디버거",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바에서 버전 선택
st.sidebar.markdown("### 📌 버전 선택")
st.sidebar.markdown("---")

version = st.sidebar.radio(
    "사용할 버전을 선택하세요",
    ["🎓 학생용 (추천)", "🔧 전문가용"],
    index=0
)

st.sidebar.markdown("---")

if version == "🎓 학생용 (추천)":
    st.sidebar.info("""
    **학생용 버전**
    - 초보자 친화적
    - 쉬운 설명
    - 학습 팁
    - 한국어 안내
    """)
else:
    st.sidebar.info("""
    **전문가용 버전**
    - 보안 분석
    - 성능 측정
    - 접근성 검사
    - 상세 분석
    """)

# 선택된 버전에 따라 다른 앱 로드
if version == "🎓 학생용 (추천)":
    # ============================================
    # 학생용 버전
    # ============================================
    import time
    import requests
    from datetime import datetime
    from anthropic import Anthropic

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        BeautifulSoup = None

    client = Anthropic(
        base_url=os.getenv("ANTHROPIC_BASE_URL"),
        api_key=api_key
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
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            results["url"] = url

            progress_placeholder = st.empty()
            progress_placeholder.info("🌐 1단계: 웹사이트에 접속 중...")

            response = requests.get(url, timeout=10)
            results["load_time"] = time.time() - start_time
            results["http_status"] = response.status_code

            if response.status_code != 200:
                results["errors"].append(f"HTTP 상태코드 오류: {response.status_code}")

            progress_placeholder.info("📄 2단계: HTML 구조 분석 중...")

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

    # 사이드바 설정
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
        test_button = st.button("🚀 테스트 시작", use_container_width=True)

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
                use_container_width=True
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

else:
    # ============================================
    # 전문가용 버전
    # ============================================
    import time
    import requests
    import json
    from datetime import datetime
    from anthropic import Anthropic
    from urllib.parse import urlparse

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        BeautifulSoup = None

    client = Anthropic(
        base_url=os.getenv("ANTHROPIC_BASE_URL"),
        api_key=api_key
    )

    st.title("🔧 Professional Web App Testing & Debugging")
    st.markdown("---")

    @st.cache_data(ttl=3600)
    def ask_ai(prompt):
        """Request AI analysis"""
        try:
            res = client.messages.create(
                model="claude-haiku",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            return res.content[0].text
        except Exception as e:
            return f"Error during AI analysis: {str(e)}"

    def test_web_app(url, check_all_links=False):
        """Comprehensive web app testing"""
        start_time = time.time()
        results = {
            "url": url,
            "status": None,
            "load_time": 0,
            "http_status": None,
            "headers": {},
            "html_analysis": {},
            "performance": {},
            "errors": [],
            "warnings": [],
            "ai_analysis": None
        }

        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            results["url"] = url

            progress_placeholder = st.empty()
            progress_placeholder.info("📡 Connecting to website...")

            response = requests.get(url, timeout=10)
            results["load_time"] = time.time() - start_time
            results["http_status"] = response.status_code

            # Header analysis
            results["headers"] = dict(response.headers)

            if response.status_code != 200:
                results["errors"].append(f"HTTP {response.status_code}")

            # Check security headers
            if 'X-Frame-Options' not in response.headers:
                results["warnings"].append("Missing X-Frame-Options security header")
            if 'X-Content-Type-Options' not in response.headers:
                results["warnings"].append("Missing X-Content-Type-Options header")
            if 'Strict-Transport-Security' not in response.headers and url.startswith('https'):
                results["warnings"].append("Missing HSTS header (HTTPS enabled)")

            progress_placeholder.info("🔍 Analyzing HTML structure...")

            if BeautifulSoup:
                soup = BeautifulSoup(response.content, 'html.parser')

                results["html_analysis"] = {
                    "title": soup.title.string if soup.title else "Not found",
                    "description": soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else None,
                    "links_count": len(soup.find_all('a')),
                    "images_count": len(soup.find_all('img')),
                    "forms_count": len(soup.find_all('form')),
                    "buttons_count": len(soup.find_all('button')),
                    "inputs_count": len(soup.find_all('input')),
                    "scripts_count": len(soup.find_all('script')),
                    "stylesheets_count": len(soup.find_all('link', rel='stylesheet')),
                    "headings": {
                        "h1": len(soup.find_all('h1')),
                        "h2": len(soup.find_all('h2')),
                        "h3": len(soup.find_all('h3')),
                    },
                    "meta_tags": len(soup.find_all('meta')),
                }

                # Check for accessibility issues
                if len(soup.find_all('h1')) != 1:
                    results["warnings"].append(f"Page should have exactly one H1 tag (found {len(soup.find_all('h1'))})")

                # Check images for alt text
                images_without_alt = len([img for img in soup.find_all('img') if not img.get('alt')])
                if images_without_alt > 0:
                    results["warnings"].append(f"{images_without_alt} images missing alt text")

                # Link checking
                broken_links = []
                external_links = []

                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith(('http://', 'https://')):
                        external_links.append(href)
                        if check_all_links:
                            try:
                                r = requests.head(href, timeout=5)
                                if r.status_code >= 400:
                                    broken_links.append(f"{href} ({r.status_code})")
                            except:
                                broken_links.append(f"{href} (Connection failed)")

                if broken_links:
                    results["html_analysis"]["broken_links"] = broken_links[:20]
                results["html_analysis"]["external_links_count"] = len(external_links)

            # Performance metrics
            results["performance"] = {
                "load_time_ms": results["load_time"] * 1000,
                "content_type": response.headers.get('Content-Type', 'Not specified'),
                "content_length": len(response.content),
                "gzip_enabled": 'gzip' in response.headers.get('Content-Encoding', ''),
            }

            if results["load_time"] > 3:
                results["warnings"].append(f"Slow load time: {results['load_time']:.2f}s (ideal: <3s)")

            results["status"] = "success"
            progress_placeholder.success("✅ Testing complete!")

        except requests.exceptions.Timeout:
            results["errors"].append("Request timeout")
            results["status"] = "error"
        except requests.exceptions.ConnectionError:
            results["errors"].append("Connection failed")
            results["status"] = "error"
        except Exception as e:
            results["errors"].append(str(e))
            results["status"] = "error"

        return results

    def ai_analyze_results(results):
        """Professional AI analysis"""
        prompt = f"""
Analyze the following web application test results and provide a professional assessment:

URL: {results['url']}
HTTP Status: {results['http_status']}
Load Time: {results['load_time']:.2f}s
Content Length: {results['performance'].get('content_length', 'N/A')} bytes

HTML Analysis:
{json.dumps(results['html_analysis'], indent=2, ensure_ascii=False)}

Performance Metrics:
{json.dumps(results['performance'], indent=2)}

Errors: {', '.join(results['errors']) if results['errors'] else 'None'}
Warnings: {', '.join(results['warnings']) if results['warnings'] else 'None'}

Please provide:
1. Overall assessment (performance, reliability, best practices)
2. Security concerns and recommendations
3. Performance optimization suggestions
4. SEO and accessibility improvements
5. Code quality observations based on structure
"""
        return ask_ai(prompt)

    # Sidebar configuration
    with st.sidebar:
        st.subheader("⚙️ Configuration")
        st.markdown("---")

        mode = st.radio(
            "Analysis Mode",
            ["Quick Scan", "Full Analysis"],
            help="Quick: Basic checks. Full: Comprehensive with all links checked"
        )

        show_details = st.checkbox("Show Detailed HTML Analysis", value=True)
        show_ai_analysis = st.checkbox("Show AI Analysis", value=True)
        show_headers = st.checkbox("Show Response Headers", value=False)

        check_all_links = st.checkbox("Check All Links", value=False, help="Slower but comprehensive")

        st.markdown("---")
        st.info("Note: Full analysis and link checking may take longer for large websites.")

    # Main content
    col1, col2 = st.columns([3, 1])

    with col1:
        url_input = st.text_input(
            "🌐 Enter website URL to test",
            placeholder="e.g., google.com or https://example.com",
            help="Supports both HTTP and HTTPS"
        )

    with col2:
        test_button = st.button("🚀 Start Test", use_container_width=True)

    st.markdown("---")

    if test_button:
        if not url_input.strip():
            st.error("❌ Please enter a URL.")
        else:
            st.info("⏳ Starting analysis...")

            test_results = test_web_app(url_input, check_all_links=(mode == "Full Analysis"))

            # Core metrics
            st.subheader("📊 Test Results")

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Status", "✅ OK" if test_results['status'] == 'success' else "❌ Error")
            with col2:
                st.metric("HTTP Code", test_results['http_status'])
            with col3:
                st.metric("Load Time", f"{test_results['load_time']:.2f}s")
            with col4:
                st.metric("Errors", len(test_results['errors']))
            with col5:
                st.metric("Warnings", len(test_results['warnings']))

            if test_results['errors']:
                st.error("❌ Errors Detected:")
                for error in test_results['errors']:
                    st.write(f"• {error}")

            if test_results['warnings']:
                st.warning("⚠️ Warnings:")
                for warning in test_results['warnings']:
                    st.write(f"• {warning}")

            # Detailed analysis
            if show_details and test_results['html_analysis']:
                st.subheader("📄 HTML Analysis")

                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                    st.metric("Links", test_results['html_analysis'].get('links_count', 0))
                with col2:
                    st.metric("Images", test_results['html_analysis'].get('images_count', 0))
                with col3:
                    st.metric("Forms", test_results['html_analysis'].get('forms_count', 0))
                with col4:
                    st.metric("Scripts", test_results['html_analysis'].get('scripts_count', 0))
                with col5:
                    st.metric("Stylesheets", test_results['html_analysis'].get('stylesheets_count', 0))
                with col6:
                    st.metric("Meta Tags", test_results['html_analysis'].get('meta_tags', 0))

                st.write(f"**Title**: {test_results['html_analysis'].get('title', 'N/A')}")
                if test_results['html_analysis'].get('description'):
                    st.write(f"**Meta Description**: {test_results['html_analysis']['description']}")

                col1, col2 = st.columns(2)
                with col1:
                    h_data = test_results['html_analysis'].get('headings', {})
                    st.metric("H1 Tags", h_data.get('h1', 0))
                    st.metric("H2 Tags", h_data.get('h2', 0))
                    st.metric("H3 Tags", h_data.get('h3', 0))
                with col2:
                    st.metric("Buttons", test_results['html_analysis'].get('buttons_count', 0))
                    st.metric("Inputs", test_results['html_analysis'].get('inputs_count', 0))
                    st.metric("External Links", test_results['html_analysis'].get('external_links_count', 0))

                if test_results['html_analysis'].get('broken_links'):
                    with st.expander("🔗 Broken Links"):
                        for link in test_results['html_analysis']['broken_links']:
                            st.code(link, language="text")

            # Performance metrics
            st.subheader("⚡ Performance")
            perf = test_results['performance']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Load Time (ms)", f"{perf.get('load_time_ms', 0):.0f}")
            with col2:
                st.metric("Content Type", perf.get('content_type', 'N/A').split(';')[0])
            with col3:
                st.metric("Content Size (KB)", f"{perf.get('content_length', 0) / 1024:.1f}")
            with col4:
                gzip_status = "✅ Yes" if perf.get('gzip_enabled') else "❌ No"
                st.metric("GZIP Enabled", gzip_status)

            # Response headers
            if show_headers and test_results['headers']:
                with st.expander("🔍 Response Headers"):
                    for key, value in test_results['headers'].items():
                        st.write(f"**{key}**: {value}")

            # AI Analysis
            if show_ai_analysis:
                st.subheader("🤖 Professional Analysis")

                with st.spinner("Analyzing with AI..."):
                    ai_analysis = ai_analyze_results(test_results)

                st.markdown(ai_analysis)

            # Report generation
            st.subheader("📋 Detailed Report")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report = f"""
╔══════════════════════════════════════════════════════════════╗
║        Professional Web App Testing & Debugging Report        ║
╚══════════════════════════════════════════════════════════════╝

📋 GENERAL INFORMATION
{'━' * 62}
Generated: {timestamp}
URL Tested: {test_results['url']}
Test Mode: {mode}
Analysis Time: {test_results['load_time']:.2f} seconds

🔍 HTTP TEST RESULTS
{'━' * 62}
Status Code: {test_results['http_status']}
Load Time: {test_results['load_time']:.2f}s
Status: {'✅ Success' if test_results['status'] == 'success' else '❌ Error'}
"""

            if test_results['errors']:
                report += f"""
Errors Detected:
{chr(10).join(['  • ' + e for e in test_results['errors']])}
"""

            if test_results['warnings']:
                report += f"""
Warnings:
{chr(10).join(['  • ' + w for w in test_results['warnings']])}
"""

            if test_results['html_analysis']:
                report += f"""
📄 HTML STRUCTURE ANALYSIS
{'━' * 62}
Page Title: {test_results['html_analysis'].get('title', 'N/A')}
Meta Description: {test_results['html_analysis'].get('description', 'Not found')}
Total Links: {test_results['html_analysis'].get('links_count', 0)}
External Links: {test_results['html_analysis'].get('external_links_count', 0)}
Images: {test_results['html_analysis'].get('images_count', 0)}
Forms: {test_results['html_analysis'].get('forms_count', 0)}
Buttons: {test_results['html_analysis'].get('buttons_count', 0)}
Input Fields: {test_results['html_analysis'].get('inputs_count', 0)}
Scripts: {test_results['html_analysis'].get('scripts_count', 0)}
Stylesheets: {test_results['html_analysis'].get('stylesheets_count', 0)}
Meta Tags: {test_results['html_analysis'].get('meta_tags', 0)}

Headings:
  • H1: {test_results['html_analysis'].get('headings', {}).get('h1', 0)}
  • H2: {test_results['html_analysis'].get('headings', {}).get('h2', 0)}
  • H3: {test_results['html_analysis'].get('headings', {}).get('h3', 0)}
"""

                if test_results['html_analysis'].get('broken_links'):
                    report += f"""
Broken Links Detected:
{chr(10).join(['  • ' + link for link in test_results['html_analysis']['broken_links']])}
"""

            report += f"""
⚡ PERFORMANCE METRICS
{'━' * 62}
Load Time: {test_results['performance'].get('load_time_ms', 0):.0f} ms
Content Type: {test_results['performance'].get('content_type', 'N/A')}
Content Size: {test_results['performance'].get('content_length', 0) / 1024:.1f} KB
GZIP Compression: {'Enabled' if test_results['performance'].get('gzip_enabled') else 'Disabled'}
"""

            if show_ai_analysis:
                report += f"""
🤖 AI PROFESSIONAL ANALYSIS
{'━' * 62}
{ai_analysis}
"""

            report += f"""
{'═' * 62}
End of Report
"""

            st.text_area("Report Content", value=report, height=300, disabled=True)

            domain = urlparse(test_results['url']).netloc.replace('.', '_')
            filename = f"professional_report_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )

    st.markdown("---")
    st.markdown("""
    ## 🔍 Features

    - **HTTP Analysis**: Status codes, headers, performance metrics
    - **HTML Structure**: Complete page analysis with accessibility checks
    - **Security Assessment**: Security headers, SSL/TLS validation
    - **Performance Profiling**: Load time, compression, content analysis
    - **Link Validation**: Automatic broken link detection
    - **Professional Report**: Detailed downloadable analysis
    """)

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
