from src.fetchers.page_fetcher import PageFetchResult
from src.models import SEOTarget
from src.services.page_analysis_service import PageAnalysisService


class CountingFetcher:
    def __init__(
        self,
        graph: dict[str, list[str]],
        *,
        final_urls: dict[str, str] | None = None,
        canonicals: dict[str, str] | None = None,
    ):
        self.graph = graph
        self.final_urls = final_urls or {}
        self.canonicals = canonicals or {}
        self.calls: list[str] = []

    def fetch(self, url: str, *, allowed_host=None):
        self.calls.append(url)
        links = self.graph.get(url, [])
        return PageFetchResult(
            url=url,
            final_url=self.final_urls.get(url, url),
            http_status=200,
            content_type="text/html",
            title=url,
            meta_description="description",
            h1="Heading",
            canonical_url=self.canonicals.get(url, self.final_urls.get(url, url)),
            robots_meta=None,
            word_count=200,
            internal_links=links,
            ai_evidence={"navigation_links": links if url.endswith("/") else []},
        )


def _target() -> SEOTarget:
    return SEOTarget(
        input_url="example.com",
        normalized_url="https://example.com/",
        normalized_domain="example.com",
    )


def test_single_crawl_fetches_normalized_internal_url_once():
    fetcher = CountingFetcher(
        {
            "https://example.com/": [
                "https://example.com/about/",
                "https://example.com/about#team",
                "https://third-party.example/page",
            ],
            "https://example.com/about": ["https://example.com/"],
        }
    )
    service = PageAnalysisService()
    service.fetcher = fetcher
    output = service.crawl_site(
        _target(),
        "run-1",
        ["https://example.com/about/"],
        max_pages=100,
    )
    assert fetcher.calls == ["https://example.com/", "https://example.com/about"]
    assert output.attempted_count == 2
    assert output.capped is False


def test_single_crawl_stops_deterministically_at_100():
    graph = {"https://example.com/": [f"https://example.com/page-{index}" for index in range(150)]}
    fetcher = CountingFetcher(graph)
    service = PageAnalysisService()
    service.fetcher = fetcher
    output = service.crawl_site(_target(), "run-1", [], max_pages=100)
    assert len(fetcher.calls) == 100
    assert len(set(fetcher.calls)) == 100
    assert output.capped is True
    assert output.discovered_count == 151


def test_redirect_www_and_canonical_aliases_persist_one_page_identity():
    fetcher = CountingFetcher(
        {
            "https://example.com/": [
                "http://www.example.com/",
                "https://example.com/about/",
                "https://www.example.com/about",
            ],
        },
        final_urls={"https://example.com/": "https://www.example.com/"},
        canonicals={"https://example.com/": "https://www.example.com/"},
    )
    service = PageAnalysisService()
    service.fetcher = fetcher

    output = service.crawl_site(_target(), "run-1", [], max_pages=100)

    assert fetcher.calls == ["https://example.com/", "https://example.com/about"]
    assert len(output.pages) == 2
    assert len({page.fetch_metadata["resolved_identity"] for page in output.pages}) == 2
    assert len(output.pages) <= output.attempted_count <= output.discovered_count
