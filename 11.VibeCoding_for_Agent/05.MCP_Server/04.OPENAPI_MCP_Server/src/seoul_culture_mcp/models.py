from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, ConfigDict


class CulturalEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    codename: str | None = None
    guname: str | None = None
    title: str | None = None
    date: str | None = None
    place: str | None = None
    org_name: str | None = None
    use_fee: str | None = None
    inquiry: str | None = None
    player: str | None = None
    program: str | None = None
    etc_desc: str | None = None
    org_link: str | None = None
    main_img: str | None = None
    rgstdate: str | None = None
    ticket: str | None = None
    strtdate: int | None = None
    end_date: int | None = None
    themecode: str | None = None
    lot: str | None = None
    lat: str | None = None
    is_free: str | None = None
    hmpg_addr: str | None = None
    pro_time: str | None = None


class EventResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    DESCRIPTION: Dict[str, str] | None = None
    DATA: List[CulturalEvent] | None = None
