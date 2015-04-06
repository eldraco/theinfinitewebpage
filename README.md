# The Infinite Web Server Honeypot

This is a quick honeypot web server that delivers an infinite web page to anyone asking for it. It sends a never ending web page that may fill up the hard disk of the attacker if the download is automatic.

The new version is designed to work as a web LaBrea honyepot. 

The new features are:
- It now uses the twisted libraries, so it supports multiple clients.
- It uses the curses libraries to show the amount of data transfered in real time.

When a client connects you can see its IP, its User-Agent, the connection time and the real live information about the data transfered. When that client disconnects, it prints the total  duration of the connection.

## Usage
Start the infinite web page

`
./TheInfiniteWebsite.py
`

Try it connecting with wget from any other host.

`
wget localhost:8800
`

In a local network is able to send data at ~2.5Mbps


# Modifications
You can change the port where the infinite web site is running by modifying the code.

# Screenshots

![Screenshot1](theinfinitewebsite-2.png "Screenshot1")
