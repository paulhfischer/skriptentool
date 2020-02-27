git fetch
git reset --hard origin/master
git clean -d -f
python3 manage.py makemigrations
python3 manage.py migrate