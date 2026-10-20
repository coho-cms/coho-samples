"""What a route can ask for: the service's Coho client."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from app.content import AsyncCoho


def coho(request: Request) -> AsyncCoho:
    """The one client the service made when it started, in `main.py`."""
    client: AsyncCoho = request.app.state.coho
    return client


Coho = Annotated[AsyncCoho, Depends(coho)]
"""A route's Coho client: name a parameter `coho: Coho`, and FastAPI passes it in."""
