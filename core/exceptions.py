class BusinessLogicError(Exception):
    """
    Exception representing any misconfiguration of our internal business logic.
    """

    def __init__(self, msg, *args: object) -> None:
        super().__init__(*args)
        self.msg = msg
