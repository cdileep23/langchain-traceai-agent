import os

from fi_instrumentation import register
from fi_instrumentation.fi_types import ProjectType
from traceai_langchain import LangChainInstrumentor


def configure_tracing() -> None:
    if not (os.environ.get("FI_API_KEY") and os.environ.get("FI_SECRET_KEY")):
        return
    tracer_provider = register(
        project_type=ProjectType.OBSERVE,
        project_name=os.environ.get("FI_PROJECT_NAME", "harbor-hotels-langchain-agent"),
    )
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
