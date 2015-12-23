"""Paramiko Interactive Shell"""
import base64
import getpass
import os
import socket
import sys
import traceback
from paramiko.py3compat import input
import paramiko
try:
    import interactive as interactive
except ImportError:
    from . import interactive as interactive

"""Setup Logging"""
paramiko.util.log_to_file('pm.log')
"""Client configuration"""
UseGSSAPI = False            
DoGSSAPIKeyExchange = False 
port = 22

"""Get hostname"""
username = ''
if len(sys.argv) > 1:
    hostname = sys.argv[1]
    if hostname.find('@') >= 0:
        username, hostname = hostname.split('@')
else:
    hostname = input('Hostname: ')
if len(hostname) == 0:
    print('*** Hostname required.')
    sys.exit(1)

if hostname.find(':') >= 0:
    hostname, portstr = hostname.split(':')
    port = int(portstr)

"""Obtain username"""
if username == '':
    default_username = getpass.getuser()
    username = input('Username [%s]: ' % default_username)
    if len(username) == 0:
        username = default_username
if not UseGSSAPI or (not UseGSSAPI and not DoGSSAPIKeyExchange):
    password = getpass.getpass('Password for %s@%s: ' % (username, hostname))

"""Use paramiko to setup ssh2 client connection"""
try:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    print('Connecting to host: %s\n' % (hostname))
    if not UseGSSAPI or (not UseGSSAPI and not DoGSSAPIKeyExchange):
        client.connect(hostname, port, username, password)
    else:
        # SSPI works only with the FQDN of the target host
        hostname = socket.getfqdn(hostname)
        try:
            client.connect(hostname, port, username, gss_auth=UseGSSAPI,
                           gss_kex=DoGSSAPIKeyExchange)
        except Exception:
            password = getpass.getpass('Password for %s@%s: ' % (username, hostname))
            client.connect(hostname, port, username, password)

    chan = client.invoke_shell()
    print(repr(client.get_transport()))
    print('Connected to host: %s\n' % (hostname))
    interactive.interactive_shell(chan)
    chan.close()
    client.close()

except Exception as e:
    print('*** Caught exception: %s: %s' % (e.__class__, e))
    traceback.print_exc()
    try:
        client.close()
    except:
        pass
    sys.exit(1)
