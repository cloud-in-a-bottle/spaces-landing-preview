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
    label: str
    tagline: str
    template: str


APPROACHES: tuple[Approach, ...] = (
    Approach(
        slug="stacked",
        label="Stacked",
        tagline="A short hero, then three equal size cards below it.",
        template="approach_stacked.html",
    ),
    Approach(
        slug="sky",
        label="In the sky",
        tagline="Pick a size right inside the hero — the cards float on the sky, no scroll.",
        template="approach_sky.html",
    ),
    Approach(
        slug="split",
        label="Split picker",
        tagline="Pitch on the left, a live size picker with one button on the right.",
        template="approach_split.html",
    ),
    Approach(
        slug="default",
        label="One default",
        tagline="Lead with the recommended size; the other two tuck in beneath it.",
        template="approach_default.html",
    ),
    Approach(
        slug="table",
        label="Spec sheet",
        tagline="A pixel comparison table laying the three sizes side by side.",
        template="approach_table.html",
    ),
)

BUILD_TAG = os.environ.get("PREVIEW_BUILD", "dev")


def _context(current_slug: str | None) -> dict[str, object]:
    return {
        "plans": PLANS,
        "approaches": APPROACHES,
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
    return Litestar(
        route_handlers=[
            overview,
            health,
            *[_make_approach_handler(a) for a in APPROACHES],
            create_static_files_router(path="/static", directories=[STATIC_DIR]),
        ],
        template_config=TemplateConfig(directory=TEMPLATES_DIR, engine=JinjaTemplateEngine),
    )


app = build_app()
