# encoding: UTF-8
"""
 this file contains all regex rules used for matching
 author:xxx
 date: 2019.10.24
"""
import re
import collections

num_ch = "[0-9]"
type_key = "(int|float|bool|char|double|void|wchar_t)"
acemodi_key = "(public|private|protected)"
var_name = "[a-zA-Z_][a-zA-Z0-9_]*"
member_name = "[a-z][a-zA-Z0-9_]*"
cls_name = "[A-Z][A-Za-z0-9_]*"
sp_line = "\n\n*"
sp = "\s*"
left_square = "\["
right_square = "\]"
left_brackets = "\("
right_brackets = "\)"
left_curbra = "\{"  # curba: curly brackets
right_curbra = "\}"
left_brackets_comma = "(,"
right_brackets_star = ")*"
num_key = "[0-9]*"
title_def = ";"
colon = ":"
or_def = '|'
none_def = ''

# array1d_key = var_name + left_square + num_key + right_square
# arraynd_key = array1d_key + '(\[[0-9]*\])*'
# array_key   = '(' + array1d_key + or_def + arraynd_key + ')'
# varORarray_key = '(' + var_name + or_def + array1d_key + or_def + arraynd_key + ')'
# repeat_varORarray_key = '(' + ',\s*' + varORarray_key + ')*'

# var_declar = type_key + sp + var_name
# array1d_declar = var_declar + left_square + num_key + right_square
# arraynd_declar = array1d_declar + '(\[[0-9]*\])*'
# array_declar   = '(' + array1d_declar + or_def + arraynd_declar + ')'
# varORarray_declar = '(' + var_declar + or_def + array1d_declar + or_def + arraynd_declar + ')'
# repeat_varORarray_declar = '(' + ',\s*' + varORarray_declar + ')*'


ptr_declar = type_key + sp + '\*(\*)*' + var_name
array1d_key = var_name + left_square + num_key + right_square
arraynd_key = array1d_key + '(\[[0-9]*\])*'
array_key   = '(' + array1d_key + or_def + arraynd_key + or_def + ptr_declar + ')'
varORarray_key = '(' + var_name + or_def + array1d_key + or_def + arraynd_key + or_def + ptr_declar + ')'
repeat_varORarray_key = '(' + ',\s*' + varORarray_key + ')*'

var_declar = type_key + sp + var_name
array1d_declar = var_declar + left_square + num_key + right_square
arraynd_declar = array1d_declar + '(\[[0-9]*\])*'
array_declar   = '(' + array1d_declar + or_def + arraynd_declar + or_def + ptr_declar + ')'
varORarray_declar = '(' + var_declar + or_def + array1d_declar + or_def + arraynd_declar + or_def + ptr_declar + ')'
repeat_varORarray_declar = '(' + ',\s*' + varORarray_declar + ')*'

pattern_intro1 = re.compile("//")
pattern_intro2 = re.compile("/\*\S*\*/")


def check_pattern(_str, pattern, rule_name):
    res = pattern.search(_str)
    if res:
        return 1
    else : 
        return 0

def rule_match(_str, pattern_dict):
    matched_result_dict = collections.OrderedDict()
    for key, value in pattern_dict.items():
        matched_result_dict[key] = check_pattern(_str, value, key)
    return matched_result_dict

def remove_annotation(_str):
    content_array = _str.split("\n")
    tmpstr = ''
    for content_str in content_array:
        content_str = content_str.strip(" ")
        intro = pattern_intro1.match(content_str)
        if intro is not None:
            if intro.pos == 0:
                continue
            else:
                content_str = content_str[:intro.pos]
        if len(content_str) == 0:
            continue
        tmpstr = tmpstr+content_str
    reslist = pattern_intro2.findall(tmpstr)
    if len(reslist) != 0:
        for res in reslist:
            tmpstr = tmpstr.replace(res,"")
    return tmpstr