def custom_user_has_user_role(user_data):
    if 'groups' in user_data and user_data['groups'] is not None:
        for group in user_data['groups']:
            if group.get('name') == 'user':
                return True
    return False


def custom_user_has_agent_role(user_data):
    if 'groups' in user_data and user_data['groups'] is not None:
        for group in user_data['groups']:
            if group.get('name') == 'agent':
                return True
    return False