import os, uuid, subprocess, logging, time, subprocess, random
from .db_utils import DBUtils
from .models import DynamicCheckChallenge, OwlContainers
from .extensions import log

class DockerUtils:
    @staticmethod
    def gen_flag():
        configs = DBUtils.get_all_configs()
        prefix = configs.get("docker_flag_prefix")
        flag = "{" + str(uuid.uuid4()) + "}"
        flag = prefix + flag #.replace("-","")
        while OwlContainers.query.filter_by(flag = flag).first() != None:
            flag = prefix + "{" + str(uuid.uuid4()) + "}"
        return flag

    @staticmethod
    def get_socket():
        configs = DBUtils.get_all_configs()
        socket = configs.get("docker_api_url")
        return socket

    @staticmethod
    def up_docker_compose(user_id, challenge_id):
        try:
            configs = DBUtils.get_all_configs()
            basedir = os.path.dirname(__file__)
            challenge = DynamicCheckChallenge.query.filter_by(id=challenge_id).first_or_404()
            flag = DockerUtils.gen_flag() if challenge.flag_type == 'dynamic' else 'static'
            socket = DockerUtils.get_socket()
            sname = os.path.join(basedir, "source/" + challenge.dirname)
            dirname = challenge.dirname.split("/")[1]
            prefix = configs.get("docker_flag_prefix")
            name = "{}_user{}_{}".format(prefix, user_id, dirname).lower()
            # TODO: UNKNOW ENVIRON
            problem_docker_run_dir = os.environ['PROBLEM_DOCKER_RUN_FOLDER']
            dname = os.path.join(problem_docker_run_dir, name)
            min_port, max_port = int(configs.get("frp_direct_port_minimum")), int(
                configs.get("frp_direct_port_maximum"))
            all_container = DBUtils.get_all_container()
            port, ports_list = random.randint(min_port, max_port), [_.port for _ in all_container]
            while port in ports_list:
                port = random.randint(min_port, max_port)

        except Exception as e:
            log("owl",
                'Stdout: {out}\nStderr: {err}',
                out=e.stdout.decode(),
                err=e.stderr.decode()
            )
            return e

        try:
            command = "cp -r {} {}".format(sname, dname)
            process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # sed port
            if flag != 'static':
                command = "cd {} && echo '{}' > flag && sed 's/9999/{}/g' docker-compose.yml > run.yml".format(dname, flag, port)
            else:
                command = "cd {} && sed 's/9999/{}/g' docker-compose.yml > run.yml".format(dname, port)
            process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # up docker-compose
            command = "cd " + dname + " && docker-compose -H={} -f run.yml up -d".format(socket)
            process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log(
                "owl",
                '[{date}] {msg}', 
                msg=name + " up."
            )
            docker_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, name)).replace("-", "")
            return (docker_id, port, flag, challenge.redirect_type)
        except subprocess.CalledProcessError as e:
            log("owl",
                'Stdout: {out}\nStderr: {err}',
                out=e.stdout.decode(),
                err=e.stderr.decode()
            )
            return e.stderr.decode()


    @staticmethod
    def down_docker_compose(user_id, challenge_id):
        try:
            configs = DBUtils.get_all_configs()
            basedir = os.path.dirname(__file__)
            socket = DockerUtils.get_socket()
            challenge = DynamicCheckChallenge.query.filter_by(id=challenge_id).first_or_404()
            dirname = challenge.dirname.split("/")[1]
            prefix = configs.get("docker_flag_prefix")
            name = "{}_user{}_{}".format(prefix, user_id, dirname).lower()
            problem_docker_run_dir = os.environ['PROBLEM_DOCKER_RUN_FOLDER'] 
            dname = os.path.join(problem_docker_run_dir, name)
        except Exception as e:
            log("owl",
                'Stdout: {out}\nStderr: {err}',
                out=e.stdout.decode(),
                err=e.stderr.decode()
            )
            return str(e)

        try:
            command = "cd {} && docker-compose -H={} -f run.yml down".format(dname, socket)
            process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            command = "rm -rf {}".format(dname)
            process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log(
                "owl",
                "[{date}] {msg}",
                msg=name + " down.",
            )
            return True
        except subprocess.CalledProcessError as e:
            log("owl",
                'Stdout: {out}\nStderr: {err}',
                out=e.stdout.decode(),
                err=e.stderr.decode()
            )
            return str(e.stderr.decode())

    @staticmethod
    def remove_current_docker_container(user_id, is_retry=False):
        configs = DBUtils.get_all_configs()
        container = DBUtils.get_current_containers(user_id=user_id)

        if container is None:
            return False
        try:
            DockerUtils.down_docker_compose(user_id, challenge_id=container.challenge_id)
            DBUtils.remove_current_container(user_id)
            return True
        except Exception as e:
            import traceback
            print(traceback.format_exc())
        # remove operation
            return False