from pydantic import BaseModel
from typing import Optional, List, Union


class Text(BaseModel):
    content: str
    link: Optional[str] = None


class Annotation(BaseModel):
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"


class RichTextItem(BaseModel):
    type: str
    text: Text
    annotations: Annotation
    plain_text: str
    href: Optional[str] = None


class SelectOption(BaseModel):
    id: str
    name: str
    color: Optional[str] = None


class DateProperty(BaseModel):
    start: str
    end: Optional[str] = None
    time_zone: Optional[str] = None


class RelationItem(BaseModel):
    id: str


class ItemRelationArray(BaseModel):
    type: str
    relation: Optional[RelationItem]


class NotionProperty(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    color: Optional[str] = None
    label: Optional[str] = None  # Para accederlo desde código
    title: Optional[List[RichTextItem]] = None
    select: Optional[SelectOption] = None
    relation: Optional[List[RelationItem]] = None
    status: Optional[SelectOption] = None
    date: Optional[DateProperty] = None
    string: Optional[str] = None
    array: Optional[List[ItemRelationArray]] = None


class NotionPage(BaseModel):
    object: Optional[str] = None
    id: Optional[str] = None
    properties: dict[str, NotionProperty]