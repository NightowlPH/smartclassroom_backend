# Smart Classroom Backend

## Description
The Smart Classroom project is a project by Nightowl, the hackerspace at Foundation University, Dumaguete, The Philippines. 
We manage our classroom access control, lights and aircon with smart devices based on the NodeMCU , NodeRED and a python/flask backend. This repository contains the backend software.
For more information see See https://wiki.foundationu.com/nightowl/smart-classroom.

## Installation
* clone the repository
* install mariadb-server pip3-virtualenv virtualenvwrapper and python3
* make a virtual environment with `mkvirtualenv smartclassroom`
* activate your virtual environment with `workon smartclassroom`
* run `pip install -r requirements.txt` to install the required packages

## Setting up the database and configuration
* create a user and password in mysql and a database "smartclassroom" owned by that user
* make a directory "instance" inside the smartclassroom_backend folder
* copy config.py to it
* add a setting to config.py `SQLALCHEMY_URI = "mysql://<user>:<password>@localhost/smartclassroom"
* run `flask db migrate` to update your database
* If this is the first time, you can load a basic database with `python run.py insert_test_data`

## More info

See https://wiki.foundationu.com/nightowl/smart-classroom


