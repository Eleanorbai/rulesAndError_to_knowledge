# -*- encoding: utf-8 -*-
import os
import time
import pandas as pd
import re
import pickle
from utils import simple_pattern
from utils import complex_pattern
import numpy as np
import collections
from utils.utils import *
import csv

import sys
sys.stdout.flush()

import pdb

def get_shixunChallenge_knowledge(standardcode_path, knowledge_name_list):
    code_list = []
    # with open('data/standardcode.csv') as csvfile:
    with open(standardcode_path) as csvfile:
        standardcode = csv.reader(csvfile)
        for row in standardcode:
            code_list.append(row)
    print(len(code_list))
    # get the involved rules of each repo
    shixunChallenge_knowledge_list = []
    pattern_dict = simple_pattern.get_all_patterns()

    def get_knowledge(knowledge_dict):
        # knowledge = np.zeros(len(knowledge_name_list))
        knowledge = []
        for knowledge_name in knowledge_name_list:
            knowledge.append(knowledge_dict[knowledge_name])
        return knowledge

    for i, row in enumerate(code_list[1:]):
        print(i)
        # pdb.set_trace()
        _,shixun_id,shixun_name,position,challenge_id,challenge_name,answer_id,answer_contents = row
        content_str = remove_annotation(answer_contents)
        simple_result_dict = rule_match(content_str, pattern_dict)
        complex_result_dict = complex_pattern.complex_pattern_checking(content_str, pattern_dict)
        knowledge = get_knowledge(dict(simple_result_dict.items() + complex_result_dict.items()))
        shixunChallenge_knowledge_list.append((shixun_id,shixun_name,position,challenge_id,challenge_name,answer_id, knowledge ))
    return shixunChallenge_knowledge_list

if __name__ == '__main__':
    standardcode_path = 'data/v1/standardcode.csv'
    knowledge_name_list = open('data/knowledge_name.txt').readlines()
    knowledge_name_list = [line.strip('\n') for line in knowledge_name_list]

    shixunChallenge_knowledge_list = get_shixunChallenge_knowledge(standardcode_path, knowledge_name_list)

    shixunChallenge_knowledge_str = "shixun_id;shixun_name;position,challenge_id;challenge_name;answer_id;knowledge\n"
    for i in range(len(shixunChallenge_knowledge_list)):
        shixun_id, shixun_name, position, challenge_id, challenge_name, answer_id, knowledge = shixunChallenge_knowledge_list[i]
        shixun_rule_str = ""
        for i in range(len(knowledge)):
            shixun_rule_str += str(knowledge[i]) + ','
        shixunChallenge_knowledge_str += str(shixun_id) + ';' + shixun_name + ';' + str(position) + ';' + \
                str(challenge_id) + ';' + challenge_name + ';' + \
                str(answer_id) + ';' + shixun_rule_str + '\n'

    with open('./data/v1/shixunChallenge_knowledge.txt', 'w') as f:
        f.writelines("".join(shixunChallenge_knowledge_str))

    

    
    




