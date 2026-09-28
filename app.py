import os

from flask import Flask, render_template

from config import APP_NAME, BRAND, SUPPORT_EMAIL, validate_env
from routes import analyze, claims, source, summary

app = Flask(__name__)

app.register_blueprint(analyze.bp)
app.register_blueprint(summary.bp)
app.register_blueprint(claims.bp)
app.register_blueprint(source.bp)


@app.get("/")
def index():
    return render_template(
        "index.html",
        app_name=APP_NAME,
        brand=BRAND,
        support_email=SUPPORT_EMAIL,
        env_missing=validate_env(),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
