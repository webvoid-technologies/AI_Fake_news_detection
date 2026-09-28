from flask import Blueprint

from routes.helpers import run_module

bp = Blueprint("claims", __name__)


@bp.post("/claims")
def claims():
    return run_module("claims", "claims_prompt.txt")


@bp.post("/fact-check")
def fact_check():
    return run_module("fact_check", "factcheck_prompt.txt")
