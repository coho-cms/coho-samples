"""The service: its routes, and the Coho client they read through."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from coho_delivery_sdk import CohoDeliveryError, config_from_env
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import site
from app.content import AsyncCoho
from app.routes import posts
from app.schemas import SiteInfo


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # The service's Coho client, for every route. What it reads, and with which credential,
    # comes from the environment, not the code: with a preview token it reads dev or a
    # branch, live; with a delivery key, released content. On your machine, they are in .env.
    async with AsyncCoho(config_from_env(os.environ)) as coho:
        app.state.coho = coho
        yield


app = FastAPI(title=site.NAME, lifespan=lifespan)
app.include_router(posts.router)


@app.get("/", tags=["site"])
async def front_page() -> SiteInfo:
    """The site's name, and where its posts are."""
    return SiteInfo(name=site.NAME, locale=site.LOCALE, posts="/posts", docs="/docs")


@app.exception_handler(CohoDeliveryError)
async def coho_refused(request: Request, error: CohoDeliveryError) -> JSONResponse:
    """
    Coho refused a read, or could not be reached properly. It is this service's problem, not
    the caller's, so it is a 502, with Coho's code for whoever reads the logs.
    """
    return JSONResponse(status_code=502, content={"code": error.code, "detail": str(error)})
