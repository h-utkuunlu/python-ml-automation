import os
import json
import argparse
import threading

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
        print("File '{}' does not exist in the given path. Exiting...".format(file_name))
        exit(1)

def retrieve_all_configs(path):
    try:
        path_list = [os.path.join(path, i) for i in os.listdir(path)]
        configs = []
        files = []
        for f in path_list:
            if f.endswith(".json"):
                configs.append(load_from_json(f))
                files.append(os.path.abspath(f))
        if len(configs) == 0:
            print("No experiments are found in the specified path. Exiting...")
            exit(1)
        else:
            return files, configs
    
    except FileNotFoundError:
        print("Path does not exist. Exiting...")
        exit(1)

def convert_arg_str_to_list(string):
    nums = [int(i) for i in string.lstrip("[").rstrip("]").split(",")]
    return nums

def thread_func(gpu_no, command_list, file_list, lock):
    while len(command_list) > 0:
        string = "[INFO] GPU %d idle" % gpu_no
        print(string)    

        # TODO: this is probably not an optimal way of handling race cond.s
        with lock:
            if len(command_list) == 0:
                return
            else:
                command = command_list.pop(0)
                filename = file_list.pop(0)
                print("[INFO] Number of experiments remaining: %d" % len(command_list))
                
        command = "CUDA_VISIBLE_DEVICES=%d %s" %(gpu_no, command)
        string = "[INFO] Thread %d executing %s" % (gpu_no, command)
        retval = os.system(command)
        
        # Move finished experiment
        if retval == 0:
            basename = os.path.basename(os.path.normpath(filename))
            dirname = os.path.dirname(filename)
            os.rename(filename, os.path.join(dirname, "completed", basename))
            #print(os.path.join(dirname, "completed", basename))

    # No more experiments left. Exit the thread
    print("[INFO] No more experiments left. Exiting thread for GPU %d" % gpu_no)
    
def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--script_path", help="Path to script to be executed")
    parser.add_argument("-e", "--exp_conf_path", help="Path that contains experiments represented as JSON files")
    parser.add_argument("-g", "--gpu", help="Available GPU's", type=str, default="[0]")
    args = parser.parse_args()

    # Load list of all configurations
    exp_files, config_list = retrieve_all_configs(args.exp_conf_path)

    # Parse config list into shell script line
    script_name = os.path.basename(os.path.normpath(args.script_path))
    script_path = os.path.dirname(args.script_path)
    exec_lines = []
    
    for config in config_list:
        string = "python %s " % script_name
        for param in config:
            string += "--%s %s " %(param, str(config[param])) 
        exec_lines.append(string)

    # Determine number of available GPUs (for thread count)
    gpus = convert_arg_str_to_list(args.gpu)
    num_gpu = len(gpus)

    # Add a completed experiment directory
    comp_path = os.path.join(args.exp_conf_path, "completed")
    if not os.path.exists(comp_path):
        os.mkdir(comp_path)
    
    # Change directory
    os.chdir(script_path)

    ## START TRAINING PROCESS

    # Create a lock
    lock = threading.Lock()
    
    # Spawn threads
    print("Working with %d GPU(s)" % num_gpu)
    thread_list = []

    for index in gpus:
        thread = threading.Thread(target=thread_func, args=(index, exec_lines, exp_files, lock))
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()


if __name__ == "__main__":
    main()
