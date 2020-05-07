import requests
import json


class NcmClient:
    def __init__(self, X_CP_API_ID, X_CP_API_KEY, X_ECM_API_ID, X_ECM_API_KEY, suppressprint=False):
        self.suppressprint = suppressprint
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
    def get_accounts(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Accounts'
        geturl = '{0}/accounts/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'name',
                          'name__in', 'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method returns a single account with its information.
    def get_account_by_name(self, account_name):
        for a in self.get_accounts(limit='200')['data']:
            if a['name'] == account_name:
                return a
        print("ERROR: Invalid Account Name: {}. Check spelling and verify account exists.".format(account_name))
        return

    # This operation creates a new sub-account.
    def create_subaccount(self, parent_account_id, subaccount_name, suppressprint=self.suppressprint):
        call_type = 'Create Subccount'
        posturl = '{0}/accounts/'.format(self.base_url)

        postdata = {
            'account': '/api/v1/accounts/{}/'.format(str(parent_account_id)),
            'name': str(subaccount_name)
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation updates a sub-account.
    def rename_subaccount(self, subaccount_id, new_subaccount_name, suppressprint=self.suppressprint):
        call_type = 'Rename Subccount'
        puturl = '{0}/accounts/{1}'.format(self.base_url, subaccount_id)

        putdata = {
            'name': str(new_subaccount_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation renames a sub-account by name instead of ID.
    def rename_subaccount_by_name(self, subaccount_name, new_subaccount_name, suppressprint=self.suppressprint):
        call_type = 'Rename Subccount By Name'

        puturl = '{0}/accounts/{1}'.format(self.base_url, self.get_account_by_name(subaccount_name)['id'])

        putdata = {
            'name': str(new_subaccount_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a sub-account.
    def delete_subaccount(self, subaccount_id, suppressprint=self.suppressprint):
        call_type = 'Delete Subccount'
        posturl = '{0}/accounts/{1}'.format(self.base_url, subaccount_id)

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a sub-account.
    def delete_subaccount_by_name(self, subaccount_name, suppressprint=self.suppressprint):
        call_type = 'Delete Subccount By Name'

        posturl = '{0}/accounts/{1}'.format(self.base_url, self.get_account_by_name(subaccount_name)['id'])

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method returns NCM activity log information.
    def get_activity_logs(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Activity Logs'
        geturl = '{0}/activity_logs/'.format(self.base_url)

        allowed_params = ['account', 'created_at__exact', 'created_at__lt', 'created_at__lte', 'created_at__gt',
                          'created_at__gte', 'action__timestamp__exact', 'action__timestamp__lt',
                          'action__timestamp__lte', 'action__timestamp__gt', 'action__timestamp__gte', 'actor__id',
                          'object__id', 'action__id__exact', 'actor__type', 'action__type', 'object__type',
                          'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives alert information with associated id.
    def get_alerts(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Alerts'
        geturl = '{0}/alerts/'.format(self.base_url)

        allowed_params = ['account', 'created_at', 'created_at_timeuuid', 'detected_at', 'friendly_info', 'info',
                          'router', 'type', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # A configuration manager is an abstract resource for controlling and monitoring config sync on a single device.
    # Each device has its own corresponding configuration manager.
    def get_configuration_managers(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Configuration Managers'
        geturl = '{0}/configuration_managers/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'router', 'router_in', 'synched',
                          'suspended', 'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method updates an configuration_managers for associated id
    def update_configuration_managers(self, configman_id, configman_json, suppressprint=self.suppressprint):
        call_type = 'Update Configuration Manager'
        puturl = '{0}/configuration_managers/{1}/'.format(self.base_url, configman_id)

        payload = str(configman_json)

        ncm = self.session.put(puturl, data=json.dumps(payload))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device app binding information for all device app bindings associated with the account.
    def get_device_app_bindings(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Device App Bindings'
        geturl = '{0}/device_app_bindings/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'group', 'group__in', 'app_version', 'app_version__in',
                          'id', 'id__in', 'state', 'state__in', 'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device app state information for all device app states associated with the account.
    def get_device_app_states(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Device App States'
        geturl = '{0}/device_app_states/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'router', 'router__in', 'app_version', 'app_version__in',
                          'id', 'id__in', 'state', 'state__in', 'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device app version information for all device app versions associated with the account.
    def get_device_app_versions(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Device App Versions'
        geturl = '{0}/device_app_versions/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'app', 'app__in', 'id', 'id__in', 'state', 'state__in',
                          'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device app information for all device apps associated with the account.
    def get_device_apps(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Device Apps'
        geturl = '{0}/device_apps/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'name', 'name__in', 'id', 'id__in', 'uuid', 'uuid__in',
                          'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method returns a list of Failover Events for a device, group, or account.
    def get_failovers(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Failovers'
        geturl = '{0}/failovers/'.format(self.base_url)

        allowed_params = ['account_id', 'group_id', 'router_id', 'started_at', 'ended_at', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation gives the list of device firmwares.
    def get_firmwares(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Firmwares'
        geturl = '{0}/firmwares/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'version', 'version__in', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation returns firmwares for a given model ID and version name.
    def get_firmware_for_product_by_version(self, product_id, firmware_name):
        for f in self.get_firmwares(version=firmware_name, limit='200')['data']:
            if f['product'] == '{0}}/products/{1}/'.format(self.base_url, str(product_id)):
                return f
        print("ERROR: Invalid Firmware Version")
        return

    # This method gives a groups list.
    def get_groups(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Groups'
        geturl = '{0}/groups/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'name', 'name__in', 'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method returns a single group.
    def get_group(self, group_id, suppressprint=self.suppressprint):
        call_type = 'Get Groups'
        geturl = '{0}/groups/'.format(self.base_url)
        params = {'id': str(group_id)}
        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method returns a single group.
    def get_group_by_name(self, group_name):
        for g in self.get_groups()['data']:
            if g['name'] == str(group_name):
                return g

        print("ERROR: Invalid Group Name. Check spelling and permissions.")
        return

    # This operation creates a new group.
    # parent_account_id: ID of parent account
    # group_name: Name for new group
    # product_name: Product model (e.g. IBR200)
    # firmware_name: Firmware version for group (e.g. 7.2.0)
    # Example: n.create_group_by_name('123456', 'My New Group', 'IBR200', '7.2.0')
    def create_group(self, parent_account_id, group_name, product_name, firmware_version, suppressprint=self.suppressprint):
        call_type = 'Create Group'
        posturl = '{0}/groups/'.format(self.base_url)

        product = self.get_product_by_name(product_name)['resource_url']
        firmware = self.get_firmware_for_product_by_version(product['id'], firmware_version)['resource_url']

        postdata = {
            'account': '/api/v1/accounts/{}/'.format(str(parent_account_id)),
            'name': str(group_name),
            'product': str(product),
            'target_firmware': str(firmware)
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation creates a new group.
    # parent_account_name: Friendly name of parent account
    # group_name: Name for new group
    # product_name: Product model (e.g. IBR200)
    # firmware_name: Firmware version for group (e.g. 7.2.0)
    # Example: n.create_group_by_name('Lab', 'My New Group', 'IBR200', '7.2.0')
    def create_group_by_name(self, parent_account_name, group_name, product_name, firmware_version, suppressprint=self.suppressprint):
        call_type = 'Create Group'
        posturl = '{0}/groups/'.format(self.base_url)

        account = self.get_account_by_name(parent_account_name)
        product = self.get_product_by_name(product_name)
        firmware = self.get_firmware_for_product_by_version(product['id'], firmware_version)

        postdata = {
            'account': '/api/v1/accounts/{}/'.format(str(account['id'])),
            'name': str(group_name),
            'product': str(product['resource_url']),
            'target_firmware': str(firmware['resource_url'])
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation renames a group.
    def rename_group(self, group_id, new_group_name, suppressprint=self.suppressprint):
        call_type = 'Rename Group'
        puturl = '{0}/groups/{1}'.format(self.base_url, group_id)

        putdata = {
            'name': str(new_group_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation renames a group by name.
    def rename_group_by_name(self, existing_group_name, new_group_name, suppressprint=self.suppressprint):
        call_type = 'Rename Group By Name'
        group_id = self.get_group_by_name(existing_group_name)['id']

        puturl = '{0}/groups/{1}'.format(self.base_url, group_id)
        putdata = {
            'name': str(new_group_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a group.
    def delete_group(self, group_id, suppressprint=self.suppressprint):
        call_type = 'Delete Group'
        posturl = '{0}/group/{1}'.format(self.base_url, group_id)

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a group.
    def delete_group_by_name(self, group_name, suppressprint=self.suppressprint):
        call_type = 'Delete Subaccount By Name'
        group_id = self.get_group_by_name(group_name)['id']

        posturl = '{0}/group/{1}'.format(self.base_url, group_id)
        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method returns a list of locations visited by a device.
    def get_historical_locations(self, router_id, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Historical Locations'
        geturl = '{0}/historical_locations/?router={1}'.format(self.base_url, router_id)

        allowed_params = ['created_at__gt', 'created_at_timeuuid__gt', 'created_at__lte', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of locations.
    def get_locations(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Locations'
        geturl = '{0}/locations/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation gets cellular heath scores, by device.
    def get_net_device_health(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Net Device Health'
        geturl = '{0}/net_device_health/'.format(self.base_url)

        allowed_params = ['net_device']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This endpoint is supplied to allow easy access to the latest signal and usage data reported by an account’s
    # net_devices without querying the historical raw sample tables, which are not optimized for a query spanning
    # many net_devices at once.
    def get_net_device_metrics(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Net Device Metrics'
        geturl = '{0}/net_device_metrics/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'update_ts__lt', 'update_ts__gt', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This endpoint is supplied to allow easy access to the latest signal and usage data reported by an account’s
    # net_devices without querying the historical raw sample tables, which are not optimized for a query spanning
    # many net_devices at once.
    def get_net_device_signal_samples(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Net Device Signal Samples'
        geturl = '{0}/net_device_signal_samples/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides information about the net device's overall network traffic.
    def get_net_device_usage_samples(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Net Device Usage Samples'
        geturl = '{0}/net_device_usage_samples/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of net devices.
    def get_net_devices(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Net Devices'
        geturl = '{0}/net_devices/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'connection_state', 'connection_state__in', 'id', 'id__in',
                          'is_asset', 'ipv4_address', 'ipv4_address', 'mode', 'mode__in', 'router', 'router__in',
                          'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of net devices filtered by type.
    def get_net_devices_by_type(self, device_type, suppressprint=self.suppressprint):
        call_type = 'Get Net Devices By Type'
        geturl = '{0}/net_devices/?type={1}'.format(self.base_url, str(device_type))

        ncm = self.session.get(geturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of net devices for a given router.
    def get_net_devices_for_router(self, router_id, suppressprint=self.suppressprint):
        call_type = 'Get Net Devices For Router'
        geturl = '{0}/net_devices/?router={1}'.format(self.base_url, str(router_id))

        ncm = self.session.get(geturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of net devices for a given router, filtered by mode (lan/wan).
    def get_net_devices_for_router_by_mode(self, router_id, mode, suppressprint=self.suppressprint):
        call_type = 'Get Net Devices For Router By Mode'
        geturl = '{0}/net_devices/?router={1}&mode={2}'.format(self.base_url, str(router_id), str(mode))

        ncm = self.session.get(geturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a list of product information.
    def get_products(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Products'
        geturl = '{0}/products/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method returns a product for a given model name..
    def get_product_by_name(self, product_name):
        for p in self.get_products(limit='200')['data']:
            if p['name'] == product_name:
                return p
        print("ERROR: Invalid Product Name")
        return

    # This operation reboots a device or a group. Fill out either the router field or group field depending on which should be rebooted.
    def reboot_device(self, router_id, suppressprint=self.suppressprint):
        call_type = 'Reboot Device'
        posturl = '{0}/reboot_activity/'.format(self.base_url)

        postdata = {
            'router': '{0}/routers/{1}/'.format(self.base_url, str(router_id))
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation reboots a device or a group. Fill out either the router field or group field depending on which should be rebooted.
    def reboot_group(self, group_id, suppressprint=self.suppressprint):
        call_type = 'Reboot Group'
        posturl = '{0}/reboot_activity/'.format(self.base_url)

        postdata = {
            'group': '{0}/groups/{1}/'.format(self.base_url, str(group_id))
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides a history of device alerts. To receive device alerts, you must enable them
    # through the ECM UI: Alerts -> Settings. The info section of the alert is firmware dependent and
    # may change between firmware releases.
    def get_router_alerts(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Router Alerts'
        geturl = '{0}/router_alerts/'.format(self.base_url)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides a history of device events. To receive device logs, you must enable them on the
    # Group settings form. Enabling device logs can significantly increase the ECM network traffic from the
    # device to the server depending on how quickly the device is generating events.
    def get_router_logs(self, router_id, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Router Logs'
        geturl = '{0}/router_logs/?router={1}'.format(self.base_url, router_id)

        allowed_params = ['created_at', 'created_at__lt', 'created_at__gt', 'created_at_timeuuid',
                          'created_at_timeuuid__in', 'created_at_timeuuid__gt', 'created_at_timeuuid__gte',
                          'created_at_timeuuid__lt', 'created_at_timeuuid__lte', 'order_by', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides information about the connection state of the device with the ECM server.
    def get_router_state_samples(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Router State Samples'
        geturl = '{0}/router_state_samples/'.format(self.base_url)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method provides information about the connection state of the device with the ECM server.
    def get_router_stream_usage_samples(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Router Stream Usage Samples'
        geturl = '{0}/router_stream_usage_samples/'.format(self.base_url)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device information with associated id.
    def get_routers(self, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Routers'
        geturl = '{0}/routers/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'group', 'group__in', 'id', 'id__in',
                          'ipv4_address', 'ipv4_address__in', 'mac', 'mac__in', 'name', 'name__in', 'state',
                          'state__in', 'state_updated_at__lt', 'state_updated_at__gt', 'updated_at__lt',
                          'updated_at__gt', 'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device information for a given router id.
    def get_router(self, router_id, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Router'
        geturl = '{0}/routers/?id={1}'.format(self.base_url, str(router_id))

        allowed_params = ['account', 'account__in', 'group', 'group__in', 'ipv4_address', 'ipv4_address__in',
                          'mac', 'mac__in', 'name', 'name__in', 'state', 'state__in', 'state_updated_at__lt',
                          'state_updated_at__gt', 'updated_at__lt', 'updated_at__gt', 'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives device information for a given router id.
    def get_router_by_name(self, router_name, suppressprint=self.suppressprint, **kwargs):
        for r in self.get_routers(limit='2000')['data']:
            if r['name'] == str(router_name):
                return r

        print("ERROR: Router name not found")
        return

    # This method gives a groups list filtered by account.
    def get_routers_for_account(self, account_id, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Routers for Account'
        geturl = '{0}/routers/?account={1}'.format(self.base_url, str(account_id))

        allowed_params = ['group', 'group__in', 'id', 'id__in', 'ipv4_address', 'ipv4_address__in',
                          'mac', 'mac__in', 'name', 'name__in', 'state', 'state__in', 'state_updated_at__lt',
                          'state_updated_at__gt', 'updated_at__lt', 'updated_at__gt', 'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method gives a groups list filtered by group.
    def get_routers_for_group(self, group_id, suppressprint=self.suppressprint, **kwargs):
        call_type = 'Get Routers for Group'
        geturl = '{0}/routers/?group={1}'.format(self.base_url, str(group_id))

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'ipv4_address', 'ipv4_address__in',
                          'mac', 'mac__in', 'name', 'name__in', 'state', 'state__in', 'state_updated_at__lt',
                          'state_updated_at__gt', 'updated_at__lt', 'updated_at__gt', 'expand', 'limit', 'offset']
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}

        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
            print("Skipping call: {}".format(call_type))
            return

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation renames a router.
    def rename_router(self, router_id, new_router_name, suppressprint=self.suppressprint):
        call_type = 'Rename Router'
        puturl = '{0}/routers/{1}/'.format(self.base_url, router_id)

        putdata = {
            'name': str(new_router_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation renames a router by name.
    def rename_router_by_name(self, existing_router_name, new_router_name, suppressprint=self.suppressprint):
        call_type = 'Rename Router By Name'
        router_id = self.get_router_by_name(existing_router_name)['id']
        print("ROUTER ID: {}".format(router_id))

        puturl = '{0}/routers/{1}/'.format(self.base_url, router_id)
        putdata = {
            'name': str(new_router_name)
        }
        print("PUTDATA: {}".format(putdata))

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a router.
    def delete_router(self, router_id, suppressprint=self.suppressprint):
        call_type = 'Delete Router'
        posturl = '{0}/routers/{1}'.format(self.base_url, router_id)

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a router by name.
    def delete_router_by_name(self, router_name, suppressprint=self.suppressprint):
        call_type = 'Delete Router'
        router_id = self.get_router_by_name(router_name)['id']
        posturl = '{0}/routers/{1}'.format(self.base_url, router_id)

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # Gets the results of a speed test job. The results are updated with the latest known state of the speed tests.
    def get_speed_test(self, speed_test_id, suppressprint=self.suppressprint):
        call_type = 'Get Speed Test'
        geturl = '{0}/speed_test/{1}/'.format(self.base_url, str(speed_test_id))

        ncm = self.session.get(geturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # TODO
    # Creates a speed test job that queues/runs speed tests for a given list of network devices.
    # def create_speed_test(self, router_ids, suppressprint=self.suppressprint):
    #    call_type = 'Create Speed Test'
    #    posturl = '{0}/speed_test/'.format(self.base_url)
    #
    #    self.__isjson(router_ids)
    #
    #    postdata = {
    #        'routers': router_ids
    #    }
    #
    #    ncm = self.session.post(posturl, data=json.dumps(postdata))
    #    result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
    #    return result

    # Deletes a speed test job. Deleting a job aborts it, but any test already started on a router will finish.
    def delete_speed_test(self, speed_test_id, suppressprint=self.suppressprint):
        call_type = 'Delete Speed Test'
        posturl = '{0}/routers/{1}'.format(self.base_url, speed_test_id)

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This method sets the IP Address for the Primary LAN for a given router id.
    def set_lan_ip_address(self, router_id, lan_ip, suppressprint=self.suppressprint):
        call_type = 'Set LAN IP Address'

        response = self.session.get('{0}/configuration_managers/?router.id={1}&fields=id'.format(
            self.base_url, str(router_id)))  # Get Configuration Managers ID for current Router from API
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

        ncm = self.session.patch('{0}/configuration_managers/{1}/'.format(self.base_url, str(configman_id)),
                             data=json.dumps(payload))  # Patch indie config with new values
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result
