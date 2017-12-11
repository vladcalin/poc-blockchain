class Actions:
    """
    Messages meaning:
    
    HELLO = initial hello message. Used for blind discovery. Any node that
            receives this message must register the sender as a peer and respond
            with a HELLO_RCV
    HELLO_RCV = same as HELLO, just without the followup HELLO_RCV
    """
    HELLO = 0
    HELLO_RCV = 1
