class message:
    
    raw = ''           
    mtype = ''          
    statuscode = ''   
    hostname = '' 
    headertag = ''
    headervalue = ''
    data = ''

    def create_fields(self, raw_data):
        
        self.raw = raw_data
        raw_words = raw_data.split('###')
        self.mtype = raw_words.pop(0)
        self.statuscode = raw_words.pop(0)
        self.hostname = raw_words.pop(0)
        self.headertag += raw_words.pop(0)
        self.headervalue += raw_words.pop(0)
        raw_words.remove('')        
        self.data = raw_words.pop(0)

    def create_raw(self):
        
        sep = '###'
        self.raw = str(self.mtype) + sep + str(self.statuscode) + sep + str(self.hostname) + sep + str(self.headertag) + sep + str(self.headervalue) + sep + sep + str(self.data)