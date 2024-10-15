import json
from datetime import datetime

def load_state(state_file, current_date_string):
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
            file_date = state.get('date', None)
            if file_date == current_date_string:
                return state
            else:
                return initialize_state(current_date_string)
    except FileNotFoundError:
        return initialize_state(current_date_string)

def save_state(state_file, current_date_string, page, total_count, in_page_count, jobs_count, stop_error):
    state = {
        'date': current_date_string,
        'page': page,
        'total_count': total_count,
        'in_page_count': in_page_count,
        'jobs_count': jobs_count,
        'stop_error': stop_error
    }
    with open(state_file, 'w') as f:
        json.dump(state, f)

def initialize_state(current_date_string):
    return {
        'date': current_date_string,
        'total_count': 0,
        'page': 1,
        'in_page_count': 0,
        'jobs_count': 0,
        'stop_error': 'False'
    }


def log_state(log_file, state_file,current_date_string):
    state=load_state(state_file,current_date_string)
    with open(log_file, 'a') as log:
        log.write(f"{datetime.now()}: {state_file} {json.dumps(state)}\n")
    state=initialize_state(current_date_string)
    save_state(state_file, current_date_string, state['page'], state['total_count'], state['in_page_count'], state['jobs_count'], state['stop_error'])



