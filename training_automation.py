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

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--script_path", help="Path to script to be executed")
parser.add_argument("-e", "--exp_conf_path", help="Path that contains experiments represented as JSON files")
parser.add_argument("-g", "--gpu", help="Available GPU's", type=str, default="[0]")
args = parser.parse_args()

# Load list of all configurations
config_list = retrieve_all_configs(args.exp_conf_path)

# Parse config list into shell script line
script_lines = []
for config in config_list:
    string = ""
    for param in config:
        string += "--%s %s " %(param, str(config[param])) 
    script_lines.append(string)

print(script_lines)
exit()

gpus = convert_arg_str_to_list(args.gpu)
for i in gpus:
    print(i)
    os.system('CUDA_VISIBLE_DEVICES=%d python playground/test.py'%i)

#files = retrieve_all_configs(args.folder_path)
