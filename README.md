# Microstore
## What is this all about?
This project was created to show how to create a mini but functional e-commerce web application using Flask, SQLite and Flask-WTF

## How do I use this?
You can easily download the source code by installing it as a zip and extracting the contents, or downloading the repository using Git
After downloading the application, you need to install some dependencies and create your own venv (virtual environment)

### Step 1: creating your own venv
First, open command prompt (Windiws) or terminal (macOS) in the project folder and entering this code

```
python -m venv venv
```

Now you have successfully created your own venv in the project folder. It should be located at /microblog

### Step 2: Install dependencies and packages
You can do this by using pip. It should be installed with your virtual environment.

Then, enter this code

```
venv\Scripts\activate
pip install flask Flask-Migrate Flask-SQLAlchemy Flask-WTF
```

You will need more than those dependencies so here is the full list
alembic==1.17.1
blinker==1.9.0
certifi==2025.10.5
charset-normalizer==3.4.4
click==8.3.0
colorama==0.4.6
Flask==3.1.2
Flask-Login==0.6.3
Flask-Migrate==4.1.0
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
greenlet==3.2.4
idna==3.11
itsdangerous==2.2.0
Jinja2==3.1.6
Mako==1.3.10
MarkupSafe==3.0.3
python-dotenv==1.2.1
requests==2.32.5
SQLAlchemy==2.0.44
stripe==13.1.1
typing_extensions==4.15.0
urllib3==2.5.0
Werkzeug==3.1.3
WTForms==3.2.1

Alternatively you can just copy and paste this code into your venv (must already be activated with venv\Scripts\activate)
```
pip install alembic==1.17.1 blinker==1.9.0 certifi==2025.10.5 charset-normalizer==3.4.4 click==8.3.0 colorama==0.4.6 Flask==3.1.2 Flask-Login==0.6.3 Flask-Migrate==4.1.0 Flask-SQLAlchemy==3.1.1 Flask-WTF==1.2.2 greenlet==3.2.4 idna==3.11 itsdangerous==2.2.0 Jinja2==3.1.6 Mako==1.3.10 MarkupSafe==3.0.3 python-dotenv==1.2.1 requests==2.32.5 SQLAlchemy==2.0.44 stripe==13.1.1 typing_extensions==4.15.0 urllib3==2.5.0 Werkzeug==3.1.3 WTForms==3.2.1

```

### Step 3: initalise database and run program
Enter this code into your command prompt or terminal

```
flask db init
flask db migrate -m 'First initialization of database'
flask db commit
```

Also do remember to create images in microstore/static/app so that you have a place to put your images for the products
After creating your database, you can finally run the application! 

```
flask run
```
If the program is not in a production server, you can type localhost:5000 and access the webpage


### FAQ
How do I install other dependencies?
- You can do this by using the pip command again
```
pip install <dependencies-names>
```

My pip does not install the dependencies
- Try using python -m before installing
```
python -m pip install <dependencies-names>
```
