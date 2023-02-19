from CTFd.utils import user as current_user
from CTFd.utils import get_config
from CTFd.models import Users
from .db_utils import DBUtils
import logging
import logging.handlers
import time

USERS_MODE = "users"
TEAMS_MODE = "teams"

def get_mode():
    mode = get_config("user_mode")
    if mode == TEAMS_MODE:
        team_id = current_user.get_current_user().team_id
        user_id = current_user.get_current_user().id
        members = Users.query.filter_by(team_id=team_id)
        for member in members:
            if DBUtils.get_current_containers(user_id=member.id):
                user_id = member.id
                break
    elif mode == USERS_MODE:
        user_id = current_user.get_current_user().id
    return user_id
    
def log(logger, format, **kwargs):
    logger = logging.getLogger(logger)
    props = {
        "date": time.strftime("%m/%d/%Y %X"),
    }
    props.update(kwargs)
    msg = format.format(**props)
    print(msg)
    logger.info(msg)