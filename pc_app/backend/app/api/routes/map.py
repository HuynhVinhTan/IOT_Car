from fastapi import APIRouter, HTTPException
import os
import json
import pathlib

router = APIRouter(prefix="/api/maps", tags=["map"])

BASE_DIR = pathlib.Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MAPS_DIR = DATA_DIR / "maps"
os.makedirs(MAPS_DIR, exist_ok=True)

ACTIVE_MAP_FILE = DATA_DIR / "active_map.txt"

@router.get("")
def list_maps():
    """List all available maps"""
    maps = []
    try:
        for f in os.listdir(MAPS_DIR):
            if f.endswith(".json"):
                with open(MAPS_DIR / f, "r") as file:
                    maps.append(json.load(file))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return maps

@router.get("/active")
def get_active_map():
    """Get currently active map"""
    if not ACTIVE_MAP_FILE.exists():
        raise HTTPException(status_code=404, detail="No active map")
    with open(ACTIVE_MAP_FILE, "r") as f:
        map_id = f.read().strip()
    path = MAPS_DIR / f"{map_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Active map not found")
    with open(path, "r") as f:
        return json.load(f)

@router.get("/{map_id}")
def get_map(map_id: str):
    """Get specific map by ID"""
    path = MAPS_DIR / f"{map_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Map not found")
    with open(path, "r") as f:
        return json.load(f)

@router.post("")
def save_map(map_data: dict):
    """Save or update a map"""
    map_id = map_data.get("id")
    map_name = map_data.get("name")
    nodes = map_data.get("nodes")
    edges = map_data.get("edges")
    if not map_id:
        raise HTTPException(status_code=400, detail="Missing map id")
    if not map_name:
        raise HTTPException(status_code=400, detail="Missing map name")
    if not isinstance(nodes, list):
        raise HTTPException(status_code=400, detail="Missing or invalid nodes")
    if not isinstance(edges, list):
        raise HTTPException(status_code=400, detail="Missing or invalid edges")
    path = MAPS_DIR / f"{map_id}.json"
    with open(path, "w") as f:
        json.dump(map_data, f, indent=2)
    return {"ok": True, "id": map_id, "upsert": True}

@router.post("/{map_id}/activate")
def activate_map(map_id: str):
    """Activate a map for autonomous mode"""
    path = MAPS_DIR / f"{map_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Map not found")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ACTIVE_MAP_FILE, "w") as f:
        f.write(map_id)
    return {"ok": True, "active_map": map_id}
