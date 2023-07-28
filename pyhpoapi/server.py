import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse

from pyhpo import Ontology
from pyhpo.stats import EnrichmentModel
try:
    from pyhpo.stats import HPOEnrichment
except ImportError:
    from pyhpoapi.helpers import MockHPOEnrichment as HPOEnrichment

import pyhpo

from pyhpoapi.routers import term, terms, annotations
from pyhpoapi import config

logger = logging.getLogger("uvicorn.error")

def custom_openapi_wrapper(app):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title='PyHPO API',
            version=config.VERSION,
            description='Use HTTP to interact with PyHPO {}'.format(
                pyhpo.__version__
            ),
            routes=app.routes,
            tags=config.OPENAPI_TAGS
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "/logo"
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    return custom_openapi


def initialize_ontology() -> None:
    data_dir = config.MASTER_DATA

    if data_dir == "":
        logger.debug("Using builtin standard ontology")
        _ = Ontology()
    else:
        logger.info(f"Loading Ontology from {data_dir}")
        _ = Ontology(data_dir)

    terms.gene_model = EnrichmentModel('gene')
    terms.omim_model = EnrichmentModel('omim')
    terms.hpo_model_genes = HPOEnrichment('gene')
    terms.hpo_model_omim = HPOEnrichment('omim')


def main():

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=config.CORS_METHODS,
        allow_headers=config.CORS_HEADERS,
    )
    app.openapi = custom_openapi_wrapper(app)

    @app.get('/logo', include_in_schema=False)
    def get_logo():
        return FileResponse(os.path.join(
            os.path.dirname(__file__),
            'resources/logo.png'
        ))

    app.include_router(
        term.router,
        prefix='/term',
        tags=['term'],
        responses={404: {'description': 'HPO Term does not exist'}}
    )

    app.include_router(
        terms.router,
        prefix='/terms',
        tags=['terms'],
        responses={
            400: {
                'description': 'Invalid HPO Term identifier in query'
            }
        }
    )

    app.include_router(
        annotations.router,
        tags=['annotations'],
        responses={404: {'description': 'Gene/Disease does not exist'}}
    )
    return app
