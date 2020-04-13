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
#if use uWsgi
uwsgi config/dev/uwsgi.ini

#if use gunicorn
gunicorn -c config/dev/gunicorn.py gunicon_server:application
```

## package in common use

+ reids  
+ memcache  
+ SQLAlchemy  
+ Jinja2  
+ Flask-Login  
+ uWSGI  
+ Flask-Script  
+ CSRFProtect  

## Links

>**The diffrent of pip and conda**  
>*https://www.anaconda.com/understanding-conda-and-pip/*
