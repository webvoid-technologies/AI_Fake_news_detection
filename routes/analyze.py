from flask import Blueprint

from routes.helpers import run_module

bp = Blueprint("analyze", __name__)


@bp.post("/analyze-url")
def analyze_url():
    return run_module("analyze", "detect_prompt.txt")


@bp.post("/misinformation")
def misinformation():
    return run_module("misinformation", "misinformation_prompt.txt")
