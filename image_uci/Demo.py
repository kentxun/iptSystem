
import  image_uci
import  ConfigParser

config_file='/home/zjc/demo/demo.ini'
image_file='/home/zjc/demo/demo.jpg'
save_path='/usr/libexec/webmin/demo/'

if __name__ == '__main__':
    obj=image_uci.imagePro()
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    obj.image_Process(image_file,config,save_path)
    
