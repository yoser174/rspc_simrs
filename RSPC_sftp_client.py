import logging.config
import configparser
import yaml
import datetime
import sys,os,glob
import paramiko
from os import walk
from stat import S_ISDIR, S_ISREG

VERSION = '0.0.1'
OUT_HL7_DIR = '/home/ubuntu/DEV/HL7'
OUT_TXT_DIR = '/home/ubuntu/DEV/TXT'


SFTP_HOST = '34.101.175.83'
SFTP_USER = '3732e197-aa95-4b93-b74d-044e052bbbd9'
SFTP_PASS = 'd1181bc7424e698ab0ffe8cabbb94c6c'

SFTP_ORDER_DIR = '/hl7/order/3732e197-aa95-4b93-b74d-044e052bbbd9'


with open('RSPC_sftp_client.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def txt_to_hl7(filename):
    logging.info('convert to HL7 [%s]' % filename)
    ftxt = configparser.RawConfigParser(allow_no_value=True)
    ftxt.read(filename)
    message_id = ftxt.get('MSH','message_id')
    message_dt = ftxt.get('MSH','message_dt')
    version = ftxt.get('MSH','version')
    order_control = ftxt.get('OBR','order_control')
    ono = ftxt.get('OBR','ono')
    source = ftxt.get('OBR','source')
    priority = ftxt.get('OBR','priority')
    clinician = ftxt.get('OBR','clinician')
    pid = ftxt.get('OBR','pid')
    pname = ftxt.get('OBR','pname')
    ptype = ftxt.get('OBR','ptype')
    birth_dt = ftxt.get('OBR','birth_dt')
    sex = ftxt.get('OBR','sex')
    comment = ftxt.get('OBR','comment')
    order_test_id = ftxt.get('OBR','order_test_id')

    # undefined
    street = ''
    city = ''
    postcode = ''



    logging.info( '* generate MSH')
    controlid = datetime.datetime.now().strftime("%Y%m%d%H%M%S")+str(int(datetime.datetime.now().microsecond / 1000)+1000)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    msg = 'MSH|^~\&|RSPC||INFINITY||'+timestamp+'|LAB1|ORM|'+str(controlid)+'||'+version+'|||||AL|ANSI|\r'    
    msg = msg + 'PID|||'+pid+'||'+pname+'^^'+ptype+'^^||'+birth_dt+'|'+sex+'|||'+street+'^'+city+'^'+postcode+'|||\r'
    msg = msg + 'ORC|'+order_control+'|'+ono+'|||'+ono+'|'+priority+'|||'+message_dt+'|'+source+'||'+clinician+'||||||||||||\r'
    msg = msg + 'NTE|'+comment+'|||||||||||\r'
    msg = msg + 'PV1||||||||||||||||||||\r'

    logging.info(order_test_id)
    tests = order_test_id.split('~')
    logging.info(tests)

    i = 1
    for test in tests:
        msg = msg + 'OBR|'+str(i)+'|'+test+'||^^||||||A|||||||||||||||||\r'
        i += 1

    logging.debug(msg)
    out_filename = controlid+'_'+ono+'.hl7'
    logging.info("buat file: [%s/%s] " % (OUT_HL7_DIR,out_filename))
    try:
        os.chdir(OUT_HL7_DIR)
        fout = open(str(out_filename),'w')
        fout.write(msg)
        fout.closed
        os.remove(filename)
    except Exception as err:
        logging.error("Tidak bisa buat file %s " % (str(filename)+'\n'+str(err)))


def get_ftp_file():
    logging.info('getting ftps files...')
    host,port = SFTP_HOST,22
    transport = paramiko.Transport((host,port))

    # Auth    
    username,password = SFTP_USER,SFTP_PASS
    transport.connect(None,username,password)

    # Go!    
    sftp = paramiko.SFTPClient.from_transport(transport)

    for entry in sftp.listdir_attr(SFTP_ORDER_DIR):
        if entry.filename.endswith('.txt'):
            logging.info(entry.filename)
            # download file
            filepath = SFTP_ORDER_DIR + '/' + entry.filename 
            localpath = OUT_TXT_DIR + '/' + entry.filename
            sftp.get(filepath,localpath)


    # Close
    if sftp: sftp.close()
    if transport: transport.close()

    # looping folder TXT dan convert to HL7
    logging.info('txt -> hl7 [%s]' % OUT_TXT_DIR)
    os.chdir(OUT_TXT_DIR)
    for file in glob.glob("*.txt"):
        logging.info(file)
        txt_to_hl7(OUT_TXT_DIR+'/'+file)

    

if __name__ == "__main__":
    logging.info('version [%s]' % VERSION)
    filename = '/home/ubuntu/DEV/LAB-20220511-L0008.txt'
    get_ftp_file()
    #ini_to_hl7(filename)

