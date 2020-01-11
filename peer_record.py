class peer_record:
    
    def __init__(self, hostname, cookie, flag, ttl, peer_welcome_port, active_count, last_contacted):
        self.hostname = hostname
        self.cookie = cookie
        self.flag = flag
        self.ttl = ttl
        self.peer_welcome_port = peer_welcome_port
        self.active_count = active_count
        self.last_contacted = last_contacted

    def peer_string(self):
        sep ='*'
        peer_str = self.hostname + sep + str(self.cookie) + sep + str(self.flag) + sep + str(self.ttl) + sep + str(self.peer_welcome_port) + sep + str(self.active_count) + sep + str(self.last_contacted)
        return peer_str
