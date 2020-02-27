regex='^[0-9]+(\.[0-9]{1,2})?$'
key=$(LC_ALL=C tr -dc "a-z0-9%^&*(-=+)" < /dev/urandom | head -c50)
if [[ $1 =~ $regex ]]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install Django
    export SECRET_KEY=$key
    git init
    git remote add origin https://gitlab.lrz.de/fischerp/skriptentool.git
    git fetch
    get reset --hard origin/master
    git clean -d -f
    #python3 manage.py makemigrations
    python3 manage.py migrate
    python3 manage.py createsuperuser
    python3 manage.py create_groups
    python3 manage.py initial_balance "$1"
    python3 manage.py runserver
else echo 'Bitte Anfangskassenstand in der Form $$$$$.$$ angeben'
fi