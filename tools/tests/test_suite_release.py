# SPDX-License-Identifier: GPL-3.0-or-later
"""suite_release.py, the release workflow's plan and pin steps, with GitHub stood in for: a tag pushed by hand, a
Nexus release with some apps out already, a draft made anew, apps without a portal bump, and the pins
written into both copies of apps.toml."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("suite_release", TOOLS / "suite_release.py")
sr = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sr
spec.loader.exec_module(sr)

SHA = "ab" * 32
MANIFEST = """# a comment that stays
[apps.check]
name = "BC-250 Board Test"
tag = "bc250-check-v3.0.1"
sha256 = "%s"
required = true

[apps.sftp]
name = "SFTP Tools"
tag = "bc250-sftp-v3.1.0"
sha256 = ""

[apps.xenia]
name = "Xenia Manager"
tag = "bc250-xenia-v1.0.1"
withdrawn = "a reason"

[apps.new]
name = "New Manager"
tag = "bc250-new-v0.1.0"
""" % SHA


def test_a_tag_pushed_by_hand_is_that_release_published_at_once():
    assert sr.plan(MANIFEST, "4.1.0", tag="bc250-sftp-v3.1.0") == {
        "apps": ["bc250-sftp-v3.1.0"], "portal": "", "draft": False}
    assert sr.plan(MANIFEST, "4.1.0", tag="bc250-new-v0.1.0") == {"apps": ["bc250-new-v0.1.0"], "portal": "",
                                                            "draft": False}
    assert sr.plan(MANIFEST, "4.1.0", tag="bc250-portal-v4.1.0") == {"apps": [], "portal": "bc250-portal-v4.1.0",
                                                               "draft": False}
    with pytest.raises(ValueError, match="is not bc250-<app>-v"):
        sr.plan(MANIFEST, "4.1.0", tag="sftp-3.1.0")


def test_a_nexus_release_brings_the_unreleased_pins_and_a_draft_portal():
    out = {"bc250-check-v3.0.1", "bc250-portal-v4.0.0"}
    found = sr.plan(MANIFEST, "4.1.0", released=out.__contains__)
    assert found == {"apps": ["bc250-sftp-v3.1.0", "bc250-new-v0.1.0"], "portal": "bc250-portal-v4.1.0",
                     "draft": True}
    assert sr.output_lines(found) == ['apps=["bc250-sftp-v3.1.0", "bc250-new-v0.1.0"]',
                                      "portal=bc250-portal-v4.1.0", "draft=true"]
    assert json.loads(sr.output_lines(found)[0].removeprefix("apps=")) == found["apps"]



def test_a_withdrawn_app_is_not_built():
    found = sr.plan(MANIFEST, "4.1.0", released=lambda tag: False)
    assert "bc250-xenia-v1.0.1" not in found["apps"]


def test_a_portal_out_already_releases_nothing_but_apps_need_a_bump():
    everything = {"bc250-check-v3.0.1", "bc250-sftp-v3.1.0", "bc250-new-v0.1.0", "bc250-portal-v4.0.0"}
    assert sr.plan(MANIFEST, "4.0.0", released=everything.__contains__) == {"apps": [], "portal": "",
                                                                           "draft": True}
    with pytest.raises(ValueError, match="bump portal/VERSION"):
        sr.plan(MANIFEST, "4.0.0", released={"bc250-portal-v4.0.0"}.__contains__)


def test_only_the_portal_a_withdrawal_for_instance():
    everything = {"bc250-check-v3.0.1", "bc250-sftp-v3.1.0", "bc250-new-v0.1.0"}
    assert sr.plan(MANIFEST, "4.1.0", released=everything.__contains__) == {"apps": [],
                                                                           "portal": "bc250-portal-v4.1.0", "draft": True}


def test_pin_sets_only_the_sha256_line_of_that_app():
    other = "cd" * 32
    text = sr.pin(MANIFEST, "bc250-sftp-v3.1.0", other)
    assert f'tag = "bc250-sftp-v3.1.0"\nsha256 = "{other}"\n' in text
    assert text.replace(other, "") == MANIFEST                      # nothing else changed, the comment included
    text = sr.pin(text, "bc250-new-v0.1.0", other)                        # an app without a sha256 line gets one
    assert text.endswith(f'tag = "bc250-new-v0.1.0"\nsha256 = "{other}"\n')


def test_pin_refuses_a_tag_the_manifest_does_not_pin():
    with pytest.raises(ValueError, match="does not pin bc250-sftp-v3.0.0"):
        sr.pin(MANIFEST, "bc250-sftp-v3.0.0", SHA)
    with pytest.raises(ValueError, match="no app for bc250-gone-v1.0.0"):
        sr.pin(MANIFEST, "bc250-gone-v1.0.0", SHA)


def test_the_checksum_comes_from_the_releases_own_sha256sums():
    sums = f"{'EF' * 32} *bc250-sftp-v3.1.0.tar.gz\n{SHA}  other.tar.gz\n"
    assert sr.sha256_of(sums, "bc250-sftp-v3.1.0.tar.gz") == "ef" * 32
    with pytest.raises(ValueError, match="does not list"):
        sr.sha256_of(sums, "bc250-new-v0.1.0.tar.gz")


def test_pin_on_the_command_line(tmp_path, monkeypatch, capsys):
    manifest = tmp_path / "apps.toml"
    manifest.write_text(MANIFEST, encoding="utf-8")
    monkeypatch.setattr(sr, "MANIFEST", manifest)
    (tmp_path / "sums" / "bc250-sftp-v3.1.0").mkdir(parents=True)
    (tmp_path / "sums" / "bc250-sftp-v3.1.0" / "SHA256SUMS").write_text(f"{'12' * 32}  bc250-sftp-v3.1.0.tar.gz\n")
    assert sr.main(["pin", str(tmp_path / "sums"), "bc250-sftp-v3.1.0"]) == 0
    assert f'sha256 = "{"12" * 32}"' in manifest.read_text(encoding="utf-8")
    before = manifest.read_bytes()
    assert sr.main(["pin", str(tmp_path / "sums"), "bc250-new-v0.1.0"]) == 1            # no SHA256SUMS: nothing written
    assert "suite_release.py pin" in capsys.readouterr().err and manifest.read_bytes() == before


def test_the_published_releases_come_from_one_listing():
    """One gh release list for the plan, not a gh release view per pinned app; a draft is not out."""
    asked = []

    def run(argv, **_kwargs):
        asked.append(argv)
        return type("Done", (), {"returncode": 0, "stdout": json.dumps(
            [{"tagName": "a-v1.0.0", "isDraft": False}, {"tagName": "portal-v2.0.0", "isDraft": True}])})()
    assert sr.published_tags(run=run) == {"a-v1.0.0"}
    assert asked == [["gh", "release", "list", "--limit", "1000", "--json", "tagName,isDraft"]]


def test_without_a_whole_listing_the_tags_are_asked_one_by_one():
    """GitHub does not answer, answers something else, or the listing is full (a release could be missing from it,
    and would be built again): no set, so the plan asks tag by tag."""
    def answers(code, out):
        return lambda argv, **_kwargs: type("Done", (), {"returncode": code, "stdout": out})()
    assert sr.published_tags(run=answers(1, "")) is None
    assert sr.published_tags(run=answers(0, "not json")) is None
    full = json.dumps([{"tagName": f"a-v1.0.{n}", "isDraft": False} for n in range(3)])
    assert sr.published_tags(limit=3, run=answers(0, full)) is None
    assert sr.published_tags(limit=4, run=answers(0, full)) == {"a-v1.0.0", "a-v1.0.1", "a-v1.0.2"}
