from flask import Blueprint

from routes.helpers import run_module

bp = Blueprint("summary", __name__)


@bp.post("/summary")
def summary():
    return run_module("summary", "summary_prompt.txt")
