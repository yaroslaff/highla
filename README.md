# HighLA - Run diagnostics on high load average

Highla checks current load average and executes set of built-in diagnostic or external script to collect data at the precise moment when load average is high.

## Install
~~~shell
# pipx way, recommended
pipx install highla

# pip3 way, obsolete. recommended to use in virtualenv
pip3 install highla
~~~

## Empty diag
highla has one required parameter - Load Average threshold. If current Load Average is lower than threshold, it will do nothing. If current Load Average is higher, it will run diagnostic specified in other arguments.

~~~shell
# no diag at all

# trigger if LA over 20 (current LA is lower, so nothing printed)
$ highla 20

# trigger if LA over 3.5 (prints timestamp and current LA on stdout)
$ highla 3.5
# 2024/11/13 01:29:01 LA: 4.05
~~~

## built-in top 
prints top-N CPU-intensive processes

~~~shell
$ highla 1 --top 5
# 2024/11/13 01:35:19 LA: 3.69
## Top CPU usage
  792682 wireguard-vanity-keygen 307.9%
  877929 highla 2.0%
  1192 irq/33-nvidia 1.0%
  2158 asterisk 1.0%
  3767 ibus-portal 1.0%

~~~

## built-in netstat

Prints summary and all connections in ESTABLISHED/CLOSE_WAIT states
~~~shell
$ highla 1 --tcp
# 2024/11/13 01:37:32 LA: 3.47
## TCP connections: ESTABLISHED: 13, LISTEN: 41, CLOSE_WAIT: 8
10.8.1.2:56286 31.9.10.169:443 ESTABLISHED
10.8.1.2:44456 81.217.149.89:443 ESTABLISHED
10.0.0.2:51832 10.0.0.5:1692 CLOSE_WAIT
10.0.0.2:40222 10.0.0.5:1989 CLOSE_WAIT
...
~~~

## bult-in log file comparison
This tool allows to detect log files which grows faster during high-la event. It accepts glob patterns (like `/var/log/apache2/*.log`, more than one pattern are allowed), measure size at first run, waits some time (`-w`, default it 5 seconds), measures size again, and prints 5 most fast growing log files and last line from each of them:

~~~shell
highla 0.01 -w 60 --size /var/log/apache2/*log
...
... waiting 60 seconds before 2nd part of diagnostics
## File sizes difference
/var/log/apache2/example.com-access.log sz: 57312780 diff: 36997
  109.118.67.166 - - [12/Nov/2024:20:13:45 +0100] "GET /favicon.ico HTTP/1.1" 200 10225 "https://www.example.com/" "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1"
/var/log/apache2/example.org-access.log sz: 5176826 diff: 4911
  66.249.76.230 - - [12/Nov/2024:20:13:47 +0100] "GET /myscript.php?ide=2283 HTTP/1.1" 200 12352 "-" "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.116 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
...
~~~
Here we see example.com access log grows faster then others and we see last log line for further manual investigation.

## External diagnostic script (e.g. to see database queries)
If option `--script /path/script.sh` given, highla will execute this script and print it's stdout.

Example script:
~~~
#!/bin/sh
mysql -u root -pNotMyRealPassword -e "SHOW FULL PROCESSLIST"
~~~

Example output:
~~~shell
## User script /root/processlist.sh
+---------+------+-----------+------+---------+------+----------+-----------------------+----------+
| Id      | User | Host      | db   | Command | Time | State    | Info                  | Progress |
+---------+------+-----------+------+---------+------+----------+-----------------------+----------+
| 3568874 | root | localhost | NULL | Query   |    0 | starting | SHOW FULL PROCESSLIST |    0.000 |
+---------+------+-----------+------+---------+------+----------+-----------------------+----------+
~~~

## Running in loop
You can start highla in tmux/screen background session or as systemd service running in loop.

In example below we run it in a loop, checking LA every 60 seconds, if if LA>5, it will print top-10 processes, TCP connections, fast-growing apache log files and custom script which will show mariadb processlist.  Results will be printed to stdout and file highla.log

~~~
highla 5 -s /root/processlist.sh -w 10 --loop 60 --top 10 --tcp --size /var/log/apache2/*log | tee highla.log
~~~
