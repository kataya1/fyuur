import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
dialect = 'postgres'

username = 'postgres'

password = 'postgres'

host = 'localhost'

port = '5432'

db_name = 'fyyur'

#if there is no password there won't be ':' in the link
if password:
    password = ':' + password

#  IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'{dialect}://{username}{password}@{host}:{port}/{db_name}'
