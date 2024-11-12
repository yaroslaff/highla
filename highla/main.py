import argparse
import psutil
import datetime
import subprocess
import glob
import os
from collections import defaultdict

from .version import __version__
import time


args = None
diag1_state = dict()


def file_sizes_by_glob(patterns):
    # Create a dictionary with filename -> size
    d = dict()
    for pattern in patterns:
        d.update({filename: os.path.getsize(filename) for filename in glob.glob(pattern)})
    return d

def diag1():
    # print timestamp 
    print(f"# {datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} LA: {psutil.getloadavg()[0]}")

    for p in psutil.process_iter(['pid', 'name']):
        p.cpu_percent(interval=None)

    time.sleep(1)

    if args.top:
        print("## Top CPU usage")
        for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[:args.top]:
            print(f"  {proc.info['pid']} {proc.info['name']} {proc.info['cpu_percent']}%")

    if args.tcp:
        connections = psutil.net_connections(kind='tcp')
        state_counts = defaultdict(int)
        for conn in connections:
            state_counts[conn.status] += 1
        state_summary = ", ".join(f"{key}: {value}" for key, value in state_counts.items())

        print(f"## TCP connections: {state_summary}")
        for conn in connections:
            if conn.status == 'LISTEN':
                continue

            laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
            print(f"{laddr} {raddr} {conn.status}")


    if args.size:
        diag1_state['sizes'] = file_sizes_by_glob(args.size); 
        for filename, size in diag1_state['sizes'].items():
            print(f"{filename} {size}")

    if args.script:
        print(f"## User script {args.script}")
        subprocess.run(args.script, shell=False)
    
def diag2():
    if args.size:
        print(f"## File sizes diff")
        sizes = file_sizes_by_glob(args.size)
        size_diff = {path: abs(sizes.get(path, 0) - diag1_state['sizes'].get(path, 0)) for path in set(sizes) | set(diag1_state['sizes'])}
        n = 5
        top_n = sorted(size_diff.items(), key=lambda item: item[1], reverse=True)[:n]
        for path, diff in top_n:
            print(f"{path} {diff}")



def one_check():
    # get LA for 1 minute
    la = psutil.getloadavg()[0]

    if la < args.LA:
        return

    diag1()
    
    if args.size:
        print(f"... waiting {args.wait} seconds before 2nd part of diagnostics")
        time.sleep(args.wait)
        diag2()
    
    if args.poll:
        print("---\n")    

def get_args():
    parser = argparse.ArgumentParser(
        description=f"HighLA - run diagnostics on high load average. ver: {__version__}"
    )
    parser.add_argument('LA', type=float, help='Load Average threshold')
    parser.add_argument('-s', '--script', help='Your custom diagnostic script')
    parser.add_argument('-w', '--wait', type=int, default=10, help='Wait time before 2nd diag run')
    parser.add_argument('--poll', type=int, metavar='SEC', help='Poll every N seconds')

    g = parser.add_argument_group('Built-in diagnostics')
    g.add_argument('--top', type=int, help='Report top N processes')
    g.add_argument('--tcp', action='store_true', default=False, help='Report TCP connections')
    g.add_argument('--size', nargs='+', help='File sizes to watch, e.g. /var/log/apache2/*.log')


    return parser.parse_args()

def main():
    global args
    args = get_args()

    if args.poll:
        while True:
            one_check()
            time.sleep(args.poll)            
    else:
        return one_check()