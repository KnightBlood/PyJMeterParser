将依赖输出到requirements.txt
pip freeze > requirements.txt

根据requirements.txt下载依赖到指定目录
pip download -d <文件夹路径> -r requirements.txt

离线安装依赖
pip install --no-index --find-links=<文件夹路径> -r requirements.txt