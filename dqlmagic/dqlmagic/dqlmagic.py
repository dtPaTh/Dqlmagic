from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, line_cell_magic)
import requests
import json
import os
from dotenv import load_dotenv 
from datetime import timedelta 
import datetime
import time

@magics_class
class DQLmagic(Magics):

    config_prefix=''

    oauth_url = None
    oauth_clientid = None
    oauth_clientsecret = None
    oauth_scope = None

    grail_apiurl = None
    access_token = None
    
    dt_tenant = None
    dt_app_context = None

    isPlatformAPI = False

    dql_default_query_timespan_minutes = 8*60

    def get_bearer(self):
        
        if (self.oauth_url is None or self.oauth_clientid is None or self.oauth_clientsecret is None or self.oauth_scope is None or self.oauth_scope is None): 
            self.access_token = None
        else:
            payload = "grant_type=client_credentials&client_id="+self.oauth_clientid+"&client_secret="+self.oauth_clientsecret+"&scope="+self.oauth_scope
            
            headers = {'content-type': "application/x-www-form-urlencoded"}
            
            try:
                response = requests.request("POST", self.oauth_url, data=payload, headers=headers)
                res = json.loads(response.text)

                self.access_token = res["access_token"]
            except:
                self.access_token = None

        return self.access_token
    

    @line_magic
    def auth_grail(self, line):

        load_dotenv() 
        
        cfgPrefix = os.getenv('dt_config_prefix')

        if len(line)>0: 
            cfgPrefix=line.strip()

        if cfgPrefix==None: cfgPrefix=''
        else: cfgPrefix+='_'
        self.config_prefix = cfgPrefix
        
        self.oauth_url = os.getenv(self.config_prefix+'dt_oauth_url')
        self.oauth_clientid = os.getenv(self.config_prefix+'dt_oauth_clientid')
        self.oauth_clientsecret = os.getenv(self.config_prefix+'dt_oauth_clientsecret')
        self.oauth_scope = os.getenv(self.config_prefix+'dt_oauth_scope')
        
        if (self.oauth_url is None): return "Missing connection parameter 'dt_oauth_url'"
        if (self.oauth_clientid is None): return "Missing connection parameter 'oauth_clientid'"
        if (self.oauth_clientsecret is None): return "Missing connection parameter 'oauth_clientsecret'"
        if (self.oauth_scope is None): return "Missing connection parameter 'oauth_scope'"

        self.grail_apiurl = os.getenv(self.config_prefix+'grail_apiurl')
        self.dt_tenant = os.getenv(self.config_prefix+"dt_tenant")
        self.dt_app_context = os.getenv(self.config_prefix+"dt_app_context")
        queryTimespan = os.getenv('dql_default_query_timespan_minutes')
        if queryTimespan != None: self.dql_default_query_timespan_minutes = int(queryTimespan)

        if (self.grail_apiurl is None): return "Missing connection parameter 'grail_apiurl'"
        if (self.dt_tenant is None): return "Missing connection parameter 'dt_tenant'"

        
        self.get_bearer()

        if (self.access_token is None):
            return "Couldn't successfully authenticate"
        else:
            return "Successfully authenticated"
    
    @line_magic
    def dql(self, line):
        return self.dql(line,None)

    @cell_magic
    def dql(self, line, cell):
       return self.dql(line, cell)
    
    @line_cell_magic
    def dql(self, line, cell=None):
        res = self.dql_raw(line,cell)
        if res:
            jdata = json.loads(res)
            return jdata["result"]["records"]
        else:
            return None

    @line_magic
    def dql_raw(self, line):
        return self.dql_raw(line,None)

    @cell_magic
    def dql_raw(self, line, cell):
        return self.dql_raw(line, cell)
    
    @line_cell_magic
    def dql_raw(self, line, cell=None):

        if (self.get_bearer() is None):
            return "Not authorized. Log in via '%auth_grail <...>"
        else : 

            dql=line
            if cell is not None:
                dql = cell
        
            queryParams = {
                "enrich":"metric-metadata"
                }
    
            headers = {
                "accept": "application/json",
                "Authorization":"Bearer "+self.access_token,
                "dt-tenant": self.dt_tenant
            }
        
            now = datetime.datetime.utcnow()

            body = {
                "query": dql,
                "defaultTimeframeStart": (now - timedelta(minutes=self.dql_default_query_timespan_minutes)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "defaultTimeframeEnd": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "timezone": "UTC",
                "locale": "en_US",
                "maxResultRecords": 1000,
                "fetchTimeoutSeconds": 60,
                "requestTimeoutMilliseconds": 1000,
                "enablePreview": True,
                "defaultSamplingRatio": 1000,
                "defaultScanLimitGbytes": 250
            }
            
            response = requests.request("POST", self.grail_apiurl+"query:execute", headers=headers, params=queryParams, json=body)
            if(response.status_code == 200):
                return response.text
            elif (response.status_code == 202):
                print ("Start polling query updates..")                
                statusQueryParams = {
                    "request-token": response.json()["requestToken"],
                    "enrich":"metric-metadata"
                    }

                polling_interval = 1

                while True:
                    statusResponse = requests.get(self.grail_apiurl+"query:poll", params=statusQueryParams)

                    if statusResponse.status_code == 200:
                        status_update = statusResponse.json()["state"]
                        if status_update == "SUCCEEDED":
                            return statusResponse.text
                        else: 
                            time.sleep(polling_interval)
                    else: 
                        return '{"result":{"records":[{"ERROR":"Failed to poll query result ('+str(statusResponse.status_code)+')"}]}}'
                    
            else:
                return '{"result":{"records":[{"ERROR":"Failed to execute query ('+str(response.status_code)+')"}]}}'
    
        