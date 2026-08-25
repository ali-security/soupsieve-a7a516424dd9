"""Test attribute selectors."""
from .. import util
import threading
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def assert_syntax_error_no_timeout(self, selector):
        """Assert the selector fails with a syntax error without taking an unreasonable amount of time."""

        results = []

        def compile_selector():
            """Compile the selector, capturing the outcome for the calling thread."""

            try:
                sv.compile(selector)
            except Exception as e:
                results.append(e)
            else:
                results.append(None)

        # `signal.alarm` is not available on all platforms, so bound the run time with a thread.
        thread = threading.Thread(target=compile_selector)
        thread.daemon = True
        thread.start()
        # A linear parse returns almost immediately, an inefficient pattern will not finish.
        thread.join(timeout=10)

        # Parsing completed instead of backtracking.
        self.assertFalse(thread.is_alive())
        # Parsing failed with a syntax error.
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], sv.SelectorSyntaxError)

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout('[a="' + ('x' * 300))

    def test_bad_attribute_unclused_single_quote(self):
        """Test bad, single quoted attribute fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout("[a='" + ('x' * 300))

    def test_bad_attribute_unclused_no_quotes(self):
        """Test bad, unquoted attribute fails for syntax error, not timeout error."""

        self.assert_syntax_error_no_timeout('[a=' + ('x' * 300))
