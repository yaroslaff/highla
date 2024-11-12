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
highla requires one parameter - Load Average threshold. If current Load Average is lower than threshold, it will do nothing. If current Load Average is higher, it will run diagnostic specified in other arguments.

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
