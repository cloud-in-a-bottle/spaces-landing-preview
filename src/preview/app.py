import os
from pathlib import Path

import attr
from litestar import Litestar
from litestar import get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.response import Template
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig

HERE = Path(__file__).parent
STATIC_DIR = HERE / "static"
TEMPLATES_DIR = HERE / "templates"


@attr.s(auto_attribs=True, frozen=True)
class PlanView:
    """A space size. Mirrors the real app's plan catalog (src/server/plans.py:
    Small/Medium/Large at $5/$10/$20) so every approach shows the actual sizes."""

    slug: str
    name: str
    memory_gb: int
    vcpus: int
    dollars: int
    good_for: str
    points: tuple[str, ...]
    featured: bool = False

    @property
    def specs(self) -> str:
        return f"{self.memory_gb} GB RAM · {self.vcpus} vCPU"


PLANS: tuple[PlanView, ...] = (
    PlanView(
        slug="small",
        name="Small",
        memory_gb=2,
        vcpus=2,
        dollars=5,
        good_for="A few light apps",
        points=("Notes, feeds, a password vault", "Plenty for getting started"),
    ),
    PlanView(
        slug="medium",
        name="Medium",
        memory_gb=4,
        vcpus=3,
        dollars=10,
        good_for="A real, everyday workload",
        points=("Media, chat, a database or two", "Comfortable headroom"),
        featured=True,
    ),
    PlanView(
        slug="large",
        name="Large",
        memory_gb=8,
        vcpus=4,
        dollars=20,
        good_for="Heavy or many apps at once",
        points=("Self-hosted models, big libraries", "Room to run a lot at once"),
    ),
)


@attr.s(auto_attribs=True, frozen=True)
class Approach:
    slug: str
    code: str
    label: str
    tagline: str
    template: str


# The chosen direction (#2, "In the sky") expanded into five variations.
SKY_APPROACHES: tuple[Approach, ...] = (
    Approach(
        slug="sky-left",
        code="2A",
        label="Left rail",
        tagline="Same idea, left-aligned: headline and lede up top, the three cards in a row on the sky below.",
        template="sky_left.html",
    ),
    Approach(
        slug="sky-side",
        code="2B",
        label="Side by side",
        tagline="Pitch on the left, the three size cards stacked on the right — everything still in the sky.",
        template="sky_side.html",
    ),
    Approach(
        slug="sky-tiered",
        code="2C",
        label="Tiered",
        tagline="Centered, with Medium raised and enlarged the way pricing pages spotlight the middle tier.",
        template="sky_tiered.html",
    ),
    Approach(
        slug="sky-compact",
        code="2D",
        label="Compact band",
        tagline="Centered headline, then one slim row of horizontal cards — the lightest, most above-the-fold.",
        template="sky_compact.html",
    ),
    Approach(
        slug="sky-config",
        code="2E",
        label="Configurator",
        tagline="A single floating panel: a Small / Medium / Large pixel toggle that swaps the price, specs, and CTA.",
        template="sky_config.html",
    ),
)

# The original #2 these five build on, kept reachable for comparison.
BASELINE = Approach(
    slug="sky",
    code="2",
    label="In the sky (original)",
    tagline="The approach these five are variations of.",
    template="approach_sky.html",
)

# The two finalists (left-aligned 2A and the centered original #2) blended five ways.
LEFT_RAIL = SKY_APPROACHES[0]  # 2A

COMBO_APPROACHES: tuple[Approach, ...] = (
    Approach(
        slug="combo-compact",
        code="C1",
        label="Compact centered",
        tagline="The original's centered look, with the headline dialed down so all three cards and their buttons sit above the fold.",
        template="combo_compact.html",
    ),
    Approach(
        slug="combo-bottle",
        code="C2",
        label="Left + bottle",
        tagline="2A's left-aligned header paired with the bobbing pixel bottle up on the right — the real cloudinabottle.org hero — cards below.",
        template="combo_bottle.html",
    ),
    Approach(
        slug="combo-split",
        code="C3",
        label="Centered title, left body",
        tagline="Keep the big centered headline for impact; the lede and fine print go left-aligned beneath it.",
        template="combo_split.html",
    ),
    Approach(
        slug="combo-twocol",
        code="C4",
        label="Two-column header",
        tagline="Headline in a left column, lede and trust points in a right column — the width of the centered version, but with left-aligned type.",
        template="combo_twocol.html",
    ),
    Approach(
        slug="combo-accent",
        code="C5",
        label="Centered + bottle",
        tagline="The compact centered header with a floating pixel bottle tucked in the corner — the original's symmetry plus the source-site art.",
        template="combo_accent.html",
    ),
)
# Gen 2: the five combos (C1–C5) bred into five new blends.
GEN2_APPROACHES: tuple[Approach, ...] = (
    Approach(
        slug="gen-tricol",
        code="D1",
        label="Three-part header",
        tagline="C4 × C2 — headline left, lede + trust points in the middle, the bobbing bottle on the right. The two-column header opened up to hold the art.",
        template="gen_tricol.html",
    ),
    Approach(
        slug="gen-title-bottle",
        code="D2",
        label="Centered title, body + bottle",
        tagline="C3 × C2 — the big centered headline, then a left-aligned lede and trust points beside the bottle.",
        template="gen_title_bottle.html",
    ),
    Approach(
        slug="gen-compact-trust",
        code="D3",
        label="Compact centered + trust row",
        tagline="C1 × C4 — the compact centered hero with one centered row of trust points under the lede. No art; cards well above the fold.",
        template="gen_compact_trust.html",
    ),
    Approach(
        slug="gen-left-compact",
        code="D4",
        label="Left + bottle, compact",
        tagline="C2 × C1 — the left-aligned bottle hero, tightened like C1 so the three cards and buttons clear the fold.",
        template="gen_left_compact.html",
    ),
    Approach(
        slug="gen-accent-trust",
        code="D5",
        label="Compact + corner bottle + trust",
        tagline="C5 × C1 × C4 — everything at once: compact centered header, floating corner bottle, and a centered trust row.",
        template="gen_accent_trust.html",
    ),
)

# The earlier approaches, still reachable from the overview.
ARCHIVE: tuple[Approach, ...] = (
    Approach("stacked", "1", "Stacked", "Hero, then three equal cards below.", "approach_stacked.html"),
    Approach("split", "3", "Split picker", "Pitch left, live picker right.", "approach_split.html"),
    Approach("default", "4", "One default", "Lead with the recommended size.", "approach_default.html"),
    Approach("table", "5", "Spec sheet", "A comparison table across sizes.", "approach_table.html"),
)

BUILD_TAG = os.environ.get("PREVIEW_BUILD", "dev")


def _context(current_slug: str | None) -> dict[str, object]:
    return {
        "plans": PLANS,
        # switcher shows the active generation (D1–D5) with its parents (C1–C5)
        "switcher_title": "Gen 2 · blends of C1–C5:",
        "switcher_set": GEN2_APPROACHES,
        "switcher_parents": COMBO_APPROACHES,
        # everything, for the overview compare rows
        "gen2": GEN2_APPROACHES,
        "combos": COMBO_APPROACHES,
        "left_rail": LEFT_RAIL,
        "baseline": BASELINE,
        "sky_approaches": SKY_APPROACHES,
        "archive": ARCHIVE,
        "build": BUILD_TAG,
        "current_slug": current_slug,
    }


@get("/", sync_to_thread=False)
def overview() -> Template:
    return Template(template_name="index.html", context=_context(current_slug=None))


@get("/health", sync_to_thread=False)
def health() -> dict[str, str]:
    return {"status": "ok"}


def _make_approach_handler(approach: Approach):
    @get("/" + approach.slug, sync_to_thread=False, name="approach_" + approach.slug)
    def _handler() -> Template:
        return Template(template_name=approach.template, context=_context(current_slug=approach.slug))

    return _handler


def build_app() -> Litestar:
    approach_handlers = [
        _make_approach_handler(a)
        for a in (*GEN2_APPROACHES, *COMBO_APPROACHES, *SKY_APPROACHES, BASELINE, *ARCHIVE)
    ]
    return Litestar(
        route_handlers=[
            overview,
            health,
            *approach_handlers,
            create_static_files_router(path="/static", directories=[STATIC_DIR]),
        ],
        template_config=TemplateConfig(directory=TEMPLATES_DIR, engine=JinjaTemplateEngine),
    )


app = build_app()
