#### Social Media API  PY_NET

RESTful API for a social media platform.

 #### Features
* Users can register, login and logout in the network using email and password.
* The API allows users to create, update and delete profiles, to retrieve their own profile and view profiles of other users.
* The API allows users to search for users profile by username.
* The API allows users to follow other users,  to view the list of users they are following and the list of users following them
* Users can create new posts, retrieve their own posts and posts of users they are following, etrieve posts by hashtags.
* Users can like and unlike posts, view the list of posts they have liked, add comments to posts and view comments on posts.
* The API allows to schedule Post creation,to select the time to create the Post before creating of it.
* The API allows only users who have a profile to create posts, comment on posts, and like posts. Implemented the ability to see the posts of only the user whose profile is subscribed to.
* The API allows to use the Swagger documentation.


#### Installation
##### Python3 must be already installed.
```
git clone https://github.com/InnaKushnir/py-net/
cd py-net
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```
* Create new SQLite DB & user
* Copy .env.sample -> .env and populate with all required data
##### Create .env file with values:
```
SECRET_KEY = <YOUR_SECRET_KEY>
CELERY_BROKER_URL = <YOUR_CELERY_BROKER_URL>
CELERY_RESULT_BACKEND = <YOUR_CELERY_RESULT_BACKEND>
```
#### Run the following necessary commands
```
python manage.py migrate
```
* Docker is used to run a Redis container that is used as a broker for Celery.
```
docker run -d -p 6379:6379 redis
```
The Celery library is used to schedule tasks and launch workers.
* Starting the Celery worker is done with the command.
```
celery -A py_net worker -l INFO -P solo
```
* The Celery scheduler is configured as follows.
```
celery -A py_net beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
* Create schedule for running sync in DB.
```
python manage.py runserver
```

