#!/usr/bin/python3
# encoding: UTF-8
"""
 this file contains complex pattern checking
 there are 6 different complex patterns
 author:xxx
 date: 2019.11.3
"""

import re
import collections
from utils import *
import simple_pattern

__complex_pattern__ = ['overload_fun', 'local_var', 'global_var', 'array_param', 'static_member_fun', 'polym_class', 'ptr_arith']

def separate_local_global_contents(_str):
    res_index = []
    _stack = []
    for i, letter in enumerate(_str):
        if letter == '{':
            _stack.append(i)
        elif letter == '}':
            if len(_stack) == 1:
                res_index.extend([_stack[0], i])
            _stack.pop()
    local_content = ''
    global_content = ''
    for i in range(int(len(res_index)/2)):
        if i == 0:
            local_content = local_content + _str[0:i]
            global_content = global_content + _str[i:(i+1)]
    return local_content, global_content

# get all function and their content, 
# return a list of 4-tuples: [fc_sidx, fd_eidx, fc_sidx, fc_eidx], record the start and end index of declaration and contents
def get_all_functions(_str, fun_declar):
    fun_contents_list = []
    fun_list = re.finditer(fun_declar, _str)
    if fun_list is None:
        return None
    fun_idxs_list = []
    last_idx = 0
    for _fun in fun_list:
        fd_sidx = _fun.start() # function declaration start index
        fd_eidx = -1 # function declaration end index
        fc_sidx = -1 # function content start index
        fc_eidx = -1 # function content start index
        _stack = []
        for i, letter in enumerate(_str[fd_sidx:]):
            # only function announcement, but declaration
            if letter == ';' and i + last_idx <= fd_eidx + 1:
                fc_eidx = i + fd_sidx
                break
            if letter == '{':
                _stack.append(i)
                if len(_stack) == 1:
                    fd_eidx = i + fd_sidx - 1
                    fc_sidx = i + fd_sidx
            elif letter == '}':
                if len(_stack)>0:
                    _stack.pop()
                if len(_stack) == 0:
                    fc_eidx = i + fd_sidx + 1
                    last_idx = fc_eidx
                    break
                    
        if fc_eidx == -1:
            fc_eidx = len(_str)
        fun_idxs_list.append([fd_sidx, fd_eidx, fc_sidx, fc_eidx])
    return fun_idxs_list

# get all function and their content, 
# return a list of 4-tuples: [fc_sidx, fd_eidx, fc_sidx, fc_eidx], record the start and end index of declaration and contents
def separate_local_global(_str):
    global_list = []
    local_list = []
    _stack = []
    for i, letter in enumerate(_str):
        if letter == '{':
            _stack.append(i)
            if len(_stack) == 1:
                sidx = i
        elif letter == '}':
            if len(_stack) > 0:
                _stack.pop()
            if len(_stack) == 0:
                eidx = i
                local_list.append([sidx, eidx])
    if len(local_list) == 0:
        global_list.append([0, len(_str)-1])
        return _str, ''
    else:
        g_idx = 0
        global_content = ''
        local_content = ''
        for i in range(len(local_list)):
            # global_list.append([g_idx, local_list[i][0]])
            global_content = global_content + _str[g_idx:local_list[i][0]] + ' '
            g_idx = local_list[i][1]+1
            local_content = local_content + _str[local_list[i][0]:local_list[i][1]+1]
        global_list.append([local_list[-1][1], len(_str)-1])
    # concat the multi segment local strs and multi-segment global str
    return  global_content, local_content
    # return global_list, local_list

def isIncludeKeyWord(content, keyword):
    if  -1 != content.find(keyword):
        pattern_str='(^'+keyword+'$)|(^'+keyword+'(\W+).*)|(.*(\W+)'+keyword+'$)|(.*(\W+)'+tmp_keyword+'(\W+).*)'
        m = re.match(r''+pattern_str+'', content)
        if m:
            return 1
    return 0

def check_overload_fun(fun_heads_list):
    fun_name_list = []
    for _str in fun_heads_list:
        if ';' in _str:
            continue
        fun_head = _str.split('(')[0]
        # print(fun_head)
        # fun_name_list.append(_str.split('(')[0].split(' ')[1])
        if len(fun_head.split(' ')) >1:
            fun_name_list.append(_str.split('(')[0].split(' ')[1])
        else :
            fun_name_list.append(fun_head)
    if len(fun_name_list) != len(set(fun_name_list)):
        return 1
    else:
        return 0

def check_local_var(local_content, var_pattern):
    res = var_pattern.search(local_content)
    if res:
        return 1
    else : 
        return 0

def check_global_var(global_content, var_pattern):
    res = var_pattern.search(global_content)
    if res:
        return 1
    else : 
        return 0

def check_array_param(fun_heads_list, fun_contents_list, ptr_var_declar_pattern):
    for _fun_head, _fun_content in zip(fun_heads_list, fun_contents_list):
        # print(_fun_head)
        res = ptr_var_declar_pattern.search(_fun_head)
        if res != None:
            return 1
            match_content = res.group()
            # print(match_content)
            ptr_name = match_content.split('*')[1]
            key_res = isIncludeKeyWord(_fun_content, ptr_name)
            if key_res == 1:
                return 1
    return 0

# def check_static_member_fun(fun_heads_list):
#     for _fun_head in fun_heads_list:
#         print(_fun_head)
#         if 'static' in _fun_head:
#             return 1
#     return 0
def check_static_member_fun(_str):
    static_fun_declar = var_declar + left_brackets + varORarray_declar + repeat_varORarray_declar + right_brackets
    res = re.search(static_fun_declar, _str)
    if res != None:
        return 1
    return 0

def check_polym_class(_str):
    cls_declar = 'class\s*' + cls_name + '\s*:\s*' + 'public\s*'  + cls_name
    polym_pattern = re.compile(cls_declar)
    polym_match_list = re.finditer(polym_pattern, _str)
    if polym_match_list is None:
        return 0
    for _polym in polym_match_list:
        _res = _polym.group()
        _cls_name = _res.split(':')[1].split(' ')[-1]
        if re.search('class \s*' + _cls_name + '\s*\{', _str) != None:
            return 1
    return 0

def check_ptr_arith(_str):
    ptr_declar = type_key + sp + "\*(\*)*" + var_name
    ptr_pattern = re.compile(ptr_declar)
    ptr_match_list = re.finditer(ptr_pattern, _str)
    for _ptr in ptr_match_list:
        _res = _ptr.group()
        _ptr_name = _res.split('*')[-1]
        if re.search(_ptr_name + '(\+\+|\+|--|-)', _str) != None:
            return 1 
    return 0

# check complex patterns
def complex_pattern_checking(_str, pattern_dict):
    global_content, local_content = separate_local_global(_str)
    fun_head_content_idxs = get_all_functions(_str, pattern_dict['function_declaration'])
    fun_heads_list = []
    fun_contents_list = []
    for i in range(len(fun_head_content_idxs)):
        fun_heads_list.append(_str[fun_head_content_idxs[i][0]:fun_head_content_idxs[i][1]])
        fun_contents_list.append(_str[fun_head_content_idxs[i][2]:fun_head_content_idxs[i][3]])
    match_res = collections.OrderedDict()
    # first check the overload function
    match_res['overload_fun'] = check_overload_fun(fun_heads_list)
    match_res['local_var']    = check_local_var(local_content, pattern_dict['variable_declaration1'])
    match_res['global_var']   = check_global_var(global_content, pattern_dict['variable_declaration1'])
    match_res['array_param']  = check_array_param(fun_heads_list, fun_contents_list, pattern_dict['pointer_variable_declaration'])
    match_res['static_member_fun'] = check_static_member_fun(_str)
    match_res['polym_class'] = check_polym_class(_str)
    match_res['ptr_arith'] = check_ptr_arith(_str)
    return match_res

    