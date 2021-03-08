import sys
import json
import yaml
import boto3
import argparse
from pprint import pprint
from pkg_resources import resource_filename

from core import utils, storage, launch

parser = argparse.ArgumentParser(description='Nimbo utilities.')
parser.add_argument('command', nargs='+', default='list_active')
parser.add_argument('--id', type=str, default='')
parser.add_argument('--ami', type=str, default='')
parser.add_argument('--noscript', action="store_true")
args = parser.parse_args()

# Load yaml config file
with open("./config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print("Config:")
pprint(config)

session = boto3.Session(profile_name='nimbo')

"""
for attr in pricing.describe_services(ServiceCode='AmazonEC2')["Services"][0]["AttributeNames"]:

    response = pricing.get_attribute_values(
        AttributeName=attr,
        MaxResults=100,
        ServiceCode='AmazonEC2',
    )
    print(attr)
    pprint(response)
    print()
sys.exit()
"""

if args.command[0] == "run":
    nimbo_ami = utils.get_latest_nimbo_ami(session)
    if nimbo_ami is not None:
        print(f"Using existing image ({nimbo_ami}).")
        launch.launch_instance_from_ami(session, config, nimbo_ami)
    else:
        print("No image found. Creating new one.")
        launch.launch_instance_from_scratch(session, config, args.noscript)

elif args.command[0] == "ssh":
    utils.ssh(session, args.id)

elif args.command[0] == "list_gpu_prices":
    utils.list_gpu_prices(session)

elif args.command[0] == "list_active":
    utils.show_active_instances(session)

elif args.command[0] == "list_stopped":
    utils.show_stopped_instances(session)

elif args.command[0] == "list_amis":
    utils.list_amis(session)

elif args.command[0] == "delete_ami":
    utils.delete_ami(session, args.ami)

elif args.command[0] == "check_instance":
    utils.check_instance(session, args.id)

elif args.command[0] == "stop_instance":
    utils.stop_instance(session, args.id)

elif args.command[0] == "delete_instance":
    utils.delete_instance(session, args.id)

elif args.command[0] == "delete_all_instances":
    utils.delete_all_instances(session, args.id)

elif args.command[0] == "check_instance":
    utils.check_instance(session, args.instance_id)

elif args.command[0] == "push":
    storage.push(session, config, args.command[1])

elif args.command[0] == "pull":
    storage.pull(session, config, args.command[1])

elif args.command[0] == "ls":
    storage.ls(session, config, args.command[1])

else:
    raise Exception(f"Command --{args.command[0]} not recognized.")
