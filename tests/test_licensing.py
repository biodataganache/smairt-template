"""A generated LICENSE must be the license it names, in full.

`LICENSE` is the one generated artifact whose exact words carry legal effect, and a
truncated license is not the license it claims to be. These tests exist because an
abbreviated GPL-3.0 header notice and a BSD-3-Clause disclaimer cut off mid-sentence
once shipped as real project licenses, hidden inside escaped single-line strings.
"""

from __future__ import annotations

import hashlib

from smairt.models import License
from smairt.project import LICENSE_EXPLANATIONS, LICENSE_TEXT

# The final substantive words of each offered license, taken from its official text. A
# license truncated anywhere before its end fails to contain its own closing clause.
LICENSE_CLOSING_TEXT = {
    License.MIT: "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.",
    License.BSD_3_CLAUSE: "OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.",
}


def test_every_offered_license_has_shipped_text_and_an_explanation() -> None:
    """A license cannot be selectable without legal text behind it.

    The wizard, the dashboard, and `smairt settings` all derive their choices from the
    License enum, so an entry without text would be offered and then fail at write time.
    """
    for license in License:
        assert license in LICENSE_TEXT, f"{license.value} is offered with no shipped text"
        assert license in LICENSE_EXPLANATIONS, f"{license.value} is offered with no explanation"
    assert set(LICENSE_TEXT) == set(License)
    assert set(LICENSE_EXPLANATIONS) == set(License)


def test_no_offered_license_is_truncated_before_its_closing_clause() -> None:
    """Each license ends with its own final clause rather than stopping partway.

    This is the specific defect that shipped: the BSD-3-Clause text ended at "DAMAGES."
    and dropped the entire limitation-of-liability sentence that follows it.
    """
    for license, closing in LICENSE_CLOSING_TEXT.items():
        rendered = LICENSE_TEXT[license].format(year=2026, holder="Example Holder")
        assert closing in rendered, f"{license.value} is truncated before its closing clause"
        assert rendered.rstrip().endswith(closing.rstrip()), (
            f"{license.value} does not end with its closing clause"
        )


def test_every_offered_license_is_checked_for_truncation() -> None:
    """Adding a license without a closing-clause assertion cannot pass silently."""
    assert set(LICENSE_CLOSING_TEXT) == set(License)


def test_license_text_carries_the_holder_and_year_it_is_given() -> None:
    for license in License:
        rendered = LICENSE_TEXT[license].format(year=2026, holder="Ada Researcher")
        assert "Ada Researcher" in rendered
        assert "2026" in rendered
        assert "{year}" not in rendered
        assert "{holder}" not in rendered


def test_a_license_is_not_offered_unless_its_full_text_is_short_enough_to_ship_inline() -> None:
    """Licenses requiring hundreds of lines were removed rather than abbreviated.

    Apache-2.0 and GPL-3.0 were offered as 17-line and 14-line summaries. Rather than
    shipping their complete text, they were withdrawn, and generated guidance tells a
    researcher to supply such a license themselves. This test records that decision so
    reintroducing a stub is a deliberate, visible act.
    """
    assert "Apache-2.0" not in {license.value for license in License}
    assert "GPL-3.0" not in {license.value for license in License}


# SHA-256 of each license's complete text with the copyright line normalized away, so the
# digest covers the license body rather than the holder. Guards the middle of a license, which
# a closing-clause assertion cannot see: a clause silently dropped from the centre of
# BSD-3-Clause would still end correctly.
LICENSE_BODY_DIGESTS = {
    License.MIT: "ac94220a7c120581bae3b5b6aadbb476ee91d124f7ac81d5bd28ee8dad2c6d65",
    License.BSD_3_CLAUSE: "53f6d3c8195318969ad6ee797d69ec2f98914dc157ec302e8a0e45fa7a2dd4da",
}


def license_body(license: License) -> str:
    """Return the license text with the holder and year removed."""
    rendered = LICENSE_TEXT[license].format(year=2026, holder="Example Holder")
    return "\n".join(
        line
        for line in rendered.splitlines()
        if "Example Holder" not in line and "2026" not in line
    )


def test_every_license_body_is_stable_and_covered_by_a_digest() -> None:
    """A license body cannot change without someone updating a digest deliberately.

    This is the check that would catch a clause removed from the middle of a license. It does
    not assert what the official text is — no test can, without shipping a second copy — but it
    makes any edit to shipped legal text a visible, intentional act.
    """
    assert set(LICENSE_BODY_DIGESTS) == set(License)
    for license in License:
        digest = hashlib.sha256(license_body(license).encode()).hexdigest()
        assert digest == LICENSE_BODY_DIGESTS[license], (
            f"{license.value} legal text changed; its digest is now {digest}. "
            "Update the digest only if the change is a deliberate correction to the license."
        )
