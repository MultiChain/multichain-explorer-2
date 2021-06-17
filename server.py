# -*- coding: utf-8 -*-

# MultiChain Explorer (c) Coin Sciences Ltd

from http.server import BaseHTTPRequestHandler, HTTPServer

import cfg
import pages
import data
import readconf
import utils
from cgi import escape
import urllib.parse

DEFAULT_CONTENT_TYPE = "text/html; charset=utf-8"
DEFAULT_HOMEPAGE = "chains"
DEFAULT_SEARCHPAGE = "search"
DEFAULT_NOTFOUNDPAGE = "notfound"
DEFAULT_CHAINPAGE = "chain"
DEFAULT_DATA_SUFFIX = "-data"

class MCEServer(BaseHTTPRequestHandler):
            
    timeout=2    
    def parse_path(self):
        
        path=self.path
#        print(path)
        self.nparams={}
        parsed_path=path.split('?')
        if len(parsed_path) == 2:
            self.nparams=urllib.parse.parse_qs(parsed_path[-1])
            for k,v in self.nparams.items():
                self.nparams[k]=v[0]

            path=parsed_path[0]
            
#        print(path)
        if path[0] == '/':
            path = path[1:]
        if len(path) > 0:
            if path[-1] == '/':
                path = path[:-1]
        if len(path) == 0:
            path=DEFAULT_HOMEPAGE
        self.params=path.split('/')    
        self.chain=None
        self.handler=None
        self.is_data=False
        
        
        for chain in cfg.chains:
            if (self.chain is None) and (chain.config["path-name"] == self.params[0]):
                self.chain=chain
                self.params=self.params[1:]
                if len(self.params) == 0:
                    self.params.append(DEFAULT_CHAINPAGE)
        if (len(self.params[0])>len(DEFAULT_DATA_SUFFIX)) and (self.params[0][-len(DEFAULT_DATA_SUFFIX):] == DEFAULT_DATA_SUFFIX):
            self.handler=getattr(cfg.data_handler, 'handle_' + self.params[0][0:-len(DEFAULT_DATA_SUFFIX)].replace('-','_'), None)
        else:
            self.handler=getattr(cfg.page_handler, 'handle_' + self.params[0], None)
            
        if self.handler is not None:
            self.params=self.params[1:]
            
                    
            
    def handle_static(self):
        try:
            path="/".join(self.params)
            found = open(cfg.htdocspath + path, "rb")
            import mimetypes
            type, enc = mimetypes.guess_type(path)
            result=found.read()
            found.close();
            return(200, [('Content-type', type or 'text/plain')],result)
        except IOError:
            self.handler=cfg.notfound_handler
            return None
                        
    
    def do_GET(self):
        
        
        self.parse_path()
        
        if self.handler is None:
            content=self.handle_static()
        if self.handler is not None:
            content=self.handler(self.chain,self.params,self.nparams)
        
        if content is None:
            content=cfg.notfound_handler()
            
        self.send_response(content[0])
        for header in content[1]:
            self.send_header(header[0], header[1])
        self.end_headers()
#        print(content[2])
        try:
            result=content[2]
            size=len(result)
            bytes_written=0
            while bytes_written<size:
                bytes_written += self.wfile.write(result[bytes_written:])
        except IOError:
            self.handler=cfg.connerror_handler
            return None
            
    def log_message(self, format, *args):
        return
        
def start():
    
    cfg.htdocspath=utils.full_dir_name(utils.file_dir_name(__file__)) + "/htdocs/"        
    cfg.page_handler=pages.MCEPageHandler()
    cfg.data_handler=data.MCEDataHandler()
    cfg.notfound_handler=getattr(cfg.page_handler, 'handle_notfound', None)
    cfg.connerror_handler=getattr(cfg.page_handler, 'handle_connerror', None)
    
    
    for i in range(0,len(cfg.chains)):
        cfg.chains[i].config["display-name"]=escape(cfg.chains[i].config["name"])
        if cfg.chains[i].config["path-name"] in [DEFAULT_HOMEPAGE,DEFAULT_SEARCHPAGE,DEFAULT_NOTFOUNDPAGE,DEFAULT_CHAINPAGE]:
            cfg.chains[i].config["path-name"] = cfg.chains[i].config["path-name"] + '-' + cfg.chains[i].config["path-ini-name"]
            cfg.chains[i].config["display-name"]=escape(cfg.chains[i].config["name"]) + '(' + escape(cfg.chains[i].config["ini-name"]) + ')'
        else:            
            for j in range(0,i):
                if cfg.chains[i].config["path-name"] == cfg.chains[j].config["path-name"]:
                    cfg.chains[i].config["path-name"] = cfg.chains[i].config["path-name"] + '-' + cfg.chains[i].config["path-ini-name"]
                    cfg.chains[i].config["display-name"]=escape(cfg.chains[i].config["name"]) + '(' + escape(cfg.chains[i].config["ini-name"]) + ')'
                
#        print(cfg.chains[i].config)
        
    hostName = "localhost"
    if not readconf.is_missing(cfg.settings['main'],'host'):
        hostName=cfg.settings['main']['host']
        
    serverPort = int(cfg.settings['main']['port'])
    try:
        webServer = HTTPServer((hostName, serverPort), MCEServer)        
    except Exception as e: 
        message="Failed to start web server: " + str(e)
        utils.log_error(message)
        print(message)
        return False        
            
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    

    webServer.server_close()
    utils.log_write("Web server stopped")
    
    return True
