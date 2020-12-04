bind = '127.0.0.1:15000'

# 是否后台运行
daemon = False

# 可选，debug，info，warning，error，critical
loglevel = 'error'

# worker数量
workers = 1

# 报错日志的输入路径，'-'表示stderr输出
errorlog = '-'

# access log文件的保存路径，'-'代表stdout输出
accesslog = '-'

# worker处理请求耗时超过次值后重启
timeout = 30

# 配置后无果，待测试
#graceful_timeout = 10
#max_requests_jitter = 10

# worker达到制定请求数后重启
max_requests = 10000

# worker类型配置,默认sync,还可以使用eventlet，gevent，tornado，gthread
worker_class = 'gevent'

