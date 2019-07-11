#!/usr/bin/env python3

import socket
import platform
import time
import subprocess
import requests
import json
import argparse


class TCPConnection:
    """
    Checks for the availability of a server port and sends a Slack notification

    Args:
        address: IP address of the server
        port: TCP port that you want to monitor
        timeout: Number of consecutive timeouts to occur before sending a Slack notification (Default: 3)

    Description:
        This module checks whether a particular port on a server is open every second, waits for atmost 2 seconds to
        establish a TCP connection and will timeout if connection can't be established
    """

    def __init__(self, address, port, timeout):
        self._address = address
        self._port = port
        self._timeout = timeout

    def tcp_connection(self):

        global failed_connection_attempts

        try:
            socket.create_connection((self._address, self._port), timeout=2)
            content = str(current_time) + " TCP connection to " + str(self._address) + " succeeded on port " + \
                      str(self._port)
            print(content, failed_connection_attempts)
            if failed_connection_attempts > 0:
                requests.post(slack_url, data=json.dumps({"text": content}))
                failed_connection_attempts = 0

        except (socket.timeout, socket.gaierror):
            failed_connection_attempts += 1
            content = str(current_time) + " TCP connection to " + str(self._address) + " failed on port " + \
                      str(self._port)
            print(content, failed_connection_attempts)
            if failed_connection_attempts >= self._timeout:
                requests.post(slack_url, data=json.dumps({"text": content}))


class ICMPConnection:
    """
    Checks for the availability of a server and sends a Slack notification

    Args:
        address: IP address of the server
        change: Percentage change in packet loss for sending Slack notification (Default=5%)
        sample_size: Sample size for calculating packet loss (in seconds) (Default=300)

    Description:
        This module send ICMP query message every second, calculates packet loss from a sample of 300 responses (by
        default) and send Slack notification in realtime if the packet loss increase/decrease by 5% (by default)
    """

    def __init__(self, address, change, sample_size):
        self._address = address
        self._change = change
        self._sample_size = sample_size

    def icmp_connection(self):

        global packet_loss
        global notify_packet_loss

        platform_identifier = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', str(platform_identifier), "1", self._address]
        output = subprocess.run(command, stdout=subprocess.PIPE)

        if len(ping_results) <= self._sample_size-1:
            ping_results.append(output.returncode)
            packet_loss = (ping_results.count(1)/len(ping_results))*100
            print(len(ping_results), ping_results)
            print(packet_loss, notify_packet_loss)
            if packet_loss - notify_packet_loss > self._change:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} increased from {:.2f}% to "
                                                                  "{:.2f}%".format(current_time, self._address,
                                                                                   notify_packet_loss, packet_loss)}))
                notify_packet_loss = packet_loss
            elif notify_packet_loss - packet_loss > self._change:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} decreased from {:.2f}% to "
                                                                  "{:.2f}%".format(current_time, self._address,
                                                                                   notify_packet_loss, packet_loss)}))
                notify_packet_loss = packet_loss
            elif packet_loss == 100.0:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} increased from {:.2f}% to "
                                                                  "{:.2f}%".format(current_time, self._address,
                                                                                   notify_packet_loss, packet_loss)}))
                notify_packet_loss = packet_loss
            else:
                pass

        elif len(ping_results) == self._sample_size:
            ping_results.append(output.returncode)
            del ping_results[0]
            packet_loss = (ping_results.count(1)/len(ping_results))*100
            if packet_loss - notify_packet_loss > self._change:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} increased from {:.2f}% to "
                                                                  "{:.2f}%".format(current_time, self._address,
                                                                                   notify_packet_loss, packet_loss)}))
                notify_packet_loss = packet_loss
            elif notify_packet_loss - packet_loss > self._change:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} decreased from {:.2f}% to "
                                                                  "{:.2f}%".format(current_time, self._address,
                                                                                   notify_packet_loss, packet_loss)}))
                notify_packet_loss = packet_loss
            elif packet_loss == 100.0:
                requests.post(slack_url, data=json.dumps({"text": "{} Packet loss for {} increased from {:.2f}% to "
                                                                  "{:.2f}%".format(current_time, self._address,
                                                                                   notify_packet_loss, packet_loss)}))
                notify_packet_loss = packet_loss
            else:
                pass

        else:
            print("This should NEVER execute. Check what's going on")


if __name__ == "__main__":

    failed_connection_attempts = 0
    ping_results = []
    packet_loss = float(0)
    notify_packet_loss = float(0)

    slack_url = "https://hooks.slack.com/services/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"

    parser = argparse.ArgumentParser(description="Test TCP/ICMP connection to a destination")
    parser.add_argument('address', help="IP Address")
    parser.add_argument('--port', dest='port', type=int, default=0, help="TCP port")
    parser.add_argument('--timeout', dest='timeout', type=int, default=3, help="Minimum number of consecutive TCP "
                                                                               "timeouts before sending a notification "
                                                                               "(Default=3)")
    parser.add_argument('--change', dest='change', type=int, default=5, help="Percentage change in packet loss for "
                                                                             "sending notification (Default=5)")
    parser.add_argument('--ssize', dest='sample_size', type=int, default=300, help="Sample size for calculating packet "
                                                                                   "loss in seconds (Default=300)")
    args = parser.parse_args()

    while True:
        current_time = time.strftime("%a, %Y-%m-%d %H:%M:%S", time.localtime())
        time.sleep(1)
        if args.port > 0:
            TCPConnection(args.address, args.port, args.timeout).tcp_connection()
        else:
            ICMPConnection(args.address, args.change, args.sample_size).icmp_connection()
