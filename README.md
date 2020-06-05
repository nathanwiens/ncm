# Cradlepoint NCM SDK
This is a Python client library for Cradlepoint NCM API

INSTALL AND RUN INSTRUCTIONS

1. Install the ncm pip package:
    ```
    pip3 install ncm
    ```

2. Set NCM API Keys. API Keys must be passed as a dictionary:
    ```
    api_keys = {
        'X-CP-API-ID': 'aaaa',
        'X-CP-API-KEY': 'bbbb',
        'X-ECM-API-ID': 'cccc',
        'X-ECM-API-KEY': 'dddd'
    }
    ```

3. Import the module and create an instance of the NcmClient object:
    ```
    from ncm import ncm
    n = ncm.NcmClient(api_keys)
    ```

4. Call functions from the module as needed. For example:
    ```
    print(n.get_accounts())
    ```
