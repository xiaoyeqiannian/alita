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

### 4.command
```
# clean .pyc .pyo
python cmd.py clean

# show all urls
python cmd.py urls

# init app
python cmd.py init

# test
python cmd.py runserver -p 8000
```

### 5.api response
```
# response
{
    code: "0000",
    data: {},
    message: "", # error message
}

# code
"0000" # OK
"2000" # DBERR
"2001" # THIRDERR
"2002" # DATAERR
"2003" # IOERR

"2100" # LOGINERR
"2101" # PARAMERR
"2102" # USERERR
"2103" # ROLEERR
"2104" # PWDERR
"2105" # VERIFYERR

"2200" # REQERR

"2300" # NODATA

"2400" # UNKOWNERR
```

### 6.Feature

+ reids  
+ memcache  
+ SQLAlchemy  
+ casbin  
+ Flask-Login 
+ Flask-JWT 
+ uWSGI  
+ Flask-Script  
+ CSRFProtect  

### 7.Links

