import os
import sys
import time

code_root = '/Volumes/Data/sonar_code_repos/'

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
                # print(_sub_sub_path)
        else:
            task_lists.append(os.path.join(_path, _sub_folder))
            # print(os.path.join(_path, _sub_folder))

print(len(task_lists))

sonar_properties_template = ""
sonar_properties_template += "sonar.projectVersion=2\n"
sonar_properties_template += "sonar.sources=.\n"
sonar_properties_template += "sonar.cxx.cppcheck.reportPath=cppcheck-result.xml\n"
sonar_properties_template += "sonar.cxx.includeDirectories=./\n"
sonar_properties_template += "sonar.cxx.cppcheck.path=/usr/local/Cellar/cppcheck/2.1/bin\n"
sonar_properties_template += "sonar.language=c++\n"
sonar_properties_template += "sonar.sourceEncoding=UTF-8\n"

# start using sonar-scanner to scan all tasks
for task in task_lists:
    n1, n2, n3 = task.split('/')[-3:]
    if n2 == 'src':
        key_name = n1 + '_' + n3.strip('\n')
    else:
        key_name = n2 + '_' + n3.strip('\n')
    print(key_name)
    current_properties = ""
    current_properties += "sonar.projectKey={}\n".format(key_name)
    current_properties += "sonar.projectName={}\n".format(key_name) 
    propertity_out = open(os.path.join(task, 'sonar-project.properties'), 'w')
    propertity_out.writelines("".join(current_properties+sonar_properties_template))
    propertity_out.close()
    os.chdir(task)
    # os.system(r'rm cppcheck-result.xml')
    if os.path.exists('cppcheck-result.xml'):
        continue
    os.system(r"cppcheck --enable=all --suppress=missingIncludeSystem --xml ./ 1> cppcheck-result.xml 2>&1")
    # time.sleep()
    os.system("sonar-scanner")
