import re

def get_description():
    description = """
    Description here
    """
    description = re.subn(r"\n{2,}", "\n", description)[0]
    description = re.subn(r"\s{2,}", " ", description)[0]
    return description.strip()
