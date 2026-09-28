from flask import Blueprint

from routes.helpers import run_module

bp = Blueprint("source", __name__)


@bp.post("/source-analysis")
def source_analysis():
    return run_module("source_analysis", "source_prompt.txt")
