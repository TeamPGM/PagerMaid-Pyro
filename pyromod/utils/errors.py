class AlreadyInConversationError(Exception):
    """
    Occurs when another exclusive conversation is opened in the same chat.
    """

    def __init__(self):
        super().__init__(
            "Cannot open exclusive conversation in a "
            "chat that already has one open conversation"
        )


class TimeoutConversationError(Exception):
    """
    Occurs when the conversation times out.
    """

    def __init__(self):
        super().__init__("Response read timed out")


class ListenerCanceled(Exception):
    """
    Occurs when the listener is canceled.
    """

    def __init__(self):
        super().__init__("Listener was canceled")
