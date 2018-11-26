import urllib.parse

def group_query(url,query,*args,**kwargs):
    query = urllib.parse.urlencode(query)
    url = url + "?" + query
    return url