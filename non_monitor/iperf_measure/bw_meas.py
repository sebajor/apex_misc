import subprocess
import time
import datetime

###
### This code runs an iperf test between the host machine and another target machine
### the results are written in a file with its timestamps
###
### In this case the idea was to measure the avaiable bandwidth between a raspberry pi
### in cerro chico with sequitor (the idea was to measure the performance of a new
### radiolink)
###
### The code is beign schedule with a cronjob (the next example runs it every 20min)
### */20 * * * * python bw_meas.p   
###


filename_chaj = '/home/apex/scripts/iperf_chaj2seq'
filename_seq = '/home/apex/scripts/iperf_seq2chaj'

cmd_chaj2seq = ['iperf3', '-c', '10.0.3.192']    ##this is the gateway at sequitor
cmd_seq2chaj = ['iperf3', '-c', '10.0.3.192','-R']


def parse_message(out_cmd):
    if(out_cmd.stderr!=b''):
        return None, None
    parse = out_cmd.stdout.decode().split('\n')
    send_result = parse[-5].split(' ')
    send_mbps = get_mbps(send_result)
    recv_result = parse[-4].split(' ')
    recv_mbps = get_mbps(recv_result)
    return send_mbps, recv_mbps

def get_mbps(result):
    units = None
    for i, word in enumerate(result):
        if('bits/sec' in word):
            units = word
            value = float(result[i-1])
    if(units is None):
        return None
    print(units)
    if(units[0] == 'k'):
        return value*1e-3
    elif(units[0] == 'M'):
        return value
    elif(units[0] == 'G'):
        return value*1e3


if __name__ == '__main__':

    out_chaj2seq = subprocess.run(cmd_chaj2seq, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    chaj2seq_send, chaj2seq_recv = parse_message(out_chaj2seq)
    f_chaj2seq = open(filename_chaj, 'a')
    f_chaj2seq.write(str(chaj2seq_send)+','+str(chaj2seq_recv)+','+str(time.time())+'\n')
    f_chaj2seq.close()

    time.sleep(10)

    out_seq2chaj = subprocess.run(cmd_seq2chaj, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    seq2chaj_send, seq2chaj_recv = parse_message(out_seq2chaj)
    f_seq2chaj = open(filename_seq, 'a')
    f_seq2chaj.write(str(seq2chaj_send)+','+str(seq2chaj_recv)+','+str(time.time())+'\n')
    f_seq2chaj.close()




    
