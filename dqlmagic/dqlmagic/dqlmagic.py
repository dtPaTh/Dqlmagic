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

    access_token = None
    grail_apiurl = None
    dt_tenant = None
    
    dql_default_query_timespan_minutes = None
    dql_default_scanlimit_gbytes = None
    dql_max_result_records = None


    def get_bearer(self):
        
        if self.oauth_url is None or self.oauth_clientid is None or self.oauth_clientsecret is None or self.oauth_scope is None: 
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

        if len(line)>0: cfgPrefix=line.strip()

        if cfgPrefix==None: cfgPrefix=''
        else: cfgPrefix+='_'
        self.config_prefix = cfgPrefix
        
        self.oauth_url = os.getenv(self.config_prefix+'dt_oauth_url')
        self.oauth_clientid = os.getenv(self.config_prefix+'dt_oauth_clientid')
        self.oauth_clientsecret = os.getenv(self.config_prefix+'dt_oauth_clientsecret')
        self.oauth_scope = os.getenv(self.config_prefix+'dt_oauth_scope')
        
        if self.oauth_url is None: return "Missing connection parameter 'dt_oauth_url'"
        if self.oauth_clientid is None: return "Missing connection parameter 'oauth_clientid'"
        if self.oauth_clientsecret is None: return "Missing connection parameter 'oauth_clientsecret'"
        if self.oauth_scope is None: return "Missing connection parameter 'oauth_scope'"

        self.grail_apiurl = os.getenv(self.config_prefix+'grail_apiurl')
        self.dt_tenant = os.getenv(self.config_prefix+"dt_tenant")
        
        if self.grail_apiurl is None: return "Missing connection parameter 'grail_apiurl'"
        if self.dt_tenant is None: return "Missing connection parameter 'dt_tenant'"

        optCfg = os.getenv('dql_default_query_timespan_minutes')
        if optCfg != None: self.dql_default_query_timespan_minutes = int(optCfg)

        optCfg = os.getenv('dql_default_scanlimit_gbytes')
        if optCfg != None: self.dql_default_scanlimit_gbytes = int(optCfg)

        optCfg = os.getenv('dql_max_result_records')
        if optCfg != None: self.dql_max_result_records= int(optCfg)

        
        self.get_bearer()

        if self.access_token is None:
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
        
        records = None
        if res:
            jdata = json.loads(res)
            records = jdata["result"]["records"]
        
        if self.shell.user_ns and len(cell) > 0: 
            if line and not line.isspace():
                self.shell.user_ns.update({line: records})
            else:
                self.shell.user_ns.update({"_dql_result": records})
            
            if records:
                return str(len(records))+" records returned"
        else:
            return records

    @line_magic
    def dql_raw(self, line):
        return self.dql_raw(line,None)

    @cell_magic
    def dql_raw(self, line, cell):
        return self.dql_raw(line, cell)
    
    @line_cell_magic
    def dql_raw(self, line, cell=None):

        if self.get_bearer() is None:
            return "Not authorized. Log in via '%auth_grail <...>"
        else: 

            if cell: dql = cell
            else: dql = line
        
            queryParams = {
                "enrich":"metric-metadata"
                }
    
            headers = {
                "accept": "application/json",
                "Authorization":"Bearer "+self.access_token,
                "dt-tenant": self.dt_tenant
            }

            body = {
                "query": dql,
                "timezone": "UTC",
                "locale": "en_US",
                "requestTimeoutMilliseconds": 1000,
                "enablePreview": True
            }

            if self.dql_default_query_timespan_minutes != None: 
                now = datetime.datetime.utcnow()
                body["defaultTimeframeStart"] = (now - timedelta(minutes=self.dql_default_query_timespan_minutes)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                body["defaultTimeframeEnd"] = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            if self.dql_default_scanlimit_gbytes != None: 
                body["defaultScanLimitGbytes"] = self.dql_default_scanlimit_gbytes

            if self.dql_max_result_records != None: 
                body["maxResultRecords"] = self.dql_max_result_records
            
            response = requests.request("POST", self.grail_apiurl+"query:execute", headers=headers, params=queryParams, json=body)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 202:
                print("Start polling results..         ", end="\r")                
                statusQueryParams = {
                    "request-token": response.json()["requestToken"],
                    "enrich":"metric-metadata"
                    }

                polling_interval = 1
                inc = 0
                while True:
                    statusResponse = requests.get(self.grail_apiurl+"query:poll", headers=headers, params=statusQueryParams)

                    if statusResponse.status_code == 200:
                        resJson = statusResponse.json()
                        status_update = resJson["state"]
                       
                        if status_update == "SUCCEEDED":
                            print("Query finished!                 ", end="\r\n") 
                            results = resJson.get("result")
                            if results:
                                metadata = results.get("metadata")
                                if metadata:
                                    meta_grail = metadata.get("grail")
                                    if meta_grail: 
                                        notifications = meta_grail.get("notifications")
                                        for n in notifications:
                                            print(n["severity"]+" - "+n["message"])
                            return statusResponse.text
                        else: 
                            if resJson.get("progress"):
                                print("Query in progress.. "+str(resJson["progress"])+"%             ", end="\r")                
                            else:
                                spinner = "|" if inc%4==1 else "/" if inc%4==2 else "-" if inc%4==3 else "\\"
                                print("Query in progress.. "+spinner+"            ", end="\r")                
                                inc+=1
                            time.sleep(polling_interval)
                    else: 
                        return '{"result":{"records":[{"ERROR":"Failed to poll query result ('+str(statusResponse.status_code)+')"}]}}'
            else:
                return '{"result":{"records":[{"ERROR":"Failed to execute query ('+str(response.status_code)+')"}]}}'
