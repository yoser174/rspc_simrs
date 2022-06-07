import configparser
import logging.config
import datetime
import yaml
import os

with open('order_ws.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

config = configparser.ConfigParser()
config.read('file.txt')

message_id = config.get('MSH','message_dt')

print(message_id)

# TODO: Parsing data xml dari yg dikirim
        logging.info( '* generate MSH')
        controlid = datetime.datetime.now().strftime("%Y%m%d%H%M%S")+str(int(datetime.datetime.now().microsecond / 1000)+1000)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        msh = 'MSH|^~\&|SISPRO||COBASIT3000||'+str(timestamp)+'|LAB1|ORM|'+str(controlid)+'||2.3|||||AL|ANSI|\r'

        for pid_root in root:
            # cek PID Segmen
            if pid_root.tag=='PID':
                logging.info('* dapat segment PID:')
                logging.info(' => "%s"' % pid_root.attrib)
                p_patid = pid_root.attrib['PATID']
                p_namex = pid_root.attrib['NAMEX']
                p_lastname = pid_root.attrib['LASTNAME']
                p_dob = pid_root.attrib['DOB']
                p_sex = pid_root.attrib['SEX']
                p_street = pid_root.attrib['STREET']
                p_city = pid_root.attrib['CITY']
                p_postcode = pid_root.attrib['POSTCODE']
                pid = 'PID|||'+str(p_patid)+'||'+str(p_lastname)+'^^'+str(p_namex)+'^^||'+str(p_dob)+'|'+str(p_sex)+'|||'+str(p_street)+'^'+str(p_city)+'^'+str(p_postcode)+'|||\r'

                # cek ORC
                for orc_root in pid_root:
                    logging.info('* dapat segment ORC:')
                    logging.info(' => "%s"' % orc_root.attrib)
                    o_control = orc_root.attrib['CONTROL']
                    # cek jika replace order, jika replace ganti jadi perintah XO
                    b_replace = False
                    orc_control = ''
                    logging.info('cek apakah control pengulangan untuk control: '+o_control)
                    if str(o_control) == str('RP'):
                        logging.info('* Replacement')
                        b_replace = True
                        o_control = 'XO'
                        orc_control = 'A'
                    
                    o_host_order_id = orc_root.attrib['HOST_ORDER_ID']
                    o_sample_id = orc_root.attrib['SAMPLEID']
                    # Cek sampel ID jika DN atau DM tidak usah buat file HL7
                    b_skip_hl7 = False
                    if str(o_sample_id[-2:]) in ('DN','DM','CX'):
                        logging.info('!!! Skip sample DN atau DM atau CX')
                        b_skip_hl7 = True

                    if (str(o_sample_id[-2:]) in ('CE','CK') and str(o_sample_id[:1]) == 'R'):
                        logging.info('!!! Skip sample CE atau CK dari Rujukan')
                        b_skip_hl7 = True

                    # cek jika tidak ada kode maka block order
                    if len(str(o_sample_id))<= 11:
                        logging.info('!!! Skip sample:%s len <= 11')
                        b_skip_hl7 = True
                    
                    o_orderdate = orc_root.attrib['ORDERDATE']
                    o_withdrawdate = orc_root.attrib['WITHDRAWDATE']
                    o_priority = orc_root.attrib['PRIORITY']
                    o_orderer = orc_root.attrib['ORDERER']
                    o_physician_code = orc_root.attrib['PHYSICIAN_CODE']
                    o_physician_name = orc_root.attrib['PHYSICIAN_NAME']
                    orc = 'ORC|'+str(o_control)+'|'+str(o_host_order_id)+'|||'+orc_control+'|'+str(o_priority)+'|||'+str(o_orderdate)+'|'+str(o_orderer)+'||'+str(o_physician_code)+'^'+str(o_physician_name)+'||||||||||||\r'

                    pre = ''                  
                    pv1 = 'PV1|||||||||||||||||||'+str(pre)+o_host_order_id+'|\r'

                    # cek OBR
                    i = 1
                    obr = ''
                    logging.info('* dapat segment OBR:')
                    for obr_root in orc_root:
                        obr_action = obr_root.attrib['ACTION']
                        # cek jika replace ganti A -> R
                        #if b_replace:
                        #    obr_action = 'R'
                        obr_testcode = obr_root.attrib['TESTCODE']
                        obr_testname = obr_root.attrib['TESTNAME']
                        obr += 'OBR|'+str(i)+'|'+str(o_host_order_id)+'||^^'+str(obr_testcode)+'|'+str(obr_testname)+'||'+str(o_withdrawdate)+'||||'+str(obr_action)+'|||||||||||||||||\r'
                        i+=1
                        
                    
                # generate HL7 Message
                logging.info('* parsing format HL7:')
                hl7 = msh + pid + pv1 + orc  + obr
                logging.info(' => "%s"'% hl7)

                # save to file
                if not b_skip_hl7:
                    orderdir = OUT
                    filename = str(o_control)+'_'+str(o_host_order_id)+'_'+str(o_withdrawdate)+'_'+str(controlid)+'.hl7'
                    logging.info("buat file: [%s\%s] " % (orderdir,filename))
                    # insert log
                    conn = sqlite3.connect(DBFILE)
                    c = conn.cursor()
                    c.execute(" INSERT INTO ws_order (patid,sampleid,status) values ('"+p_patid+"','"+o_host_order_id+"',1) ")
                    conn.commit()
                    conn.close()
                    os.chdir(orderdir)
                    try:
                        fout = open(str(filename),'w')
                        fout.write(hl7)
                        fout.closed
                    except Exception, err:
                        logging.error("Tidak bisa buat file %s " % (str(filename)+'\n'+str(err)))
