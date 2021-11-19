import icapclient

from pprint import pprint

conn = icapclient.ICAPConnection('127.0.0.1', 13440)
conn.request('RESPMOD', '/home/img.PNG', service="wwrespmod") #conn.request(arg1="type de service utilisé", arg2="fichier à scanner", arg3="service utilisé")
resp = conn.getresponse()
print(resp.icap_status)

#doc : https://pypi.org/project/icapclient3/#description