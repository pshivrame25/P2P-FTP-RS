import socket
import threading
import sys
import os 
import time
from message import *
from peer_record import *
from rfc_record import *
from itertools import chain
import os    


def P2P_registration():
    
    global RS_server, RS_port, RFC_client, rfc_s_port, cookie
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client_socket.connect((RS_server, RS_port))
    RFC_client = client_socket.getsockname()[0]
    i_m_reg = message()
    i_m_reg.statuscode = 'ERR'
    o_m_reg = message()
    o_m_reg.mtype = 'Register'
    o_m_reg.statuscode = 'OK'
    o_m_reg.hostname = RFC_client
    o_m_reg.headertag ='WelcomePort'                                                                                 
    o_m_reg.headervalue = str(rfc_s_port)
    o_m_reg.data = ''
    o_m_reg.create_raw()
    print ("\nRegistration message sent:", o_m_reg.raw,"|||\n")
    client_socket.send(o_m_reg.raw.encode())                                                            
    RS_reply = client_socket.recv(1024).decode()                                                         
    i_m_reg.create_fields(RS_reply)                                                                   
    cookie = i_m_reg.headervalue
    print ("\nRegistration reply received:", i_m_reg.raw,"|||\n")
    client_socket.close()
    time.sleep(10)                  
    return None



                                                                      
    
def gui():
    global RS_server, RS_port, RFC_client, cookie, shut
    global peer_i, index_of_rfc
    global peer_list_file, list_of_rfc_file, peer_list, list_of_rfc
    log_file_name = 'log_file.txt'
    log_file = open(log_file_name, mode = 'w')
    log_file.write('*TESTING*\n')

    

    user_input = 'a'
    print ("P2P RFC Transfer Client\n")
    print ("#######################\n")
    print ("Welcome to P2P RFC Transfer Client\n")
    for req_list_of_rfc in range(8643, 8704) :
        print ("User Menu")
        print ("PRESs R or r for requesting rfc\n")
        print ("Press Q or q to leave the service\n")
        user_input = input("Enter your choice:")
        req_rfc_id = req_list_of_rfc
        rfc_file_name = 'rfc' + str(req_rfc_id) + '.txt'
        print(rfc_file_name)
        i_m_gtrfc = message()
        found_rfc = 0
        if os.path.isfile(rfc_file_name):
            found_rfc = 1
            print ("RFC found in local peer\n")
        if user_input == 'R' or user_input == 'r':
            log_file = open(log_file_name, mode = 'a+')
            log_file.write('\n----Requested:'+str(time.process_time()))
            
            if not(found_rfc):                                                                                           
                o_m_pqy = message()
                o_m_pqy.mtype = 'PQuery'
                o_m_pqy.statuscode = 'OK'
                o_m_pqy.hostname = RFC_client
                o_m_pqy.headertag = 'Cookie'
                o_m_pqy.headervalue = str(cookie)
                o_m_pqy.data = ''
                o_m_pqy.create_raw()
                print ("PQuery message sent\n", o_m_pqy.raw)
                pquery_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                pquery_socket.connect((RS_server, RS_port))
                pquery_socket.send(o_m_pqy.raw.encode())                                                            
                RS_reply = pquery_socket.recv(1024).decode()                                                             
                pquery_socket.close()
                print ("PQuery Reply received\n", RS_reply)
                i_m_pqy = message()
                i_m_pqy.create_fields(RS_reply)
 
                peer_s_index = i_m_pqy.data.split('--')                                                          
                
                if peer_s_index:
                    peer_s_index = peer_s_index[0:len(peer_s_index)-1]

                peer_i = []

                for peer_str in peer_s_index:
                    peer_attr = peer_str.split('*')
                    peer = peer_record(peer_attr[0], peer_attr[1], peer_attr[2], peer_attr[3], peer_attr[4], peer_attr[5], peer_attr[6])
                    peer_i.append(peer)

                peer_list_file = 'peer_list_file.txt'                                                                   
                peer_list = open(peer_list_file, mode = 'w')
                for peer in peer_i:
                    peer_str = peer.peer_string()
                    peer_list.write(peer_str)
                peer_list.close()
                
                req_rfc_id = req_list_of_rfc
                rfc_file_name = 'rfc' + str(req_rfc_id)+'.txt'
                o_m_rqy = message()
                o_m_rqy.mtype = 'RFCQuery'
                o_m_rqy.statuscode = 'OK'
                o_m_rqy.hostname = RFC_client
                o_m_rqy.headertag = ''
                o_m_rqy.headervalue = ''
                o_m_rqy.data = req_rfc_id
                o_m_rqy.create_raw()

                for peer in peer_i:                                                                                  
                    print ("Trying to contact peer(RFCQuery)--->", peer.hostname)
                    conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    conn_socket.connect((peer.hostname, int(peer.peer_welcome_port)))
                    conn_socket.send(o_m_rqy.raw.encode())
                    print ("RFCQuery message sent to ",peer.hostname, "-->", o_m_rqy.raw, "|||\n")
                    i_m_rqy = message()
                    peer_reply = conn_socket.recv(1024).decode()                                                         
                    print ("RFCQuery reply received:",peer_reply,"|||\n")
                    conn_socket.close()
                    
                    i_m_rqy.create_fields(peer_reply)

                    if int(i_m_rqy.headervalue) > 0:                                                                  
                        req_rfc_s_index = i_m_rqy.data.split('--')                                               
                        req_index_of_rfc = []
                        
                        if req_rfc_s_index:
                            req_rfc_s_index = req_rfc_s_index[0:len(req_rfc_s_index)-1]
                        while req_rfc_s_index:                                                                      
                            req_rfc_attr = req_rfc_s_index.pop(0).split('*')
                            req_rfc_rec = rfc_record(req_rfc_attr[0], req_rfc_attr[1], req_rfc_attr[2], req_rfc_attr[3])
                            req_index_of_rfc.append(req_rfc_rec)
                            index_of_rfc.append(req_rfc_rec)                                                                 

                        for req_rfc_rec in req_index_of_rfc:                                                                    
                            
                            o_m_gtrfc = message()
                            o_m_gtrfc.mtype = 'GetRFC'
                            o_m_gtrfc.statuscode = 'OK'
                            o_m_gtrfc.hostname = RFC_client
                            o_m_gtrfc.headertag = ''
                            o_m_gtrfc.headervalue = ''
                            o_m_gtrfc.data = req_rfc_id
                            o_m_gtrfc.create_raw()
                            if req_rfc_rec.hostname == '192.168.0.129':                                                     #Input IP of first peer 
                                getrfc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                getrfc_socket.connect((req_rfc_rec.hostname,50012))                                         #Input port of first peer
                                getrfc_socket.send(o_m_gtrfc.raw.encode())
                            elif req_rfc_rec.hostname == '192.168.0.208':                                                     #Input IP of second peer 
                                getrfc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                getrfc_socket.connect((req_rfc_rec.hostname,1259))                                         #Input port of second peer
                                getrfc_socket.send(o_m_gtrfc.raw.encode())
                            elif req_rfc_rec.hostname == '192.168.0.208':                                                     #Input IP of third peer 
                                getrfc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                getrfc_socket.connect((req_rfc_rec.hostname,1259))                                         #Input port of third peer
                                getrfc_socket.send(o_m_gtrfc.raw.encode())
                            elif req_rfc_rec.hostname == '192.168.0.208':                                                     #Input IP of fourth peer 
                                getrfc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                getrfc_socket.connect((req_rfc_rec.hostname,1259))                                         #Input port of fourth peer
                                getrfc_socket.send(o_m_gtrfc.raw.encode())
                            elif req_rfc_rec.hostname == '192.168.0.208':                                                     #Input IP of fifth peer 
                                getrfc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                getrfc_socket.connect((req_rfc_rec.hostname,1259))                                         #Input port of fifth peer
                                getrfc_socket.send(o_m_gtrfc.raw.encode())
                            elif req_rfc_rec.hostname == '192.168.0.208':                                                     #Input IP of sixth peer 
                                getrfc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                getrfc_socket.connect((req_rfc_rec.hostname,1259))                                         #Input port of sixth peer
                                getrfc_socket.send(o_m_gtrfc.raw.encode())

                            print ("GetRFC message sent:", o_m_gtrfc.raw, "|||\n")
                                                                            
                            peer_reply = getrfc_socket.recv(204800).decode('utf-8')                                                      
                            i_m_gtrfc = message()
                            i_m_gtrfc.create_fields(peer_reply)
                            print ("GetRFC reply received from:", i_m_gtrfc.hostname, "with statuscode:",i_m_gtrfc.statuscode,"|||\n")
                            rfc_file = open(rfc_file_name, mode='w')
                            rfc_file.write(i_m_gtrfc.data)
                            rfc_file.close()
                            print('rfc found remotely\n')
                            getrfc_socket.close()
                            found_rfc = 1                                                                             
                            break
                           
                    if found_rfc:                                                                                         
                        break
                
            if found_rfc:
                log_file.write('----Retrieved:'+str(time.clock()))
                log_file.close()
                try:
                    rfc_file = open(rfc_file_name, mode = 'rb')
                    print ("\nRFC file written into local database")
                    rfc_file.close()
                except:
                    print ("Requested RFC not in memory")
            else:
                print ("Requested RFC not in database")
            list_of_rfc = open(list_of_rfc_file, mode = 'w')
            for rfc_rec in index_of_rfc:
                rfc_rec_str = rfc_rec.rfc_rec_string() + '--'
                list_of_rfc.write(rfc_rec_str)
            list_of_rfc.close()
            
        elif user_input == 'Q' or user_input == 'q':
            list_of_rfc = open(list_of_rfc_file, mode = 'w')
            for rfc_rec in index_of_rfc:                                                                          
                rfc_rec_str = rfc_rec.rfc_rec_string() + '--'
                list_of_rfc.write(rfc_rec_str)                                                                    
            list_of_rfc.close()                                                                                   
            
            o_m_leave = message()
            o_m_leave.mtype = 'Leave'
            o_m_leave.statuscode = 'OK'
            o_m_leave.hostname = RFC_client
            o_m_leave.headertag = 'Cookie'
            o_m_leave.headervalue = str(cookie)
            o_m_leave.data = ''
            o_m_leave.create_raw()
            print ("Leave message sent:", o_m_leave.raw, "|||\n")
            i_m_leave = message()
            leave_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            leave_socket.connect((RS_server, RS_port))
            leave_socket.send(o_m_leave.raw.encode())                                                       

            RS_reply = leave_socket.recv(1024).decode()                                                               
            print ("Leave reply received:", RS_reply, "|||\n")
            cookie_file = open('cookie.txt', mode = 'w+')
            cookie_file.write(cookie)
            cookie_file.close()
            log_file.close()
            shut = True
            return	
        else:
            print ("Input is not valid, please enter correct input")
            
def KeepAlive():
    past_time_secs = 0

    while True:
        present_time_secs = int(time.clock())
        if present_time_secs - past_time_secs == 7199:                                                                       
            o_m_kpa = message()
            o_m_kpa.mtype = 'KeepAlive'
            o_m_kpa.statuscode = 'OK'
            o_m_kpa.hostname = RFC_client
            o_m_kpa.headertag ='Cookie'
            o_m_kpa.headervalue = str(cookie)
            o_m_kpa.data = ''
            o_m_kpa.create_raw()
            print ("KeepAlive message sent:", o_m_kpa.raw, "|||\n")
            keepalive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            keepalive_socket.send(o_m_kpa.raw.encode())
    
            rs_reply = keepalive_socket.recv(1024).decode() 
            print ("KeepAlive reply received:", peer_reply,"|||\n" )           
            past_time_secs = present_time_secs
    
#***************************************************************************************************************************************************************

RS_server = '192.168.0.208'                                                                                                         
RS_port = 65423
rfc_s_port =49153
shut = False
cookie = '00000'
list_of_rfc_file = 'list_of_rfc_file.txt'
index_of_rfc = []

P2P_registration()                                                                                                       

display_thread = threading.Thread(target = gui(), args = '')
display_thread.start()

keepalive_thread =   threading.Thread(target = KeepAlive(), args = '')
keepalive_thread.start()

while True:
    if shut == True:
        print ("Thanks for using P2P client\nNow shutting down...")
        sys.exit(1)
