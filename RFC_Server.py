import socket
import threading
import time
import sys
import os
from message import *
from peer_record import *
from rfc_record import *    


def handling(conn_socket, ip_addr):
    
    global list_of_rfc, list_of_rfc_file, index_of_rfc
    
    raw_data = conn_socket.recv(1024).decode() 
    i_m = message()
    i_m.create_fields(raw_data)
    print ("Message received:", raw_data,"|||\n")
    if i_m.mtype == 'RFCQuery':                                                                         
        req_rfc_id = i_m.data
        o_m = message()
        o_m.mtype = 'RFCQueryReply'
        o_m.statuscode = 'OK'
        o_m.hostname = rfc_s
        o_m.headertag = 'NoOfOccurrences'                                                           
        rfc_rec_sep = '--'
        occurrences = 0
        reply_list = ''
        for rfc_rec in index_of_rfc:                                                                         
            if req_rfc_id == str(rfc_rec.id):                                                                  
                reply_list += rfc_rec.rfc_rec_string() + rfc_rec_sep                                         
                occurrences += 1
        print ("Occurrences:",occurrences)
        o_m.headervalue = str(occurrences)                                                          
        o_m.data = reply_list
        o_m.create_raw()
        print ("Reply to RFC Query sent:", o_m.raw, "|||\n")
        conn_socket.send(o_m.raw.encode())

    elif i_m.mtype == 'GetRFC':                                                                          
        rfc_file_name = 'rfc' + i_m.data + '.txt'
        for rfc_rec in index_of_rfc:
            if i_m.data == rfc_rec.id:
               break
            else:
                pass
        file_present = False
        try:                                                                                               
            rfc_file = open(rfc_file_name, mode = 'rb')                                                    
            file_present = True
        except:
            file_present = False
        if file_present:
            o_m = message()                                                                            
            o_m.mtype = 'GetRFCReply'
            o_m.statuscode = 'OK'
            o_m.hostname = rfc_s
            o_m.headertag = ''
            o_m.headervalue = ''
            o_m.data = rfc_file.read(204800)
            o_m.create_raw()
            print ("Reply to GetRFC sent:", o_m.raw, "|||\n")
            rfc_file.close()
            conn_socket.send(o_m.raw.encode('utf-8'))
            
            rfc_rec_new = rfc_rec                                                                          
            rfc_rec_new.hostname = ip_addr
            index_of_rfc.append(rfc_rec_new)                                                                 
            print ("Length of rfc index:",len(index_of_rfc))
            list_of_rfc  = open(list_of_rfc_file, mode = 'w')
            print ("Recreating the list_of_rfc_file:")
            for rfc_rec in index_of_rfc:
                rfc_rec_str = rfc_rec.rfc_rec_string() + '--'
                print ("rfc_rec_str:", rfc_rec_str) 
                list_of_rfc.write(rfc_rec_str)
            list_of_rfc.close()
        else:                                                                                            
            o_m = message()                                                                              
            o_m.mtype = 'GetRFCReply'
            o_m.statuscode = 'ERR'
            o_m.hostname = rfc_s
            o_m.headertag = ''
            o_m.headervalue = ''
            o_m.data = ''
            o_m.create_raw()
            print ("GetRFCReply sent----------------------->|||\n")
            conn_socket.send(o_m.raw.encode())

    else:
        o_m = message()                                                                                
        o_m.mtype = 'InvalidMsgmtypeReply'
        o_m.statuscode = 'ERR'
        o_m.hostname = rfc_s
        o_m.headertag = ''
        o_m.headervalue = ''
        o_m.data = ''
        o_m.create_raw()

        conn_socket.send(o_m.raw.encode())

    conn_socket.close()                                                                                    

def update_ttl():
    global list_of_rfc_file, index_of_rfc
    past_time_secs = 0
    file_write = False
    while True:
        present_time_secs = int(time.clock())
        if present_time_secs - past_time_secs == 1:                                                         
            for rfc_rec in index_of_rfc:
                i = index_of_rfc.index(rfc_rec)
                index_of_rfc.remove(rfc_rec)
                rfc_rec.ttl = str(int(rfc_rec.ttl) - 1)
                if int(rfc_rec.ttl) <= 0:                                                                            
                    rfc_rec.flag = False
                    file_write = True
                index_of_rfc.insert(i, peer)
            if file_write:  
                list_of_rfc = open(list_of_rfc_file, mode = 'w')
                for a_rfc_rec in index_of_rfc:
                    a_rfc_rec_str = a_rfc_rec.rfc_rec_string() + '--'
                    list_of_rfc.write(a_rfc_rec_str)
                list_of_rfc.close()
                file_write = False
            past_time_secs = present_time_secs

def create_title(filename):
    rfc_file = open(filename, mode ='r')
    content = rfc_file.read()
    rfc_file.close()
    end = content.index('Abstract')
    title_end = end-2
    pointer = end
    while pointer >= 0:
        if content[pointer-3:pointer] == '\n\n\n':
            break 
        pointer-=1
    title_start = pointer
    return content[title_start:title_end]
    


list_of_rfc_file = 'list_of_rfc_file.txt'
list_of_rfc = open(list_of_rfc_file, mode = 'w')
for rfc_id in range(8643, 8653):
    rfcfile = 'rfc'+str(rfc_id)+'.txt'
    if os.path.isfile(rfcfile):
        with open(rfcfile, 'r') as content_file:
            content = content_file.read()
        list_of_rfc = open(list_of_rfc_file, mode = 'a+')
        index_of_rfc = rfc_record(rfc_id, create_title(rfcfile), socket.gethostbyname(socket.gethostname()), '7200')
        list_of_rfc.write(index_of_rfc.rfc_rec_string()+'--')
        list_of_rfc.close()

list_of_rfc = open(list_of_rfc_file, mode = 'r')                                                           
list_of_rfc_content = list_of_rfc.read()
rfc_s_index = list_of_rfc_content.split('--')                                                                     
if rfc_s_index:
    rfc_s_index = rfc_s_index[0:len(rfc_s_index)-1]
list_of_rfc.close()

index_of_rfc = []
if rfc_s_index:
    while rfc_s_index:
        rfc_str = rfc_s_index.pop(0)
        rfc_attr = rfc_str.split('*')
        rfc_rec = rfc_record(rfc_attr[0], rfc_attr[1], rfc_attr[2], rfc_attr[3])
        index_of_rfc.append(rfc_rec)

print ("\nrfc index loaded and its length is", len(index_of_rfc))

#***********************************************************************************************************************************************************************



rfc_s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rfc_s_port = 49153                                                                             
rfc_s = socket.gethostbyname(socket.gethostname())
rfc_s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
rfc_s_socket.bind((rfc_s, rfc_s_port))                                                        

rfc_s_socket.listen(1)                                                                                
print ("RFC server listening on port ",rfc_s_port,"\n")
  

past_time_secs = 0

while True:
    rfc_connection_socket, peer_addr = rfc_s_socket.accept()                                              
    print ("New connection received from:", peer_addr[0], "\n")
    rfc_connection_thread = threading.Thread(target = handling, args = (rfc_connection_socket, peer_addr[0]))  
    rfc_connection_thread.daemon = True                                                                    
    rfc_connection_thread.start()
