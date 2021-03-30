import os
from os.path import join
import sys
import json
import yaml
import boto3
from pprint import pprint
from pkg_resources import resource_filename

from .core import access, utils, storage, launch, config_utils
from .core.paths import NIMBO, CWD, CONFIG


def run(args):

    if args[0] == "generate-config":
        config_utils.generate_config()

    else:
        # Load yaml config file
        assert os.path.isfile(CONFIG), \
            f"Nimbo configuration file '{CONFIG}' not found.\n" \
            "You can run 'nimbo generate-config' for guided config file creation."

        with open(CONFIG, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        config = config_utils.fill_defaults(config)
        config_utils.verify_correctness(config)
        print()

        session = boto3.Session(profile_name=config["aws_profile"], region_name=config["region_name"])

        # Add user-id to config
        config["user_id"] = session.client("sts").get_caller_identity()["UserId"]

        if args[0] == "run":
            launch.run_job(session, config, args[1])

        elif args[0] == "launch":
            launch.run_job(session, config, "_nimbo_launch")

        elif args[0] == "launch-and-setup":
            launch.run_job(session, config, "_nimbo_launch_and_setup")

        elif args[0] == "ssh":
            utils.ssh(session, config, args[1])

        elif args[0] == "list-gpu-prices":
            utils.list_gpu_prices(session)

        elif args[0] == "list-spot-gpu-prices":
            utils.list_spot_gpu_prices(session)

        elif args[0] == "list-active":
            utils.show_active_instances(session, config)

        elif args[0] == "list-stopped":
            utils.show_stopped_instances(session, config)

        elif args[0] == "check-instance":
            utils.check_instance(session, args[1])

        elif args[0] == "stop-instance":
            utils.stop_instance(session, args[1])

        elif args[0] == "delete-instance":
            utils.delete_instance(session, args[1])

        elif args[0] == "delete-all-instances":
            utils.delete_all_instances(session, config)

        elif args[0] == "create-bucket":
            storage.create_bucket(session, args[1])

        elif args[0] == "push":
            storage.push(session, config, args[1])

        elif args[0] == "pull":
            storage.pull(session, config, args[1])

        elif args[0] == "ls":
            storage.ls(session, config, args[1])

        # elif args[0] == "create-key-pair":
        #    access.create_key_pair(session, args[1])

        # elif args[0] == "delete-key-pair":
        #    access.delete_key_pair(session, args[1])

        elif args[0] == "allow-current-device":
            access.allow_inbound_current_device(session, args[1])

        elif args[0] == "list-instance-profiles":
            access.list_instance_profiles(session)

        elif args[0] == "create-instance-profile":
            access.create_instance_profile(session, args[1])

        elif args[0] == "create-instance-profile-and-role":
            access.create_instance_profile_and_role(session)

        elif args[0] == "test-access":
            launch.run_access_test(session, config)

        else:
            raise Exception(f"Nimbo command '{args[0]}' not recognized.")


def main():
    run(sys.argv[1:])
