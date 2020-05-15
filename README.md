# Cradlepoint NCM SDK
This is a Python client library for Cradlepoint NCM API

INSTALL AND RUN INSTRUCTIONS

1. Install the ncm pip package:
    ```
    pip3 install -i https://test.pypi.org/simple/ ncm
    ```

2. Create a config.py file with your NCM API Keys:
    ```
    X_CP_API_ID = 'aaaa'
    X_CP_API_KEY = 'bbbb'
    X_ECM_API_ID = 'cccc'
    X_ECM_API_KEY = 'dddd'
    ```

3. Create a Python script, import the module, and create an instance of the NcmClient object:
    ```
    import config
    from ncm import ncm
    n = ncm.NcmClient(config.X_CP_API_ID, config.X_CP_API_KEY, config.X_ECM_API_ID, config.X_ECM_API_KEY)
    ```

4. Call functions from the module as needed. For example:
    ```
    print(n.get_accounts())
    ```
