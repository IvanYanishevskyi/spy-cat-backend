from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import httpx

# Import our modules
from db import get_db, engine
from models.database_models import Base, SpyCat, Mission, Target
from models.api_models import (
    SpyCatCreate, SpyCatUpdate, SpyCatResponse,
    MissionCreate, MissionResponse, TargetResponse, TargetNotesUpdate
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spy Cat Agency API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# TheCatAPI validation function
async def validate_cat_breed(breed: str) -> bool:
    """Validate cat breed using TheCatAPI"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://api.thecatapi.com/v1/breeds")
            if response.status_code == 200:
                breeds = response.json()
                breed_names = [b["name"].lower() for b in breeds]
                return breed.lower() in breed_names
            return False
        except:
            return False

# Helper function to check if cat is available for mission
def is_cat_available(cat_id: int, db: Session) -> bool:
    """Check if cat has any incomplete missions"""
    active_mission = db.query(Mission).filter(
        Mission.cat_id == cat_id,
        Mission.complete == False
    ).first()
    return active_mission is None

# Helper function to check if all targets are complete
def check_mission_completion(mission: Mission) -> bool:
    """Check if all targets in mission are complete"""
    return all(target.complete for target in mission.targets)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Spy Cat Agency API", "status": "running"}



#Endpoints for Spy Cats


@app.post("/spy-cats/", response_model=SpyCatResponse)
async def create_spy_cat(spy_cat: SpyCatCreate, db: Session = Depends(get_db)):
    """Create a new spy cat"""
    # Validate breed with TheCatAPI
    if not await validate_cat_breed(spy_cat.breed):
        raise HTTPException(status_code=400, detail="Invalid cat breed")
    
    db_cat = SpyCat(
        name=spy_cat.name,
        years_of_experience=spy_cat.years_of_experience,
        breed=spy_cat.breed,
        salary=spy_cat.salary
    )
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.get("/spy-cats/", response_model=List[SpyCatResponse])
async def list_spy_cats(db: Session = Depends(get_db)):
    """Get all spy cats"""
    return db.query(SpyCat).all()

@app.get("/spy-cats/{cat_id}", response_model=SpyCatResponse)
async def get_spy_cat(cat_id: int, db: Session = Depends(get_db)):
    """Get a single spy cat"""
    cat = db.query(SpyCat).filter(SpyCat.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Spy cat not found")
    return cat

@app.put("/spy-cats/{cat_id}", response_model=SpyCatResponse)
async def update_spy_cat(cat_id: int, spy_cat: SpyCatUpdate, db: Session = Depends(get_db)):
    """Update spy cat salary"""
    cat = db.query(SpyCat).filter(SpyCat.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Spy cat not found")
    
    cat.salary = spy_cat.salary
    db.commit()
    db.refresh(cat)
    return cat

@app.delete("/spy-cats/{cat_id}")
async def delete_spy_cat(cat_id: int, db: Session = Depends(get_db)):
    """Remove spy cat from system"""
    cat = db.query(SpyCat).filter(SpyCat.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Spy cat not found")
    
    db.delete(cat)
    db.commit()
    return {"message": "Spy cat deleted successfully"}


@app.post("/missions/", response_model=MissionResponse)
async def create_mission(mission_data: MissionCreate, db: Session = Depends(get_db)):
    """Create a mission with targets"""
    db_mission = Mission()
    db.add(db_mission)
    db.flush()  
    
    for target_data in mission_data.targets:
        db_target = Target(
            mission_id=db_mission.id,
            name=target_data.name,
            country=target_data.country,
            notes=target_data.notes
        )
        db.add(db_target)
    
    db.commit()
    db.refresh(db_mission)
    return db_mission

@app.get("/missions/", response_model=List[MissionResponse])
async def list_missions(db: Session = Depends(get_db)):
    """Get all missions"""
    return db.query(Mission).all()

@app.get("/missions/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: int, db: Session = Depends(get_db)):
    """Get a single mission"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@app.delete("/missions/{mission_id}")
async def delete_mission(mission_id: int, db: Session = Depends(get_db)):
    """Delete a mission (only if not assigned to a cat)"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if mission.cat_id:
        raise HTTPException(status_code=400, detail="Cannot delete mission assigned to a cat")
    
    db.delete(mission)
    db.commit()
    return {"message": "Mission deleted successfully"}

@app.put("/missions/{mission_id}/assign/{cat_id}")
async def assign_mission_to_cat(mission_id: int, cat_id: int, db: Session = Depends(get_db)):
    """Assign a mission to a cat"""
    # Check if mission exists
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Check if cat exists
    cat = db.query(SpyCat).filter(SpyCat.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Spy cat not found")
    
    # Check if mission is already assigned
    if mission.cat_id:
        raise HTTPException(status_code=400, detail="Mission already assigned to a cat")
    
    # Check if cat is available
    if not is_cat_available(cat_id, db):
        raise HTTPException(status_code=400, detail="Cat is already assigned to another mission")
    
    # Assign mission
    mission.cat_id = cat_id
    db.commit()
    return {"message": f"Mission {mission_id} assigned to cat {cat_id}"}

@app.put("/missions/{mission_id}/targets/{target_id}/notes")
async def update_target_notes(mission_id: int, target_id: int, notes_data: TargetNotesUpdate, db: Session = Depends(get_db)):
    """Update notes for a target"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    target = db.query(Target).filter(
        Target.id == target_id,
        Target.mission_id == mission_id
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Check if target or mission is complete
    if target.complete:
        raise HTTPException(status_code=400, detail="Cannot update notes for completed target")
    
    if mission.complete:
        raise HTTPException(status_code=400, detail="Cannot update notes for completed mission")
    
    target.notes = notes_data.notes
    db.commit()
    return {"message": "Notes updated successfully"}

@app.put("/missions/{mission_id}/targets/{target_id}/complete")
async def complete_target(mission_id: int, target_id: int, db: Session = Depends(get_db)):
    """Mark target as complete and check if mission is complete"""
    # Get mission and target
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    target = db.query(Target).filter(
        Target.id == target_id,
        Target.mission_id == mission_id
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Mark target as complete
    target.complete = True
    
    # Check if all targets are complete
    if check_mission_completion(mission):
        mission.complete = True
    
    db.commit()
    return {"message": "Target marked as complete"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)