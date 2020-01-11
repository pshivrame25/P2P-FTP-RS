import socket
import threading
import sys
import os
import time
import random
from message import *
from peer_record import *


def gen_cookie():                                                                                      
    
    global peer_i
    uniq_cookie = 1
    while True:
        r_cookie = random.randrange(start = 10000, stop = 99999, step = 1)
        for peer in peer_i:
            if r_cookie == int(peer.cookie):
                uniq_cookie = 0
        if uniq_cookie:
            break
    return r_cookie

def day_limit(peer_time_str):
    
    peer_time = time.strptime(peer_time_str, '%a %b %d %H:%M:%S %Y')                                        
    now_time = time.strptime(time.asctime(), '%a %b %d %H:%M:%S %Y')

    if now_time[7] - peer_time[7] <= 30:                                                                    
        return True
    else:
        return False


def handler(conn_socket, ip_addr):                                                                     
    
    global peer_i, peer_list_file
    raw_data = conn_socket.recv(1024).decode()
    print ("New message received\n",raw_data)
    i_m = message()
    i_m.create_fields(raw_data)
    
    new_peer_flag = 0   
    if i_m.mtype == 'Register':                                                                     
        new_peer_flag = 1
        for peer in peer_i:                                                                         
            if i_m.hostname == peer.hostname:
                old_peer_i = peer_i.index(peer)
                new_peer_flag = 0
            
        if new_peer_flag:
            peer_welcome_port = i_m.headervalue
            last_contacted = time.asctime()
            active_count = 1                                                                            
            flag = True
            ttl = 7200
            cookie = gen_cookie()
            new_peer = peer_record(i_m.hostname, cookie, flag, ttl, peer_welcome_port, active_count, last_contacted)              
            peer_i.append(new_peer)                                                                
            peer_list = open(peer_list_file, mode = 'a')
            peer_str = new_peer.peer_string() + '--'
            peer_list.write(peer_str)
            peer_list.close()
        else:                                                                                          
            peer = peer_i[old_peer_i]
            peer_i.remove(peer)
            peer.flag = True
            cookie = peer.cookie
            peer.peer_welcome_port = i_m.headervalue
            if day_limit(peer.last_contacted):
               peer.active_count = int(peer.active_count)+ 1
            else:
               peer.active_count = 1
            peer.last_contacted = time.asctime()
            peer_i.insert(old_peer_i, peer)
            peer_list = open(peer_list_file, mode = 'w')
            for peer in peer_i:
                peer_str = peer.peer_string() + '--'
                peer_list.write(peer_str)
            peer_list.close()
            
        o_m_reg = message()                                                                        
        o_m_reg.mtype = 'RegisterReply'
        o_m_reg.statuscode = 'OK'
        o_m_reg.hostname = server
        o_m_reg.headertag='Cookie'
        o_m_reg.headervalue=str(cookie)
        o_m_reg.data = ''
        o_m_reg.create_raw()
        print ("RegisterReply sent:", o_m_reg.raw,"@@\n")        
        conn_socket.send(o_m_reg.raw.encode())                                                       
    
    elif i_m.mtype == 'PQuery':
        o_m_pqy = message()
        o_m_pqy.mtype = 'PQueryReply'
        o_m_pqy.statuscode = 'OK'
        o_m_pqy.hostname = server
        o_m_pqy.headertag=''
        o_m_pqy.headervalue=''
        peer_sep = '--'
        peer_reply = ''

        peer_list = open(peer_list_file, mode = 'r+')                                                           
        peer_s_index = [line.split('--') for line in peer_list.readlines()]                                
        if peer_s_index:
            peer_s_index = peer_s_index[0]
            peer_s_index = peer_s_index[0:len(peer_s_index)-1]

        peer_list.close()

        peer_i = []

        while peer_s_index:
            peer_str = peer_s_index.pop(0)
            peer_attr = peer_str.split('*')
            peer = peer_record(peer_attr[0], peer_attr[1], peer_attr[2], peer_attr[3], peer_attr[4], peer_attr[5], peer_attr[6])
            peer_i.append(peer)
        for peer in peer_i:                                                                    #
            if peer.flag == 'True':
                if peer.hostname != i_m.hostname:
                    peer_reply += peer.peer_string() + str(len(peer_i)) + peer_sep                                     
        o_m_pqy.data = peer_reply
        o_m_pqy.create_raw()
        print ("PQueryReply sent:", o_m_pqy.raw,"@@\n")
        conn_socket.send(o_m_pqy.raw.encode())
			
    elif i_m.mtype == 'keepAlive':                                                                   
        peer_list = open(peer_list_file, mode = 'w')
        for peer in peer_i:
            if i_m.hostname == peer.hostname:                                                       
                i = peer_i.index(peer)
                peer_i.remove(peer)
                peer.ttl = 7200
                peer.flag = True
                peer.active_count += 1
                peer_i.insert(i, peer)
            peer_str = peer.peer_string() + '--'
            peer_list.write(peer_str)
        peer_list.close()

        o_m = message()
        o_m.type = 'keepAliveReply'
        o_m.statuscode = 'OK'
        o_m.hostname = server
        o_m.headertag = ''
        o_m.headervalue = ''
        o_m.data = ''
        o_m.create_raw()		    
        print ("keepAliveReply sent:", o_m.raw,"@@\n")
        conn_socket.send(o_m.raw.encode())

    elif i_m.mtype == 'Leave':
        peer_list = open(peer_list_file, mode = 'w')
        for peer in peer_i:
            if i_m.hostname == peer.hostname:                                                  
                i = peer_i.index(peer)
                peer_i.remove(peer)
                peer.flag = False
                peer_i.insert(i, peer)
            peer_str = peer.peer_string() + '--'
            peer_list.write(peer_str)
        peer_list.close()
        o_m = message()
        o_m.type = 'LeaveReply'
        o_m.statuscode = 'OK'
        o_m.hostname = server
        o_m.headertag = ''
        o_m.headervalue = ''
        o_m.data = ''
        o_m.create_raw()		    
        print ("LeaveReply sent:\n", o_m.raw,"@@\n")
        conn_socket.send(o_m.raw.encode())
        
    conn_socket.close()
    return None                                                                                       

def update_ttl():
    global peer_list_file, peer_i
    past_time_secs = 0
    file_write = False
    while True:
        present_time_secs = int(time.clock())
        if present_time_secs - past_time_secs == 1:                                                         
            for peer in peer_i:
                i = peer_i.index(peer)
                peer_i.remove(peer)
                peer.ttl = str(int(peer.ttl) - 1)
                if int(peer.ttl) <= 0:                                                                            
                    peer.flag = False
                    file_write = True
                peer_i.insert(i, peer)
            if file_write:  
                peer_list = open(peer_list_file, mode = 'w')
                for a_peer in peer_i:
                    a_peer_str = a_peer.peer_string() + '--'
                    peer_list.write(a_peer_str)
                peer_list.close()
                file_write = False
            past_time_secs = present_time_secs



global peer_i, peer_list_file
peer_list_file = 'peer_list_file.txt'
try:
    peer_list = open(peer_list_file, mode = 'r+')                                                           
    peer_s_index = [line.split('--') for line in peer_list.readlines()]                                
    if peer_s_index:
        peer_s_index = peer_s_index[0]
        peer_s_index = peer_s_index[0:len(peer_s_index)-1]

    peer_list.close()

    peer_i = []

    while peer_s_index:
        peer_str = peer_s_index.pop(0)
        peer_attr = peer_str.split('*')
        peer = peer_record(peer_attr[0], peer_attr[1], peer_attr[2], peer_attr[3], peer_attr[4], peer_attr[5], peer_attr[6])
        peer_i.append(peer)
except:
    peer_list = open(peer_list_file, mode ='w')
    peer_list.close()
    peer_i = []

#************************************************************************************************************************************************************************



global server, port
server = '192.168.0.152'
port = 65423

ttl_thread = threading.Thread(target = update_ttl, args = '')
ttl_thread.start()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((server, port))                                                                     
server_socket.listen(1)                                                                                
print ("Server listening on ", port,"...")
while True:
    connection_socket, peer_addr = server_socket.accept()                                               
    print ("New connection received from ", peer_addr[0])
    connection_thread = threading.Thread(target = handler, args = (connection_socket, peer_addr[0]))    
    connection_thread.daemon = True                                                                    
    connection_thread.start()
