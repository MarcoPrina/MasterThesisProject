# MasterThesisProject
## Initial settings:
The program now consists of six folders, plus the [requirements](requirements.txt) file, which contains all the dependencies; [manage](manage.py) which is an indispensable configuration file for Django, and [html_frontend](html_frontend.html) which contains the HTML, javascript, and CSS code to add to the page of Kiroteca and which will be analyzed later.

One folder contains Tint, which as we will see, is used for the grammatical analysis of the text, another contains Mallet, used for the LDA; the third, djangoTesi, contains the project settings files while the backend contains all the code to manage and analyze the data.

The last two folders are not present in the repository because inserted in gitignore, they must be created, one with the name "Credentials" and must contain all the access files used by the program, while the other "Media" containing three subfolders: "Video", “Audio” and “YoutubeCaptions” which will be used as folders to temporarily store data still to be processed, if any files remain inside them it is because they have caused some kind of error and must be analyzed.

To run the program, after downloading it and creating a python virtual environment (tested on python 3.6, 3.7, 3.8) and installing all the dependencies contained in requirements.txt on it, the database must be set. To do this, download and install Postgresql, then add a server named "djangotesi" and as user "admin", these names can be changed in the file [settings](djangoTesi/settings.py) in the DATABASE section; for the password instead, you need to create a "Credentials/db_password.txt" file containing only the latter.

For the other credentials you will need to: create a “Credentials/django_password.txt” file containing a string of about twenty random characters including letters, numbers, and special characters; after which you need to add the "Credentials/vimeo_credential.txt" file containing a token that can be used to authenticate to the Unipv Vimeo account; also you need to enter the credentials to be used to download subtitles from YouTube such as "Credentials/client_secret_youtube.json" and those to access Google Cloud "Credentials/credentials_googleCloud.json". The latter two must be generated from the Google Cloud console by creating a project and granting it permissions to use the youtube API and the Speech-to-text service.

The database and Django credentials are used in the [settings.py](djangoTesi/settings.py) file while the other three in the [parseVideo](backend/AggregateData/parseVideo.py) file in the “AnalyzeVideo” class.

Being both Tint and Mallet written in java it is essential to have an updated version of the same on the machine.

In Google Cloud you need to create a bucket called “video-lessons” in the “europe-west1” region; in the class "Speech2text" I left the method "create_bucket()" which does it automatically, but you have to run it once.

To create the database tables you need to run the commands "python manage.py makemigrations" and "python manage.py migrate", after which you need to create a superuser with "python manage.py createsuperuser" indicate the required data such as username and password that then they will be used to access the server administration panel.

To launch the server just run "python manage.py runserver"

## Program structure:
The program consists of three fundamental parts, the backand server which includes the API and the database, its administrative site, and the page on Kiroteca.

To better understand the various parts of the program and their operation, I proceed with an example of a use case.

First, you need to enter the data of the courses and lessons in the backend, to do this we go to the server/admin site and log in with the data entered when creating the Django superuser.

![Home page](screenshot/Screenshot_2020-10-19 Analisi corsi Unipv.png?raw=true "Title")

