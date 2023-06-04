import os
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from webapp.model import Database
from webapp.model import organization_user
from webapp.model import AccessKey
from scripts.upload_create import issue_access_key, logger


def get_users_without_access_keys(db: Session) -> list:
    stmt = (
        select(organization_user.c.user_id, organization_user.c.organization_id)
        .outerjoin(AccessKey,
                   (organization_user.c.user_id == AccessKey.user_id)
                   & (organization_user.c.organization_id == AccessKey.organization_id))
        .where(AccessKey.id == None)  # pylint: disable=C0121
    )
    users_without_keys = db.execute(stmt).all()
    logger.info("Found %d users without access keys", len(users_without_keys))
    return users_without_keys


def issue_keys_to_users_without_keys(db: Session):
    users_without_keys = get_users_without_access_keys(db)
    for user, org in users_without_keys:
        issue_access_key(org, user)


if __name__ == "__main__":
    with Database(os.environ['DATABASE_URL']).get_session() as database:
        issue_keys_to_users_without_keys(database)
