import multiprocessing
import os

if not os.path.exists("/tmp/iu/list.json"):
    if not os.path.exists("/tmp/iu"):
        os.mkdir("/tmp/iu")
    with open('/tmp/iu/list.json', 'w') as f:
        f.write("[]")

mem_mb = int(os.getenv("MEM_SIZE", os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 1024 **2))
w = multiprocessing.cpu_count() * 2 + 1
each_mem = 70
need_mem = w * each_mem

while(need_mem > mem_mb):
    w = w-1
    need_mem = w * each_mem

workers = w
worker_class = "flask_sockets.worker"
secure_scheme_headers = {'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}
timeout = 300