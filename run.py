import argparse
import subprocess
import time
import signal
import os
import basicHttp as bh
import virtualhost as vh
import keepalive as ka
import rangeheader as rh
import parallelhttp as ph

def main():
    parser = argparse.ArgumentParser(description='HTTP tests')
    parser.add_argument('http_server', help='Path to http server file.')
    parser.add_argument('config_file', help='Path to configuration file.')
    args = parser.parse_args()

    try:
        proc = subprocess.Popen(['python', args.http_server, args.config_file])
    except subprocess.CalledProcessError as err:        
        print("Could not start server: {}".format(err))

    print('server started successfully')    
    time.sleep(1)

    total_score = 0
    tests = [(bh.basicHttp, 30), (vh.virtualhost, 20), (ph.parallelhttp, 20), 
            (ka.keepalive, 15), (rh.rangeheader, 15)]
    for test, scaler in tests:
        t = test(args.config_file)
        result = t.run() * scaler
        total_score += result

    print("---------------------\nTotal score is: {}".format(total_score))

    # stop service 
    os.kill(proc.pid, signal.SIGUSR1)

if __name__ == '__main__':
    main()