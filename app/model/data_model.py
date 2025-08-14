from typing import Dict, Optional, List, Union
from pydantic import BaseModel


# Submodelos para cada tipo de propiedad Notion

class NotionSelect(BaseModel):
    id: str
    name: str
    color: str

class NotionStatus(BaseModel):
    id: str
    name: str
    color: str

class NotionRelation(BaseModel):
    id: str

class NotionRollupItem(BaseModel):
    type: str
    relation: List[NotionRelation]

class NotionRollup(BaseModel):
    type: str
    array: List[NotionRollupItem]
    function: str

class NotionFormula(BaseModel):
    type: str
    string: Optional[str]

class NotionDate(BaseModel):
    start: str
    end: Optional[str]
    time_zone: Optional[str]

class NotionTitleText(BaseModel):
    plain_text: str

class NotionTitle(BaseModel):
    type: str
    text: Dict[str, Union[str, None]]
    plain_text: str

class NotionProperty(BaseModel):
    id: str
    type: str
    title: Optional[List[NotionTitle]] = None
    select: Optional[NotionSelect] = None
    checkbox: Optional[bool] = None
    status: Optional[NotionStatus] = None
    date: Optional[NotionDate] = None
    formula: Optional[NotionFormula] = None
    relation: Optional[List[NotionRelation]] = None
    rollup: Optional[NotionRollup] = None
    rich_text: Optional[List] = None

class NotionData(BaseModel):
    object: str
    id: str
    created_time: str
    last_edited_time: str
    properties: Dict[str, NotionProperty]
    url: Optional[str]

class NotionSource(BaseModel):
    type: str
    automation_id: Optional[str]
    action_id: Optional[str]
    event_id: Optional[str]
    user_id: Optional[str]
    attempt: Optional[int]

class NotionPage(BaseModel):
    source: NotionSource
    data: NotionData