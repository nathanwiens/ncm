import config
import requests
import json

base_url = 'https://www.cradlepointecm.com/api/v2'


class NcmClient:
    def __init__(self, X_CP_API_ID, X_CP_API_KEY, X_ECM_API_ID, X_ECM_API_KEY):
        self.session = requests.session()
        self.base_url = 'https://www.cradlepointecm.com/api/v2'
        self.session.headers.update({
            'X-CP-API-ID': X_CP_API_ID,
            'X-CP-API-KEY': X_CP_API_KEY,
            'X-ECM-API-ID': X_ECM_API_ID,
            'X-ECM-API-KEY': X_ECM_API_KEY,
            'Content-Type': 'application/json'
        })

    def __isjson(self, myjson):
        """
        Args:
            myjson: String variable to be validated if it is JSON
        Returns: None
        """
        try:
            json_object = json.loads(myjson)
        except ValueError:
            return False
        return True

    def __returnhandler(self, statuscode, returntext, objtype, suppressprint):

        validreturn = self.__isjson(returntext)
        noerr = False
        errmesg = ''

        if validreturn:
            returntext = json.loads(returntext)

            try:
                errmesg = returntext['errors']
            except KeyError:
                noerr = True
            except TypeError:
                noerr = True

        if str(statuscode) == '200' and validreturn:
            if suppressprint is False:
                print('{0} Operation Successful - See returned data for results\n'.format(str(objtype)))
            return returntext
        elif str(statuscode) == '200':
            if suppressprint is False:
                print('{0} Operation Successful\n'.format(str(objtype)))
            return None
        elif str(statuscode) == '201' and validreturn:
            if suppressprint is False:
                print('{0} Added Successfully - See returned data for results\n'.format(str(objtype)))
            return returntext
        elif str(statuscode) == '201':
            if suppressprint is False:
                print('{0} Added Successfully\n'.format(str(objtype)))
            return None
        elif str(statuscode) == '204' and validreturn:
            if suppressprint is False:
                print('{0} Deleted Successfully - See returned data for results\n'.format(str(objtype)))
            return returntext
        elif str(statuscode) == '204':
            print('{0} Deleted Successfully\n'.format(str(objtype)))
            return None
        elif str(statuscode) == '400' and validreturn and noerr is False:
            if suppressprint is False:
                print('Bad Request - See returned data for error details\n')
            return errmesg
        elif str(statuscode) == '400' and validreturn and noerr:
            if suppressprint is False:
                print('Bad Request - See returned data for details\n')
            return returntext
        elif str(statuscode) == '400':
            if suppressprint is False:
                print('Bad Request - No additional error data available\n')
        elif str(statuscode) == '401' and validreturn and noerr is False:
            if suppressprint is False:
                print('Unauthorized Access - See returned data for error details\n')
            return errmesg
        elif str(statuscode) == '401' and validreturn:
            if suppressprint is False:
                print('Unauthorized Access')
            return returntext
        elif str(statuscode) == '404' and validreturn and noerr is False:
            if suppressprint is False:
                print('Resource Not Found - See returned data for error details\n')
            return errmesg
        elif str(statuscode) == '404' and validreturn:
            if suppressprint is False:
                print('Resource Not Found')
            return returntext
        elif str(statuscode) == '500':
            if suppressprint is False:
                print('HTTP 500 - Server Error')
            return returntext
        elif validreturn and noerr is False:
            if suppressprint is False:
                print('HTTP Status Code: {0} - See returned data for error details\n'.format(str(statuscode)))
            return errmesg
        else:
            print('HTTP Status Code: {0} - No returned data\n'.format(str(statuscode)))

    # Return a list of accounts
    def get_accounts(self, suppressprint=False):
        calltype = 'Get Accounts'
        geturl = '{0}/accounts'.format(self.base_url)
        ncm = self.session.get(geturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, calltype, suppressprint)
        return result

    # Return a list of groups
    def get_groups(self, account, suppressprint=False):
        calltype = 'Get Groups'
        geturl = '{0}/groups/?account={1}'.format(self.base_url, str(account))
        ncm = self.session.get(geturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, calltype, suppressprint)
        return result

    # Return a list of routers by account
    def get_routers_for_account(self, account_id, suppressprint=False):
        calltype = 'Get Routers for Group'
        geturl = '{0}/routers/?account={1}'.format(self.base_url, str(account_id))

        ncm = self.session.get(geturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, calltype, suppressprint)
        return result

    # Return a list of routers by group
    def get_routers_for_group(self, group_id, suppressprint=False):
        calltype = 'Get Routers for Group'
        geturl = '{0}/routers/?group={1}'.format(self.base_url, str(group_id))

        ncm = self.session.get(geturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, calltype, suppressprint)
        return result

    # Return a single router
    def get_router(self, router_id, suppressprint=False):
        calltype = 'Get Routers for Group'
        geturl = '{0}/routers/{1}/'.format(self.base_url, str(router_id))

        ncm = self.session.get(geturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, calltype, suppressprint)
        return result

    def set_lan_ip_address(self, router_id, lan_ip, suppressprint=False):
        calltype = 'Set LAN IP Address'

        response = self.session.get('{0}/configuration_managers/?router.id={1}&fields=id'.format(self.base_url, str(router_id)))  # Get Configuration Managers ID for current Router from API
        response = json.loads(response.content.decode("utf-8"))  # Decode the response and make it a dictionary
        configman_id = response['data'][0]['id']  # get the Configuration Managers ID from response
        payload = {
            "configuration": [
                {
                    "lan": {
                        "00000000-0d93-319d-8220-4a1fb0372b51": {
                            "_id_": "00000000-0d93-319d-8220-4a1fb0372b51",
                            "ip_address": lan_ip
                        }
                    }
                },
                []
            ]
        }
        ncm = requests.patch('{0}/configuration_managers/{1}/'.format(self.base_url, str(configman_id)),
                           data=json.dumps(payload))  # Patch indie config with new values
        result = self.__returnhandler(ncm.status_code, ncm.text, calltype, suppressprint)
        return result
