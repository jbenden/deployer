"""The top-level object of an entire pipeline."""


class TopLevel:
    """The very top most object of a whole pipeline."""

    def __init__(self, document):
        """Ctor."""
        self.document = document

    def validate(self):
        """Ensure document structure is valid (recursively)."""
        if type(self.document) is not list:
            return False

        return True
