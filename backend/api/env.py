import os
from dotenv import load_dotenv
from os.path import join, dirname, abspath

current_dir = dirname(abspath(__file__))  
dotenv_path = join(current_dir, '.env')  
load_dotenv(dotenv_path)



class Env:
    DATABASE = os.environ.get("DATABASE")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("MYSQL_ROOT_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME")
    
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALGORITHM = os.environ.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
 
  

        
