from configparser import ConfigParser
import os.path
from qiniu import Auth,put_file,etag,BucketManager,put_stream,config,put_data

section = "qiniu_teacher"

class UploadImage():
    ''' 用于上传图片到七牛云 '''
    def __init__(self):
        self.access_key,self.secret_key,self.bucket_name,self.url = self.mysql_conf(section)
        self.q = Auth(access_key=self.access_key, secret_key=self.secret_key)

    def uplode(self,image_content,name):
        token = self.q.upload_token(self.bucket_name, name, 3600)
        ret, info = put_data(token, name, image_content)
        img_url = os.path.join(self.url,name)
        return img_url

    def mysql_conf(self,section):
        config = ConfigParser()
        config.read("/home/py/project/homeland/homeland/info.conf")
        if config.has_section(section):
            access_key = config.get(section, "access_key")
            secret_key = config.get(section, "secret_key")
            bucket_name = config.get(section, "bucket_name")
            url = config.get(section, "url")
            return access_key,secret_key,bucket_name,url
        else:
            raise Exception("读取mysql配置出现错误")

if __name__ == '__main__':
    import requests
    upload_image = UploadImage()
    response = requests.get("http://xfjy.chd.edu.cn/_mediafile/zerui24/2018/10/31/2fl0mvf7b5.png")

    upload_image.uplode(response.content,name="test.png")