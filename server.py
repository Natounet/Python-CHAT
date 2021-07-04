import socket
from threading import *
import threading
import datetime
import sys

#Couleurs
CYAN = '\033[1;36;48m'
END = '\033[1;37;0m'

#------------------------------------------ Classes -------------------------

class User:

    def __init__(self, params, username, public_key=""):
        self.conn = params[0]
        self.addr = params[1]
        self.username = username 
        self.public_key = public_key

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

def recuperer_utilisateurs():
    ''' None -> Str 
    Récupère le nom d'utilisateur de tous les utilisateurs présents'''
    
    usernames = []
    for user in client_list:
        usernames.append(user.username)

    return usernames

def broadcast(conn='',message='',self=True):
    ''' Socket, Str, Bool -> None
        Etant donnée que côté client on ne sauvegarde pas ce que l'on a envoyé mais la conversation entière
        On va envoyé le message à tout le monde, y compris l'envoyeur ( sauf si self=False'''

    for user in client_list:
        # Si l'on ne veut pas envoyé le message à l'envoyeur
        if user.conn == conn and self==False:
            continue
        try:
            send(user.conn,message)
        except: # Si le socket est mort
            user.conn.close()
            client_list.remove(user)
            print(f"{user.conn} s'est déconnecté")



def clientthread(User):
    ''' User ( conn, addr, username, public_key) -> None
        Fonction s'occupant de chaques clients, elle est appelée à la création des threads'''
    send(conn,f"Welcome ! {User.username}")
    global compteur_connecte
    compteur_connecte += 1
    if (compteur_connecte == 1):
        send(User.conn,f"Vous êtes actuellement seul dans la salle.")
    else:
        send(User.conn,f"Il y a actuellement dans la salle : {recuperer_utilisateurs()}")
                

    # A chaque fois qu'on crée un thread de connexion, on affiche aux autres qu'on s'est connecté
    broadcast(User.conn,message=f"{temps()} - {User.username} s'est connecté",self=False)

    while True:
        try:
            # On attend la réception d'un message


            message = receive(User.conn)

            # Si on récupère un message
            if message:
                print(f"{temps()} - {User.addr} - {User.username}: {message}".rstrip())
                logging(f"{temps()} - {User.addr} - {User.username}: {message}\n",date)
                broadcast(User.conn,f"{temps()} - {CYAN}{User.username}{END}: {message}")


            # Si la connexion est rompue ( Client deconnecté )
            else:
                for user in client_list:
                    if user.conn == User.conn:
                        client_list.remove(user)
                        print(f"{temps()} - {User.addr} - {User.username} s'est déconnecté")
                        logging(f"{temps()} - {User.addr} - {User.username} s'est déconnecté\n",date)
                        broadcast(User.conn,f"{temps()} - {User.username} s'est déconnecté")
                        compteur_connecte -= 1
                        if (compteur_connecte == 1):
                            broadcast(User.conn,f"Vous êtes actuellement seul dans la salle.")
        
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


        client_list.append(User((conn,addr),username))

        # Creation of the thread
        ct = threading.Thread(target=clientthread,args=(User((conn,addr),username),))
        ct.start()
    except KeyboardInterrupt:
        serversocket.close()
        print("Fermeture du serveur")
        sys.exit()
