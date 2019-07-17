import os

from django.urls import re_path
from django.views import static


DOCS_APP_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_HTML_DIR = os.path.join(DOCS_APP_DIR, "build", "html")

app_name = "docs"
urlpatterns = [
    re_path(r"^$", static.serve, {"path": "index.html", "document_root": DOCS_HTML_DIR}, name="docs"),
    re_path(r"^(?P<path>.*)$", static.serve, {"document_root": DOCS_HTML_DIR}),
]
