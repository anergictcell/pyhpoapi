import logging
import os

from pyhpoapi import server

logger = logging.getLogger("uvicorn.error")

if os.environ.get("PYHPOAPI_DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.debug("Logging level set to DEBUG")

server.initialize_ontology()
app = server.main()
