import os
import time
import requests
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

        print(f"🌐 {url} 접속 중...")
        response = requests.get(url, timeout=10)
        results["load_time"] = time.time() - start_time
        results["http_status"] = response.status_code

        if response.status_code != 200:
            results["errors"].append(f"HTTP {response.status_code}")

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

def generate_debug_report(test_results):
    """디버깅 보고서 생성"""
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

    return report

def save_report(url, report, ai_analysis):
    """보고서를 파일에 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(url).netloc.replace('.', '_')
    filename = f"debug_report_{domain}_{timestamp}.txt"

    full_report = report + f"""
🤖 AI 분석 결과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{ai_analysis}

════════════════════════════════════════════════════════════
"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_report)

    return filename

def main():
    print("\n🤖 웹앱 자동 테스트 & 디버깅 매크로")
    print("=" * 60)
    url = input("🌐 테스트할 웹앱 URL을 입력하세요: ").strip()

    if not url:
        print("❌ URL을 입력해주세요.")
        return

    print(f"\n⏳ '{url}' 테스트 시작...\n")

    test_results = test_web_app(url)

    if test_results['status'] == 'error':
        print("⚠️ 웹사이트 접속에 실패했습니다.")

    print("🔎 AI가 결과를 분석 중...")
    ai_analysis = ai_analyze_results(test_results)

    report = generate_debug_report(test_results)
    print(report)
    print("\n🤖 AI 분석:")
    print(ai_analysis)

    filename = save_report(url, report, ai_analysis)
    print(f"\n✅ 보고서 저장: {filename}")

if __name__ == "__main__":
    main()
