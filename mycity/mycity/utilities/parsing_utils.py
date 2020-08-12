import re

"Methods for dealing with parsing text"

def escape_characters(text: str) -> str:
    """
    removes reserved characters from text
    """
    text = re.sub(r'(?<!\\)&', '&apos;', text)
    text = re.sub(r'(?<!\\)\"', '&quot;', text)
    text = re.sub(r'(?<!\\)“', '&quot;', text)
    text = re.sub(r'(?<!\\)”', '&quot;', text)
    text = re.sub(r'(?<!\\)\'', '&apos;', text)
    return text
