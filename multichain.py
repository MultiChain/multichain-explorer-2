# -*- coding: utf-8 -*-

# MultiChain Explorer 2 (c) Coin Sciences Ltd
# All rights reserved under BSD 3-clause license

import cfg
import utils
import readconf
import base64 
#import requests
from urllib import request
from urllib import parse
import urllib
import json
from collections import OrderedDict
import time

def multichain_init_rpc_parameters(chain):
    
    if readconf.is_missing(cfg.settings[chain],'datadir'):
        cfg.settings[chain]["datadir"]="~/.multichain"
        
    datadir=cfg.settings[chain]["datadir"] + "/" + cfg.settings[chain]["name"] + "/"
    datadir=utils.full_dir_name(datadir)
        
    if readconf.is_missing(cfg.settings[chain],'rpcport'):
        params_file=datadir + "params.dat"
        if not utils.file_exists(params_file):
            utils.print_error("Couldn't find MultiChain directory " + datadir)            
            return False
        params=readconf.read_plain_config_file(params_file)         
        if params['default-rpc-port'] is None:
            utils.print_error("Couldn't find default-rpc-port in " + params_file)            
            return False
        cfg.settings[chain]["rpcport"] = params['default-rpc-port'].split("#", 1)[0].rstrip()
        
    conf_file=datadir + "multichain.conf"     
    if readconf.is_missing(cfg.settings[chain],'rpcuser') or readconf.is_missing(cfg.settings[chain],'rpcpassword'):   
        
        if not utils.file_exists(conf_file):
            utils.print_error("Couldn't find configuration file " + conf_file)            
            return False
                
        conf=readconf.read_plain_config_file(conf_file)    

        if readconf.is_missing(cfg.settings[chain],'rpcuser'):            
            if readconf.is_missing(conf,'rpcuser'):
                utils.print_error("Couldn't find rpcuser in " + conf_file)            
                return False
            cfg.settings[chain]['rpcuser']=conf['rpcuser']
            
        if readconf.is_missing(cfg.settings[chain],'rpcpassword'):            
            if readconf.is_missing(conf,'rpcpassword'):
                utils.print_error("Couldn't find rpcpassword in " + conf_file)            
                return False
            cfg.settings[chain]['rpcpassword']=conf['rpcpassword']
            
        if not readconf.is_missing(conf,'rpcport'):
            cfg.settings[chain]['rpcport']=conf['rpcport']            
    
    return True


class MCEChain:

    def __init__(self, name):
        self.name=name
        self.config = cfg.settings[name].copy()
        self.config["ini-name"]=name
        self.config["path-name"]=parse.quote_plus(self.config['name'])
        self.config["path-ini-name"]=parse.quote_plus(name)

    def initialize(self):
        
        url="http://127.0.0.1"
        if not readconf.is_missing(self.config,'rpchost'):
            url=self.config['rpchost']
        
        url=url + ":" + self.config["rpcport"]
        userpass64 = base64.b64encode((self.config['rpcuser'] + ":" + self.config['rpcpassword']).encode("ascii")).decode("ascii")

        headers={
            "Content-Type" : "application/json",
            "Connection" : "close",
            "Authorization" : "Basic " + userpass64
            }
        
        self.config['multichain-url']=url
        self.config['multichain-headers']=headers
        
#        print(self.config)        
        
        return True            

    def request(self, method, params=[]):
        
        payload=json.dumps({
            "id" : int(round(time.time() * 1000)),
            "method" : method,
            "params" : params
        })
        
        headers=self.config['multichain-headers'].copy()
        headers["Content-Length"] = str(len(payload))
        
        try:
    #        req = requests.post(cfg.multichain_url, data=payload, headers=headers)
        
            data = str(payload)
            data = data.encode('utf-8')
            ureq =  request.Request(self.config['multichain-url'], data=data)
            for header,value in headers.items():
                ureq.add_header(header, value)
            req = request.urlopen(ureq)
        except urllib.error.HTTPError as e:
            resp=e.read()      
            req_json=json.loads(resp.decode('utf-8'))
            if req_json['error'] is not None:
                req_json['error']="Error " + str(req_json['error'] ['code']) + ": " + req_json['error']['message']
            return req_json
        except urllib.error.URLError as e:
            error_str="MultiChain is not running: " + str(e.reason)
            req_json={
                'result': None,
                'error' : error_str,
                'connection-error' : True
            }
            return req_json            
            
#        except Exception as error:
#            print("C")
#            error_str="MultiChain is not running: " + str(error)
#            print(str(error))
#            req_json={
#                'result': None,
#                'error' : error_str,
#                'connection-error' : True
#            }
#            utils.print_error(error_str)
#            return req_json
            
        resp=req.read()      
#        req_json=json.loads(resp.decode('utf-8'))
        req_json=json.loads(resp.decode('utf-8'),object_pairs_hook=OrderedDict)
        
        if req_json is None:
            error_str="MultiChain connection error"
            req_json={
                'result': None,
                'error' : error_str,
                'connection-error' : True
            }
#            utils.print_error(error_str)
            
        return req_json
        
