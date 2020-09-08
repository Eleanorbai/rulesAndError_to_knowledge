# -*- coding: utf8
import csv
import numpy as np
import multiprocessing
import pdb

csv.field_size_limit(100000000)
sth = 0.5 # similar threshold
errinfo_errid_dict = {}
errid = 0
eps=0.01

data_root = 'data/compile_errors/'

def getSimilarRatioOfCommonSubstr(ori_str1, ori_str2):
    def parse_str(in_str):
        split_str = in_str.split('\'')
        res_str = ""
        for i in range(len(split_str)):
            if i%2==0:
                res_str += split_str[i]
        return res_str
    str1 = parse_str(ori_str1).replace(' ', '').strip(':')
    str2 = parse_str(ori_str2).replace(' ', '').strip(':')
    lstr1 = len(str1)
    lstr2 = len(str2)
    # pdb.set_trace()
    if (float(lstr2) / (lstr1+eps) < sth) or float(lstr1) / (lstr2+eps) < sth:
        return 0
    record = [[0 for i in range(lstr2+1)] for j in range(lstr1+1)]
    maxNum = 0 
    p = 0
    for i in range(lstr1):
        for j in range(lstr2):
            if str1[i] == str2[j]:
                record[i+1][j+1] = record[i][j] + 1
                if record[i+1][j+1] > maxNum:
                    maxNum = record[i+1][j+1]
                    p = i + 1
    # return str1[p-maxNum:p], maxNum
    return 2*float(maxNum) / float((len(str1)+len(str2)))

def union_find(nodes, edges):
    father = [0]*len(nodes) 
    for node in nodes:
        father[node] = node
    for edge in edges:  # 标记父节点
        head = edge[0]
        tail = edge[1]
        father[tail] = head

    for node in nodes:
        while True:
            father_of_node = father[node]
            if father_of_node != father[father_of_node]:
                father[node] = father[father_of_node]
            else:
                break
    return father
 
# extract the error content from a string
def parse_err_content(input_err_content):
    err_content = input_err_content.replace('‘', '$').replace('’', '$')
    err_content = err_content.replace('\'', '$')
    split_str = err_content.split('$')
    res_str = ""
    for i in range(len(split_str)):
        if i%2==0:
            res_str += split_str[i]
    return res_str

def parse_compile_error_info(info_str):
    global errid
    global errinfo_errid_dict
    lines = info_str.split('\n')
    err_id_list = []
    for line in lines:
        if 'error' in line:
            temp = line.split('error')[-1]
            errinfo = parse_err_content(temp)
            #errinfo = temp.split('\'')[0] + temp.split('\'')[-1]
            if len(errinfo)<5:
                continue
            if '.h:' in errinfo:
                errinfo = errinfo.split('.h:')[-1]
            if '.c:' in errinfo:
                errinfo = errinfo.split('.c:')[-1]
            if '.cpp:' in errinfo:
                errinfo = errinfo.split('.cpp:')[-1]

            if errinfo not in errinfo_errid_dict.keys():
                errinfo_errid_dict[errinfo] = errid
                err_id_list.append(errid)
                errid += 1
            else:
                err_id_list.append(errinfo_errid_dict[errinfo])
    return list(set(err_id_list))

f_csv = csv.reader(x.replace('\0', '') for x in open('compile_err_4_c++.csv'))
headers = next(f_csv)

res_compile_err = []
index = 0
for row in f_csv:
    if index % 1000 == 0:
        print('parse {}'.format(str(index)), flush=True)
    # if index > 100000:
        # break
    index += 1
    # _, out_put, actual_output, git_url, repo_name, shixun_id = row
    try:
        _, out_put, actual_output, git_url, repo_name, shixun_id, position, _ = row
    except:
        continue
    if 'successfully' in out_put:
        continue
    else:
        current_err_list = parse_compile_error_info(out_put)
        res_compile_err.append( (repo_name, shixun_id, position, current_err_list ) )

err_out = open(data_root + 'compile_err_dict_before_merge.txt', 'w')
for k, v in errinfo_errid_dict.items():
    err_out.write(k + ': ' + str(v) + '\n')
err_out.close()

hashable_compile_err = []
for (repo_name, shixun_id, position, current_err_list) in res_compile_err:
    err_list_str = "["
    for _id in current_err_list:
        err_list_str += str(_id) + ","
    err_list_str += "]"
    hashable_compile_err.append(repo_name.strip('\r').strip('\n') + '\t' + str(shixun_id) + '\t' + str(position) + '\t' + err_list_str + '\n')
# remove repeated items
hashable_compile_err = list(set(hashable_compile_err))
with open(data_root + 'compile_err_res_before_merge.txt', 'w') as fout:
    fout.writelines("".join(hashable_compile_err))

def common_substr_fun(i):
    similarity_vec = np.zeros(len(errinfo_list))
    similarity_vec[i] = 1
    for j in range(i+1, len(errinfo_list)):
        similarity_vec[j] = getSimilarRatioOfCommonSubstr(errinfo_list[i], errinfo_list[j])
    return similarity_vec

# merge highly similar errors in errinfo_errid_dict
errinfo_list = list(errinfo_errid_dict.keys())
print('length of error information list: {}'.format(str(len(errinfo_list))), flush=True)
pool = multiprocessing.Pool(processes=48)
similarity_vec_list = pool.map(common_substr_fun, range( len(errinfo_list)-1 ) )
# for i in range( len(errinfo_list)-1 ):
#    common_substr_fun(i)
# pdb.set_trace()
similarity_matrix = np.array(similarity_vec_list).reshape(-1, len(errinfo_list))
print('max common sub-string finished', flush=True)

similarity_matrix[ similarity_matrix > sth ] = 1
nodes = sorted(list(errinfo_errid_dict.values()))
edges = []
for i in range(similarity_matrix.shape[0]-1):
    for j in range(i+1, similarity_matrix.shape[1]):
        if similarity_matrix[i, j] == 1:
            edges.append([i, j])
nodes_father = union_find(nodes, edges)
print('union-find finished', flush=True)

err_out = open(data_root + 'compile_err_dict_after_merge.txt', 'w')
for father_node in set(nodes_father):
    err_out.write(errinfo_list[father_node] + ': ' + str(father_node) + '\n')
err_out.close()
hashable_compile_err = []
for (repo_name, shixun_id, position, current_err_list) in res_compile_err:
    # update error id lists due to error merge
    merged_err_list = []
    for errid in current_err_list:
        merged_err_list.append(nodes_father[errid])
    merged_err_list = list(set(merged_err_list))
    err_list_str = "["
    for _id in merged_err_list:
        err_list_str += str(_id) + ","
    err_list_str += "]"
    hashable_compile_err.append(repo_name.strip('\r').strip('\n') + '\t' + str(shixun_id) + '\t' + str(position) + '\t' + err_list_str + '\n')
res_out = open(data_root + 'compile_err_res_after_merge.txt', 'w')
# remove repeated items
hashable_compile_err = list(set(hashable_compile_err))
for item in hashable_compile_err:
    res_out.write(item)
res_out.close()


# repoUrl_shixunid_errlist_dict = {}
# # for (repo_name, shixun_id, position, current_err_list) in hashable_compile_err:
# for line in hashable_compile_err:
#     repo_name, shixun_id, position, current_err_list = line.strip('\n').split('\t')
#     current_err_list = [int(v) for v in current_err_list.strip('[').strip(']').split(',')[:-1]]
#     # repoUrl = repo_name.split('-')[0].replace('/', '_') + '_step' + str(position)
#     repoUrl = repo_name.split('-')[0].split('/')[-1]  + '_step' + str(position)
#     if repoUrl not in repoUrl_shixunid_errlist_dict.keys():
#         repoUrl_shixunid_errlist_dict[repoUrl] = (shixun_id, current_err_list)
#     else:
#         old_shixun_id, old_current_err_list = repoUrl_shixunid_errlist_dict[repoUrl]
#         # assert shixun_id == old_shixun_id, 'shixun_id is error!'
#         current_err_list = old_current_err_list + current_err_list
#         repoUrl_shixunid_errlist_dict[repoUrl] = (shixun_id, current_err_list)
# repoUrl_shixunid_errlist_strs = ""
# for repo_url, (shixun_id, err_list) in repoUrl_shixunid_errlist_dict.items():
#     err_list_str = ""
#     for _id in list(set(err_list)):
#         err_list_str += str(_id) + ","
#     _str = repo_url + ' ' + str(shixun_id) + ' ' + err_list_str
#     repoUrl_shixunid_errlist_strs += _str + '\n'
# res_out = open(data_root + 'repoUrl_shixunid_errlist.txt', 'w')
# res_out.write(repoUrl_shixunid_errlist_strs)
# res_out.close()