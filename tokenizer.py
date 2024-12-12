import re

def simple_tokenizer(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return words