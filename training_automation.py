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

def convert_arg_str_to_list(string):
    nums = [int(i) for i in string.lstrip("[").rstrip("]").split(",")]
    return nums
    
parser = argparse.ArgumentParser()
parser.add_argument("folder_path", help="Path that contains JSON files to be converted into experiments")
parser.add_argument("-g", "--gpu", help="Available GPU's", type=str, default="[0]")
args = parser.parse_args()

gpus = convert_arg_str_to_list(args.gpu)
for i in gpus:
    print(i)
    os.system('CUDA_VISIBLE_DEVICES=%d python playground/test.py'%i)

#files = retrieve_all_configs(args.folder_path)
