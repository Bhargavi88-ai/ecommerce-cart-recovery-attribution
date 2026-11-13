from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from app.database import get_db, SessionLocal, Base, engine
from app.config import settings
from app.generator.synthetic_data_generator import SyntheticDataGenerator
from app.exports.exporter import DatasetExporter
from app.generator.db_loader import populate_database_from_dataset

router = APIRouter(prefix="/generator", tags=["Generator"])

_generator_state = {
    "status": "IDLE",
    "last_run": None,
    "scale": None,
    "seed": None,
    "message": "Ready to generate data."
}


class GeneratorRunRequest(BaseModel):
    scale: str = "starter"  # starter or full
    seed: int = 20261022
    populate_db: bool = True


def _run_generation_task(scale: str, seed: int, populate_db: bool):
    global _generator_state
    try:
        _generator_state["status"] = "RUNNING"
        _generator_state["scale"] = scale
        _generator_state["seed"] = seed
        _generator_state["message"] = f"Generating {scale} dataset with seed {seed}..."

        gen = SyntheticDataGenerator(seed=seed, scale=scale)
        dataset = gen.generate_dataset()

        exp = DatasetExporter(export_dir=settings.EXPORTS_DIR)
        manifest = exp.export_all(dataset, scale=scale, seed=seed)

        if populate_db:
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            try:
                populate_database_from_dataset(db, dataset)
            finally:
                db.close()

        _generator_state["status"] = "COMPLETED"
        _generator_state["last_run"] = datetime.now(timezone.utc).isoformat()
        _generator_state["message"] = f"Successfully generated {scale} dataset ({len(dataset['carts']):,} carts)."
    except Exception as e:
        _generator_state["status"] = "FAILED"
        _generator_state["message"] = f"Error during generation: {str(e)}"


@router.post("/run")
def trigger_generation(req: GeneratorRunRequest, background_tasks: BackgroundTasks):
    global _generator_state
    if _generator_state["status"] == "RUNNING":
        raise HTTPException(status_code=409, detail="A generation task is already actively running.")

    background_tasks.add_task(_run_generation_task, req.scale, req.seed, req.populate_db)
    return {
        "status": "ACCEPTED",
        "message": f"Generation triggered for scale '{req.scale}' with seed {req.seed}.",
        "scale": req.scale,
        "seed": req.seed
    }


@router.get("/status")
def get_generator_status():
    global _generator_state
    return _generator_state

