from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

from config import settings
from core.deps import get_db

oauth = OAuth()

AuthenticationError = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED, detail="Unable to authenticate!"
)

NotEnoughPower = HTTPException(
    status_code=HTTP_403_FORBIDDEN, detail="Insufficient access rights!"
)


if settings.OIDC:
    oauth.register(
        name="provider",
        server_metadata_url=settings.OIDC_SERVER_METADATA_URL,
        client_kwargs={"scope": settings.OIDC_SCOPE},
        client_id=settings.OIDC_CLIENT_ID,
        client_secret=settings.OIDC_CLIENT_SECRET,
    )
else:
    raise NotImplemented

router = APIRouter()


@router.route("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.provider.authorize_redirect(request, redirect_uri)


@router.route("/auth")
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.provider.authorize_access_token(request)
    except OAuthError:
        raise AuthenticationError
    user = await oauth.provider.parse_id_token(request, token)
    # TODO replace with something correct
    # member = members.get_by_sub(db, user.get('sub'))
    # if not member:
    #     new_member = CreateMember(**{
    #         "name": user.get("name", ""),
    #         "sub": user.get("sub"),
    #         "username": user.get("preferred_username"),
    #         "email": user.get("email")
    #     })

    #     member = members.create(db, obj_in=new_member)
    # elif member.name != user.get("name") \
    #         or member.username != user.get("preferred_username") \
    #         or member.email != user.get("email"):
    #     updated_member = UpdateMember(**{
    #         "name": user.get("name", member.name),
    #         "username": user.get("preferred_username", member.username),
    #         "email": user.get("email", member.email)
    #     })

    #     member = members.update(db, db_obj=member, obj_in=updated_member)
    # request.session['user'] = dict(member)
    return RedirectResponse(url="/")


@router.route("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")
