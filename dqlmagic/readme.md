# Dqlmagic

An IPython magic function allowing to use DQL in your notebooks.

Dynatrace Query Language (DQL) is a powerful tool to explore your data and discover patterns, identify anomalies and outliers, create statistical modeling, and more based on data stored in Dynatrace Grail storage. 

Dqlmagic makes DQL queries available to be used in jupyter notebooks.

## Available magic functions

### dql <dql_query>
Allows to run a DQL query and returns the response records as json array.

Available as inline and cell function. 

### dql_raw <dql_query>
Allows to run a DQL query and returns the response in raw json format as provided by the api.

Available as inline and cell function. 

### auth_grail <config_prefix>
Inline function connecting to the grail cluster. 

Reads connection parameters from .env file: 
```
dt_oauth_url="https://sso.dynatrace.com/sso/oauth2/token"

dt_oauth_clientid="<YOUR-CLIENT-ID>"
dt_oauth_clientsecret="<YOUR-CLIENT-SECRET>"
dt_oauth_scope="<YOUR-ACCESS-SCOPE>"

dt_tenant="<YOUR-TENANT-ID>"
grail_apiurl="https://<YOUR-TENANT-ID>.live.dynatrace.com/api/v2/dql/query"
```

The ```<config_prefix>``` is **optional** to be used if you have multiple configs stored in your .env file like e.g. 

```
dt_config_prefix="DEV"

DEV_dt_oauth_url="https://sso.dynatrace.com/sso/oauth2/token"
DEV_dt_oauth_clientid="<YOUR-DEV-CLIENT-ID>"
DEV_dt_oauth_clientsecret="<YOUR-DEV-CLIENT-SECRET>"
DEV_dt_oauth_scope="<YOUR-DEV-ACCESS-SCOPE>"
DEV_dt_tenant="<YOUR-DEV-TENANT-ID>"
DEV_grail_apiurl="https://<YOUR-DEV-TENANT-ID>.apps.dynatracelabs.com/platform/storage/query/v1/"

PROD_dt_oauth_url="https://sso.dynatrace.com/sso/oauth2/token"
PROD_dt_oauth_clientid="<YOUR-PROD-CLIENT-ID>"
PROD_dt_oauth_clientsecret="<YOUR-PROD-CLIENT-SECRET>"
PROD_dt_oauth_scope="<YOUR-PROD-ACCESS-SCOPE>"
PROD_dt_tenant="<YOUR-PROD-TENANT-ID>"
PROD_grail_apiurl="https://<YOUR-PROD-TENANT-ID>.apps.dynatracelabs.com/platform/storage/query/v1/"

```

With the parameter ```dt_config_prefix```, you set the default config prefix used, if %auth_grail parameter ```<config_prefix>``` is not provided.

For more details on how to setup API oauth clients in Dynatrace see [Configure and manage account API OAuth clients
](https://www.dynatrace.com/support/help/how-to-use-dynatrace/account-management/identity-access-management/account-api-oauth)

For more details on .env file see [How to NOT embedded credential in Jupyter notebook](https://yuthakarn.medium.com/how-to-not-show-credential-in-jupyter-notebook-c349f9278466) or [python-dotenv](https://pypi.org/project/python-dotenv/)