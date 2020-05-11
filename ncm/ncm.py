import requests
import json

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
        try:
            json_object = json.loads(myjson)
        except ValueError:
            return False
        return True

    def __returnhandler(self, statuscode, returntext, objtype, suppressprint):

        if str(statuscode) == '200':
            if suppressprint is False:
                print('{0} Operation Successful - See returned data for results\n'.format(str(objtype)))
            return returntext
        elif str(statuscode) == '200':
            if suppressprint is False:
                print('{0} Operation Successful\n'.format(str(objtype)))
            return None
        elif str(statuscode) == '201':
            if suppressprint is False:
                print('{0} Added Successfully - See returned data for results\n'.format(str(objtype)))
            return returntext
        elif str(statuscode) == '201':
            if suppressprint is False:
                print('{0} Added Successfully\n'.format(str(objtype)))
            return None
        elif str(statuscode) == '204':
            if suppressprint is False:
                print('{0} Deleted Successfully\n'.format(str(objtype)))
            return None
        elif str(statuscode) == '400':
            if suppressprint is False:
                print('Bad Request - See returned data for details\n')
            return returntext
        elif str(statuscode) == '400':
            if suppressprint is False:
                print('Bad Request - No additional error data available\n')
        elif str(statuscode) == '401':
            if suppressprint is False:
                print('Unauthorized Access')
            return returntext
        elif str(statuscode) == '404':
            if suppressprint is False:
                print('Resource Not Found')
            return returntext
        elif str(statuscode) == '500':
            if suppressprint is False:
                print('HTTP 500 - Server Error')
            return returntext
        else:
            print('HTTP Status Code: {0} - No returned data\n'.format(str(statuscode)))

    def __paginated_results(self, geturl, allowed_params, call_type, suppressprint=suppress_print, **kwargs):
        params = self.__parse_kwargs(kwargs, allowed_params)
        params.update({'limit': '500'})
        results = []
        page = 0
        while geturl:
            page = page + 1
            ncm = self.session.get(geturl, params=params)
            if not (200 <= ncm.status_code < 300):
                break
            self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
            geturl = ncm.json()['meta']['next']
            for d in ncm.json()['data']:
                results.append(d)
        return results

    def __parse_kwargs(self, kwargs, allowed_params):
        params = {k: v for (k, v) in kwargs.items() if k in allowed_params}
        if 'limit' not in params:
            params.update({'limit': '500'})

        bad_params = {k: v for (k, v) in kwargs.items() if k not in allowed_params}
        if len(bad_params) > 0:
            print("INVALID PARAMETERS: ")
            print(bad_params)
        return params

    def get_accounts(self, suppressprint=suppress_print, **kwargs):
        """
        Returns accounts with details.

        Will only return up to 500 results. Use get_account_all for the full list

        :param suppressprint: False by default. Set to true if HTTP Request results should not be printed.
        :type suppressprint: bool
        :param kwargs: A list of allowed parameters can be found on developers.cradlepoint.com.
        :return: A list of accounts based on API Key.
        """

        call_type = 'Get Accounts'
        geturl = '{0}/accounts/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'name',
                          'name__in', 'expand', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    def get_accounts_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Accounts (All)'
        geturl = '{0}/accounts/'.format(self.base_url)
        allowed_params = ['account', 'account__in', 'id', 'id__in', 'name',
                          'name__in', 'expand', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    def get_account_by_id(self, account_id, suppressprint=suppress_print):
        """
        This method returns a single account with its information.
        """

        return self.get_accounts(id=account_id, suppressprint=suppressprint)[0]

    # This method returns a single account with its information.
    def get_account_by_name(self, account_name, suppressprint=suppress_print):
        return self.get_accounts(name=account_name, suppressprint=suppressprint)[0]

    # This operation creates a new subaccount.
    def create_subaccount_by_parent_id(self, parent_account_id, subaccount_name, suppressprint=suppress_print):
        call_type = 'Subaccount'
        posturl = '{0}/accounts/'.format(self.base_url)

        postdata = {
            'account': '/api/v1/accounts/{}/'.format(str(parent_account_id)),
            'name': str(subaccount_name)
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This operation creates a new subaccount using the parent account name.
    def create_subaccount_by_parent_name(self, parent_account_name, subaccount_name, suppressprint=suppress_print):
        return self.create_subaccount_by_parent_id(self.get_account_by_name(
            parent_account_name, suppressprint=suppressprint)['id'], subaccount_name, suppressprint=suppressprint)

    # This operation updates a subaccount.
    def rename_subaccount_by_id(self, subaccount_id, new_subaccount_name, suppressprint=suppress_print):
        call_type = 'Subaccount'
        puturl = '{0}/accounts/{1}/'.format(self.base_url, str(subaccount_id))

        putdata = {
            "name": str(new_subaccount_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This operation renames a subaccount by name instead of ID.
    def rename_subaccount_by_name(self, subaccount_name, new_subaccount_name, suppressprint=suppress_print):
        return self.rename_subaccount_by_id(self.get_account_by_name(
            subaccount_name, suppressprint=suppressprint)['id'], new_subaccount_name, suppressprint=suppressprint)

    # This operation deletes a sub-account.
    def delete_subaccount_by_id(self, subaccount_id, suppressprint=suppress_print):
        call_type = 'Subccount'
        posturl = '{0}/accounts/{1}'.format(self.base_url, subaccount_id)

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.text, call_type, suppressprint)
        return result

    # This operation deletes a sub-account.
    def delete_subaccount_by_name(self, subaccount_name, suppressprint=suppress_print):
        return self.delete_subaccount_by_id(self.get_account_by_name(
            subaccount_name, suppressprint=suppressprint)['id'])

    # This method returns NCM activity log information.
    def get_activity_logs(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Activity Logs'
        geturl = '{0}/activity_logs/'.format(self.base_url)

        allowed_params = ['account', 'created_at__exact', 'created_at__lt', 'created_at__lte', 'created_at__gt',
                          'created_at__gte', 'action__timestamp__exact', 'action__timestamp__lt',
                          'action__timestamp__lte', 'action__timestamp__gt', 'action__timestamp__gte', 'actor__id',
                          'object__id', 'action__id__exact', 'actor__type', 'action__type', 'object__type',
                          'limit']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method gives alert information with associated id.
    def get_alerts(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Alerts'
        geturl = '{0}/alerts/'.format(self.base_url)

        allowed_params = ['account', 'created_at', 'created_at_timeuuid', 'detected_at', 'friendly_info', 'info',
                          'router', 'type', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # A configuration manager is an abstract resource for controlling and monitoring config sync on a single device.
    # Each device has its own corresponding configuration manager.
    def get_configuration_managers(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Configuration Managers'
        geturl = '{0}/configuration_managers/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'router', 'router_in', 'synched',
                          'suspended', 'expand', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method updates an configuration_managers for associated id
    def update_configuration_managers(self, configman_id, configman_json, suppressprint=suppress_print):
        call_type = 'Configuration Manager'
        puturl = '{0}/configuration_managers/{1}/'.format(self.base_url, configman_id)

        payload = str(configman_json)

        ncm = self.session.put(puturl, data=json.dumps(payload))
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This method gives device app binding information for all device app bindings associated with the account.
    def get_device_app_bindings(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Device App Bindings'
        geturl = '{0}/device_app_bindings/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'group', 'group__in', 'app_version', 'app_version__in',
                          'id', 'id__in', 'state', 'state__in', 'expand', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method gives device app state information for all device app states associated with the account.
    def get_device_app_states(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Device App States'
        geturl = '{0}/device_app_states/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'router', 'router__in', 'app_version', 'app_version__in',
                          'id', 'id__in', 'state', 'state__in', 'expand', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method gives device app version information for all device app versions associated with the account.
    def get_device_app_versions(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Device App Versions'
        geturl = '{0}/device_app_versions/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'app', 'app__in', 'id', 'id__in', 'state', 'state__in',
                          'expand', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method gives device app information for all device apps associated with the account.
    def get_device_apps(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Device Apps'
        geturl = '{0}/device_apps/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'name', 'name__in', 'id', 'id__in', 'uuid', 'uuid__in',
                          'expand', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method returns a list of Failover Events for a device, group, or account.
    def get_failovers(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Failovers'
        geturl = '{0}/failovers/'.format(self.base_url)

        allowed_params = ['account_id', 'group_id', 'router_id', 'started_at', 'ended_at', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This operation gives the list of device firmwares.
    def get_firmwares(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Firmwares'
        geturl = '{0}/firmwares/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'version', 'version__in', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This operation gives the full paginated list of device firmwares.
    def get_firmwares_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Firmwares (all)'
        geturl = '{0}/firmwares/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'version', 'version__in', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This operation returns firmwares for a given model ID and version name.
    def get_firmware_for_product_by_version(self, product_id, firmware_name):
        for f in self.get_firmwares(version=firmware_name, limit='500')['data']:
            if f['product'] == '{0}/products/{1}/'.format(self.base_url, str(product_id)):
                return f
        print("ERROR: Invalid Firmware Version")
        return

    # This method gives a groups list.
    def get_groups(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Groups'
        geturl = '{0}/groups/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'name', 'name__in', 'expand', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method gives a groups list.
    def get_groups_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Groups (All)'
        geturl = '{0}/groups/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'id', 'id__in', 'name', 'name__in', 'expand', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method returns a single group.
    def get_group_by_id(self, group_id, suppressprint=suppress_print):
        return self.get_groups(id=group_id, suppressprint=suppressprint)[0]

    # This method returns a single group.
    def get_group_by_name(self, group_name, suppressprint=suppress_print):
        return self.get_groups(name=group_name, suppressprint=suppressprint)[0]

    def create_group_by_parent_id(self, parent_account_id, group_name, product_name, firmware_version,
                                  suppressprint=suppress_print):
        """This operation creates a new group.

        :param parent_account_id: ID of parent account
        :param group_name: Name for new group
        :param product_name: Product model (e.g. IBR200)
        :param firmware_version: Firmware version for group (e.g. 7.2.0)
        :param suppressprint:
        :return:

        Example: n.create_group_by_parent_id('123456', 'My New Group', 'IBR200', '7.2.0')
        """

        call_type = 'Group'
        posturl = '{0}/groups/'.format(self.base_url)

        product = self.get_product_by_name(product_name)
        firmware = self.get_firmware_for_product_by_version(product['id'], firmware_version)

        postdata = {
            'account': '/api/v1/accounts/{}/'.format(str(parent_account_id)),
            'name': str(group_name),
            'product': str(self.get_product_by_name(product_name)['resource_url']),
            'target_firmware': str(firmware['resource_url'])
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    def create_group_by_parent_name(self, parent_account_name, group_name, product_name, firmware_version,
                                    suppressprint=suppress_print):
        """This operation creates a new group.

        :param parent_account_name: Name of parent account
        :param group_name: Name for new group
        :param product_name: Product model (e.g. IBR200)
        :param firmware_version: Firmware version for group (e.g. 7.2.0)
        :param suppressprint:
        :return:

        Example: n.create_group_by_parent_name('Parent Account', 'My New Group', 'IBR200', '7.2.0')
        """

        return self.create_group_by_parent_id(
            self.get_account_by_name(parent_account_name, suppressprint=suppressprint)['id'], group_name, product_name,
            firmware_version, suppressprint=suppressprint)

    # This operation renames a group.
    def rename_group_by_id(self, group_id, new_group_name, suppressprint=suppress_print):
        call_type = 'Group'
        puturl = '{0}/groups/{1}/'.format(self.base_url, group_id)

        putdata = {
            "name": str(new_group_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This operation renames a group by name.
    def rename_group_by_name(self, existing_group_name, new_group_name, suppressprint=suppress_print):
        return self.rename_group_by_id(
            self.get_group_by_name(existing_group_name)['id'], new_group_name, suppressprint=suppressprint)

    # This operation deletes a group.
    def delete_group_by_id(self, group_id, suppressprint=suppress_print):
        call_type = 'Group'
        posturl = '{0}/groups/{1}/'.format(self.base_url, group_id)

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This operation deletes a group.
    def delete_group_by_name(self, group_name, suppressprint=suppress_print):
        return self.delete_group_by_id(
            self.get_group_by_name(group_name)['id'], suppressprint=suppressprint)

    # This method returns a list of locations visited by a device.
    def get_historical_locations(self, router_id, suppressprint=suppress_print, **kwargs):
        call_type = 'Historical Locations'
        geturl = '{0}/historical_locations/?router={1}'.format(self.base_url, router_id)

        allowed_params = ['created_at__gt', 'created_at_timeuuid__gt', 'created_at__lte', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    def get_historical_locations_all(self, router_id, suppressprint=suppress_print, **kwargs):
        call_type = 'Historical Locations'
        geturl = '{0}/historical_locations/?router={1}'.format(self.base_url, router_id)

        allowed_params = ['created_at__gt', 'created_at_timeuuid__gt', 'created_at__lte', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method gives a list of locations.
    def get_locations(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Locations'
        geturl = '{0}/locations/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    def get_locations_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Locations'
        geturl = '{0}/locations/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This operation gets cellular heath scores, by device.
    def get_net_device_health(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Net Device Health'
        geturl = '{0}/net_device_health/'.format(self.base_url)

        allowed_params = ['net_device']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # TODO
    # Check if all __in calls are string or list, process accordingly

    # This endpoint is supplied to allow easy access to the latest signal and usage data reported by an account’s
    # net_devices without querying the historical raw sample tables, which are not optimized for a query spanning
    # many net_devices at once.
    def get_net_device_metrics(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Net Device Metrics'
        geturl = '{0}/net_device_metrics/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'update_ts__lt', 'update_ts__gt', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This endpoint is supplied to allow easy access to the latest signal and usage data reported by an account’s
    # net_devices without querying the historical raw sample tables, which are not optimized for a query spanning
    # many net_devices at once.
    def get_net_device_metrics_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Net Device Metrics'
        geturl = '{0}/net_device_metrics/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'update_ts__lt', 'update_ts__gt', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This endpoint is supplied to allow easy access to the latest signal and usage data reported by an account’s
    # net_devices without querying the historical raw sample tables, which are not optimized for a query spanning
    # many net_devices at once.
    def get_net_device_signal_samples(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Get Net Device Signal Samples'
        geturl = '{0}/net_device_signal_samples/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This endpoint is supplied to allow easy access to the latest signal and usage data reported by an account’s
    # net_devices without querying the historical raw sample tables, which are not optimized for a query spanning
    # many net_devices at once.
    def get_net_device_signal_samples_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Net Device Signal Samples'
        geturl = '{0}/net_device_signal_samples/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method provides information about the net device's overall network traffic.
    def get_net_device_usage_samples(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Net Device Usage Samples'
        geturl = '{0}/net_device_usage_samples/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method provides information about the net device's overall network traffic.
    def get_net_device_usage_samples_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Net Device Usage Samples'
        geturl = '{0}/net_device_usage_samples/'.format(self.base_url)

        allowed_params = ['net_device', 'net_device__in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method gives a list of net devices.
    def get_net_devices(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Net Devices'
        geturl = '{0}/net_devices/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'connection_state', 'connection_state__in', 'id', 'id__in',
                          'is_asset', 'ipv4_address', 'ipv4_address', 'mode', 'mode__in', 'router', 'router__in',
                          'expand', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method gives a list of net devices.
    def get_net_devices_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Net Devices'
        geturl = '{0}/net_devices/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'connection_state', 'connection_state__in', 'id', 'id__in',
                          'is_asset', 'ipv4_address', 'ipv4_address', 'mode', 'mode__in', 'router', 'router__in',
                          'expand', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method gives a list of net devices for a given router.
    def get_net_devices_for_router(self, router_id, suppressprint=suppress_print):
        return self.get_net_devices(router=router_id, suppressprint=suppressprint)

    def get_net_devices_metrics_for_wan(self, suppressprint=suppress_print, **kwargs):
        ids = []
        for net_device in self.get_net_devices_all(mode='wan'):
            ids.append(net_device['id'])
        idstring = ','.join(str(x) for x in ids)
        return self.get_net_device_metrics_all(net_device__in=idstring, suppressprint=suppressprint)

    def get_net_devices_metrics_for_mdm(self, suppressprint=suppress_print, **kwargs):
        ids = []
        for net_device in self.get_net_devices_all(is_asset=True):
            ids.append(net_device['id'])
        idstring = ','.join(str(x) for x in ids)
        return self.get_net_device_metrics_all(net_device__in=idstring, suppressprint=suppressprint)

    # This method gives a list of net devices for a given router, filtered by mode (lan/wan).
    def get_net_devices_for_router_by_mode(self, router_id, mode, suppressprint=suppress_print):
        return self.get_net_devices(router=router_id, mode=mode, suppressprint=suppressprint)

    # This method gives a list of product information.
    def get_products(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Products'
        geturl = '{0}/products/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method gives a list of product information.
    def get_products_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Products (All)'
        geturl = '{0}/products/'.format(self.base_url)

        allowed_params = ['id', 'id__in', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method returns a single product by ID.
    def get_product_by_id(self, product_id):
        return self.get_products(id=product_id)[0]

    # This method returns a single product for a given model name.
    def get_product_by_name(self, product_name):
        for p in self.get_products():
            if p['name'] == product_name:
                return p
        print("ERROR: Invalid Product Name")
        return

    # This operation reboots a device.
    def reboot_device(self, router_id, suppressprint=suppress_print):
        call_type = 'Reboot Device'
        posturl = '{0}/reboot_activity/'.format(self.base_url)

        postdata = {
            'router': '{0}/routers/{1}/'.format(self.base_url, str(router_id))
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This operation reboots a group.
    def reboot_group(self, group_id, suppressprint=suppress_print):
        call_type = 'Reboot Group'
        posturl = '{0}/reboot_activity/'.format(self.base_url)

        postdata = {
            'group': '{0}/groups/{1}/'.format(self.base_url, str(group_id))
        }

        ncm = self.session.post(posturl, data=json.dumps(postdata))
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This method provides a history of device alerts. To receive device alerts, you must enable them
    # through the ECM UI: Alerts -> Settings. The info section of the alert is firmware dependent and
    # may change between firmware releases.
    def get_router_alerts(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Router Alerts'
        geturl = '{0}/router_alerts/'.format(self.base_url)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method provides a history of device alerts. To receive device alerts, you must enable them
    # through the ECM UI: Alerts -> Settings. The info section of the alert is firmware dependent and
    # may change between firmware releases.
    def get_router_alerts_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Router Alerts (All)'
        geturl = '{0}/router_alerts/'.format(self.base_url)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method provides a history of device events. To receive device logs, you must enable them on the
    # Group settings form. Enabling device logs can significantly increase the ECM network traffic from the
    # device to the server depending on how quickly the device is generating events.
    def get_router_logs(self, router_id, suppressprint=suppress_print, **kwargs):
        call_type = 'Router Logs'
        geturl = '{0}/router_logs/?router={1}'.format(self.base_url, router_id)

        allowed_params = ['created_at', 'created_at__lt', 'created_at__gt', 'created_at_timeuuid',
                          'created_at_timeuuid__in', 'created_at_timeuuid__gt', 'created_at_timeuuid__gte',
                          'created_at_timeuuid__lt', 'created_at_timeuuid__lte', 'order_by', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method provides a history of device events. To receive device logs, you must enable them on the
    # Group settings form. Enabling device logs can significantly increase the ECM network traffic from the
    # device to the server depending on how quickly the device is generating events.
    def get_router_logs_all(self, router_id, suppressprint=suppress_print, **kwargs):
        call_type = 'Router Logs (All)'
        geturl = '{0}/router_logs/?router={1}'.format(self.base_url, router_id)

        allowed_params = ['created_at', 'created_at__lt', 'created_at__gt', 'created_at_timeuuid',
                          'created_at_timeuuid__in', 'created_at_timeuuid__gt', 'created_at_timeuuid__gte',
                          'created_at_timeuuid__lt', 'created_at_timeuuid__lte', 'order_by', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method provides information about the connection state of the device with the ECM server.
    def get_router_state_samples(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Router State Samples'
        geturl = '{0}/router_state_samples/'.format(self.base_url)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method provides information about the connection state of the device with the ECM server.
    def get_router_state_samples_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Router State Samples'
        geturl = '{0}/router_state_samples/'.format(self.base_url)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method provides information about the connection state of the device with the ECM server.
    def get_router_stream_usage_samples(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Router Stream Usage Samples'
        geturl = '{0}/router_stream_usage_samples/'.format(self.base_url)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method provides information about the connection state of the device with the ECM server.
    def get_router_stream_usage_samples_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Router Stream Usage Samples'
        geturl = '{0}/router_stream_usage_samples/'.format(self.base_url)

        allowed_params = ['router', 'router_in', 'created_at', 'created_at__lt', 'created_at__gt',
                          'created_at_timeuuid', 'created_at_timeuuid__in', 'created_at_timeuuid__gt',
                          'created_at_timeuuid__gte', 'created_at_timeuuid__lt', 'created_at_timeuuid__lte',
                          'order_by', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method gives device information with associated id.
    def get_routers(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Routers'
        geturl = '{0}/routers/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'group', 'group__in', 'id', 'id__in',
                          'ipv4_address', 'ipv4_address__in', 'mac', 'mac__in', 'name', 'name__in', 'state',
                          'state__in', 'state_updated_at__lt', 'state_updated_at__gt', 'updated_at__lt',
                          'updated_at__gt', 'expand', 'limit', 'offset']
        params = self.__parse_kwargs(kwargs, allowed_params)

        ncm = self.session.get(geturl, params=params)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # This method gives device information with associated id.
    def get_routers_all(self, suppressprint=suppress_print, **kwargs):
        call_type = 'Routers (All)'
        geturl = '{0}/routers/'.format(self.base_url)

        allowed_params = ['account', 'account__in', 'group', 'group__in', 'id', 'id__in',
                          'ipv4_address', 'ipv4_address__in', 'mac', 'mac__in', 'name', 'name__in', 'state',
                          'state__in', 'state_updated_at__lt', 'state_updated_at__gt', 'updated_at__lt',
                          'updated_at__gt', 'expand', 'limit', 'offset']
        return self.__paginated_results(geturl, allowed_params, call_type, suppressprint, **kwargs)

    # This method gives device information for a given router id.
    def get_router_by_id(self, router_id, suppressprint=suppress_print):
        return self.get_routers(id=router_id, suppressprint=suppressprint)[0]

    # This method gives device information for a given router id.
    def get_router_by_name(self, router_name, suppressprint=suppress_print):
        return self.get_routers(name=router_name, suppressprint=suppressprint)[0]

    # This method gives a groups list filtered by account.
    def get_routers_for_account(self, account_id, suppressprint=suppress_print, **kwargs):
        return self.get_routers(account=account_id, suppressprint=suppressprint, **kwargs)

    # This method gives a groups list filtered by group.
    def get_routers_for_group(self, group_id, suppressprint=suppress_print, **kwargs):
        return self.get_routers(group=group_id, suppressprint=suppressprint, **kwargs)

    # This operation renames a router.
    def rename_router_by_id(self, router_id, new_router_name, suppressprint=suppress_print):
        call_type = 'Router'
        puturl = '{0}/routers/{1}/'.format(self.base_url, router_id)

        putdata = {
            'name': str(new_router_name)
        }

        ncm = self.session.put(puturl, data=json.dumps(putdata))
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This operation renames a router by name.
    def rename_router_by_name(self, existing_router_name, new_router_name, suppressprint=suppress_print):
        return self.rename_router_by_id(
            self.get_router_by_name(existing_router_name)['id'], new_router_name, suppressprint=suppressprint)

    # This operation deletes a router by ID.
    def delete_router_by_id(self, router_id, suppressprint=suppress_print):
        call_type = 'Router'
        posturl = '{0}/routers/{1}/'.format(self.base_url, router_id)

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This operation deletes a router by name.
    def delete_router_by_name(self, router_name, suppressprint=suppress_print):
        return self.delete_router_by_id(
            self.get_router_by_name(router_name)['id'], suppressprint=suppressprint)

    # Gets the results of a speed test job. The results are updated with the latest known state of the speed tests.
    def get_speed_test(self, speed_test_id, suppressprint=suppress_print):
        call_type = 'Speed Test'
        geturl = '{0}/speed_test/{1}/'.format(self.base_url, str(speed_test_id))

        ncm = self.session.get(geturl)
        result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
        return result

    # TODO
    # Creates a speed test job that queues/runs speed tests for a given list of network devices.
    # def create_speed_test(self, router_ids, suppressprint=suppress_print):
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
    #    result = self.__returnhandler(ncm.status_code, ncm.json()['data'], call_type, suppressprint)
    #    return result

    # Deletes a speed test job. Deleting a job aborts it, but any test already started on a router will finish.
    def delete_speed_test(self, speed_test_id, suppressprint=suppress_print):
        call_type = 'Speed Test'
        posturl = '{0}/speed_test/{1}'.format(self.base_url, str(speed_test_id))

        ncm = self.session.delete(posturl)
        result = self.__returnhandler(ncm.status_code, ncm.json(), call_type, suppressprint)
        return result

    # This method sets the IP Address for the Primary LAN for a given router id.
    def set_lan_ip_address(self, router_id, lan_ip, suppressprint=suppress_print):
        call_type = 'LAN IP Address'

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
