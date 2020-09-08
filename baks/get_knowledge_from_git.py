# -*- encoding: utf-8 -*-
import os
import time
import pandas as pd
import re
import pickle
import simple_pattern
import complex_pattern
import numpy as np
import collections
from utils import *

import sys
sys.stdout.flush()

import pdb

code_root = '/Volumes/Data/sonar_code_repos/'

# get all the git repo
task_lists = []
for _folder in os.listdir(code_root): 
    if '.git' in _folder:
        continue
    _path = os.path.join(code_root, _folder)
    for _sub_folder in os.listdir(_path):
        _sub_path = os.path.join(_path, _sub_folder)
        if '.git' in _sub_folder:
            continue
        if 'src' in _sub_folder:
            for _sub_sub_folder in os.listdir(_sub_path):
                _sub_sub_path = os.path.join(_sub_path, _sub_sub_folder)
                task_lists.append(_sub_sub_path)
        else:
            task_lists.append(os.path.join(_path, _sub_folder))


repo_name_list = []
# concat all files in a repo into a string
git_content_list = []
for git_path in task_lists:
    # get the repo_name for each task
    n1, n2, n3 = git_path.split('/')[-3:]
    if n2 == 'src':
        repo_name = n1 + '_' + n3.strip('\n')
    else:
        repo_name = n2 + '_' + n3.strip('\n')
    repo_name_list.append(repo_name)

    git_content = ""
    for _file in os.listdir(git_path):
        _sub_path = os.path.join(git_path, _file)
        if not os.path.isdir(_sub_path):
            ext = os.path.splitext(_file)[-1]
            if ext in ['.cpp', '.hpp', '.h', '.cc', '.c']:
                for line in open(_sub_path).readlines():
                    git_content += str(line) + '\n'
    git_content_list.append(git_content)

print(len(git_content_list))

# get the involved rules of each repo
result_rule = []
pattern_name = ''
pattern_dict = simple_pattern.get_all_patterns()
for i, row in enumerate(git_content_list):
    print(i)
    # if i != 18245:
    #     continue
    # pdb.set_trace()
    content_str = remove_annotation(row)
    simple_result_dict = rule_match(content_str, pattern_dict)
    complex_result_dict = complex_pattern.complex_pattern_checking(content_str, pattern_dict)
    result_rule.append( simple_result_dict.values() + complex_result_dict.values() )
    pattern_name = simple_result_dict.keys() + complex_result_dict.keys()

result_array = np.array(result_rule)
pattern_show_num = np.sum(result_array, axis=0)
np.savetxt('./data/git_data/pattern_show_num.txt', pattern_show_num, fmt='%d')
np.savetxt('./data/git_data/match_result_newdata.txt', result_array, fmt='%d')


# get the names of all repos 
repo_name_list = [name + '\n' for name in repo_name_list]
repo_name_out = open('./data/git_data/repo_name_for_result.txt', 'w')
repo_name_out.writelines("".join(repo_name_list))
repo_name_out.close()

pattern_name_num = [ pattern_name[i] + ': ' + str(pattern_show_num[i]) for i in range(len(pattern_name)) ]
pattern_name_num_out = open('./data/git_data/pattern_name_num.txt', 'w')
pattern_name_num_out.writelines('\n'.join(pattern_name_num))
pattern_name_num_out.close()

name_pattern_dict = {}
old_name2semantic_list = open('data/name2semantic.txt').readlines()
for line in old_name2semantic_list:
    name_pattern_dict[line.split(':')[0]] = line.split(':')[1].split('\n')[0]

new_name2semantic_list = []
for name in pattern_name:
    if name in name_pattern_dict:
        new_name2semantic_list.append(name + ':' + name_pattern_dict[name])
new_name2semantic_out = open('data/git_data/name2semantic.txt', 'w')
new_name2semantic_out.writelines('\n'.join(new_name2semantic_list))
new_name2semantic_out.close()

pattern_name_out = open('./data/git_data/pattern_name_newdata.txt', 'w')
pattern_name_out.writelines('\n'.join(pattern_name))
pattern_name_out.close()
with open("./data/git_data/code_rule_newdata.pkl","wb") as file:
    pickle.dump(result_rule, file)


# # compute the std
# match_result = np.loadtxt('./data/git_data/match_result_newdata.txt')
# match_result_str = []
# for i in range(match_result.shape[0]):
#     temp_str = ""
#     for j in range(match_result.shape[1]):
#         temp_str += str( int(match_result[i, j]) )
#     match_result_str.append(temp_str)
# # pdb.set_trace()
# unique_match_result = set(match_result_str)
# print(len(unique_match_result))