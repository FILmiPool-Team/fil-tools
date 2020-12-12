#!/usr/bin/env python3

from __future__ import print_function
import time
import json
import re
import sys
import subprocess as sp
from datetime import datetime


def print(s, end='\n', file=sys.stdout):
    file.write(s + end)
    file.flush()


fee_cap = "100000000000"


def init_check():
    while True:
        out = sp.getoutput("echo \'{\"foo\": 0}\' | jq .")
        if out != '{\n  "foo": 0\n}':
            print("please install jq command"
                  "eg: apt install jq"
                  "exit!")
            exit(0)

        out = sp.getoutput("timeout 2s lotus sync wait")
        if not out.endswith('Done!'):
            print('lotus sync wait output:')
            print(out)
            continue

        print('check passed')
        return


def loop():
    # vars and definitions
    class MsgInfo(object):
        def __init__(self, t, f, n):
            self.view_time = t
            self.from_addr = f
            self.nonce = n

    msg_dict = dict()

    while True:
        local_pending_msgs_str = sp.getoutput("lotus mpool pending --local | jq -s '.'")
        local_pending_msgs = json.loads(local_pending_msgs_str)

        if len(local_pending_msgs) == 0:
            msg_dict = dict()
            print("no pending message!")
        else:
            # clear msg_dict
            current_ids = set()
            for m in local_pending_msgs:
                msg_id = m['CID']['/']
                current_ids.add(msg_id)
            for msg_id in list(msg_dict):
                if msg_id not in current_ids:
                    del msg_dict[msg_id]

            # add new msgs to msg_dict
            for m in local_pending_msgs:
                msg_id = m['CID']['/']
                if msg_id not in msg_dict:
                    from_addr = m['Message']['From']
                    nonce = m['Message']['Nonce']
                    vt = int(round(time.time()))
                    msg_dict[msg_id] = MsgInfo(vt, from_addr, nonce)

            # dump pending messages
            now = datetime.now()
            ts = now.strftime("%Y/%m/%d-%H:%M:%S")
            print("dump msg_dict:")
            for key in msg_dict:
                print(ts + ' ' + msg_dict[key].from_addr + ' ' + str(msg_dict[key].nonce) + ' ' + str(msg_dict[key].view_time))

            # deal with blocked msgs
            curr_time = int(round(time.time()))
            for info in msg_dict:
                diff = curr_time - msg_dict[info].view_time
                if diff > 40:
                    from_addr = msg_dict[info].from_addr
                    nonce = msg_dict[info].nonce

                    cmd = "lotus mpool replace --gas-feecap " + fee_cap + " --gas-premium 1000 " \
                          + from_addr + " " + str(nonce)
                    print("\nrunning command:\n" + cmd)
                    out = sp.getoutput(cmd)

                    match = re.match(r'ERROR: failed to push new message to mempool: message from (.*) with nonce (.*) '
                                     r'already in mpool, increase GasPremium to (.*) from (.*) to trigger replace by '
                                     r'fee: replace by fee has too low GasPremium', out)
                    if match:
                        print("adjusting gas-premium and try again ...")
                        # m_from = match.group(1)
                        # m_nonce = match.group(2)
                        m_gaspremium = match.group(3)

                        command = "lotus mpool replace --gas-feecap " + fee_cap + " --gas-premium " + \
                                  m_gaspremium + " " + from_addr + " " + str(nonce)
                        print("running command:\n" + command)
                        out2 = sp.getoutput(command)
                        print(out2)
                    else:
                        print(out)

        # sleep
        print("sleep 20 seconds\n")
        # sys.stdout.flush()
        time.sleep(20)


def main():
    init_check()
    loop()


if __name__ == "__main__":
    main()
