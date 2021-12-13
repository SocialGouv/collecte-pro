import icapclient

from pprint import pprint

icapclient.set_debug_stdout(True)
icapclient.set_debug_level(10)
conn = icapclient.ICAPConnection('127.0.0.1', 13440)
conn.request('RESPMOD', '/home/almorin/ecollecte/ecollecte/media/taille_ecollecte.PNG', service='icap')
resp = conn.getresponse()
print(resp.icap_status)

#doc : https://pypi.org/project/icapclient3/#description