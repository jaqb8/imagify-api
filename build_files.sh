#   build_files.sh
pip install -r requirements.txt
python3.9 mysql_setup.py
python3.9 manage.py collectstatic