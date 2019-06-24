#!/usr/bin/env python3

import socket
import platform
import re
import time
import subprocess
import requests
import json
import argparse

class TCPConnection:

    def __init__(self, address, port, timeout=3):
        self._address = address
        self._port = port
        self._timeout = timeout

    def tcp_connection(self):

        global failed_connection_attempts

        try:
#            print(self._address, self._port)
            s = socket.create_connection((self._address, self._port), timeout=2)
            content = str(current_time) + " TCP connection to " + str(self._address) + " succeeded on port " + str(self._port)
#            print(content, failed_connection_attempts)
            if failed_connection_attempts > 0:
                requests.post(slack_url, data=json.dumps({"text":"{} TCP connection to {} succeeded on port {}".format(current_time, self._address, self._port)}))
                failed_connection_attempts = 0

        except (socket.timeout, socket.gaierror) as error:
#            print(self._address, self._port)
            failed_connection_attempts += 1
            content = str(current_time) + " TCP connection to " + str(self._address) + " failed on port " + str(self._port)
#            print(content, failed_connection_attempts)
            if failed_connection_attempts >= self._timeout:
                requests.post(slack_url, data=json.dumps({"text":"{} TCP connection to {} failed on port {}".format(current_time, self._address, self._port)}))


class ICMPConnection:

    def __init__(self, address, packet_count=1):
        self._address = address
        self._packet_count = packet_count

    def icmp_connection(self):

        global packet_loss
        global previous_packet_loss

        packet_count_platform_identifier = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', str(packet_count_platform_identifier), str(self._packet_count), self._address]
        output = subprocess.run(command, stdout=subprocess.PIPE)
#        print(current_time,output.returncode)

        if len(ping_results) <= 299:
            ping_results.append(output.returncode)
            packet_loss = (ping_results.count(1)/len(ping_results))*100
#            print(len(ping_results), ping_results, packet_loss)
            if packet_loss > previous_packet_loss:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} increased from {}% to {}%".format(current_time, self._address, previous_packet_loss, packet_loss)}))
            elif packet_loss == previous_packet_loss:
                pass
            else:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} decreased from {}% to {}%".format(current_time, self._address, previous_packet_loss, packet_loss)}))

        elif len(ping_results) == 300:
            ping_results.append(output.returncode)
            del ping_results[0]
            packet_loss = (ping_results.count(1)/len(ping_results))*100
#            print(len(ping_results), ping_results, packet_loss)
            if packet_loss > previous_packet_loss:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} increased from {}% to {}%".format(current_time, self._address, previous_packet_loss, packet_loss)}))
            elif packet_loss == previous_packet_loss:
                pass
            else:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} decreased from {}% to {}%".format(current_time, self._address, previous_packet_loss, packet_loss)}))

        else:
            print("This should NEVER execute. Check what's going on")

        print(packet_loss, previous_packet_loss)
        previous_packet_loss = packet_loss



if __name__ == "__main__":

    failed_connection_attempts = 0
    ping_results = []
    packet_loss = float(0)
    previous_packet_loss = float(0)

    slack_url = "https://hooks.slack.com/services/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"

    parser = argparse.ArgumentParser(description="Test TCP/ICMP connection to a destination")
    parser.add_argument('address', help="Address to be monitored")
    parser.add_argument('--port', dest='port', type=int, default=0, help="TCP port")
    args = parser.parse_args()

#    print(args.address, args.port)
    while True:
        current_time = time.strftime("%a, %Y-%m-%d %H:%M:%S", time.localtime())
        time.sleep(1)
        if args.port > 0:
            TCPConnection(args.address, int(args.port)).tcp_connection()
#            print(args.address, args.port)
        else:
            ICMPConnection(args.address).icmp_connection()
#            print(args.address, args.port)