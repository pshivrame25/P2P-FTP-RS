class rfc_record:
    
    def __init__(self, id, title, hostname, ttl = 7200): 
        self.id = id
        self.title = title
        self.hostname = hostname
        self.ttl = ttl  

    def rfc_rec_string(self):
        sep ='*'
        rfc_rec_str = str(self.id) + sep + str(self.title) + sep + str(self.hostname) + sep + str(self.ttl)
        return rfc_rec_str



