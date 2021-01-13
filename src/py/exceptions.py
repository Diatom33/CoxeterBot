# Represents any error that's on the user's fault.
class CDError(Exception):
    pass

# Error thrown when a redirect chain is encountered.
class RedirectCycle(Exception):
    pass

# Error when reading a template.
class TemplateError(Exception):
    pass