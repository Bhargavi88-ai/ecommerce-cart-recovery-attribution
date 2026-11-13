import os
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import settings

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("")
def list_exports():
    export_dir = settings.EXPORTS_DIR
    if not os.path.exists(export_dir):
        return {"files": [], "manifest": None}

    manifest_path = os.path.join(export_dir, "source_manifest.json")
    manifest_data = None
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            pass

    files = []
    for fname in os.listdir(export_dir):
        fpath = os.path.join(export_dir, fname)
        if os.path.isfile(fpath):
            files.append({
                "filename": fname,
                "size_bytes": os.path.getsize(fpath),
                "modified_at": os.path.getmtime(fpath)
            })

    return {"files": files, "manifest": manifest_data}


@router.get("/{filename}")
def download_export_file(filename: str):
    # Prevent path traversal
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(settings.EXPORTS_DIR, safe_filename)
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Export file '{safe_filename}' not found.")

    media_type = "text/csv" if safe_filename.endswith(".csv") else "application/json" if safe_filename.endswith(".json") else "text/plain"
    return FileResponse(filepath, media_type=media_type, filename=safe_filename)
