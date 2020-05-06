import config
import requests
import json

base_url = 'https://www.cradlepointecm.com/api/v2'
suppress_print = False


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

    # This method gives a list of accounts with its information.
    def get_accounts(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Accounts'
        geturl = '{0}/accounts/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'name',
                          'name__in', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation creates a new sub-account.
    def create_subaccount(self, parent_account_id, subaccount_name, suppressprint=suppress_print):
        call_type = 'Create Subccount'
        posturl = '{0}/accounts/'.format(self.base_url)

        postdata = {
            'account': '/api/v1/accounts/{}/'.format(str(parent_account_id)),
            'name': str(subaccount_name)
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation updates a sub-account.
    def update_subaccount(self, subaccount_id, subaccount_name, suppressprint=suppress_print):
        call_type = 'Update Subccount'
        puturl = '{0}/accounts/{1}'.format(self.base_url, subaccount_id)

        putdata = {
            'name': str(subaccount_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a sub-account.
    def delete_subaccount(self, subaccount_id, suppressprint=suppress_print):
        call_type = 'Delete Subccount'
        posturl = '{0}/accounts/{1}'.format(self.base_url, subaccount_id)

        ncm = self.session.delete(posturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a sub-account.
    def delete_subaccount_by_name(self, subaccount_name, suppressprint=suppress_print):
        call_type = 'Delete Subccount By Name'

        posturl = ''
        for account in self.get_accounts()['data']:
            if account['name'] == str(subaccount_name):
                posturl = '{0}/accounts/{1}'.format(self.base_url, account['id'])
                continue

        if posturl is '':
            print("ERROR: No Account found with name: {}".format(str(subaccount_name)))
        else:
            ncm = self.session.delete(posturl)
            #
            # Call return handler function to parse NCM response
            #
            result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
            return result

    # This method returns NCM activity log information.
    def get_activity_logs(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Activity Logs'
        geturl = '{0}/activity_logs/'.format(self.base_url)

        allowed_params = ['account', 'created_at__exact', 'created_at__lt', 'created_at__lte', 'created_at__gt',
                          'created_at__gte', 'action__timestamp__exact', 'action__timestamp__lt',
                          'action__timestamp__lte','action__timestamp__gt', 'action__timestamp__gte', 'actor__id',
                          'object__id', 'action__id__exact', 'actor__type', 'action__type', 'object__type']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives alert information with associated id.
    def get_alerts(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Alerts'
        geturl = '{0}/alerts/'.format(self.base_url)

        allowed_params = ['account', 'created_at', 'created_at_timeuuid', 'detected_at', 'friendly_info', 'info',
                          'router', 'type']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # A configuration manager is an abstract resource for controlling and monitoring config sync on a single device.
    # Each device has its own corresponding configuration manager.
    def get_configuration_managers(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Configuration Managers'
        geturl = '{0}/configuration_managers/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'router', 'router_in', 'synched',
                          'suspended', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method updates an configuration_managers for associated id
    def update_configuration_managers(self, configman_id, configman_json, suppressprint=suppress_print, **kwargs):
        call_type = 'Update Configuration Manager'
        puturl = '{0}/configuration_managers/{1}/'.format(self.base_url, configman_id)

        payload = str(configman_json)

        ncm = self.session.put(puturl, data=json.dumps(payload))
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device app binding information for all device app bindings associated with the account.
    def get_device_app_bindings(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Device App Bindings'
        geturl = '{0}/device_app_bindings/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'group', 'group__in', 'app_version', 'app_version__in',
                          'id', 'id__in', 'state', 'state__in', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device app state information for all device app states associated with the account.
    def get_device_app_states(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Device App States'
        geturl = '{0}/device_app_states/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'router', 'router__in', 'app_version', 'app_version__in',
                          'id', 'id__in', 'state', 'state__in', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device app version information for all device app versions associated with the account.
    def get_device_app_versions(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Device App Versions'
        geturl = '{0}/device_app_versions/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'app', 'app__in', 'id', 'id__in', 'state', 'state__in', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device app information for all device apps associated with the account.
    def get_device_apps(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Device Apps'
        geturl = '{0}/device_apps/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'name', 'name__in', 'id', 'id__in', 'uuid', 'uuid__in', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method returns a list of Failover Events for a device, group, or account.
    def get_failovers(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Failovers'
        geturl = '{0}/failovers/'.format(self.base_url)

        allowed_params = ['account_id', 'group_id', 'router_id', 'started_at', 'ended_at', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation gives the list of device firmwares.
    def get_firmwares(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Firmwares'
        geturl = '{0}/firmwares/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'version', 'version__in', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a groups list.
    def get_groups(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Groups'
        geturl = '{0}/groups/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'name', 'name__in', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation creates a new group.
    # parent_account_id: ID of parent account
    # group_name: Name for new group
    # product_name: Product model (e.g. IBR200)
    # firmware_name: Firmware version for group (e.g. 7.2.0)
    def create_group(self, parent_account_id, group_name, product_name, firmware_name, suppressprint=suppress_print):
        call_type = 'Create Group'
        posturl = '{0}/groups/'.format(self.base_url)

        product = ''
        firmware = ''

        for p in self.get_products(limit='200')['data']:
            if p['name'] == product_name:
                product = p['id']
                print("PRODUCT: {}".format(product))
                continue

        for f in self.get_firmwares(version=firmware_name)['data']:
            if f['product'] == 'https://www.cradlepointecm.com/api/v2/products/{}/'.format(product):
                firmware = f['id']

        if product is '':
            print("ERROR: Invalid Product Name")
            return
        if firmware is '':
            print("ERROR: Invalid Firmware Version")
            return

        postdata = {
            'account': '/api/v1/accounts/{}/'.format(str(parent_account_id)),
            'name': str(group_name),
            'product': 'https://www.cradlepointecm.com/api/v2/products/{}/'.format(str(product)),
            'target_firmware': 'https://www.cradlepointecm.com/api/v2/firmwares/{}/'.format(str(firmware))
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation creates a new group.
    # parent_account_name: Friendly name of parent account
    # group_name: Name for new group
    # product_name: Product model (e.g. IBR200)
    # firmware_name: Firmware version for group (e.g. 7.2.0)
    # Example: n.create_group_by_name('Lab', 'My New Group', 'IBR200', '7.2.0')
    def create_group_by_name(self, parent_account_name, group_name, product_name, firmware_name, suppressprint=suppress_print):
        call_type = 'Create Group'
        posturl = '{0}/groups/'.format(self.base_url)

        account = ''
        product = ''
        firmware = ''

        for a in self.get_accounts()['data']:
            if a['name'] == parent_account_name:
                account = a['id']
                continue

        for p in self.get_products(limit='200')['data']:
            if p['name'] == product_name:
                product = p['id']
                print("PRODUCT: {}".format(product))
                continue

        for f in self.get_firmwares(version=firmware_name)['data']:
            if f['product'] == 'https://www.cradlepointecm.com/api/v2/products/{}/'.format(product):
                firmware = f['id']

        if account is '':
            print('ERROR: Invalid Account Name')
            return
        if product is '':
            print("ERROR: Invalid Product Name")
            return
        if firmware is '':
            print("ERROR: Invalid Firmware Version")
            return

        postdata = {
            'account': '/api/v1/accounts/{}/'.format(str(account)),
            'name': str(group_name),
            'product': 'https://www.cradlepointecm.com/api/v2/products/{}/'.format(str(product)),
            'target_firmware': 'https://www.cradlepointecm.com/api/v2/firmwares/{}/'.format(str(firmware))
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    #TODO: CREATE UPDATE_GROUP AND UPDATE_GROUP_BY_NAME FUNCTIONS

    # This operation updates a group.
    def update_group(self, group_id, suppressprint=suppress_print):
        call_type = 'Update Group By Name'
        puturl = '{0}/groups/{1}'.format(self.base_url, group_id)

        #TODO
        putdata = {
            # 'name': str(subaccount_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation updates a group.
    def update_group_by_name(self, group_name, suppressprint=suppress_print):
        call_type = 'Update Group By Name'
        #TODO
        #puturl = '{0}/groups/{1}'.format(self.base_url, subaccount_id)

        #TODO
        putdata = {
            # 'name': str(subaccount_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a group.
    def delete_group(self, group_id, suppressprint=suppress_print):
        call_type = 'Delete Subccount'
        posturl = '{0}/group/{1}'.format(self.base_url, group_id)

        ncm = self.session.delete(posturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    #TODO
    # This operation deletes a group.
    def delete_group_by_name(self, group_id, suppressprint=suppress_print):
        call_type = 'Delete Subccount By Name'
        #TODO
        #posturl = '{0}/group/{1}'.format(self.base_url, group_id)

        ncm = self.session.delete(posturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result


    # This method returns a list of locations visited by a device.
    def get_historical_locations(self, router_id, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Historical Locations'
        geturl = '{0}/historical_locations/?router={1}'.format(self.base_url, router_id)

        allowed_params = ['created_at__gt', 'created_at_timeuuid__gt', 'created_at__lte', 'limit']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of locations.
    def get_locations(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Locations'
        geturl = '{0}/locations/'.format(self.base_url)

        allowed_params = ['id', 'id__in']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation gets cellular heath scores, by device.
    def get_net_device_health(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Net Device Health'
        geturl = '{0}/net_device_health/'.format(self.base_url)

        allowed_params = ['net_device']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This endpoint is supplied to allow easy access to the latest signal and usage data reported by an account’s
    # net_devices without querying the historical raw sample tables, which are not optimized for a query spanning
    # many net_devices at once.
    def get_net_device_metrics(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Net Device Metrics'
        geturl = '{0}/net_device_metrics/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'update_ts__lt', 'update_ts__gt']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This endpoint is supplied to allow easy access to the latest signal and usage data reported by an account’s
    # net_devices without querying the historical raw sample tables, which are not optimized for a query spanning
    # many net_devices at once.
    def get_net_device_signal_samples(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Net Device Signal Samples'
        geturl = '{0}/net_device_signal_samples/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte', 'order_by']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides information about the net device's overall network traffic.
    def get_net_device_usage_samples(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Net Device Usage Samples'
        geturl = '{0}/net_device_usage_samples/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte', 'order_by']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of net devices.
    def get_net_devices(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Net Devices'
        geturl = '{0}/net_devices/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'connection_state', 'connection_state__in', 'id', 'id__in',
                          'is_asset', 'ipv4_address', 'ipv4_address', 'mode', 'mode__in', 'router', 'router__in',
                          'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of net devices filtered by type.
    def get_net_devices_by_type(self, device_type, suppressprint=suppress_print):
        call_type = 'Get Net Devices By Type'
        geturl = '{0}/net_devices/?type={1}'.format(self.base_url, str(device_type))

        ncm = self.session.get(geturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of net devices for a given router.
    def get_net_devices_for_router(self, router_id, suppressprint=suppress_print):
        call_type = 'Get Net Devices For Router'
        geturl = '{0}/net_devices/?router={1}'.format(self.base_url, str(router_id))

        ncm = self.session.get(geturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of net devices for a given router, filtered by mode (lan/wan).
    def get_net_devices_for_router_by_mode(self, router_id, mode, suppressprint=suppress_print):
        call_type = 'Get Net Devices For Router By Mode'
        geturl = '{0}/net_devices/?router={1}&mode={2}'.format(self.base_url, str(router_id), str(mode))

        ncm = self.session.get(geturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of product information.
    def get_products(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Products'
        geturl = '{0}/products/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides a history of device alerts. To receive device alerts, you must enable them
    # through the ECM UI: Alerts -> Settings. The info section of the alert is firmware dependent and
    # may change between firmware releases.
    def get_router_alerts(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Router Alerts'
        geturl = '{0}/router_alerts/'.format(self.base_url, router_id)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt', 'created_at_timeuuid',
                          'created_at_timeuuid__in', 'created_at_timeuuid__gt', 'created_at_timeuuid__gte',
                          'created_at_timeuuid__lt', 'created_at_timeuuid__lte', 'order_by']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides a history of device events. To receive device logs, you must enable them on the
    # Group settings form. Enabling device logs can significantly increase the ECM network traffic from the
    # device to the server depending on how quickly the device is generating events.
    def get_router_logs(self, router_id, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Router Logs'
        geturl = '{0}/router_logs/?router={1}'.format(self.base_url, router_id)

        allowed_params = ['created_at', 'created_at__lt', 'created_at__gt', 'created_at_timeuuid',
                          'created_at_timeuuid__in', 'created_at_timeuuid__gt', 'created_at_timeuuid__gte',
                          'created_at_timeuuid__lt', 'created_at_timeuuid__lte', 'order_by']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides information about the connection state of the device with the ECM server.
    def get_router_state_samples(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Router State Samples'
        geturl = '{0}/router_state_samples/'.format(self.base_url, router_id)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt', 'created_at_timeuuid',
                          'created_at_timeuuid__in', 'created_at_timeuuid__gt', 'created_at_timeuuid__gte',
                          'created_at_timeuuid__lt', 'created_at_timeuuid__lte', 'order_by']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides information about the connection state of the device with the ECM server.
    def get_router_stream_usage_samples(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Router Stream Usage Samples'
        geturl = '{0}/router_stream_usage_samples/'.format(self.base_url, router_id)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt', 'created_at_timeuuid',
                          'created_at_timeuuid__in', 'created_at_timeuuid__gt', 'created_at_timeuuid__gte',
                          'created_at_timeuuid__lt', 'created_at_timeuuid__lte', 'order_by']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device information with associated id.
    def get_routers(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Routers'
        geturl = '{0}/routers/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'group', 'group__in', 'id', 'id__in',
                          'ipv4_address', 'ipv4_address__in', 'mac', 'mac__in', 'name', 'name__in', 'state',
                          'state__in', 'state_updated_at__lt', 'state_updated_at__gt', 'updated_at__lt',
                          'updated_at__gt', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device information for a given router id.
    def get_router(self, router_id, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Router'
        geturl = '{0}/routers/?id={1}'.format(self.base_url, str(router_id))

        allowed_params = ['account', 'account__in', 'group', 'group__in', 'ipv4_address', 'ipv4_address__in',
                          'mac', 'mac__in', 'name', 'name__in', 'state', 'state__in', 'state_updated_at__lt',
                          'state_updated_at__gt', 'updated_at__lt', 'updated_at__gt', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a groups list filtered by account.
    def get_routers_for_account(self, account_id, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Routers for Account'
        geturl = '{0}/routers/?account={1}'.format(self.base_url, str(account_id))

        allowed_params = ['group', 'group__in', 'id', 'id__in', 'ipv4_address', 'ipv4_address__in',
                          'mac', 'mac__in', 'name', 'name__in', 'state', 'state__in', 'state_updated_at__lt',
                          'state_updated_at__gt', 'updated_at__lt', 'updated_at__gt', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a groups list filtered by group.
    def get_routers_for_group(self, group_id, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Routers for Group'
        geturl = '{0}/routers/?group={1}'.format(self.base_url, str(group_id))

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'ipv4_address', 'ipv4_address__in',
                          'mac', 'mac__in', 'name', 'name__in', 'state', 'state__in', 'state_updated_at__lt',
                          'state_updated_at__gt', 'updated_at__lt', 'updated_at__gt', 'expand']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)

        ncm = self.session.get(geturl, params=params)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # Gets the results of a speed test job. The results are updated with the latest known state of the speed tests.
    def get_speed_test(self, speed_test_id, suppressprint=suppress_print):
        call_type = 'Get Speed Test'
        geturl = '{0}/speed_test/{1}/'.format(self.base_url, str(speed_test_id))

        ncm = self.session.get(geturl)
        #
        # Call return handler function to parse NCM response
        #
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method sets the IP Address for the Primary LAN for a given router id.
    def set_lan_ip_address(self, router_id, lan_ip, suppressprint=suppress_print):
        call_type = 'Set LAN IP Address'

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
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result
