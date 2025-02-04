# fetch-receipt-processor-challenge

This project includes a Dockerized setup, so you don't need to install Python. You must have Docker installed, however.

--- For the end user ---

docker build -t my-django-app .
docker run -p 8000:8000 my-django-app

Now navigate to localhost in a web browser, and paste the URL:

http://127.0.0.1:8000/

If the user wants to access the Django admin, they must create a superuser inside the running container:

docker run -p 8000:8000 -e DJANGO_SUPERUSER_USERNAME=admin \
                           -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
                           -e DJANGO_SUPERUSER_PASSWORD=admin123 \
                           my-django-app python manage.py createsuperuser --noinput

Now, when navigating to the admin console, you can log in with credentials
username: admin
pwd: admin123

--- Additional notes for local development only ---

(local development only) Activate the venv before doing anything.
source ./.virtualenvs/djangodev/Scripts/activate
(You can use powershell, git bash, or another CLI)

To access the admin portal:
<user/email/password for this app>
user: admin
email: admin@example.com
password: FetchReceipt

To run this locally, (no Docker):
Start the server with:
python manage.py runserver

and then navigate to either 

http://127.0.0.1:8000/polls , or
http://127.0.0.1:8000/admin , email/pwd = from above

