# -*- encoding: utf-8 -*-
# use python3 to run this code

import numpy as np
import os
import io
import pdb


def get_shixunChallenge_knowledge_dict(shixunChallenge_knowledge_path):
    shixunChallenge_knowledge_dict = {}
    # with open('data/standard_code/shixunChallenge_knowledge.txt') as f:
    with open(shixunChallenge_knowledge_path) as f:
        for line in f.readlines()[1:]:
            shixun_id, _, position, _, _, _, knowledge = line.strip('\n').split(';')
            knowledge = [int(line) for line in knowledge.strip(',').split(',')]
            _key = shixun_id + '_' + position
            if _key in shixunChallenge_knowledge_dict.keys():
                continue
            else:
                shixunChallenge_knowledge_dict[_key] = knowledge
    return shixunChallenge_knowledge_dict

# since the repo_ruleid_all.txt only records repo_path, we need to build a map from repo_path to shixunid and challengeid
def build_repopath_shixunChallenge_dict(old_repo_path, new_repo_path):
    repopath_shixunChallenge_dict = {}
    print('start to build a map from repo_path to shixunid&challengeid')
    # with open('./data/git_data/sqlresult.csv.bak.csv') as f:
    with open(old_repo_path) as f:
        for line in f.readlines()[1:]:
            _, _, shixun_id, _, _, repo_url, _, _  = line.split(',')
            # assume there are no more  than 10 steps in one repo
            for _idx in range(10):
                _key = repo_url.split('/')[-1].split('.')[0].split('-')[0] + '_step' + str(_idx+1)
                if _key not in repopath_shixunChallenge_dict.keys():
                    repopath_shixunChallenge_dict[_key] = shixun_id.strip('\"') + '_' + str(_idx+1)
    # with open('data/git_data/execute_result.txt') as f:
    with open(new_repo_path) as f:
        for line in f.readlines()[1:]:
            path, shixun_id, task_name = line.split('\t')
            repo_url = path.split('/')[-1].split('.')[0].split('-')[0] 
            for _idx in range(10):
                _key = repo_url.split('_')[0] + '_step' + str(_idx+1)
                if _key not in repopath_shixunChallenge_dict.keys():
                    repopath_shixunChallenge_dict[_key] = shixun_id.strip('\"') + '_' + str(_idx+1)
    print('build ended')
    return repopath_shixunChallenge_dict


def get_rulesid_repos_dict(sonar_result_path):
    rulesid_content_dict = {}
    rulesid_content_list = []
    rulesid_repos_dict = {}
    # repo_rules = open('data/git_data/repo_ruleid_all.txt').readlines()[2:]
    repo_rules = open(sonar_result_path).readlines()[2:]
    for i in range(len(repo_rules)):
        repo_name, ruleid, rule_content = repo_rules[i].split('|')[:3]
        if '_' not in repo_name:
            continue # filter LZ1 repo
        repopath = repo_name.strip(' ').split('_')[-2].split('-')[0] + '_' + repo_name.strip(' ').split('_')[-1]
        ruleid = ruleid.strip(' ')
        rule_content = rule_content.strip(' ')
        if ruleid not in rulesid_content_dict.keys():
            rulesid_content_dict[ruleid] = rule_content
            rulesid_content_list.append(ruleid + '|' + rule_content + '\n')
        # get all repos that may involves a given rule
        if ruleid not in rulesid_repos_dict.keys():
            rulesid_repos_dict[ruleid] = [repopath]
        else :
            rulesid_repos_dict[ruleid].append(repopath)
    rulesid_to_content_out = open('data/rulesid_to_content.txt', 'w')
    rulesid_to_content_out.writelines("".join(rulesid_content_list))
    rulesid_to_content_out.close()
    return rulesid_repos_dict


def get_rulesid_knowledge(shixunChallenge_knowledge_dict, repopath_shixunChallenge_dict, rulesid_repos_dict):
    rulesid_knowledge_list = []
    # link the rulesid_repos_dict to repos_knowledge_dict by taskid
    knowledge_num = len(shixunChallenge_knowledge_dict.values()[0])
    print("knowledge_num: {}".format(str(knowledge_num)))
    non_exist_repopath = []
    non_exist_shixunChallenge = []
    for rule_id, repos_list in rulesid_repos_dict.items():
        involved_knowledge = np.ones(knowledge_num)
        print("ruleid:{}".format(str(rule_id))),
        for repopath in repos_list:
            # repopath = repopath.split('-')[0]
            if repopath in repopath_shixunChallenge_dict.keys():
                shixunChallenge = repopath_shixunChallenge_dict[repopath]
            else:
                # print("repo {} not in standard code".format(repopath))
                non_exist_repopath.append(repopath)
                continue
            if shixunChallenge in shixunChallenge_knowledge_dict.keys():
                knowledge = shixunChallenge_knowledge_dict[shixunChallenge]
            else:
                # print("{} not in shixunChallenge_dict".format(shixunChallenge))
                non_exist_shixunChallenge.append(shixunChallenge)
                continue
            involved_knowledge = involved_knowledge * np.array(knowledge)
        
        involved_knowledge_str = ''
        for i in list(involved_knowledge):
            involved_knowledge_str += str(int(i)) + ' '
        rulesid_knowledge_list.append(str(rule_id) + ' ' + involved_knowledge_str + '\n')
    # with open('data/non_exist_repopath.txt','w') as fout:
    #     fout.writelines("\n".join(non_exist_repopath))
    # with open('data/non_exist_shixunChallenge.txt','w') as fout:
    #     fout.writelines("\n".join(non_exist_shixunChallenge))

    return rulesid_knowledge_list

if __name__ == '__main__':
    shixunChallenge_knowledge_path = 'data/v1/shixunChallenge_knowledge.txt'
    old_repo_path = 'data/old_repoUrl_list.csv'
    new_repo_path = 'data/new_repoUrl_list.txt'
    sonar_result_path = 'data/repoStep_ruleid_all.txt'

    shixunChallenge_knowledge_dict = get_shixunChallenge_knowledge_dict(shixunChallenge_knowledge_path)
    repopath_shixunChallenge_dict = build_repopath_shixunChallenge_dict(old_repo_path, new_repo_path)    

    rulesid_repos_dict = get_rulesid_repos_dict(sonar_result_path)

    rulesid_knowledge_list = get_rulesid_knowledge(shixunChallenge_knowledge_dict, repopath_shixunChallenge_dict, rulesid_repos_dict)

    rulesid_knowledge_out = open('data/v1/rulesid_to_knowledge.txt', 'w')
    rulesid_knowledge_out.writelines("".join(rulesid_knowledge_list))
    rulesid_knowledge_out.close()

