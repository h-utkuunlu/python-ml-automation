import os
import json
import argparse

def load_from_json(file_name):
    try:
        with open(file_name, 'rb') as f:
            try:
                opt_dict = json.load(f)
            except TypeError:
                print("File is not a json file")
                exit(1)
        return opt_dict

    except FileNotFoundError:
        print("File '{}' does not exist in the given path".format(file_name))
        exit(1)

def retrieve_all_configs(path):
    try:
        path_list = [os.path.join(path, i) for i in os.listdir(path)]
        configs = []
        for f in path_list:
            if f.endswith(".json"):
                configs.append(load_from_json(f))
        return configs
    
    except FileNotFoundError:
        print("Path does not exist")
        exit(1)
        
parser = argparse.ArgumentParser()
parser.add_argument("folder_path", help="Path that contains JSON files to be converted into experiments")
args = parser.parse_args()

files = retrieve_all_configs(args.folder_path)
print(files)
exit()

opt_dict = load_from_json(args.folder_path)

print(opt_dict["name"])
