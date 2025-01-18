'''
Author: 于小丘 海枫
Date: 2024-08-06 09:52:15
LastEditors: Yuerchu admin@yuxiaoqiu.cn
LastEditTime: 2024-12-13 13:13:38
FilePath: /HeyAuth/clean.py
Description: 海枫授权系统 清理脚本 HeyAuth Cleanup Script

此脚本用于清理项目中的 __pycache__ 目录
This script is used to clean up the __pycache__ directory in the project

Copyright (c) 2018-2024 by 于小丘Yuerchu, All Rights Reserved. 
'''
import os
import shutil
import pkg.log as log

# 需要遍历的目录 
# Directory to traverse
root_dir = os.getcwd()

# 遍历目录 
# Traverse the directory

try:
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 跳过虚拟环境目录 
        # Skip the virtual environment directory
        if "venv" in dirnames:
            dirnames.remove("venv")

        if "__pycache__" in dirnames:
            # 获取 __pycache__ 目录的全路径 
            # Get the full path of the __pycache__ directory
            pycache_dir = os.path.join(dirpath, "__pycache__")

            # 删除目录 
            # Remove directory
            shutil.rmtree(pycache_dir)
            log.info(f"Removed: {pycache_dir}")

except Exception as e:
    log.error(f"Error: {e}")

finally:
    log.success("Cleaned up the cache directory")