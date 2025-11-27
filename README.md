# 🤖 Bot Discord : Noru - Gestion de l'Historique et Conversation

Un bot Discord polyvalent codé en Python (`discord.py`) qui offre des fonctionnalités de gestion d'historique de commandes par utilisateur et un système de conversation arborescente simple, ainsi que des utilitaires classiques.

## 🌟 Fonctionnalités Principales

* **Historique des Messages/Commandes :** Chaque message/commande envoyé(e) par un utilisateur est enregistré(e), à l'exception de la commande `!last` elle-même, pour un historique précis.
* **Conversation Arborescente :** Un système de dialogue interactif et structuré pour engager les utilisateurs (via la commande `!help`).
* **Auto-Sauvegarde :** L'historique et l'état de la conversation sont sauvegardés automatiquement toutes les 60 secondes dans un fichier `data.json`.
* **Prefixe :** Toutes les commandes utilisent le préfixe **`!`**.

***

## ⚙️ Installation et Démarrage

Suivez ces étapes pour mettre votre bot en ligne.

### 1. Prérequis

Vous devez avoir **Python 3.10 ou supérieur** et **Git** installés.

### 2. Cloner le Dépôt

Ouvrez votre terminal et accédez à l'emplacement où vous souhaitez enregistrer le projet :

```bash
git clone [https://github.com/Berkan958/Bot-roblox.git](https://github.com/Berkan958/Bot-roblox.git)
cd Bot-roblox

### 3. Installation des Dépendances
Installez la bibliothèque discord.py :

```bash
pip install discord.py

Commandes de Conversation
Ces commandes vous permettent d'interagir avec le système de dialogue arborescent.

!last (Affiche la dernière commande/message.)
!history (Affiche les 20 dernières commandes/messages.)
!clearhistory (Vide votre historique.)
!stats (Affiche le nombre total de messages/commandes envoyés au bot.)
!ping (Teste la réactivité du bot.)
!quote (Affiche une citation aléatoire.)
!commands ou !cmds (Affiche cette liste de commandes.)
!help (Démarre ou continue la conversation.)
!answer [réponse] (Répond à la question posée par le bot.)
!reset (Réinitialise la conversation.)
!speakabout [sujet] (Vérifie si le bot peut parler d'un sujet.)