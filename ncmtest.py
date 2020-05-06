import config, ncm

n = ncm.NcmClient(config.X_CP_API_ID, config.X_CP_API_KEY, config.X_ECM_API_ID, config.X_ECM_API_KEY)

for account in n.get_accounts()['data']:
    for group in n.get_groups(account['id'])['data']:
        for router in n.get_routers_for_group(group['id'])['data']:
            print("Account Name: {}\nGroup Name: {}\nEndpoint Name: {}\n\n".format(account['name'], group['name'], router['name']))
