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


class QRCodeWebError(Exception):
    """
    Occurs when the QR code is not scanned.
    """

    def __init__(self, msg: str):
        self.msg = msg
        super().__init__("QR code not scanned")


class QRCodeWebCodeError(QRCodeWebError):
    """
    Occurs when the QR code is not scanned.
    """

    def __init__(self, code: str):
        self.code = code
        super().__init__("QR code not scanned")


class QRCodeWebNeedPWDError(QRCodeWebError):
    """
    Occurs when the account needs to be verified.
    """

    def __init__(self, hint: str):
        self.hint = hint
        super().__init__("Account needs to be verified")
