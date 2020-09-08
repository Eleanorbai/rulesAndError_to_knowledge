# rules&errors to knowledge

### 步骤： 

1. python `tools/crawl_standardcode.py`. 
   
   抓取每个 **shixunChallenge** 对应的标准代码，结果保存在 `data/v1/standardcode.csv`;
   
2. python `tools/get_code_fromGit.py`. 

   根据 **repo_path** 拉取学生代码。代码库较多，确保保存的位置磁盘空间足够(需要占用10+GB空间);

3. python `tools/getRules_by_sonarscan.py`. 

   使用 **sonarqube** 软件对学生代码进行扫描，获取代码存在的 **rules**，并将结果以 **txt** 文件格式导出，存放于`data/repoStep_ruleid_all.txt`；**rule_id** 和 ** rules** 的**content** 匹配在文件在 `data/rulesid_to_content.txt`; 

4. python `get_rule_knowledge.py`. 获取 **rules** 到 **knowledge** 的映射。保存在 `data/v1/rulesid_to_knowledge.txt`，第一列记录了规则的编号，规则编号到规则内容的映射记录在 `data/rulesid_to_content.txt` 文件里。需要使用到步骤1的结果 `data/v1/shixunChallenge_knowledge.txt` 和步骤3的结果`data/repoStep_ruleid_all.txt`，结果以矩阵形式(规则数量x知识点数量);

5. 1) python `tools/parse_compileErr.py`. 对 educoder 导出的学生代码编译错误结果 `compile_err_4_c++.csv` 进行处理，获取学生代码出现的所有编译错误。由于 `compile_err_4_c++.csv` 并没有给错误编号，只给出了错误消息字符串，对所有错误消息字符串进行归类合并编号，涉及到的算法是 **最长公共子序列** 和 **并查集**，结果保存在 `data/compile_errors/errid_to_content_after_merge.txt`

   (**错误内容** 和 **error_ID**);       

   2) 获取学生代码和其出现的编译错误 **error IDs list**，结果保存在 `data/compile_errors/compile_err_res_after_merge.txt`;

6. python `get_compileErr_to_knowledge.py`. 获取 **error_ID** 到 **knowledge** 的映射关系，结果保存于 `data/v1/errid_to_knowledge.txt` (第一列为errid，2～177列为 **knowledge** 是否出现)