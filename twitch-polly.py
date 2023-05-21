from boto3 import Session
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from configparser import ConfigParser
from urllib.parse import urlparse,parse_qsl
from traceback import format_exc
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from sdnotify import SystemdNotifier
import json

config_path='twitch-polly.ini'

config=ConfigParser()
config['AWS']={
    'aws_access_key_id':'',
    'aws_secret_access_key':'',
    'region_name':''
}
config['network']={
    'IP':'localhost',
    'port':0
}
config['twitch-bot-auth']={
    'url':'',
    'access-tier':1000,
    'ssml-tier':2000,
    'neural-tier':3000
}

config.read(config_path)
config.write(open(config_path,'w'))

polly=Session(**config['AWS']).client('polly')

class TwitchPolly(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if 'authorization' not in self.headers:
                return self.send_error(401)
            url=config['twitch-bot-auth'].get('url')
            headers={'authorization':self.headers['authorization']}
            request=Request(url,headers=headers)
            validation=json.loads(urlopen(request).read().decode())
            print(str(validation))
            if int(validation['tier']) < int(config['twitch-bot-auth']['access-tier']):
                return self.send_error(402,explain='user requires sub teir '+config['twitch-bot-auth'].getint('access-tier'))
            if(self.path.startswith('/synthesize_speech')):
                args=dict(parse_qsl(urlparse(self.path).query))
                if 'Engine' in args and args['engine'] == 'neural' and int(validation['tier']) < int(config['twitch-bot-auth']['neural-tier']):
                    return self.send_error(402,explain='user requires sub teir '+config['twitch-bot-auth'].getint('neural-tier'))
                if 'TextType' in args and args['TextType'] == 'ssml' and int(validation['tier']) < int(config['twitch-bot-auth']['ssml-tier']):
                    return self.send_error(402,explain='user requires sub teir '+config['twitch-bot-auth'].getint('ssml-tier'))
                response=polly.synthesize_speech(**args)
                self.send_response(200)
                self.send_header('content-type', response['ContentType'])
                response=response['AudioStream'].read()
                self.send_header('content-length', len(response))
                self.end_headers()
                return self.wfile.write(response)
            if(self.path.startswith('/describe_voices')):
                args=dict()
                if int(validation['tier']) < int(config['twitch-bot-auth']['neural-tier']):
                    args['Engine']='standard'
                response=polly.describe_voices(**args)
                voices=response['Voices']
                while('NextToken' in response):
                    args['NextToken']=response['NextToken']
                    response=polly.describe_voices(**args)
                    voices+=response['Voices']
                response=json.dumps(voices).encode()
                self.send_response(200)
                self.send_header('content-length', len(response))
                self.end_headers()
                return self.wfile.write(response)
            return self.send_error(404)
        except HTTPError as error:
            response=error.read()
            self.send_response(error.code)
            self.send_header('content-length', len(response))
            self.end_headers()
            return self.wfile.write(response)
        except:
            exc=format_exc()
            self.send_error(500,explain=exc)
            return print(exc)

ip=config['network'].get('IP')
port=config['network'].getint('port')
server=ThreadingHTTPServer((ip,port),TwitchPolly)
port=server.server_port
config['network']['port']=str(port)
config.write(open(config_path,'w'))
SystemdNotifier().notify('READY=1')
server.serve_forever()