# -*- coding:utf-8 -*-

import uci
from PIL import Image, ImageDraw, ImageFont
from ftplib import FTP
import os,logging
import time,hashlib
import ConfigParser

font_dict = {'Tibe': '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'}
color_dict = {'白色': '#FFFFFF', '红色': '#FF0000', '黄色': '#FFFF00', '黑色': '#000000', '绿色': '#7FFF00'}
nowtime=time.strftime('%Y-%m-%d',time.localtime(time.time()))
filename='image_uci_Running'+nowtime+'.log'
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(filename)s.%(funcName)s] %(levelname)s %(message)s',
                datefmt='%c',
                filename=filename,
                filemode='w')

class init_Setup:
    def __init__(self):
        self.c = uci.UCI('/etc/config')
        # Image_process
        self.lines = self.c.get('iptsys', 'text2image', 'lines')
        self.separatorStr = self.c.get('iptsys', 'text2image', 'separatorStr')
        #self.authentication = self.c.get('iptsys', 'text2image', 'authentication')
        self.font = self.c.get('iptsys', 'text2image', 'font')
        self.fontsize = self.c.get('iptsys', 'text2image', 'fontsize')
        self.position = self.c.get('iptsys', 'text2image', 'position')
        self.maxsize = self.c.get('iptsys', 'text2image', 'maxsize')
        self.display = self.c.get('iptsys', 'text2image', 'display')
        self.imagequality=self.c.get('iptsys','text2image','imagequality')

        # Interseciton
        '''
        self.intersection = self.c.get('iptsys', 'global', 'intersection')
        self.intersectionId = self.c.get('iptsys', 'global', 'intersectionId')
        self.direction = self.c.get('iptsys', 'global', 'direction')
        self.directionCode = self.c.get('iptsys', 'global', 'directionCode')
        self.latitude = self.c.get('iptsys', 'global', 'latitude')
        self.longitude = self.c.get('iptsys', 'global', 'longitude')
        self.systemId = self.c.get('iptsys', 'global', 'systemId')
        '''
        self.directory = self.c.get('iptsys', 'source', 'directory')
        self.Settings = self.c.get('iptsys', 'source', 'Settings')
        self.RFID = self.c.get('iptsys', 'source', 'RFID')
        self.format=self.c.get('iptsys', 'source','format')
        self.scan_period=self.c.get('iptsys','source','scan_period')

        # FTP
        self.address = self.c.get('iptsys', 'dest', 'address')
        self.dir = self.c.get('iptsys', 'dest', 'directory')
        self.port = self.c.get('iptsys', 'dest', 'port')
        self.username = self.c.get('iptsys', 'dest', 'username')
        self.passwd = self.c.get('iptsys', 'dest', 'password')
        logging.info('Successful read system config !')

class Ftp_handle(init_Setup):
    def __init__(self):
        init_Setup.__init__(self)
        self.ftp = None
        self.bufsize = 1024
        logging.info('FTPlib init succesfully !')

    def initEnv(self):
        try:
            if self.ftp is None:
                self.ftp = FTP()
                self.ftp.connect(self.address, int(self.port))
                self.ftp.login(self.username, self.passwd)
                logging.info(self.address+' connected  successfully')
                logging.info(self.ftp.getwelcome())
        except:
            logging.error('Fail Connect! ')

    def ftpUpload(self, filename, localdir):
        self.ftp.cwd('/home/uftp')
        try:
            self.ftp.cwd('./' + localdir)
            logging.info('Change the FTPdir to '+localdir)
        except:
            logging.info(localdir+' does not exsit. Create now')
            self.ftp.mkd(localdir)
            self.ftp.cwd('./' + localdir)

        file_handle = open(filename, 'rb')
        try:
            file_name = os.path.basename(filename)
            self.ftp.storbinary("STOR " + file_name, file_handle, self.bufsize)
            logging.info('Transform '+file_name+' successfully')
        except:
            logging.error('Fail to Upload '+file_name)


class imagePro(init_Setup):
    def __init__(self):
        init_Setup.__init__(self)
        self.image_process = None
        logging.info('ImageProcess module init successfully.')

    def get_md5(self,file_path):
        try:
            f = open(file_path, 'rb')
            md5_obj = hashlib.md5()
            while True:
                d = f.read(8096)
                if not d:
                    break
                md5_obj.update(d)
            hash_code = md5_obj.hexdigest()
            f.close()
            md5 = str(hash_code).lower()
            logging.info('Get md5 successfully.')
            return md5
        except:
            logging.error('Can not calculate MD5 value.')

    def setText(self, image_file, config):
        map_dict = {'Settings': '设备编号', 'LocalName': '路口', 'LocalDirection': '方向'
            , 'snapTime1': '抓拍时间', 'LaneNo.': '车道号', 'PlateLicenseCode': '号牌号码'
            , 'PlateLicenseColor': '号牌颜色', 'RFID': 'RFID编号', 'MD5': '防伪码'}
        txt=[]
        try:
            if len(self.display)==1:
                txt=[map_dict['Settings']+':'+self.Settings+self.separatorStr
                    +map_dict['RFID']+':'+self.RFID+self.separatorStr
                    +map_dict['MD5']+':'+self.get_md5(image_file)+self.separatorStr,
                     map_dict['LocalName']+':'+config.get('基本信息','LocalName')+self.separatorStr
                    +map_dict['LocalDirection']+':'+config.get('基本信息','LocalDirection')+self.separatorStr
                    +map_dict['LaneNo.']+':'+config.get('基本信息','LaneNo.')+self.separatorStr,
                     map_dict['PlateLicenseCode']+':'+config.get('基本信息','PlateLicenseCode')+self.separatorStr
                    +map_dict['PlateLicenseColor']+':'+config.get('基本信息','PlateLicenseColor')+self.separatorStr
                    +map_dict['snapTime1']+':'+config.get('FullFileName','snapTime1')+self.separatorStr
                     ]
                logging.info('Default setting.')
                return txt
            else:
                for i in range(len(self.display)):
                    map = ''
                    if i==0:continue
                    else:
                        for t in self.display[i].split('-'):
                            if t == 'Settings':
                                map=map+map_dict[t]+':'+self.Settings+self.separatorStr
                            if t == 'RFID':
                                map=map+map_dict[t]+':'+self.RFID+self.separatorStr
                            if t == 'MD5':
                                map=map+map_dict[t]+':'+self.get_md5(image_file)+self.separatorStr
                            if t == 'snapTime1':
                                a=config.get('FullFileName',t)
                                pr_time=a[:4]+'-'+a[4:6]+'-'+a[6:8]+' '+a[8:10]+':'+a[10:12]+':'+a[12:14]+':'+a[14:]
                                map=map+map_dict[t]+':'+pr_time+self.separatorStr
                            elif t=='LocalName'or t=='LocalDirection' or t=='LaneNo.'\
                                    or t=='PlateLicenseColor' or t=='PlateLicenseCode':
                                map=map+map_dict[t]+':'+config.get('基本信息',t)+self.separatorStr
                        txt.append(map)
                logging.info('Read the setting from users.')
                return txt
        except:
            logging.error('Fail to Get text info.')

    def image_Process(self, file_path,config_in,save_path):
        t1=time.time()
        texts=self.setText(file_path,config_in)
        platlocation=config_in.get('基本信息', 'plateRecgRect')

        # use in linux
        imageProcess = Image.open(file_path)
	t2=time.time()
 	logging.info('read'+str(t2-t1))
       
        if int(self.fontsize) > int(self.maxsize):
            logging.info('Font Maxsize is ' + self.maxsize)
            return
        width,height=imageProcess.size

	a,b,c,d=platlocation.split(',')
        a = int(a)
        b = int(b)
        c = int(c)
        x1 = a - 4 * c
        x2 = a + 8 * c
        y1 = b - 6 * c
        y2 = b + 2 * c

        if x1 < 0: x1 = 0
        if y1 < 0: y1 = 0
        if x2 > width: x2 = width
        if y2 > height: y2 = height
	t8=time.time()
	logging.info('draw1 '+str(t8-t2))

        im = ImageDraw.Draw(imageProcess)
	t9=time.time()
	logging.info('draw2 '+str(t9-t8))
        im.rectangle([x1, y1, x2, y2], outline='green')
        #im.rectangle([x1, y1, x2, y2], outline=color_dict['绿色'])
	t5=time.time()
	logging.info('draw '+str(t5-t2))

        font_size = int((height/ 300) * int(self.fontsize))
        space_size = int(font_size / 5)
        text_height = int(int(self.lines) * (font_size + space_size * 2))

        txt = Image.new('RGB', (width, text_height), color_dict['黑色'])
        draw_txt = ImageDraw.Draw(txt)
	
   
        in_font = ImageFont.truetype(font_dict[self.font], font_size)

        for i in range(len(texts)):
            draw_txt.text((10, ((i + 1) * space_size + i * font_size)), texts[i].decode('utf-8'), font=in_font,
                          fill=color_dict['白色'])
	t6=time.time()
	logging.info('make text '+str(t6-t5))
 	target = Image.new('RGB', (width, height + text_height))        
	if self.position == 'bottom':
            target.paste(imageProcess, (0, 0))
            target.paste(txt, (0, height))
        else:
            target.paste(txt, (0, 0))
            target.paste(imageProcess, (0, text_height))
        output_name= 'processed_' + os.path.basename(file_path)
	t3=time.time()
	logging.info('paste '+str(t3-t6))
        target.save(save_path + output_name, format='JPEG', quality=int(self.imagequality))
	t4=time.time()
        logging.info('save '+str(t4-t3))
	logging.info('total '+str(t4-t1))
        a = config_in.get('FullFileName', 'snapTime1')
        pr_time = a[:4] + ':' + a[4:6] + ':' + a[6:8] + '-' + a[8:10] + ':' + a[10:12] + ':' + a[12:14]
        os.system('exiftool -g -Make=utis  -XPComment='+config_in.get('基本信息','PlateLicenseCode')
                  +' -ExposureTime='+a+' -DateTime='+pr_time+' '+save_path + output_name)
        logging.info('Processe the '+os.path.basename(file_path)+' successfully.')
        
        del draw_txt
        del im


    def Process(self, element,new_ftp):
        now=time.time()
        t1, t2, t3, t4, t5, t6, t7, t8, t9 = time.localtime(now)
        dir_path = os.path.dirname(element.rstrip('\n'))
        try:
            config = ConfigParser.ConfigParser()
            config.read(element.rstrip('\n'))
            logging.info('Read '+element.rstrip('\n')+' successfully.')
        except:
            logging.error('Can not read '+element.rstrip('\n')+'.')
        #text = self.setText(config)
        filename=os.path.splitext(element.rstrip('\n'))
        image_file = filename[0]+'.jpg'
        save_path='/home/zjc/output/'
        self.image_Process(image_file, config,save_path)
        output = 'processed_' + os.path.basename(image_file)
        c=time.time()
        logging.info(str(c-now))
        new_ftp.ftpUpload('/home/zjc/output/' + output,
                          str(t1) + str(t2) + str(t3))
        logging.info('Successfully upload.')



def mainFunc():
    obj=imagePro()
    new_ftp=Ftp_handle()
    new_ftp.initEnv()
    no_process_file = []
    while 1:
        a = time.time()
        period=float(obj.scan_period)/60.0
       
        r = os.popen('find '+obj.directory+' -cmin '+str(period)  +' -iname "*.ini"')
        #r = os.popen('find '+obj.directory+'  -iname "*.ini"')
        for i in r.readlines():
            try:
                obj.Process(i,new_ftp)
                #f.write('Find ' + os.path.basename(i.rstrip('\n')) + ' and successfully process'+'\n')
                logging.info('find '+i.rstrip('\n'))
            except:
                logging.error(i.rstrip('\n')+' can not')
                no_process_file.append(i.rstrip(('\n')))

        for t in no_process_file:
            try:
		new_ftp.quit()
		new_ftp.initEnv()
                obj.Process(t,new_ftp)
                logging.info(t.rstrip('\n')+' Try again.')
            except:
                logging.error(t.rstrip('\n')+' can not process.')

        no_process_file=[]
        scan_period=int(obj.scan_period)
        #if scan_period < 5 or scan_period > 60:
         #   logging.error('scan_period is not normal.')
          #  scan_period=30

        b = time.time()
        time.sleep(scan_period - (b - a))

    f.close()

if __name__ == '__main__':
    mainFunc()
