from datetime import datetime
from typing import Iterable

from fastapi import APIRouter
from sqlalchemy import select, exists, func
from sqlalchemy.sql.functions import count

from src.api.exceptions import (
    UserHasRoomException,
    TooManyInvitationsException,
    InvitationAlreadySentException,
    InvitationNotExistException,
    InvitationExpiredException,
    NotYoursInvitationException,
)
from src.api.utils import (
    USER_DEPENDENCY,
    ROOM_DEPENDENCY,
    check_invitation_exists,
)
from src.config import SETTINGS_DEPENDENCY
from src.db_sessions import DB_SESSION_DEPENDENCY
from src.models.sql import User, Room, Invitation
from src.schemas.method_input_schemas import (
    InvitePersonBody,
    AcceptInvitationBody,
    DeleteInvitationBody,
    RejectInvitationBody,
)
from src.schemas.method_output_schemas import (
    IncomingInvitationsResponse,
    IncomingInvitationInfo,
    SentInvitationsResponse,
    SentInvitationInfo,
    UserInfo,
)

router = APIRouter(prefix="/invitation")


@router.post("/create", response_description="The id of created invitation")
async def invite_person(
    user: USER_DEPENDENCY,
    room: ROOM_DEPENDENCY,
    addressee: InvitePersonBody,
    db: DB_SESSION_DEPENDENCY,
    settings: SETTINGS_DEPENDENCY,
) -> int:
    number_of_invitations = (
        await db.execute(select(count()).select_from(Invitation).where(Invitation.sender_id == user.id))
    ).scalar()
    if number_of_invitations >= settings.MAX_INVITATIONS:
        raise TooManyInvitationsException()

    if (
        await db.execute(
            select(exists(Invitation)).where(
                Invitation.sender_id == user.id, func.lower(Invitation.addressee_alias) == addressee.alias.lower()
            )
        )
    ).scalar():
        raise InvitationAlreadySentException()

    invite = Invitation(sender_id=user.id, addressee_alias=addressee.alias, room_id=room.id)
    db.add(invite)
    await db.commit()

    return invite.id


@router.post("/accept", response_description="The id of the room the invitation led to")
async def accept_invitation(user: USER_DEPENDENCY, invitation: AcceptInvitationBody, db: DB_SESSION_DEPENDENCY) -> int:
    if user.room_id is not None:
        raise UserHasRoomException()

    invitation = await db.get(Invitation, invitation.id)
    if invitation is None:
        raise InvitationNotExistException()
    if invitation.expiration_date <= datetime.now():
        await db.delete(invitation)
        await db.commit()
        raise InvitationExpiredException()

    if user.alias is None or invitation.addressee_alias.lower() != user.alias.lower():
        raise NotYoursInvitationException()

    user.room_id = invitation.room_id
    await db.delete(invitation)
    await db.commit()

    return invitation.room_id


@router.post("/inbox", response_description="A list of the invitations addressed to a user")
async def get_incoming_invitations(user: USER_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> IncomingInvitationsResponse:
    response = IncomingInvitationsResponse(invitations=[])
    if user.alias is None:
        return response

    invitations: Iterable[Invitation] = (
        await db.scalars(select(Invitation).where(func.lower(Invitation.addressee_alias) == user.alias.lower()))
        if user.alias is not None
        else []
    )
    for i in invitations:
        if i.expiration_date <= datetime.now():
            await db.delete(i)
            continue
        room_name = (await db.get_one(Room, i.room_id)).name
        sender: User = await db.get_one(User, i.sender_id)
        response.invitations.append(
            IncomingInvitationInfo(
                id=i.id,
                sender=UserInfo.model_validate(sender, from_attributes=True),
                room=i.room_id,
                room_name=room_name,
            )
        )

    await db.commit()
    return response


@router.post("/sent", response_description="The list of sent invitations")
async def get_sent_invitations(user: USER_DEPENDENCY, db: DB_SESSION_DEPENDENCY) -> SentInvitationsResponse:
    invitations: list[SentInvitationInfo] = []
    i: Invitation
    for i in await db.scalars(select(Invitation).where(Invitation.sender_id == user.id)):
        if i.expiration_date <= datetime.now():
            await db.delete(i)
            continue
        room_name = (await db.get_one(Room, i.room_id)).name
        invitations.append(
            SentInvitationInfo(id=i.id, addressee=i.addressee_alias, room=i.room_id, room_name=room_name)
        )

    return SentInvitationsResponse(invitations=invitations)


@router.post("/delete", response_description="True if the invitation was deleted")
async def delete_invitation(user: USER_DEPENDENCY, invitation: DeleteInvitationBody, db: DB_SESSION_DEPENDENCY) -> bool:
    invitation = await check_invitation_exists(invitation.id, user.id, db)
    await db.delete(invitation)
    await db.commit()

    return True


@router.post("/reject", response_description="True if the invitation was rejected")
async def reject_invitation(user: USER_DEPENDENCY, invitation: RejectInvitationBody, db: DB_SESSION_DEPENDENCY) -> bool:
    invitation = await db.get(Invitation, invitation.id)
    if invitation is None:
        raise InvitationNotExistException()

    if user.alias is None or invitation.addressee_alias.lower() != user.alias.lower():
        raise NotYoursInvitationException()

    await db.delete(invitation)
    await db.commit()

    return True
