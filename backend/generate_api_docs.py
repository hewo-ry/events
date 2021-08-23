from fastapi.openapi.docs import get_redoc_html

from fastapi.openapi.utils import get_openapi

from pathlib import Path
from main import app
import json
import sys
from config import settings


def main():
    if len(sys.argv) > 1:
        build = sys.argv[1]
    else:
        build = settings.BUILD

    base_path = Path("docs/api")
    with open(base_path.joinpath("index.html"), "w") as html:
        html.write(
            get_redoc_html(
                openapi_url=app.openapi_url,
                title=app.title,
            ).body.decode("utf-8")
        )
    with open(base_path.joinpath("openapi.json"), "w") as j:
        j.write(
            json.dumps(
                get_openapi(
                    title=settings.SERVER_NAME,
                    version=f"{settings.VERSION}:{build}",
                    description="Hewo Events API Specification",
                    routes=app.routes,
                )
            )
        )


if __name__ == "__main__":
    main()
