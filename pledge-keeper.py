#!/usr/bin/env python3

from __future__ import print_function
import time
import sys
import subprocess as sp


def print(s, end='\n', file=sys.stdout):
    file.write(s + end)
    file.flush()


class SectorInfo(object):
    def __init__(self, id_p, number_p, worker_p, hostname_p, task_p, state_p, time_p):
        self.id = id_p
        self.numer = number_p
        self.worker = worker_p
        self.hostname = hostname_p
        self.task = task_p
        self.state = state_p
        self.time = time_p


def init_check():
    while True:
        return


def loop():
    while True:
        # vars
        ap_num = pc1_num = pc2_num = c2_num = 0

        # get sealing jobs
        out = sp.getoutput("lotus-miner sealing jobs")
        # if not out.startswith("ID"):
        #     pass # todo

        # statistic
        first_line = True
        for line in out.splitlines():
            if first_line:
                first_line = False
                continue
            arr = line.split()
            sector_info = SectorInfo(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6])
            if sector_info.task == "AP":
                ap_num += 1
            if sector_info.task == "PC1":
                pc1_num += 1
            if sector_info.task == "PC2":
                pc2_num += 1
            if sector_info.task == "C2":
                c2_num += 1
        print("AP: " + str(ap_num) + " PC1: " + str(pc1_num) + " PC2: " + str(pc2_num) + " C2: " + str(c2_num))

        # strategy
        out = sp.getoutput("lotus-miner sectors pledge")
        print(out)

        # sleep
        print("sleep 10 minutes\n")
        time.sleep(10*60)


def main():
    init_check()
    loop()


if __name__ == "__main__":
    main()
