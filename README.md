# Cradlepoint NCM SDK
Libary of functions for NCM API calls

INSTALL AND RUN INSTRUCTIONS

1. Rename the config_example.py file to config.py and change the variables to match API Keys for your NCM Account

2. Create a Python script (or use ncmtest.py as an example), and import the files:
```
import config, ncm
```

3. Create an instance of the NcmClient object:
```
n = ncm.NcmClient(config.X_CP_API_ID, config.X_CP_API_KEY, config.X_ECM_API_ID, config.X_ECM_API_KEY)
```

4. Call functions from the library as needed. For example:
```
print(n.get_accounts())
```
