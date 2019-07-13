# ReachabilityCheck
Monitor the status of a server (using ICMP) or a service (by checking open TCP port) and send alerts on Slack

This program does the following:
  * Send a Slack notification whenever  
    - TCP connection to a port on a server fails  
    - Packet loss increase/decrease by a certain value
  * Save all the notifications sent to Slack in a file on the local directory  

> This program makes use of Slack's **Incoming Webhooks** feature to post messages. Replace **_slack_url_** variable in the **_\__name__ == \__main___** section of the program with your Incoming Webhook **_\<url>_** to post messages to your slack.  

## ICMP Connection
This method send ICMP packets to a destination to check whether it is alive or dead. By default, ICMP queries are sent every second and the results are stored until the sample size reaches 300. Packet loss is calculated based on how many packets are lost until then (with every query) and if the loss is greater than 5%, a notification is sent to Slack and saved to a file in the same directory. 

**Default Values:**  
```
    Query Interval: 1 Second
    Maximum Sample Size: 300
    Percentage change in packet loss to send a notification: 5%  
```
**Simple Usage:** &nbsp;&nbsp;&nbsp;&nbsp;` python3 ReachabilityCheck.py <URL> `    
**Options:**  
```
    [-s][--size]   Maximum Sample Size  
    [-c][--change] Percentage change in packet loss  
```  
## TCP Connection
This method tries to connect to a TCP port on a server. By default, it tries every second and sends a notification to Slack and saves it to a file if there were 3 **consecutive** failures. Failure count will reset upon success.

**Default Values:**  
```
    Query Interval: 1 Second
    Consecutive Timeouts allowed before sending notification: 3  
```
**Simple Usage:** &nbsp;&nbsp;&nbsp;&nbsp;` python3 ReachabilityCheck.py <URL> --port [PORT] `    
**Options:**  
```
    [-ct][--ctimeout]   Maximum consecutive timeouts allowed
```  

Finally, you can always do ` python3 ReachabilityCheck.py --help ` to check usage and all available options
