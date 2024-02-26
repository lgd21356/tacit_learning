import pickle

dict1_path = "/home/li/walk-these-ways-a1/walk-these-ways/runs/gait-conditioned-agility/2024-01-08/train/105343.499672/parameters.pkl"
dict2_path = "/home/li/walk-these-ways-a1/walk-these-ways/runs/gait-conditioned-agility/pretrain-a1/train/081719.645276/parameters.pkl"

with open(dict1_path, 'rb') as file:
    dict1 = pickle.load(file)
with open(dict2_path, 'rb') as file:
    dict2 = pickle.load(file)

# find the difference between two dictionaries
print(dict1.keys())
print(dict2.keys())

def print_nested_dict(dictionary, parent_key=''):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            if parent_key:
                new_key = f"{parent_key}.{key}"
            else:
                new_key = key
            print_nested_dict(value, new_key)
        else:
            if parent_key:
                print(f"{parent_key}.{key}: {value}")
            else:
                print(f"{key}: {value}")


import numpy as np
import torch

def compare_values(val1, val2):
    try:
        if isinstance(val1, (np.ndarray, torch.Tensor)) and isinstance(val2, (np.ndarray, torch.Tensor)):
            return np.array_equal(val1, val2), False
        else:
            return val1 == val2, False
    except Exception as e:
        return False, True

def find_dict_difference(dict1, dict2, path=""):
    for key in set(dict1.keys()) | set(dict2.keys()):
        new_path = f"{path}.{key}" if path else key

        if key in dict1 and key in dict2:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                find_dict_difference(dict1[key], dict2[key], path=new_path)
            else:
                equal, error = compare_values(dict1[key], dict2[key])
                if not equal:
                    print(f"Difference at {new_path}: {dict1[key]} vs {dict2[key]}")
                if error:
                    print(f"Error comparing values at {new_path}")
        elif key in dict1:
            print(f"Key {new_path} present in dict1 but not in dict2: {dict1[key]}")
        elif key in dict2:
            print(f"Key {new_path} present in dict2 but not in dict1: {dict2[key]}")



find_dict_difference(dict1, dict2)
