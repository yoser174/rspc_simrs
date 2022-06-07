import paramiko
import configparser
from base64 import decodebytes


sftp_host = '34.101.175.83'
sftp_user = '3732e197-aa95-4b93-b74d-044e052bbbd9'
sfpt_pass = 'd1181bc7424e698ab0ffe8cabbb94c6c'

paramiko.util.log_to_file("paramiko.log")

# Open a transport
host,port = sftp_host,22
transport = paramiko.Transport((host,port))

# Auth    
username,password = sftp_user,sfpt_pass
transport.connect(None,username,password)

# Go!    
sftp = paramiko.SFTPClient.from_transport(transport)

# Download
filepath = "/hl7/order/3732e197-aa95-4b93-b74d-044e052bbbd9/LAB-20220518-L0003.txt"
localpath = "/home/ubuntu/DEV/LAB-20220511-L0008.txt"
sftp.get(filepath,localpath)

# Upload
#filepath = "/home/foo.jpg"
#localpath = "/home/pony.jpg"
#sftp.put(localpath,filepath)

# Close
if sftp: sftp.close()
if transport: transport.close()


# buka file INI
config = configparser.ConfigParser()
config.read(filepath)

message_id = config.get('MSH','message_dt')

print(message_id)

