select storage.* 
from storage 
where sha1 = {storage.sha1} and bucket = {storage.bucket};