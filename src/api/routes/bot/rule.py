from typing import Annotated

from fastapi import APIRouter, Body
from sqlalchemy import select

from src.api.utils import (
    ROOM_DEPENDENCY,
    check_rule_exists,
)
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import Rule
from src.schemas.method_input_schemas import (
    CreateRuleBody,
    EditRuleBody,
)
from src.schemas.method_output_schemas import RuleInfo

router = APIRouter(prefix="/rule")


@router.post("/create", response_description="The id of the created rule")
async def create_rule(room: ROOM_DEPENDENCY, rule: CreateRuleBody, db: DB_SESSION_DEPENDENCY) -> int:
    rule_obj = Rule(name=rule.name, text=rule.text, room_id=room.id)
    db.add(rule_obj)
    await db.commit()
    return rule_obj.id


@router.post("/list", response_description="List of rules")
async def list_rules(room: ROOM_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> list[RuleInfo]:
    rules: list[Rule] = await db.scalars(select(Rule).where(room_id=room.id)).all()
    return [RuleInfo.model_validate(rule, from_attributes=True) for rule in rules]


@router.post("/edit")
async def edit_rule(room: ROOM_DEPENDENCY, rule: EditRuleBody, db: DB_SESSION_DEPENDENCY) -> None:
    rule_obj = await check_rule_exists(rule.id, room.id, db)
    if rule.name:
        rule_obj.name = rule.name
    if rule.text:
        rule_obj.text = rule.text
    await db.commit()


@router.post("/delete", response_description="True if the rule was deleted")
async def delete_rule(room: ROOM_DEPENDENCY, rule_id: Annotated[int, Body()], db: DB_SESSION_DEPENDENCY) -> None:
    rule = await check_rule_exists(rule_id, room.id, db)
    await db.delete(rule)
    await db.commit()
