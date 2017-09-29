import argparse
import subprocess
import time
import signal
import os
import basicHttp as bh
import virtualhost as vh

# Test = [(basicHttp, 0.3), (virtulhost, 0.2), (parallelHTTP, 0.2), 
#           (keepAlive, .15), (rangeHeader, .15)]

tests = [(bh.basicHttp, 0.3), (vh.virtualhost, 0.2)]

def main():

    parser = argparse.ArgumentParser(description='HTTP tests')
    parser.add_argument('http_server', help='Path to http server file.')
    parser.add_argument('config_file', help='Path to configuration file.')
    args = parser.parse_args()

    print(type(args), args.http_server, args.config_file)

    try:
        proc = subprocess.Popen(['python', args.http_server, args.config_file])
    except subprocess.CalledProcessError as err:        
        print("Could not start server: {}".format(err))

    print('server started successfully')    
    time.sleep(1)

    total_score = 0
    for test, scale in tests:
        t = test(args.config_file)
        result = t.run() * scale
        total_score += result

    print("---------------------\nTotal score is: {}".format(total_score * 100))

    # stop service 
    os.kill(proc.pid, signal.SIGUSR1)

if __name__ == '__main__':
    main()