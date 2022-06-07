import logging.config
import configparser
import yaml

VERSION = '0.0.1'



with open('RSPC_sftp_result.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def hl7_to_ini(filename):
    logging.info('proses file [%s]...' % filename)

    with open(filename) as f:
        lines = f.readlines()
        logging.debug(lines)
        for line in lines:
            logging.debug(line[:3])
            if line[:3] == 'MSH':
                logging.debug(line)
                message_id = line.split('|')[9]
                message_dt = line.split('|')[6]
                version = line.split('|')[11]
            if line[:3] == 'PID':
                logging.debug(line)
                pid = line.split('|')[3]
                pname = line.split('|')[5]
                birth_dt = line.split('|')[7]


    
    msg = '[MSH]\r\n'
    msg += 'message_id='+message_id+'\r\n'
    msg += 'message_dt='+message_dt+'\r\n'
    msg += 'version='+version+'\r\n'
    msg += '[OBR]\r\n'
    msg += 'pid='+pid+'\r\n'
    msg += 'apid=\r\n'
    msg += 'pname='+pname+'\r\n'
    msg += 'title=\r\n'
    msg += 'ptype=\r\n'
    msg += 'birth_dt='+birth_dt+'\r\n'
    msg += 'pid='+pid+'\r\n'
    msg += 'pid='+pid+'\r\n'
    msg += 'pid='+pid+'\r\n'
    msg += 'pid='+pid+'\r\n'
    


    logging.info(msg)



if __name__ == "__main__":
    logging.info('version [%s]' % VERSION)
    hl7_to_ini('/home/ubuntu/DEV/RSPC/202206071232110064088.hl7')