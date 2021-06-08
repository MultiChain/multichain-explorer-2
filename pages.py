# -*- coding: utf-8 -*-

from urllib import parse

DEFAULT_REFRESH=5000
HIDDEN_REFRESH=5000000
DEFAULT_NATIVE_CURRENCY_ID='0-0-0'
DEFAULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->

    <title>%(title)s</title>

    <!-- Bootstrap and Theme -->
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/bootstrap-theme.min.css" rel="stylesheet">
    <link href="/mce.css" rel="stylesheet">

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="/js/jquery-1.11.3.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/js/bootstrap.min.js"></script>
    <script src="/mce.js"></script>

    %(myheader)s
</head>
<body>
    <div class="container">
	<table><tr><td>
	<a title="Back to home" href="/"><img src="/logo32.png" alt="MultiChain logo" /></a>
	</td><td style="padding-left: 10px;" valign="middle">
	<h1>%(h1)s</h1>
	</td></tr></table>
    %(body)s
    
    <br><br>
    <p style="font-size: smaller">
        <span style="font-style: italic">
            Powered by <a href="https://github.com/MultiChain/multichain-explorer-2">MultiChain Explorer 2</a>
        </span>
    </p>
    </div>
</body>
</html>
"""

DEFAULT_TEMPVARS={
            "title":"",
            "myheader":"",
            "h1":"",
            "body":"",
            }

DEFAULT_HEADERS=[("Content-type", "text/html")]
DEFAULT_LOADING_HTML="Loading..."

class MCEPageHandler():

    def __init__(self):
        self.template=DEFAULT_TEMPLATE
        self.template_vars=DEFAULT_TEMPVARS.copy()
        self.headers=DEFAULT_HEADERS
        self.status=200
        self.refresh=DEFAULT_REFRESH
        self.objects=[]        
        
        return 
        
    def standard_response(self,tvars):
        if len(self.objects) > 0:
            refresh_script='<script>var timer=0;function getdata(){'
            for obj in self.objects:
                nparams_str=''
                if 'params' in obj:
                    if len(obj['params']) > 0:
                        nparams=[]    
                        for k,v in obj['params'].items():
                            nparams.append(str(k) + '=' + str(v))
                        nparams_str='?' + '&'.join(nparams)    
                refresh_script += 'const xhr_' + obj['id'] + ' = new XMLHttpRequest();'
                refresh_script += 'xhr_' + obj['id'] + '.open("GET","/' + '/'.join(obj['path']) + nparams_str + '" , true);'
                refresh_script += 'xhr_' + obj['id'] + '.onreadystatechange = function () {'
                refresh_script += 'if (this.readyState == 4 && this.status == 200) {'                
                refresh_script += ' document.getElementById("' + obj['id'] + '").innerHTML=this.responseText;'
                refresh_script += '$(\'[data-toggle="popover"]\').popover();'
#                refresh_script += ' document.getElementById("' + obj['id'] + '").scrollIntoView();'
                refresh_script += '}'                
                refresh_script += '};'
                refresh_script += 'xhr_' + obj['id'] + '.send();'
            refresh_script += '}; '            
#            refresh_script += '$(document).ready(function(){getdata();});</script>'
            refresh_script += '$(document).ready(function(){getdata();timer=setInterval(function(){getdata()}, ' + str(self.refresh) + ');'
            refresh_script += 'if(document.addEventListener) document.addEventListener("visibilitychange", visibilityChanged);});'
            refresh_script += 'function visibilityChanged() {clearTimeout(timer);if(!document.hidden)getdata();timer = setInterval(function(){getdata()}, (document.hidden) ? '+ str(HIDDEN_REFRESH) + ' : ' + str(self.refresh) + ');}</script>'
            tvars['myheader']=refresh_script
#            print(refresh_script)
            
        return (self.status, self.headers, bytes(self.template % tvars,"utf-8"))
        
    def handle_chains(self,chain,params,nparams):
        
        tvars=self.template_vars.copy();
        body = '<div id="chains">' + DEFAULT_LOADING_HTML + '</div>'
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer"
        tvars['h1']="MultiChain Explorer"

# List of divs to be updated and elements of the path which should retreive data for this div
        self.objects=[]
        self.objects.append({"id":"chains","path":["chains-data"]});
        
        
        return self.standard_response(tvars)
        
    def handle_chain(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        body = ''   
        body += '<div class="container">'
        body += '<div class="row">'
        body += '<div class="col-md-6" id="summary">'
        body += '</div>'
        body += '<div class="col-md-6" id="parameters">'
        body += '</div>'
        body += '</div>'
        body += '</div>'
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name']
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>'

# List of divs to be updated and elements of the path which should retreive data for this div
        self.objects=[]
        self.objects.append({"id":"summary","path":[chain.config['path-name'],"chainsummary-data"]});
        self.objects.append({"id":"parameters","path":[chain.config['path-name'],"chainparameters-data"]});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    
    def handle_stream(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        
        body = ''   
        body += '<div id="summary">' + DEFAULT_LOADING_HTML + '</div>'
        body += '<h3>Recently Published <a href="/'+chain.config['path-name']+"/streamitems/"+entity_quoted+'">Items</a></h3>'
        body += '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
#        body += '<h3>Recently Created <a href="/'+chain.config['path-name']+"/streamkeys/"+entity_quoted+'">Keys</a></h3>'
#        body += '<div id="keys">' + DEFAULT_LOADING_HTML + '</div>'
#        body += '<h3><a href="/'+chain.config['path-name']+"/streampublishers/"+entity_quoted+'">Publishers</a></h3>'
#        body += '<div id="publishers">' + DEFAULT_LOADING_HTML + '</div>'
        
        tvars['body']=body          
        title=" - stream: " + entity_name
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + title
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + title

# List of divs to be updated and elements of the path which should retreive data for this div
        self.objects=[]
        self.objects.append({"id":"summary","path":[chain.config['path-name'],"streamsummary-data",entity_quoted]});
        self.objects.append({"id":"items","path":[chain.config['path-name'],"streamitems-data",entity_quoted],"params":{"onlylast":1}});
        self.objects.append({"id":"keys","path":[chain.config['path-name'],"streamkeys-data",entity_quoted],"params":{"onlylast":1}});
        self.objects.append({"id":"publishers","path":[chain.config['path-name'],"streampublishers-data",entity_quoted],"params":{"onlylast":1}});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_asset(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        
        body = ''   
        body += '<div id="summary">' + DEFAULT_LOADING_HTML + '</div>'
        body += '<h3>Latest <a href="/'+chain.config['path-name']+"/assettransactions/"+entity_quoted+'">Transactions</a></h3>'
        body += '<div id="transactions">' + DEFAULT_LOADING_HTML + '</div>'
#        body += '<h3>Asset <a href="/'+chain.config['path-name']+"/assetissues/"+entity_quoted+'">Issues</a></h3>'
#        body += '<div id="issues">' + DEFAULT_LOADING_HTML + '</div>'
#        body += '<h3>Asset <a href="/'+chain.config['path-name']+"/assetholders/"+entity_quoted+'">Holders</a></h3>'
#        body += '<div id="holders">' + DEFAULT_LOADING_HTML + '</div>'
        
        tvars['body']=body          
        title=" - asset: " + entity_name
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + title
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + title

        self.objects=[]
        self.objects.append({"id":"summary","path":[chain.config['path-name'],"assetsummary-data",entity_quoted]});
        self.objects.append({"id":"transactions","path":[chain.config['path-name'],"assettransactions-data",entity_quoted],"params":{"onlylast":1}});
#        self.objects.append({"id":"issues","path":[chain.config['path-name'],"assetissues-data",entity_quoted],"params":{"onlylast":1}});
        self.objects.append({"id":"holders","path":[chain.config['path-name'],"assetholders-data",entity_quoted],"params":{"onlylast":1}});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
    
    def handle_address(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        
        body = ''   
        body += '<div id="summary">' + DEFAULT_LOADING_HTML + '</div>'
        body += '<h3>Latest <a href="/'+chain.config['path-name']+"/addresstransactions/"+str(params[0])+'">Transactions</a></h3>'
        body += '<div id="transactions">' + DEFAULT_LOADING_HTML + '</div>'

#        body = ''   
#        body += '<h3>Permissions</h3>'
#        body += '<div id="permissions">' + DEFAULT_LOADING_HTML + '</div>'
#        body += '<h3>Latest <a href="/'+chain.config['path-name']+"/addresstransactions/"+str(params[0])+'">Transactions</a></h3>'
#        body += '<div id="transactions">' + DEFAULT_LOADING_HTML + '</div>'
#        body += '<h3>Latest <a href="/'+chain.config['path-name']+"/addressassets/"+str(params[0])+'">Asset Balances</a></h3>'
#        body += '<div id="assets">' + DEFAULT_LOADING_HTML + '</div>'
#        body += '<h3><a href="/'+chain.config['path-name']+"/addressstreams/"+str(params[0])+'">Published in Streams</a></h3>'
#        body += '<div id="streams">' + DEFAULT_LOADING_HTML + '</div>'
        
        tvars['body']=body          
        title=" - address: " + str(params[0])
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + title
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + title

        self.objects=[]
        self.objects.append({"id":"summary","path":[chain.config['path-name'],"addresssummary-data",str(params[0])]});
        self.objects.append({"id":"transactions","path":[chain.config['path-name'],"addresstransactions-data",str(params[0])],"params":{"onlylast":1}});
#        self.objects.append({"id":"permissions","path":[chain.config['path-name'],"addresspermissions-data",str(params[0])]});
#        self.objects.append({"id":"transactions","path":[chain.config['path-name'],"addresstransactions-data",str(params[0])],"params":{"onlylast":1}});
#        self.objects.append({"id":"assets","path":[chain.config['path-name'],"addressassets-data",str(params[0])],"params":{"onlylast":1}});
#        self.objects.append({"id":"streams","path":[chain.config['path-name'],"addressstreams-data",str(params[0])],"params":{"onlylast":1}});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
    
    def handle_streams(self,chain,params,nparams):        
        return self.do_entities(chain,params,nparams,"streams","Streams")
        
    def handle_assets(self,chain,params,nparams):        
        return self.do_entities(chain,params,nparams,"assets","Assets")

    def handle_blocks(self,chain,params,nparams):        
        return self.do_entities(chain,params,nparams,"blocks","Blocks")

    def handle_transactions(self,chain,params,nparams):        
        return self.do_entities(chain,params,nparams,"transactions","Transactions")

    def handle_addresses(self,chain,params,nparams):        
        return self.do_entities(chain,params,nparams,"addresses","Addresses")
        
    def handle_peers(self,chain,params,nparams):        
        return self.do_entities(chain,params,nparams,"peers","Peers")

    def handle_miners(self,chain,params,nparams):        
        return self.do_entities(chain,params,nparams,"miners","Miners")
        
    def do_entities(self,chain,params,nparams,name,display_name):
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        body = '<div id="'+name+'">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        title=" - " + display_name
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + title
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + title

# List of divs to be updated and elements of the path which should retreive data for this div
        self.objects=[]
        self.objects.append({"id":name,"path":[chain.config['path-name'],name+"-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
        
    def handle_assetissues(self,chain,params,nparams):
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name + " - asset issues"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/asset/"+entity_quoted+'">' + entity_name + '</a>' + " - asset issues"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"assetissues-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_addressstreams(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + str(params[0]) + " - address streams"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/address/"+str(params[0])+'">' + str(params[0]) + '</a>' + " - address streams"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"addressstreams-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_addressassets(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + str(params[0]) + " - address assets"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/address/"+str(params[0])+'">' + str(params[0]) + '</a>' + " - address assets"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"addressassets-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_addresstransactions(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + str(params[0]) + " - address transactions"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/address/"+str(params[0])+'">' + str(params[0]) + '</a>' + " - address transactions"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"addresstransactions-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_blocktransactions(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - block " + str(params[0]) + " - transactions"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - block " + '<a href="/'+chain.config['path-name']+"/block/"+str(params[0])+'">' + str(params[0]) + '</a>' + " - transactions"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"blocktransactions-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_assettransactions(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name + " - asset transactions"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/asset/"+entity_quoted+'">' + entity_name + '</a>' + " - asset transactions"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"assettransactions-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_assetholders(self,chain,params,nparams):
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars['body']=body          
        if entity_quoted != DEFAULT_NATIVE_CURRENCY_ID:
            tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name + " - asset holders"
            tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/asset/"+entity_quoted+'">' + entity_name + '</a>' + " - asset holders"
        else:
            tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - Native Currency holders"
            tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - Native Currency holders"
            
        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"assetholders-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_assetholdertransactions(self,chain,params,nparams):
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        if entity_quoted != DEFAULT_NATIVE_CURRENCY_ID:
            tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + str(params[1]) + " - transactions for asset " + entity_name
            tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/address/"+str(params[1])+'">' + str(params[1]) + '</a>' + " - transactions for asset " + '<a href="/'+chain.config['path-name']+"/asset/"+entity_quoted+'">' + entity_name + '</a>'
        else:
            tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + str(params[1]) + " - Native Currency transactions"
            tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/address/"+str(params[1])+'">' + str(params[1]) + '</a>' + " - Native Currency transactions"
            
        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"assetholdertransactions-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_globalpermissions(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - global permissions"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - global permissions"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"globalpermissions-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_assetpermissions(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name + " - asset permissions"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/asset/"+entity_quoted+'">' + entity_name + '</a>' + " - asset permissions"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"assetpermissions-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_streampermissions(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name + " - stream permissions"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/stream/"+entity_quoted+'">' + entity_name + '</a>' + " - stream permissions"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"streampermissions-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_streamitems(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name+ " - stream items"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/stream/"+entity_quoted+'">' + entity_name + '</a>' + " - stream items"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"streamitems-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_streamkeys(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name + " - stream keys"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/stream/"+entity_quoted+'">' + entity_name + '</a>' + " - stream keys"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"streamkeys-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_streampublishers(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name + " - stream publishers"
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/stream/"+entity_quoted+'">' + entity_name + '</a>' + " - stream publishers"

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"streampublishers-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_keyitems(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 2:
            return self.handle_notfound(chain,params,nparams)
                    
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
                
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name + " - items for key " + parse.unquote_plus(str(params[1]))
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/stream/"+entity_quoted+'">' + entity_name + '</a>' + " - items for key " + parse.unquote_plus(str(params[1]))

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"keyitems-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_publisheritems(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)
            
        if len(params) < 2:
            return self.handle_notfound(chain,params,nparams)
            
        entity_quoted=params[0]            
        entity_name=parse.unquote_plus(entity_quoted)
        
        tvars=self.template_vars.copy();
        body = '<div id="items">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + " - " + entity_name + " - items published by " + str(params[1])
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - " + '<a href="/'+chain.config['path-name']+"/stream/"+entity_quoted+'">' + entity_name + '</a>' + " - items published by " + '<a href="/'+chain.config['path-name']+"/address/"+str(params[1])+'">' + str(params[1]) + '</a>'

        self.objects=[]
        self.objects.append({"id":"items","path":[chain.config['path-name'],"publisheritems-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_block(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)

        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
#        body = '<div id="block">' + DEFAULT_LOADING_HTML + '</div>'
        
        body = ''   
        body += '<div id="summary">' + DEFAULT_LOADING_HTML + '</div>'
#        body += '<h3><a href="/'+chain.config['path-name']+"/blocktransactions/"+str(params[0])+'">Transactions</a></h3>'
#        body += '<div id="transactions">' + DEFAULT_LOADING_HTML + '</div>'
        
        tvars['body']=body          
        title=" - block " + params[0]
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + title
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + title

# List of divs to be updated and elements of the path which should retreive data for this div
        self.objects=[]
        self.objects.append({"id":"summary","path":[chain.config['path-name'],"blocksummary-data",str(params[0])]});
#        self.objects.append({"id":"transactions","path":[chain.config['path-name'],"blocktransactions-data",str(params[0])],"params":nparams});
#        self.objects.append({"id":"transactions","path":[chain.config['path-name'],"blocktransactions-data",str(params[0])],"params":{"onlylast":1}});
#        self.objects.append({"id":"block","path":[chain.config['path-name'],"block-data"]+params});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_transaction(self,chain,params,nparams):
        
        if chain is None:
            return self.handle_notfound(chain,params,nparams)

        if len(params) < 1:
            return self.handle_notfound(chain,params,nparams)
            
        tvars=self.template_vars.copy();
        body = '<div id="transaction">' + DEFAULT_LOADING_HTML + '</div>'
        
        
        tvars['body']=body          
        title=" - transaction: " + params[0]
        tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + title
        tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + " - transaction: " + params[0][0:10] + "..."

# List of divs to be updated and elements of the path which should retreive data for this div
        self.objects=[]
        self.objects.append({"id":"transaction","path":[chain.config['path-name'],"transaction-data"]+params,"params":nparams});
        
        self.template_vars=tvars
        return self.standard_response(tvars)
        
    def handle_notfound(self,chain=None,params=None,nparams=None):
        tvars=self.template_vars.copy();
        tvars['body']='<p class="error">Sorry, page does not exist on this server.</p>';
        
        title=" - Page Not Found"
        if chain is None:
            tvars['title']="MultiChain Explorer" + title
            tvars['h1']='<a href="/">' + title + '</a>'
        else:
            tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + title
            tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + title
        self.template_vars=tvars
        self.status=404
        self.objects=[]
        return self.standard_response(tvars)
        
    def handle_connerror(self,chain=None,params=None,nparams=None):
        tvars=self.template_vars.copy();
        tvars['body']='<p class="error"></p>';
        title=""
        if chain is None:
            tvars['title']="MultiChain Explorer" + title
            tvars['h1']='<a href="/">' + title + '</a>'
        else:
            tvars['title']="MultiChain Explorer - " + chain.config['display-name'] + title
            tvars['h1']='<a href="/'+chain.config['path-name']+'">' + chain.config['display-name'] + '</a>' + title
        self.template_vars=tvars
        self.status=404
        self.objects=[]
        return self.standard_response(tvars)
        
        
        