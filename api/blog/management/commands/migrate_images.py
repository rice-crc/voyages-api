import os
import requests
import json
from django.core.management.base import BaseCommand, CommandError
from blog.models import *
from filebrowser.sites import site
from filebrowser.base import FileListing,FileObject
from django.core.files.images import ImageFile
import requests
import shutil



class Command(BaseCommand):
	help = 'rebuilds the options flatfiles'
	def handle(self, *args, **options):
		
		def download_sv_img(fpath,baseurl):
			fname=os.path.basename(fpath)
			print(post,fpath,fname)
			r = requests.get(baseurl+fpath_str, stream=True)
			print(r.status_code)
			if r.status_code == 200:
				new_fpath=os.path.join(site.storage.location,site.directory,fname)
				with open(new_fpath, 'wb') as f:
					r.raw.decode_content = True
					shutil.copyfileobj(r.raw, f)
					return new_fpath
			else:
				print("could not find",baseurl+fpath_str)
				return None
		
		
		## for future reference, per https://django-filebrowser.readthedocs.io/en/latest/filelisting.html
		### this will get all the file objects in my uploads folder
# 		def filter_listing(item):
# 			return item.filetype != "Folder"
# 		filelisting=FileListing(site.directory,filter_func=filter_listing)
# 		for f in filelisting.files_walk_filtered():
# 			print(f)
		
		sv_blogimages_baseurl="https://www.slavevoyages.org/documents/"

		posts=Post.objects.all()
		for post in posts:
			post_thumbnail=post.thumbnail
			fpath_str=str(post_thumbnail)
			new_img_fpath=download_sv_img(fpath_str,sv_blogimages_baseurl)
			if new_img_fpath is not None:
				fo=FileObject(new_img_fpath)
				post.thumbnail=fo
				post.save()
				print(post)
# 				post_thumbnail.fpath=new_img_fpath
# 				print(post_thumbnail.__dict__)
			
			
