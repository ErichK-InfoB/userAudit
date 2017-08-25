import boto3
import json
import os

class s3ObjHandler:

    s3 = boto3.resource('s3')
    def __init__(self, bucket=None  ):
        if not bucket:
            self.err("Bad bucket var")
        self.s3 = boto3.resource('s3')
        self.bucket = [s3.Bucket(bucket)]

#accept bad inputs or usage and exit
    def err(self, string):
        print(string)
        exit()

    def putObj(self, name, value=self.data):
        if not value:
            self.err("No value to put. Exiting")
        self.bucket.put_object(Key=name, Body=value)

    def getObj(self, name):
        self.bucket.download_file(name, 'tmp.txt')
        with open('tmp.txt', 'w') as f:
            self.data = json.load(f)
    def getJSON(self, jsDat):
        self.data = jsDat
    


