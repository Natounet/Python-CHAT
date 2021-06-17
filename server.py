import socket
from threading import *
import threading
import datetime
import sys

#Couleurs
CYAN = '\033[1;36;48m'
END = '\033[1;37;0m'


#------------------------------------------ Fonctions -------------------------



def logging(message,date):
    ''' Str,str -> None
        Fonction qui s'occupe de créer les logs de conversation.'''

    with open(f'logs/{date}.log','a') as fichier:
        fichier.write(message)

    return

def receive(s):
    ''' Socket -> Str
    Reçoit les données du serveur en bytes et les converti en string '''
    return s.recv(2048).decode('utf-8')

def send(s,message):
    ''' Socket, str -> None
    Converti notre string en bytes et envoie les données au serveur'''
    s.sendall(bytes(message+'\n','utf-8'))
    return

def broadcast(conn='',message='',self=True):
    ''' Socket, Str, Bool -> None
        Etant donnée que côté client on ne sauvegarde pas ce que l'on a envoyé mais la conversation entière
        On va envoyé le message à tout le monde, y compris l'envoyeur ( sauf si self=False'''

    for clients in client_list:
        # Si l'on ne veut pas envoyé le message à l'envoyeur
        if clients == conn and self==False:
            continue
        try:
            send(clients,message)
        except: # Si le socket est mort
            clients.close()
            client_list.remove(clients)
            print(f"{conn} s'est déconnecté")



def clientthread(conn,addr, username):
    ''' Socket, ? , Str -> None
        Fonction s'occupant de chaques clients, elle est appelée à la création des threads'''
    send(conn,f"Welcome ! {username}")
    global compteur_connecte
    compteur_connecte += 1
    if (compteur_connecte == 1):
                send(conn,f"Vous êtes actuellement seul dans la salle.")

    # A chaque fois qu'on crée un thread de connexion, on affiche aux autres qu'on s'est connecté
    broadcast(conn,message=f"{temps()} - {username} s'est connecté",self=False)

    while True:
        try:
            # On attend la réception d'un message


            message = receive(conn)

            # Si on récupère un message
            if message:
                print(f"{temps()} - {addr} - {username}: {message}".rstrip())
                logging(f"{temps()} - {addr} - {username}: {message}\n",date)
                broadcast(conn,f"{temps()} - {CYAN}{username}{END}: {message}")

            # Si la connexion est rompue
            else:
                if conn in client_list:
                    client_list.remove(conn)
                    print(f"{temps()} - {addr} - {username} s'est déconnecté")
                    logging(f"{temps()} - {addr} - {username} s'est déconnecté\n",date)
                    broadcast(conn,f"{temps()} - {username} s'est déconnecté")
                    compteur_connecte -= 1
                    if (compteur_connecte == 1):
                        broadcast(conn,f"Vous êtes actuellement seul dans la salle.")
        except:
            continue


def setup():
    ''' Fonction s'occupant du setup de l'ip, du port et du nombre de connexions'''
    if len(sys.argv) < 2:
        print("Usage : server.py <PORT>")
        sys.exit()
    else:
        hostname = str("")
        port = int(sys.argv[1])
        con_max = 10

        date = datetime.datetime.now()
        date.strftime("%d/%m/%y-%H:%M:%S")

        logging(f"{temps()} - Lancement du serveur\n",date)

    return hostname,port,con_max,date

def temps():
    ''' Fonction retournant l'heure actuelle '''
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")

    return current_time



client_list = []

hostname,port,con_max,date = setup()
compteur_connecte = 0 # Nombre de connecté

# Creation of the server socket TCP/IPV4
serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# Setting up the ip and the port
serversocket.bind((hostname,port))
print(f"Server ON - Port: {port}",end='\n')


# Listen con_max connections
serversocket.listen(con_max)

while True:
    try:
        (conn, addr) = serversocket.accept()
        username = receive(conn)
        compteur_connecte
        print(f"{temps()} - {addr} - {username} s'est connecté")
        logging(f"{temps()} - {addr} - {username} s'est connecté\n", date)

        client_list.append(conn)

        # Creation of the thread
        ct = threading.Thread(target=clientthread,args=(conn,addr,username))
        ct.start()
    except KeyboardInterrupt:
        serversocket.close()
        print("Fermeture du serveur")
        sys.exit()