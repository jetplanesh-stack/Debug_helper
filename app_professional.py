import os
import time
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from urllib.parse import urlparse
import json

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")

client = Anthropic(
    base_url=base_url,
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
        error_msg = str(e)
        # Detect API authentication errors
        if "401" in error_msg or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
            return f"""
❌ **API Authentication Error (401)**

Problem: Your API key is invalid or expired.

Solution:
1. Check the API key in .env file
2. Generate a new API key at https://console.anthropic.com/
3. Update .env file with the correct key
4. Restart the app

Current error: {error_msg}
"""
        return f"❌ Error during AI analysis: {error_msg}"

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
    test_button = st.button("🚀 Start Test", use_container_width=True, key="professional_test")

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
            use_container_width=True,
            key="professional_download"
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
