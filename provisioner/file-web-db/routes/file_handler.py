import os
import pathlib
import yaml

_DATABASE_DIRECTORY = pathlib.Path("/var/www/data/")

def list_files():
    file_list = {}
    file_list['list'] = os.listdir(_DATABASE_DIRECTORY)
    # file_list = os.listdir(_DATABASE_DIRECTORY)
    print(file_list)
    return(file_list)


def convert_json_to_yaml(infile):
    with open(f"{_DATABASE_DIRECTORY}/{infile}", "r") as file:
        print(f"{_DATABASE_DIRECTORY}/{infile}")
        yaml_data = yaml.dump(json.load(file))
        print(yaml_data)
        return(yaml_data)

def convert_yaml_to_json(infile):
    noalias_dumper = yaml.dumper.SafeDumper
    noalias_dumper.ignore_aliases = lambda self, data: True
    with open(f"{_DATABASE_DIRECTORY}/{infile}", "r") as file:
        print(f"{_DATABASE_DIRECTORY}/{infile}")
        json_data = yaml.safe_load(file)
        print(json_data)
        return(json_data)

def write_json_to_yml(data):
    outfile = data['variables']['routerName'].lower()
    with open(f"{_DATABASE_DIRECTORY}/{outfile}.yml", "w") as file:
        yaml.dump(data, file, default_flow_style=False)
        return True
    return False


def delete_file(filename):
    file_path = f"{_DATABASE_DIRECTORY}/{filename}.yml"
    if os.path.exists(file_path):
        os.remove(file_path)
    return

def get_store_data(branch):
    branch_file = branch + '.yml'
    file_list = list_files()
    if 'base.yml' in file_list['list']:file_list['list'].remove('base.yml')
    if branch_file in file_list['list']:
        branch_data = convert_yaml_to_json(branch_file)
        print(branch_data)
        return branch_data
    return False

def get_all():
    return_list = []
    file_list = list_files()
    if 'base.yml' in file_list['list']:file_list['list'].remove('base.yml')
    for branch_file in file_list['list']:
        branch_data = convert_yaml_to_json(branch_file)
        return_list.append(branch_data['variables'])
    return return_list

def update_file(data):
    branch_file = data['variables']['routerName'].lower() + '.yml'
    file_list = list_files()
    LOG.debug(f"=============>{file_list}")
    if branch_file in file_list['list']:
        return write_json_to_yml(data)
    else:
        return False
