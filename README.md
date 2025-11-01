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

### Step 3: initalise database and run program
Enter this code into your command prompt or terminal

```
flask db init
flask db migrate -m 'First initialization of database'
flask db commit
```

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
