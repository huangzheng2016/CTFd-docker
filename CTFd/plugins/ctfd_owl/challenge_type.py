from CTFd.plugins.challenges import BaseChallenge
from CTFd.plugins.flags import get_flag_class, FlagException
from CTFd.utils.user import get_ip
from flask import Blueprint, current_app
from CTFd.utils.modes import get_model
from CTFd.models import (
    db,
    Solves,
    Fails,
    Flags,
    Challenges,
    ChallengeFiles,
    Tags,
    Hints,
    Users,
    Notifications,
)
import math
from CTFd.utils.uploads import delete_file
from .models import DynamicCheckChallenge, OwlContainers
from .extensions import get_mode

class DynamicCheckValueChallenge(BaseChallenge):
    id = "dynamic_docker_owl"  # Unique identifier used to register challenges
    name = "dynamic_docker_owl"  # Name of a challenge type
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "ctfd-owl-challenge",
        __name__,
        template_folder="templates",
        static_folder="assets",
        url_prefix="/plugins/ctfd_owl"
    )
    challenge_model = DynamicCheckChallenge

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = DynamicCheckChallenge.query.filter_by(id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "initial": challenge.initial,
            "decay": challenge.decay,
            "minimum": challenge.minimum,
            "description": challenge.description,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """

        data = request.form or request.get_json()
        print(data)
        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            setattr(challenge, attr, value)

        Model = get_model()

        solve_count = (
            Solves.query.join(Model, Solves.account_id == Model.id)
                .filter(
                Solves.challenge_id == challenge.id,
                Model.hidden == False,
                Model.banned == False,
            )
                .count()
        )

        # It is important that this calculation takes into account floats.
        # Hence this file uses from __future__ import division
        value = (
                        ((challenge.minimum - challenge.initial) / (challenge.decay ** 2))
                        * (solve_count ** 2)
                ) + challenge.initial

        value = math.ceil(value)

        if value < challenge.minimum:
            value = challenge.minimum

        challenge.value = value

        db.session.commit()
        return challenge

    @classmethod
    def delete(cls, challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:
        :return:
        """
        Fails.query.filter_by(challenge_id=challenge.id).delete()
        Solves.query.filter_by(challenge_id=challenge.id).delete()
        Flags.query.filter_by(challenge_id=challenge.id).delete()
        OwlContainers.query.filter_by(id=challenge.id).delete()
        files = ChallengeFiles.query.filter_by(challenge_id=challenge.id).all()
        for f in files:
            delete_file(f.id)
        ChallengeFiles.query.filter_by(challenge_id=challenge.id).delete()
        Tags.query.filter_by(challenge_id=challenge.id).delete()
        Hints.query.filter_by(challenge_id=challenge.id).delete()
        DynamicCheckChallenge.query.filter_by(id=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()

    @classmethod
    def attempt(cls, challenge, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        chal = DynamicCheckChallenge.query.filter_by(id=challenge.id).first()
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        user_id = get_mode()

        if chal.flag_type == 'static':
            flags = Flags.query.filter_by(challenge_id=challenge.id).all()
            for flag in flags:
                try:
                    if get_flag_class(flag.type).compare(flag, submission):
                        return True, "Correct"
                except FlagException as e:
                    return False, str(e)
            return False, "Incorrect"

        flag = OwlContainers.query.filter_by(user_id=user_id, challenge_id=challenge.id).first()
        subflag = OwlContainers.query.filter_by(flag=submission).first()

        if subflag:
            try:
                fflag = flag.flag
            except Exception as e:
                fflag = ""
            if (fflag == submission):
                return True, "Correct"
            else:
                flaguser = Users.query.filter_by(id=user_id).first()
                subuser = Users.query.filter_by(id=subflag.user_id).first()

                if (flaguser.name == subuser.name):
                    return False, "Incorrect Challenge"
                else:
                    if flaguser.type == "admin":
                        return False, "Admin Test Other's Flag"
                    message = flaguser.name + " Submitted " + subuser.name + "'s Flag."
                    db.session.add(Notifications(title="Cheat Found", content=message))
                    flaguser.banned = True
                    db.session.commit()
                    messages = {"title": "Cheat Found", "content": message, "type": "background", "sound": True}
                    current_app.events_manager.publish(data=messages, type="notification")
                    return False, "Cheated"
        elif flag:
            return False, "Incorrect"
        else:
            return False, "Please solve it during the container is running"

    @classmethod
    def solve(cls, user, team, challenge, request):
        """
        This method is used to insert Solves into the database in order to mark a challenge as solved.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        chal = DynamicCheckChallenge.query.filter_by(id=challenge.id).first()
        data = request.form or request.get_json()
        submission = data["submission"].strip()

        Model = get_model()

        solve = Solves(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(req=request),
            provided=submission,
        )
        db.session.add(solve)

        solve_count = (
            Solves.query.join(Model, Solves.account_id == Model.id)
                .filter(
                Solves.challenge_id == challenge.id,
                Model.hidden == False,
                Model.banned == False,
            )
                .count()
        )

        # We subtract -1 to allow the first solver to get max point value
        solve_count -= 1

        # It is important that this calculation takes into account floats.
        # Hence this file uses from __future__ import division
        value = (
                        ((chal.minimum - chal.initial) / (chal.decay ** 2)) * (solve_count ** 2)
                ) + chal.initial

        value = math.ceil(value)

        if value < chal.minimum:
            value = chal.minimum
        chal.value = value

        db.session.commit()
