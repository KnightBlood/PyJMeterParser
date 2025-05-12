import re

def keep_after_hash(string):
    return string.split('#')[-1] if '#' in string else string

def keep_before_question_mark(string):
    return string.split('?')[0] if '?' in string else string

def keep_after_regex(pattern, string):
    return re.sub(pattern, '', string) if re.search(pattern, string) else string