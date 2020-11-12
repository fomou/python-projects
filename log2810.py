import tkinter as tk
from PIL import Image,ImageTk
from tkinter import messagebox
from collections import deque
import queue

# les classes d'exceptions
class DuplicateError(Exception):
    pass
class VertexNotExist(Exception):
    pass

#la classe Graphe elle gère tout ce qui est en rapport avec les sommets et les arrêts entre ceux-ci
class Graphe:
    #le constructeur par défaut de graphe
    def __init__(self):
        self.dict={}
        self.sommetList=[]

    """""
     méthode: ajouet_sommet
     description: ajoute un sommet dans le graphe 
     @paramètres: sommet, borne
     @retour: aucun
    """""
    def ajouter_sommet(self,sommet,borne):
        if sommet in self.dict:
            raise DuplicateError("le sommet "+str(sommet)+ " existe déjà on ne peut pas le dupliquer")

        else:
            self.dict[sommet]=[]
            self.dict[sommet].append(borne)


    """""
     méthode: ajouet_arret
     description: ajoute un arret qui relie un sommet a un autre et le coût qui est associé dans le graphe 
     @paramètres: start, end,cost
     @retour: aucun
    """""
    def ajouter_arrete(self,start,end,cost):
        if start not in self.dict:
            raise VertexNotExist("le point de depart "+str(start)+" n\'existe pas dans le graphe ")
        elif end not in self.dict:
            raise VertexNotExist("le point d\'arriver "+str(end)+" n\'existe pas dans le graphe ")

        else:
            temp=[end,cost]
            self.dict[start].append(temp)


    """
    methode: contientBorne
    description: nous indique si un sommet contient une borne de recharge
    @paramètre:sommet
    @retour: bool 
    """
    def containBorne(self,sommet):
        return self.dict[str(sommet)][0]==1

    """
    methode: trouver_borne_proche
    description: permet de trouver la borne la plus proche a partir d'un sommet donné
    @paramètre:sommet
    @retour: sommetProche 
    """
    def trouver_borne_proche(self,sommetActuel):
        distanceMin=float('inf')
        sommetActuel=str(sommetActuel)
        sommetProche=''
        for sommet in self.dict:
            distance=self.dijkstra(sommetActuel,sommet)[0]
            if distanceMin>distance and self.containBorne(sommet)==True:
                sommetProche=sommet
                distanceMin=distance
        return sommetProche

    """
    methode: dijkstra
    description: on implémente l'algorithme de Dijkstra,qui donne le chemin entre un 
        point a et un point b dans le graphe, nous renvoie une liste dont le prémier element est
        le cout du trajet et le second est la suite de sommets par lesquels il faut passer 
    @paramètre:start,end
    @retour: l[] 
    """
    def dijkstra(self,start,stop):
        start=str(start)
        stop=str(stop)
        visited=[]
        l={}
        if start not in self.dict:
            raise VertexNotExist("Le sommet ", start, " n\'existe pas")
        elif start not in self.dict:
            raise VertexNotExist("Le sommet ", stop, " n\'existe pas")
        else:
            for sommet in self.dict:
                l[sommet]=[]
                l[sommet].append(float('inf'))
                l[sommet].append([])

            #iniliation du depart
            l[start][0]=0
            l[start][1].append(start)
            while stop not in visited :
                sommetMin=0
                distanceMin=float('inf')
                for e in l :
                    if e not in visited:
                        if l[e][0] < distanceMin:
                            distanceMin=l[e][0]
                            sommetMin=e
                visited.append(sommetMin)
                neigbour=self.dict[sommetMin]
                #mttre à jour les coûts des distance
                for i in range(1,len(neigbour)):
                    if l[sommetMin][0]+neigbour[i][1]<l[neigbour[i][0]][0]:
                        l[neigbour[i][0]][0]= l[sommetMin][0]+neigbour[i][1]

                        #mettre à jour les étiquettes 
                        l[neigbour[i][0]][1].clear()
                        for a in l[sommetMin][1]:
                            l[neigbour[i][0]][1].append(a)
                        l[neigbour[i][0]][1].append(neigbour[i][0])

            return l[stop]

class GestionnaireApp:
    def __init__(self):
        self.graphe=Graphe()
        self.niveauBatterie=100
        self.tempDeCharge=10
        self.clients={}
        self.out=''

    def reinitialiserGraphe(self):
        self.graphe=Graphe()

    """
    méthode: batterieFaible
    description: permet de verifier si la batterie est en dessous du seuil critique
    @parametre: aucun
    @retour: bool
    """
    def batterieFaible(self):
        return self.niveauBatterie<=15

    def actualiserNiveauBatterie(self,temp):
        self.niveauBatterie-=temp
    """
    methode: temprRecharge 
    description: permet de recharger la batterie et calcul le temp total qui est associé à cet recharge
    @parametre:pointActuel
    @retour: temp
    """
    def tempsRecharge(self,pointActuel):

            proche=self.graphe.trouver_borne_proche(pointActuel)
            tempTrajet=self.deplacer(pointActuel,proche)
            self.out+='----> recharge '
            self.niveauBatterie=100
            return (tempTrajet+10)

    """
    permet de determiner si un point est sur le plus cheminqui mène d'un point à l'autre
    """
    def estSurChemin(self,a,b,checkPoint):

        return checkPoint in self.graphe.dijkstra(a,b)[1]

    """
    mtehode: afficherGraphe
    description: permet d'afficher le graphe sous la forme demander
    @parmetre aucun
    @retour: aucun

    """
    def afficherGraphe(self):
        string=""
        for sommet in self.graphe.dict:
            print("(",sommet,end='')
            string+='('+str(sommet)
            a=self.graphe.dict[sommet]
            print(", ",a[0],", (", end='')
            string+=", "+str(a[0])+", ("
            for i in range(1,len(a)):
                print("(",a[i][0],", ", a[i][1],")", end='')
                string+="("+str(a[i][0])+", "+str(a[i][1])+")"
                if i!=len(a)-1:
                    print(',',end='')
                    string+=','
            print("))")
            string+=('))\n')
        return string
    
    """
    methode: creerGraphe
    description: permet de créer le graphe a partir d'un fichier qui contient les information de l'arrondissement
    @parametre:nomFichier
    @retour: aucun
    """
    def creerGraphe(self,nomFichier):
        file =open(nomFichier,'r')
        temp=[]
        self.reinitialiserGraphe()
        for ligne in file:
             s=ligne.strip("\n\r")
             l=s.split(",")
             temp.append(l)

        file.close()
        index=0
        while len(temp[index])!=1:
            self.graphe.ajouter_sommet(temp[index][0],int(temp[index][1]))
            self.graphe.sommetList.append(temp[index][0])
            index+=1

        index+=1

        for i in range(index,len(temp)):
           self.graphe.ajouter_arrete(temp[i][0],temp[i][1],int(temp[i][2]))
           self.graphe.ajouter_arrete(temp[i][1],temp[i][0],int(temp[i][2]))

        return self.graphe

    """
    methode: plus court chemin 
    description: trouver le chemin le plus cour entre deux points en utilisant l'algorithme de 
                Dijkstra sur le graphe qui decrit l'arrondissements
    @parametre:a,b
    @retour: aucun
    """

    def plusCourtChemin(self,a,b):
        chemin=self.graphe.dijkstra(a,b)[1]
        duree=self.graphe.dijkstra(a,b)[0]

        string='le plus court chemin de '+a+' à '+b+' est :\n'
        string+=chemin.pop(0)
        for s in chemin:
            string+='---> '+s

        string+='\nle cout est : '+str(duree)+'\n'
        string+='le niveau de batterie est: '+str(self.niveauBatterie-duree)
        print(string)
        return string

    
    """
    méthode: deplacer
    description: permet de se deplacer d'un point a un point b et 
    @parametre: a,b
    @retour: temps
    """
    def deplacer(self,a,b):
        temp=self.graphe.dijkstra(a,b)[0]
        chemin=self.graphe.dijkstra(a,b,)[1]
        self.niveauBatterie-=temp

        for i in range(1,len(chemin)):
            self.out+='--->'+chemin[i]
        return temp

    """
    méthode: calculPourcentageBatterie
    description: calcul le niveau de la batterie sur un trajet 
    @parametre: niveauActuel, a,b
    @retour: niveauActuel
    """
    def calculPourcentageBatterie(self,niveauActuel,a,b):
        return niveauActuel-self.graphe.dijkstra(a,b)[0]

    """
    la methode: actualiserAttente
    description: cette méthode met à jour les delai des client 
    @paramtre: temp,listeClient
    @retour:aucun
    """
    def actualiserAttente(self,temp,listClient):
        for i in range(len(listClient)):
            listClient[i]['duree']-=temp

    def traiterRequete(self):
        file=open('requetes.txt')
        nb_place=[]#queue.Queue(4)

        string=''
        for ligne in file:
             s=ligne.strip("\n\r")
             l=s.split(",")
             if len(l)==1 :
                pointDeDepart=l.pop(0)

             else :
                temp={}
                temp['ID']=l[0]
                temp['depart']=l[1]
                temp['arrivee']=l[2]
                temp['duree']=int(l[3])
                self.clients['Client '+l[0]]=temp

        file.close()
        string+=pointDeDepart+'--->'


        file_client= []
        #on remplie la file FIFO
        for client in self.clients:
            file_client.append(self.clients[client])

        #pour pouvoir utiliser un file(FIFO)
        point1=file_client[0]['depart']

        string+=point1+'--->'
        start=point1
        self.out+=pointDeDepart

        temp=self.deplacer(pointDeDepart,point1)
        self.actualiserAttente(temp,file_client)

        pointArrive=[]

        while len(file_client)!=0:
  
            #pick up les clients


            client1=file_client[0]
            pointArrive.append(client1['arrivee'])
            okTotakeClient2=False
            okTotakeClient3=False
            nb_place.append(client1)

            if len(file_client)>=2 :

                
                client2=file_client[1]
                #check si on peut ajout 2e client

                #temp pour aller chercher le 2e
                temp1=self.graphe.dijkstra(client1['depart'],client2['depart'])[0]

                if self.niveauBatterie-temp<15:
                    temp1+=self.tempsRecharge(client1['depart'])
                    self.niveauBatterie=100
                    string+=client1['depart']+'---> recharge --->'

                #temp du point de depart client
                temp2=self.graphe.dijkstra(client2['depart'],client1['arrivee'])[0]

                if self.niveauBatterie-temp2<15:
                    temp2+=self.tempsRecharge(client2['depart'])
                    self.niveauBatterie=100
                    string+=' recharge --->'

                tempArri2=self.graphe.dijkstra(client1['arrivee'],client2['arrivee'])[0]

                if self.niveauBatterie-tempArri2<15:
                    temp2+=self.tempsRecharge(client1['arrivee'])
                    self.niveauBatterie=100
                    string+=client1['arrivee']+'---> recharge --->'
                

                if temp1+temp2<(client1['duree']) and temp1+temp2+tempArri2<(client2['duree']):
                    self.actualiserAttente(temp1,file_client)
                    self.deplacer(start,client2['depart'])
                    string+=client2['depart']+'--->'
                    start=client2['depart']
                    nb_place.append(client2)
                    okTotakeClient2=True

                if okTotakeClient2==True and len(file_client)>=3 :
                    client3=file_client[2]
                    temp1=self.graphe.dijkstra(client2['depart'],client3['depart'])[0]
                    if self.niveauBatterie-temp1<15:
                        temp1+=self.tempsRecharge(client2['depart'])
                        self.niveauBatterie=100
                        string+='recharge --->'

                    temp2=self.graphe.dijkstra(client3['depart'],client1['arrivee'])[0]
                    if self.niveauBatterie-temp2<15:
                        temp2+=self.tempsRecharge(client3['depart'])
                        string+=client3['depart']+'---> recharge --->'
                        self.niveauBatterie=100

                    tempArri2=self.graphe.dijkstra(client1['arrivee'],client2['arrivee'])[0]

                    if self.niveauBatterie-tempArri2<15:
                        temp2+=self.tempsRecharge(client1['arrivee'])
                        self.niveauBatterie=100
                    temparr3=self.graphe.dijkstra(client2['arrivee'],client3['arrivee'])[0]

                    if self.niveauBatterie-temparr3<15:
                        temparr3+=self.tempsRecharge(client2['arrivee'])
                        self.niveauBatterie=100

                    if temp1+temp2<client1['duree'] and temp1+temp2+tempArri2<client2['duree'] and (temp1+temp2+tempArri2+temparr3)<client3['duree']:
                        string+=client3['depart']+'--->'
                        self.deplacer(start,client3['depart'])
                        start=client3['depart']
                        okTotakeClient3=True
                        self.actualiserAttente(temp1,file_client)
                        nb_place.append(client3)
                        
    
                if okTotakeClient3==True and len(file_client)>=4 :
                    client4=file_client[3]
                    temp1=self.graphe.dijkstra(client3['depart'],client4['depart'])[0]
                    if self.niveauBatterie-temp1<15:
                        temp1+=self.tempsRecharge(client3['depart'])
                        self.niveauBatterie=100

                    temp2=self.graphe.dijkstra(client4['depart'],client1['arrivee'])[0]
                    if self.niveauBatterie-temp2<15:
                        temp2+=self.tempsRecharge(client4['depart'])
                        self.niveauBatterie=100

                    tempArri2=self.graphe.dijkstra(client1['arrivee'],client2['arrivee'])[0]

                    if self.niveauBatterie-tempArri2<15:
                        temp2+=self.tempsRecharge(client1['arrivee'])
                        self.niveauBatterie=100
                    temparr3=self.graphe.dijkstra(client2['arrivee'],client3['arrivee'])[0]

                    if self.niveauBatterie-temparr3<15:
                        temparr3+=self.tempsRecharge(client2['arrivee'])
                        self.niveauBatterie=100

                    temparr4=self.graphe.dijkstra(client3['arrivee'],client4['arrivee'])[0]

                    if self.niveauBatterie-temparr4<15:
                        temparr4+=self.tempsRecharge(client3['arrivee'])
                        self.niveauBatterie=100

                    if temp1+temp2<client1['duree'] and temp1+temp2+tempArri2<client2['duree'] and (temp1+temp2+tempArri2+temparr3)<client3['duree'] and (temp1+temp2+tempArri2+temparr3+temparr4)<client4['duree']:
                        self.deplacer(start,client4['depart'])
                        start=client4['depart']
                        okTotakeClient3=True
                        self.actualiserAttente(temp1,file_client)
                        nb_place.append(client4)

            #aller deposer les clients qui ont été embarqués
            while True:
                if len(nb_place)==0:
                    break
                c=nb_place.pop(0)
                file_client.pop(0)

                self.actualiserAttente(self.deplacer(start,c['arrivee']),file_client)
                
                string+='debarquement client'+c['ID']+'--->'
                self.out+='--->debarquement client '+c['ID']
                start=c['arrivee']
                print('le niveau de la batterie',self.niveauBatterie)
                if len(nb_place)!=0 and self.niveauBatterie-self.graphe.dijkstra(start,nb_place[0]['arrivee'])[0]<15:
                    self.actualiserAttente(self.tempsRecharge(start),file_client)
                    start=self.graphe.trouver_borne_proche(start)


            #on enleve les client dont on peut pas respecter la contrainte de temp
            for i in range(len(file_client)-1,0,-1):
                if file_client[i]['duree']<=0:
                    file_client.remove(file_client[i])  
            
        print(self.out)
        return self.out


""""
interface graphique qui utilise la bibliotheque tkinter
"""

class Interface:
    global graphe
    global gestionnaire
    gestionnaire=GestionnaireApp()
    graphe=gestionnaire.creerGraphe('arrondissements.txt')
    def __init__(self):
        self.Window=tk.Tk()
        self.Window.title("Application Uber")
        self.Window.geometry("800x800")
        menubar=tk.Menu(self.Window)
        mainMenu=tk.Menu(menubar,tearoff=0)
        mainMenu.add_command(labe="Mettre à jour",command=self.actualiser)
        mainMenu.add_command(labe="actualiser")
        mainMenu.add_command(labe="Quitter",command=self.Window.destroy)
        menubar.add_cascade(label="Fichier",menu=mainMenu)
        self.bit="question"
        menubar.add_command(label="Aide",command=self.showText)
        self.Window.config(menu=menubar)

        self.printFrame=tk.Frame(self.Window,bg='cyan',width=800,height=750)
        self.printFrame.pack(fill='both',expand=1)
        aceuil='\n\n************************* bienvenu dans l\'interface de notre TP1 de LOG2810 ********************************\n\n L\'affichage du graphe actuel est: '
        tk.Label(self.printFrame,text=aceuil,font=('Arial',11),fg='white',bg='black').pack(fill='both',expand=1)

        self.toString=gestionnaire.afficherGraphe()
        self.grapheString=tk.Message(self.printFrame,text=self.toString,font=('Arial',16))
        self.grapheString.pack(fill='both',expand=1)

        self.updateButton=tk.Button(self.Window,text="METTRE A JOUR",fg='white',bd=10,bg='green',command=self.update)
        self.updateButton.pack(fill='both',expand=1)

        self.cheminButton=tk.Button(self.Window,text=" COURT CHEMIN",bd=7,fg='white',bg='orange',command=self.trouverChemin)
        self.cheminButton.pack(fill='both',expand=1)


        self.traiterButton=tk.Button(self.Window,text=" TRAITER REQUETE",bd=4,fg='black',bg='yellow',command=self.traiterRequete)
        self.traiterButton.pack(fill='both',expand=1)

        self.exitButton=tk.Button(self.Window,text='QUITTER',underline=0,bg='red',command=self.quitter)
        self.exitButton.pack(fill='both',expand=1)

    def actualiser(self):
        self.grapheString.forget()
        self.grapheString=tk.Message(self.printFrame,text=self.toString,font=('Arial',16))
        self.grapheString.pack(fill='both',expand=1)

    def quitter(self):
        mes=messagebox.askquestion('exit app','vous etes sûr de vouloir quitter ?')
        if mes=='yes':
            self.Window.destroy()
        #canevas=tk.Canvas(self.Window,width=200,height=100)
        #canevas.grid(row=0,column=2,columnspan=5,rowspan=5)
    def showText(self):
        global text
        global helpFrame

        self.printFrame.forget()
        self.cheminButton.forget()
        self.updateButton.forget()
        self.traiterButton.forget()
        self.exitButton.forget()
        text="Bonjour! bienvenu dans notre application mini Uber!\n"
        text+="vous avez Quatre boutton si dessus qui permet de faire des opérations dont vous voulez\n\n"
        text+="1) Le bouton en vert vous permet de mettre à jour le graphe pour cela vous devez entrer le nom de votre fichier sans l'extension txt et vous verez au dessus le nouveau graphe apparaitre\n\n"
        text+="2) Le bouton en Orange  vous permet de trouver le chemin le  chemin le plus court entre deux points \n\n"
        text+="3) Le bouton en jaune  vous permet de traiter des clients contenu dans le fichier requete.txt \n\n"
        text+="4) Le bouton en Rouge  vous permet de fermer notre application un message de confirmation vous est demander \n\n"


        helpFrame=tk.Frame(self.Window,width=400,height=400)
        helpFrame.pack(fill='both',expand=1)
        text=tk.Message(helpFrame,text=text
                        ,font=('Arial',14))
        text.pack(fill='both',expand=1)

        tk.Button(helpFrame,text='OK',bd=5,bg='green',padx=10,command=self.hideMessage).pack()

    def hideMessage(self):
        helpFrame.destroy()
        self.printFrame.pack(fill='both',expand=1)
        self.updateButton.pack(fill='both',expand=1)
        self.cheminButton.pack(fill='both',expand=1)
        self.traiterButton.pack(fill='both',expand=1)
        self.exitButton.pack(fill='both',expand=1)
    def afficherInterface(self):
        self.Window.mainloop()

    def trouverChemin(self):
        global frame
        global entre1,entre2
        self.cheminButton.forget()
        self.updateButton.forget()
        self.traiterButton.forget()
        self.exitButton.forget()
        frame=tk.Frame(self.Window,width=400,height=350)
        frame.pack(fill='both',expand=1)

        entre1=tk.Entry(frame)
        entre1.grid(row=0,column=1)

        entre2=tk.Entry(frame)
        entre2.grid(row=1,column=1)

        tk.Label(frame,text='voutre point de depart :').grid(row=0,column=0)
        tk.Label(frame,text='voutre point d\'arrivée :').grid(row=1,column=0)

        tk.Button(frame,text='OK',bd=5,bg='green',padx=10,command=self.validerEntre).grid(row=2,column=0)

        tk.Button(frame,text='<< Retour',padx=10,bd=5,bg='red',command=self.retour).grid(row=2,column=3)

    def validerEntre(self):
        global depard,arrive
        try:
            depard=str(entre1.get())
            arrive=str(entre2.get())
            # if len(newGraphe.dict)!=0:
            #      graphe=newGraphe
            chemin=gestionnaire.plusCourtChemin(depard,arrive)
            # chemin+=che[1][0]
            # for i in range(1,len(che[1])):
            #     chemin+='---> '+ che[1][i]

            # chemin+='\n Le coût est : '+ str(che[0])
            lab=tk.Message(frame,text=chemin,font=('',16),bg='yellow')
            lab.grid(row=3,padx=50,pady=50,columnspan=5)

        except VertexNotExist:
            messagebox.showerror('Erreur','l\'un de vos de vos sommet n\'existe pas')


    def retour(self):
        frame.destroy()
        self.printFrame.pack(fill='both',expand=1)
        self.updateButton.pack(fill='both',expand=1)
        self.cheminButton.pack(fill='both',expand=1)
        self.traiterButton.pack(fill='both',expand=1)
        self.exitButton.pack(fill='both',expand=1)

    def update(self):
        global updateFrame
        global fileName
        global file_entry
        self.cheminButton.forget()
        self.updateButton.forget()
        self.traiterButton.forget()
        self.exitButton.forget()
        updateFrame=tk.Frame(self.Window,width=200,height=200)
        updateFrame.pack(fill='both',expand=1)

        tk.Label(updateFrame,text='Veuillez entrer le nom du fichier:').grid(row=0,column=0)
        file_entry=tk.Entry(updateFrame,bd=3)
        file_entry.grid(row=0,column=1)
        tk.Button(updateFrame,text='Creer Graphe',bd=3,command=self.creerGraphe).grid(row=2,column=0)
        updateFrame.bind("<Return>",self.creerGraphe)
        tk.Button(updateFrame,text='<< RETOUR',bg='red',justify=tk.RIGHT,command=self.exitUpdate).grid(row=2,column=2)

    def creerGraphe(self):
         global newGraphe
         newGraphe=Graphe()
         try:
             name=str(file_entry.get())+'.txt'
             newGraphe=gestionnaire.creerGraphe(name)
             self.toString=gestionnaire.afficherGraphe()
             self.grapheString.forget()
             self.grapheString=tk.Message(self.printFrame,text=self.toString,font=('Arial',16))
             self.grapheString.pack(fill='both',expand=1)
             #self.grapheString.forget()
            #  s=gestionnaire.afficherGraphe()
            #  self.grapheString=tk.Message(self.printFrame,text=s,font=('Arial',16))
            #  self.grapheString.pack(fill='both',expand=1)

         except FileNotFoundError:
            messagebox.showerror('erreur','le nom du fichier que vous avez saisi n\'est pas trouvable veuillez un autre nom de fichier')

    def exitUpdate(self):
        updateFrame.destroy()
        self.printFrame.pack(fill='both',expand=1)
        self.updateButton.pack(fill='both',expand=1)
        self.cheminButton.pack(fill='both',expand=1)
        self.traiterButton.pack(fill='both',expand=1)
        self.exitButton.pack(fill='both',expand=1)
        self.grapheString.pack(fill='both',expand=1)

    def traiterRequete(self):
        global requetFrame
        self.printFrame.forget()
        self.cheminButton.forget()
        self.updateButton.forget()
        self.traiterButton.forget()
        self.exitButton.forget()

        requetFrame=tk.LabelFrame(self.Window,text='Traitement des requete',font=('Arial',14))
        requetFrame.pack(fill='both',expand=1)

        text='le taritement des requetes contenues dans le fichier requêtes.txt est :\n\n'+gestionnaire.traiterRequete()

        tk.Message(requetFrame,text=text,font=('Arial',16),bg='yellow').pack(fill='both',expand=1)

        tk.Button(requetFrame,text='terminer',command=self.finish).pack()

    def finish(self):
        requetFrame.destroy()
        self.printFrame.pack(fill='both',expand=1)
        self.updateButton.pack(fill='both',expand=1)
        self.cheminButton.pack(fill='both',expand=1)
        self.traiterButton.pack(fill='both',expand=1)
        self.exitButton.pack(fill='both',expand=1)


if __name__=="__main__":

    # interface=Interface()
    # interface.afficherInterface()
  # photo=Image.open('icons8-shutdown-64.png')

    print('\n\n************************* bienvenu dans l\'interface de notre TP1 de LOG2810 ********************************\n\n\n')
    
    graphe=Graphe()
    gestionnaire=GestionnaireApp()
    gestionnaire.creerGraphe('arrondissements.txt')
    
    print(' (a) Mettre à jour la carte.')
    print('\n\n (b) Déterminer le plus court chemin sécuritaire. ')
    print('\n\n (c) Traiter les requêtes. ')
    print('\n\n (d) Quitter. \n\n\n')
    print('\n\n (e) utiliser interface graphique. \n\n\n')

    while True:

        print('\n\nle graphe actuel est :\n\n')
        gestionnaire.afficherGraphe()
        choix=str(input('\n\n\nVeuillez choisir une option: '))

        if choix=='d':
            break
        elif choix=='a':
            gestionnaire.reinitialiserGraphe()
            nomFichier=str(input('veuillez entrer le nom du fichier: '))
            gestionnaire.creerGraphe(nomFichier)

        elif choix=='b':
            depart=str(input('donnez le point de départ : '))
            arrive=str(input('donnez le point d\'arrivee : '))
            try:
                gestionnaire.plusCourtChemin(depart,arrive)

            except VertexNotExist:
                print('vos données ne sont pas correctes')

        elif choix=='c':
            gestionnaire.traiterRequete()

        elif choix=='e':
            print('Warning! Notre interface graphique utilise Tkinter pour pouvoir \nl\'utiliser vous devez avoir la bibliothèque tkinter\n\n')
            confir=str(input('voulez-vous continuer ? y/n'))
            if confir=='y':
                interface=Interface()
                interface.afficherInterface()
