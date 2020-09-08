# -*- encoding: utf-8 -*-
# use python3 to run this code

import numpy as np
import os
import io
import pdb
from get_rules_knowledge import get_shixunChallenge_knowledge_dict

def get_errid_shixunChallengelist_dict(compile_err_path):
    errid_shixunChallengelist_dict = {}
    with open(compile_err_path) as fin:
        for error_id_list in fin.readlines()[1:]:
            repo_path, shixun_id, position, err_ids = error_id_list.strip('\n').split('\t')
            shixunChallenge = shixun_id.strip('\"') + '_' + position.strip('\"')
            err_ids = err_ids.strip('[').strip(']').split(',')[:-1]
            err_ids = [int(_errid) for _errid in err_ids]
            for _id in err_ids:
                if _id not in errid_shixunChallengelist_dict.keys():
                    errid_shixunChallengelist_dict[_id] = [shixunChallenge]
                else :
                    errid_shixunChallengelist_dict[_id].append(shixunChallenge)
    return errid_shixunChallengelist_dict

def get_error_knowledge_dict(errid_shixunChallengelist_dict, shixunChallenge_knowledge_dict):
    errid_knowledge_list = []
    knowledge_num = len(shixunChallenge_knowledge_dict.values()[0])
    # link the errid_repos_dict to repos_knowledge_dict by taskid
    for error_id, shixunChallenge_list in errid_shixunChallengelist_dict.items():
        involved_knowledge = np.ones(knowledge_num)
        for shixunChallenge in shixunChallenge_list:
            if shixunChallenge in shixunChallenge_knowledge_dict.keys():
                knowledge = np.array(shixunChallenge_knowledge_dict[shixunChallenge])
                # pdb.set_trace()
                involved_knowledge = involved_knowledge * knowledge
            else:
                continue # do nothing
        involved_knowledge_str = ''
        for i in list(involved_knowledge):
            involved_knowledge_str += ('1' if i>0 else '0') + ' '
        if '0' not in involved_knowledge_str or '1' not in involved_knowledge_str:
            continue
        errid_knowledge_list.append(str(error_id) + ' ' + involved_knowledge_str + '\n')
    return errid_knowledge_list

if __name__ == '__main__':
    shixunChallenge_knowledge_path = 'data/v1/shixunChallenge_knowledge.txt'
    compile_err_path = './data/compile_errors/compile_err_res_after_merge.txt'

    shixunChallenge_knowledge_dict = get_shixunChallenge_knowledge_dict(shixunChallenge_knowledge_path)
    errid_shixunChallenge_dict = get_errid_shixunChallengelist_dict(compile_err_path)

    errid_knowledge_list = get_error_knowledge_dict(errid_shixunChallenge_dict, shixunChallenge_knowledge_dict)

    errid_knowledge_out = open('./data/v1/errid_to_knowledge.txt', 'w')
    errid_knowledge_out.writelines("".join(errid_knowledge_list))
    errid_knowledge_out.close()
