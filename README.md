# Demo Applation of Flask Using Python3.7

## The preliminary

### 1.something need install
```
sudo apt install mysql-server
sudo apt install redis
sudo apt install memcached
```

### 2.create isolated python environments
```
# use virtualenv
pip install -r requirements.txt
# use conda
conda env create -f alita.yaml
```

### 3.start server
```
# use uWsgi
uwsgi config/alita/uwsgi.ini

# use gunicorn
gunicorn -c config/alita/gunicorn.py gunicon_server:application

# directly
python cmd.py runserver -p 15000
```

## Feature

+ reids  
+ memcache  
+ SQLAlchemy  
+ casbin  
+ Flask-Login 
+ Flask-JWT 
+ uWSGI  
+ Flask-Script  
+ CSRFProtect  

## Links

>**The diffrent of pip and conda**  
>*https://www.anaconda.com/understanding-conda-and-pip/*
