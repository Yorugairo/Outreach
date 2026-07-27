from email.message import Message

from src.fetchers.http_client import SafeHTTPResponse
from src.fetchers.page_fetcher import PageFetcher


class StubHTTP:
    def __init__(self, body: str):
        self.body = body

    def fetch(self, url: str, *, allowed_hosts=None):
        headers = Message()
        headers["content-type"] = "text/html"
        return SafeHTTPResponse(
            requested_url=url,
            final_url=url,
            status=200,
            headers=headers,
            body=self.body.encode(),
        )


def test_page_parser_persists_bounded_ai_evidence():
    body = """
    <html><head><title>Example</title>
    <meta property="og:site_name" content="Example Co">
    <script type="application/ld+json">
    {"@type":"Organization","name":"Example Co"}
    </script></head><body>
    <nav><a href="/services">Services</a></nav>
    <h1>What does Example Co do?</h1>
    <p>Example Co provides a concise direct answer with useful detail for customers.</p>
    <h2>How does it work?</h2><p>It works in three clear steps.</p>
    <ul><li>One</li><li>Two</li></ul>
    <a href="https://source.example/research">Source</a>
    </body></html>
    """
    result = PageFetcher(http_client=StubHTTP(body)).fetch(
        "https://example.com/",
        allowed_host="example.com",
    )
    evidence = result.ai_evidence
    assert evidence["direct_answer_count"] >= 1
    assert evidence["question_heading_count"] == 2
    assert evidence["list_count"] == 1
    assert evidence["schema_version"] == "ai-page-evidence.v2"
    assert evidence["navigation_links"] == ["https://example.com/services"]
    assert "Organization" in evidence["json_ld_types"]
    assert evidence["json_ld_valid"] is True
    assert "Organization" in result.schema_types


def test_navigation_social_and_generic_numbers_are_not_authority_evidence():
    body = """
    <html><head><title>Example</title></head><body>
    <header><a href="https://facebook.com/example">Facebook</a></header>
    <main>
      <h1>Example Glass</h1>
      <p>Call 555-123-4567 for glass service.</p>
    </main>
    <footer><a href="https://directory.example/profile">Directory</a></footer>
    </body></html>
    """
    evidence = PageFetcher(http_client=StubHTTP(body)).fetch(
        "https://example.com/",
        allowed_host="example.com",
    ).ai_evidence

    assert evidence["external_citation_count"] == 0
    assert evidence["specific_evidence_count"] == 0
    assert evidence["heading_hierarchy_valid"] is True


def test_multiple_h1s_and_unaligned_schema_fail_conservative_checks():
    body = """
    <html><head><script type="application/ld+json">
    {"@type":"Organization","name":"Different Brand"}
    </script></head><body><main>
    <h1>Example Glass</h1><p>Example Glass provides custom installations.</p>
    <h1>Second Main Heading</h1><p>Unrelated paragraph content for this page.</p>
    </main></body></html>
    """
    evidence = PageFetcher(http_client=StubHTTP(body)).fetch(
        "https://example.com/",
        allowed_host="example.com",
    ).ai_evidence

    assert evidence["h1_count"] == 2
    assert evidence["heading_hierarchy_valid"] is False
    assert evidence["json_ld_visible_alignment"] is False
