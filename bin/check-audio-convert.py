import os
from bs4 import BeautifulSoup
import json
import boto3
import logging

BUCKET_NAME = 'blog.tdinvoke.net'
LOCAL_PATH = r'D:\Projects\red rook\sources\s3\blog-tdinvoke-net'
TAG = 'serverless'
PREFIX = 'tags/'+TAG
FILE_PATH = os.path.join(LOCAL_PATH,TAG+'.html')

def main():
    # only sync serverless folder down to local
    # check if local s3 folder exist
    try:
        if not os.path.exists(LOCAL_PATH):
            os.makedirs(LOCAL_PATH)
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(BUCKET_NAME)
        for obj in bucket.objects.filter(Prefix = PREFIX):
            bucket.download_file(obj.key,FILE_PATH)
        logging.info(f'Downloaded s3 bucket {BUCKET_NAME} - {PREFIX} to {FILE_PATH}')
        fp = open(FILE_PATH, encoding="utf8")
        content = fp.read()
        fp.close()
        soup = BeautifulSoup(content,"html.parser")
        posts = []
        for post in soup.findAll("div",{"class":"post-list"}):
            title = post.find("h3",{"class":"article-header"})
            strTitle = title.find("a").getText().strip()
            entry = post.find("div",{"class":"article-entry"})
            figures = entry.findAll("figure")
            for figure in figures:
                figure.clear()
            dictPost = {
                "title" : strTitle,
                "entry" : entry.getText()
            }
            posts.append(dictPost)
        
        jcPost = open("posts.json", encoding="utf8")
        cPost = json.loads(jcPost.read())
        crtPosts = [i for i in posts if i not in cPost]
        rmvPosts = [i for i in cPost if i not in posts]
        
        print(crtPosts)
        print(rmvPosts)
        # upload to s3 bucket of list to remove and add
    except:
        logging.exception(sys.exc_info()[0])


if __name__ == "__main__":
    main()