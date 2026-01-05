# -*- coding: utf-8 -*-
from .instances import router as instances_router
from .deployment import router as deployment_router
from .releases import router as releases_router

__all__ = ["instances_router", "deployment_router", "releases_router"]
