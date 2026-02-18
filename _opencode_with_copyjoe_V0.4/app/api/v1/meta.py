from fastapi import APIRouter, Depends

from app.api.deps import meta_service
from app.schemas.meta import CopyFormGuideResponse
from app.services.meta_service import MetaService

router = APIRouter()


@router.get("/meta/copy-form-guide", response_model=CopyFormGuideResponse)
def copy_form_guide(service: MetaService = Depends(meta_service)) -> CopyFormGuideResponse:
    return service.copy_form_guide()
