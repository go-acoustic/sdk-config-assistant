"""
Unit tests for generate_sdk_patched.py: build-note injection and its warning,
Pro-tier overrides, effect enum clamping, the pageView/type2 URL fix, logging
flags by mode, validator modes and loading the base initLogSignal.js.
"""
import io
import os
import pathlib
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

import generate_sdk_patched as gen  # noqa: E402  (after path fix)


# ---------------------------------------------------------------------------
# Helper: build a minimal profile dict
# ---------------------------------------------------------------------------
def _profile(tier="Premium", production_domain="www.example.com"):
    return {
        "customer": {
            "tier": tier,
            "productionDomain": production_domain,
            "appKey": "TEST_APP_KEY",
            "collectorUrl": "https://collector.example.com",
        },
        "settings": {"tier": tier, "fakeSignals": True},
        "signals": {},
        "inspection": {},
    }


# ---------------------------------------------------------------------------
# 1. Build-note format
# ---------------------------------------------------------------------------
class TestBuildNote(unittest.TestCase):
    def test_build_note_format(self):
        """build_full_sdk embeds 'Domain - DDMMYYYY' in the SDK string."""
        profile = _profile(production_domain="www.mysite.co.uk")
        sdk = gen.build_full_sdk("function initLogSignal(){}", profile)
        # pattern: domain - DDMMYYYY
        self.assertRegex(sdk, r"www\.mysite\.co\.uk - \d{8}")

    def test_build_note_fallback_domain(self):
        """When productionDomain is absent, uses 'unknown'."""
        profile = _profile()
        del profile["customer"]["productionDomain"]
        sdk = gen.build_full_sdk("function initLogSignal(){}", profile)
        self.assertIn("unknown -", sdk)


# ---------------------------------------------------------------------------
# 2. Pro-tier overrides
# ---------------------------------------------------------------------------
class TestProTierOverrides(unittest.TestCase):
    _PRO_FLAGS = [
        "gestures.enabled = false",
        "ajaxListener.enabled = false",
        "core.frames = {}",
        "domCapture.enabled = false",
        "overstat.enabled = false",
        "mousemove.enabled = false",
    ]

    def _sdk_for_tier(self, tier):
        """Build the SDK Config from the real template for the given tier."""
        return gen.build_full_sdk("function initLogSignal(){}", _profile(tier=tier))

    def test_template_has_injection_point(self):
        """The overrides go in before the first `return config;`; without it they silently vanish."""
        self.assertIn("        return config;", gen.SDK_TEMPLATE_PATH.read_text(encoding="utf-8"))

    def test_pro_tier_injects_all_six_overrides(self):
        sdk = self._sdk_for_tier("Pro")
        for flag in self._PRO_FLAGS:
            self.assertIn(flag, sdk, f"Missing Pro-tier flag: {flag}")

    def test_connect_pro_tier_injects_overrides(self):
        sdk = self._sdk_for_tier("Connect Pro")
        self.assertIn("gestures.enabled = false", sdk)

    def test_connect_pro_hyphen_variant(self):
        sdk = self._sdk_for_tier("connect-pro")
        self.assertIn("gestures.enabled = false", sdk)

    def test_premium_tier_no_overrides(self):
        sdk = self._sdk_for_tier("Premium")
        self.assertNotIn("Pro-tier overrides", sdk)

    def test_ultimate_tier_no_overrides(self):
        sdk = self._sdk_for_tier("Ultimate")
        self.assertNotIn("Pro-tier overrides", sdk)

    def test_promotional_tier_no_overrides(self):
        """'Promotional' contains 'pro' as substring — must NOT trigger Pro-tier."""
        sdk = self._sdk_for_tier("Promotional")
        self.assertNotIn("Pro-tier overrides", sdk)

    def test_approved_tier_no_overrides(self):
        """'Approved' contains 'pro' as substring — must NOT trigger Pro-tier."""
        sdk = self._sdk_for_tier("Approved")
        self.assertNotIn("Pro-tier overrides", sdk)


# ---------------------------------------------------------------------------
# 3. Effect enum clamping (_field_lines)
# ---------------------------------------------------------------------------
class TestEffectClamping(unittest.TestCase):
    def _lines_for_effect(self, source_value="positive"):
        """Call _field_lines with a single 'effect' field mapped via dataLayer."""
        fields = {"effect": {"source": "dataLayer", "path": "ecommerce.effect"}}
        return "\n".join(gen._field_lines(fields))

    def test_effect_output_uses_var_not_const(self):
        out = self._lines_for_effect()
        self.assertIn("var _eff", out)
        self.assertNotIn("const _eff", out)

    def test_effect_clamps_to_positive_or_negative(self):
        out = self._lines_for_effect()
        self.assertIn("_eff === 'negative' ? 'negative' : 'positive'", out)

    def test_effect_has_schema_comment(self):
        out = self._lines_for_effect()
        self.assertIn("neutral", out.lower())  # comment mentions it


# ---------------------------------------------------------------------------
# 4. URL fix — _source_expr type2 fallback
# ---------------------------------------------------------------------------
class TestUrlFix(unittest.TestCase):
    def test_type2_url_uses_href_split(self):
        """type2 fallback must use location.href.split('?')[0], not pathname."""
        expr = gen._source_expr({"source": "type2", "path": "screenview.url"})
        self.assertIn("location.href.split('?')[0]", expr)
        self.assertNotIn("location.pathname", expr)

    def test_type2_url_strips_query_string(self):
        expr = gen._source_expr({"source": "type2", "path": "screenview.url"})
        self.assertIn("split('?')[0]", expr)


# ---------------------------------------------------------------------------
# 5. Build-note substitution warning (stderr)
# ---------------------------------------------------------------------------
class TestBuildNoteWarning(unittest.TestCase):
    def test_warning_on_template_mismatch(self):
        """build_full_sdk warns on stderr when the template has no build-note to replace."""
        with tempfile.TemporaryDirectory() as d:
            tpl = pathlib.Path(d) / "sdk-template.js"
            tpl.write_text(gen.SDK_INSERT_MARKER + "\n        return config;\n", encoding="utf-8")
            err = io.StringIO()
            with patch.object(gen, "SDK_TEMPLATE_PATH", tpl), redirect_stderr(err):
                gen.build_full_sdk("function initLogSignal(){}", _profile(production_domain="www.test.com"))
        self.assertIn("build-note substitution found no match", err.getvalue())

    def test_no_warning_with_real_template(self):
        err = io.StringIO()
        with redirect_stderr(err):
            gen.build_full_sdk("function initLogSignal(){}", _profile())
        self.assertNotIn("build-note substitution found no match", err.getvalue())


# ---------------------------------------------------------------------------
# Logging flags follow settings.mode (production must turn errorLog off)
# ---------------------------------------------------------------------------
class TestLoggingFlags(unittest.TestCase):
    BASE = "var cfg = { errorLog: true, eventLog: false, signalsLog: true, fakeSignals: true, signals: {} };"

    def _flags(self, mode):
        profile = _profile()
        profile["settings"]["mode"] = mode
        js = gen.configure_init_log_signal(self.BASE, profile)
        return {k: re.search(k + r"\s*:\s*(true|false)", js).group(1)
                for k in ("errorLog", "eventLog", "signalsLog", "fakeSignals")}

    def test_production_flags(self):
        # "production" is the mode the skill writes; "real" is its older name and must behave the same.
        for mode in ("production", "real"):
            with self.subTest(mode=mode):
                f = self._flags(mode)
                self.assertEqual(f["fakeSignals"], "false")
                self.assertEqual(f["errorLog"], "false")
                self.assertEqual(f["eventLog"], "false")
                self.assertEqual(f["signalsLog"], "true")

    def test_test_mode_flags(self):
        f = self._flags("test")
        self.assertEqual(f["fakeSignals"], "true")
        self.assertEqual(f["errorLog"], "true")
        self.assertEqual(f["signalsLog"], "true")


# ---------------------------------------------------------------------------
# validate_profile.py accepts the production mode under both names
# ---------------------------------------------------------------------------
class TestValidatorModes(unittest.TestCase):
    def test_modes(self):
        import validate_profile as vp
        self.assertEqual(vp.ALLOWED_MODES, {"test", "production", "real"})
        self.assertEqual(vp.PRODUCTION_MODES, {"production", "real"})
        self.assertNotIn("staging", vp.ALLOWED_MODES)


# ---------------------------------------------------------------------------
# load_base(): shipped asset, fallback order, helper injection
# ---------------------------------------------------------------------------
_FAKE_BASE = (
    "function initLogSignal() {\n"
    "    function logEnhanced(x) { return x; }\n"
    "    const help = { cssGet: cssGet, };\n"
    "}\n"
)


class TestLoadBase(unittest.TestCase):
    def test_asset_ships_with_skill(self):
        js = gen._LOCAL_BASE_JS.read_text(encoding="utf-8")
        self.assertIn("function initLogSignal", js)
        self.assertIn("function logEnhanced(", js)
        self.assertIn("cssGet: cssGet,", js)

    def test_explicit_path_injects_helpers(self):
        js = gen.load_base(gen._LOCAL_BASE_JS)
        self.assertIn("jsonLdGet: jsonLdGet,", js)

    def test_no_path_uses_asset_and_injects_helpers(self):
        with patch.object(gen, "fetch_base_from_cdn", side_effect=AssertionError("CDN must not be called")):
            js = gen.load_base(None)
        self.assertIn("jsonLdGet: jsonLdGet,", js)

    def test_missing_explicit_path_falls_back_to_asset(self):
        with patch.object(gen, "fetch_base_from_cdn", side_effect=AssertionError("CDN must not be called")):
            js = gen.load_base(gen.Path("/nonexistent/initLogSignal.js"))
        self.assertIn("jsonLdGet: jsonLdGet,", js)

    def test_missing_asset_falls_back_to_cdn(self):
        with patch.object(gen, "_LOCAL_BASE_JS", gen.Path("/nonexistent/assets/initLogSignal.js")), \
             patch.object(gen, "fetch_base_from_cdn", return_value=_FAKE_BASE) as cdn:
            js = gen.load_base(None)
        cdn.assert_called_once()
        self.assertIn("jsonLdGet: jsonLdGet,", js)

    def test_missing_explicit_path_and_missing_asset_fall_back_to_cdn(self):
        with patch.object(gen, "_LOCAL_BASE_JS", gen.Path("/nonexistent/assets/initLogSignal.js")), \
             patch.object(gen, "fetch_base_from_cdn", return_value=_FAKE_BASE) as cdn:
            js = gen.load_base(gen.Path("/nonexistent/other/initLogSignal.js"))
        cdn.assert_called_once()
        self.assertIn("jsonLdGet: jsonLdGet,", js)

    def test_asset_matches_reviewed_hash(self):
        import hashlib
        digest = hashlib.sha256(gen._LOCAL_BASE_JS.read_bytes()).hexdigest()
        self.assertEqual(
            digest, gen.INIT_LOG_SIGNAL_SHA256,
            "assets/initLogSignal.js changed: follow 'Updating assets/initLogSignal.js' in RELEASING.md",
        )

    def test_invalid_asset_falls_back_to_cdn(self):
        with tempfile.TemporaryDirectory() as d:
            bad = gen.Path(d) / "initLogSignal.js"
            bad.write_text("<html>not the file</html>", encoding="utf-8")
            with patch.object(gen, "_LOCAL_BASE_JS", bad), \
                 patch.object(gen, "fetch_base_from_cdn", return_value=_FAKE_BASE) as cdn:
                js = gen.load_base(None)
        cdn.assert_called_once()
        self.assertIn("jsonLdGet: jsonLdGet,", js)

if __name__ == "__main__":
    unittest.main()
