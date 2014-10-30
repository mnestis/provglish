import json, urllib2

SETTINGS = {
    "host": "localhost",
    "port": 8080
}

class RealisationException(Exception):
    pass

def realise_sentence(spec):
    req = urllib2.Request("http://%s:%s/generateSentence" % (SETTINGS["host"], SETTINGS["port"]),
                          data=json.dumps(spec),
                          headers={"Content-Type":"application/json"})
    try:
        response = urllib2.urlopen(req).read()
    except Exception, e:
        raise RealisationException(e)
    
    return response
