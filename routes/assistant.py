from rag import service
from fastapi import APIRouter,HTTPException
from schemas import AskRequest,AskResponse

router=APIRouter(prefix="/ask",tags=['Assistant'])
@router.post("/",response_model=AskResponse)
def ask(req:AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400,detail="Question cannot be empty")
    try:
        return service.generate_text(req.question)
    except Exception:
        raise HTTPException(status_code=503,detail="Assistant is not available right now, try again later")
