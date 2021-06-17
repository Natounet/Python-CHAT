import socket
import select 
import sys
import msvcrt
import os
import time
import datetime



# ------------------------- Functions -----------------------

def clear():
   # Mac/linux
   if os.name == 'posix':
      _ = os.system('clear')
   else:
    # Windows
      _ = os.system('cls')

def connection(ip,port,username):
    ''' Str,Int,Str -> None 
        Fonction créant la connection au serveur cible'''
        
    try: # On tente de se connecter au serveur
        s.connect((ip,port))
        
    except: # Si la connexion échoue
        print("Connection failed.")

    print(f"Connexion réussie à : {ip}:{port}")
    send(s,username) # Envoie du nom de l'utilisateur au serveur
    time.sleep(1)
    

def receive(s):
    ''' Socket -> Str 
    Reçoit les données du serveur en bytes et les converti en string '''
    return s.recv(2048).decode('utf-8')



def send(s,message):
    ''' Socket, str -> None 
    Converti notre string en bytes et envoie les données au serveur'''    
    s.sendall(bytes(message,'utf-8'))
    return

def affichage():
    ''' None -> None 
    Fonction s'occupe de l'affichage, chaque message reçu et envoyés sont enregistré dans
    liste_message. ( Log de la conversation ) qui sera à chaque fois réaffichée'''

    clear()
    print(liste_message)


# --------------------------------------- Main ----------------------

# Setup

# SI on a pas défini des arguments
if len(sys.argv) != 3:
    print("Connection au serveur par défaut : natounet.com:8888")
    ip = "natounet.com"
    port = 8888

# Si on a défini les arguments    
else:
    ip = str(sys.argv[1])
    port = int(sys.argv[2])

print("Bienvenue sur le client de chat")
username = str(input("Nom d'utilisateur : "))

# Creation of the TCP/IPV4 Socket
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
liste_message = ""

# Si on a pas défini de nom d'utilisateur
if username.rstrip() == "":
    username = "Invité"


# Connexion au serveur
connection(ip,port,username)

clear()
print(receive(s)) #Message de bienvenue


# Main
while True:
    try:
        socket_list = [ s]
        read_socket,write_socket,error_socket = select.select(socket_list,socket_list,[])
        if msvcrt.kbhit(): 
            read_socket.append(sys.stdin)

        for sockets in read_socket:
            # Si on veut recevoir un message du server
            affichage()

            # Quand on reçoit un message
            if sockets == s:
                message = receive(s)
                liste_message += (message)
                affichage()
                

            else:
                # Quand on veut envoyer un message au serveur
                message = str(input("> ")) # On récupère ce qu'on écrit dans la console
                send(s,message)
                sys.stdout.flush()
                affichage()
    except:
        print("Connexion interrompue")
        sys.exit()
