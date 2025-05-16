import sys
import subprocess
from pathlib import Path
import json
from typing import List
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
app = FastAPI(title="eCFR Analyzer DEMO", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

# -- load once -------------------------------------------------------
DATA_DIR = Path("data")
app.state.regs = json.loads((DATA_DIR / "regulations.json").read_text())
app.state.metrics = json.loads((DATA_DIR / "metrics.json").read_text())


# ─── helper to (re)load regs + metrics into app.state ─────────────────────────
def _reload_state():
    regs_path = DATA_DIR / "regulations.json"
    metrics_path = DATA_DIR / "metrics.json"
    app.state.regs = json.loads(regs_path.read_text())
    app.state.metrics = json.loads(metrics_path.read_text())


@app.post("/api/reload")
async def reload_data(bg: BackgroundTasks):
    """Run fetch_data.py + analytics.py then hot‑swap app.state."""
    python_exe = sys.executable

    def task():
        try:
            subprocess.run([python_exe, "fetch_data.py"], check=True)
            subprocess.run([python_exe, "analytics.py"], check=True)
            _reload_state()
            logging.info("Reload completed")
        except Exception as exc:
            logging.exception("Reload failed: %s", exc)

    bg.add_task(task)
    return JSONResponse({"status": "started"})


# -- API routes ------------------------------------------------------
@app.get("/api/metrics")
async def get_metrics():
    return app.state.metrics


@app.get("/api/search")
async def search_sections(
    q: str = Query(..., min_length=3, max_length=60),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
):
    """Substring search across section labels with pagination."""
    q_lower = q.lower()
    hits: List[dict] = []
    for title_num, tree in app.state.regs.items():
        stack = [tree]
        while stack:
            node = stack.pop()
            if not isinstance(node, dict):
                continue
            if (
                node.get("type") == "section"
                and q_lower in node.get("label", "").lower()
            ):
                hits.append(
                    {
                        "title": title_num,
                        "identifier": node.get("identifier"),
                        "label": node.get("label"),
                    }
                )
            stack.extend(node.get("children", []))
    total = len(hits)
    paged = hits[offset : offset + limit]
    return {
        "query": q,
        "offset": offset,
        "limit": limit,
        "total": total,
        "results": paged,
    }


@app.get("/api/sections/{title_num}/{section_id}")
async def get_section(title_num: str, section_id: str):
    tree = app.state.regs.get(title_num)
    if not tree:
        raise HTTPException(status_code=404, detail="Title not found")
    stack = [tree]
    while stack:
        node = stack.pop()
        if node.get("type") == "section" and node.get("identifier") == section_id:
            return node
        stack.extend(node.get("children", []))
    raise HTTPException(status_code=404, detail="Section not found")
