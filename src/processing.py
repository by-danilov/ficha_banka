def filter_by_state(data, state='EXECUTED'):
    return [item for item in data if item.get('state') == state]
