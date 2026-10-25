"""JSON-LD @graph handling in scripts/parse_html.py.

A valid @graph document keeps @context on the root and @type on each member.
Flattening used to drop the root @context, so every member looked like a block
with no @context (#333).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from parse_html import parse_html  # noqa: E402

GRAPH_HTML = """<html><head><title>t</title>
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
  {"@type":"Organization","@id":"#org","name":"Acme"},
  {"@type":"WebSite","name":"Acme","publisher":{"@id":"#org"}}
]}
</script></head><body><h1>x</h1></body></html>"""


def test_graph_members_keep_the_document_context():
    result = parse_html(GRAPH_HTML)
    assert [node["@type"] for node in result["schema"]] == ["Organization", "WebSite"]
    assert all(node["@context"] == "https://schema.org" for node in result["schema"])


def test_graph_member_keeps_its_own_context():
    html = """<html><head><script type="application/ld+json">
    {"@context":"https://schema.org","@graph":[
      {"@context":"https://schema.org/docs","@type":"Article","name":"Note"}
    ]}
    </script></head></html>"""
    result = parse_html(html)
    assert result["schema"] == [
        {"@context": "https://schema.org/docs", "@type": "Article", "name": "Note"}
    ]


def test_graph_without_context_does_not_invent_one():
    html = """<html><head><script type="application/ld+json">
    {"@graph":[{"@type":"Organization","name":"Acme"}]}
    </script></head></html>"""
    result = parse_html(html)
    assert result["schema"] == [{"@type": "Organization", "name": "Acme"}]
    assert "@context" not in result["schema"][0]


def test_single_object_schema_is_unchanged():
    html = """<html><head><script type="application/ld+json">
    {"@context":"https://schema.org","@type":"Organization","name":"Acme"}
    </script></head></html>"""
    result = parse_html(html)
    assert result["schema"] == [
        {"@context": "https://schema.org", "@type": "Organization", "name": "Acme"}
    ]


def test_schema_skill_does_not_require_type_on_a_graph_container():
    text = (REPO_ROOT / "skills" / "seo-schema" / "SKILL.md").read_text(encoding="utf-8")
    assert "Flag any" not in text or "without `@context` or `@type`" not in text
    assert "@graph" in text
    assert "container is not an entity" in text
