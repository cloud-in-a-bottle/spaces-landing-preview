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
    """A pricing card on the merged landing page. Mirrors the real app's plan
    catalog (src/server/plans.py: Small/Medium/Large at $5/$10/$20) so the
    styling preview shows the actual sizes and prices."""

    name: str
    specs: str
    dollars: int
    points: tuple[str, ...]
    featured: bool = False


PLANS: tuple[PlanView, ...] = (
    PlanView(
        name="Small",
        specs="2 GB RAM · 2 vCPU",
        dollars=5,
        points=("Enough for a few light apps", "Notes, feeds, a password vault"),
    ),
    PlanView(
        name="Medium",
        specs="4 GB RAM · 3 vCPU",
        dollars=10,
        points=("Room for a real workload", "Media, chat, a database or two"),
        featured=True,
    ),
    PlanView(
        name="Large",
        specs="8 GB RAM · 4 vCPU",
        dollars=20,
        points=("For heavier or many apps", "Self-hosted models, big libraries"),
    ),
)

BUILD_TAG = os.environ.get("PREVIEW_BUILD", "dev")


@get("/", sync_to_thread=False)
def landing() -> Template:
    return Template(template_name="landing.html", context={"plans": PLANS, "build": BUILD_TAG})


@get("/health", sync_to_thread=False)
def health() -> dict[str, str]:
    return {"status": "ok"}


def build_app() -> Litestar:
    return Litestar(
        route_handlers=[
            landing,
            health,
            create_static_files_router(path="/static", directories=[STATIC_DIR]),
        ],
        template_config=TemplateConfig(directory=TEMPLATES_DIR, engine=JinjaTemplateEngine),
    )


app = build_app()
