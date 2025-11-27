import discord
from discord.ext import commands
import json
import os
import random
import asyncio

TOKEN = "Votre Token Ici"

intents = discord.Intents.default()
intents.message_content = True


class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node

class LinkedHistory:
    def __init__(self):
        self.head = None
    def add(self, command: str):
        self.head = Node(command, self.head)
    def to_list(self):
        result, current = [], self.head
        while current:
            result.append(current.value)
            current = current.next
        return list(reversed(result))
    def clear(self):
        self.head = None
    @classmethod
    def from_list(cls, lst):
        linked = cls()
        for item in lst:
            linked.add(item) 
        return linked

class HistoryManager:
    """Gère l'historique des commandes pour chaque utilisateur."""
    def __init__(self):
        self.user_histories = {}
    def _get_history(self, user_id: int) -> LinkedHistory:
        uid = str(user_id)
        if uid not in self.user_histories:
            self.user_histories[uid] = LinkedHistory()
        return self.user_histories[uid]
    def record(self, user_id: int, command: str):
        self._get_history(user_id).add(command)
    def last(self, user_id: int):
        history = self._get_history(user_id)
        return history.head.value if history.head else None
    def all(self, user_id: int):
        return self._get_history(user_id).to_list()
    def clear(self, user_id: int):
        self._get_history(user_id).clear()
    def serialize(self):
        return {uid: hist.to_list() for uid, hist in self.user_histories.items()}
    def deserialize(self, data: dict):
        self.user_histories = {uid: LinkedHistory.from_list(lst) for uid, lst in data.items()}

history_manager = HistoryManager()


class ConvNode:
    def __init__(self, node_id: str, text: str, topic: str = None):
        self.id = node_id
        self.text = text
        self.topic = topic
        self.children = []
    def link(self, answer: str, child_node: "ConvNode"):
        self.children.append((answer.lower(), child_node))

class Conversation:
    def __init__(self):
        self.root = self._create_tree()
        self.user_positions = {}
        self.node_index = {}
        self._index_nodes(self.root)
    def _index_nodes(self, node: ConvNode):
        self.node_index[node.id] = node
        for _, child in node.children:
            self._index_nodes(child)
    def _create_tree(self) -> ConvNode:
        root = ConvNode("root", "Salut ! Tu veux parler de jeux vidéo, oui ou non ?", topic="jeux vidéo")
        yes_node = ConvNode("yes_gaming", "Super ! Tu préfères les jeux solo ou multi ?", topic="préférence de jeu")
        no_node = ConvNode("no_gaming", "Pas de souci, on pourra parler d'autre chose plus tard.", topic="autre")
        root.link("oui", yes_node)
        root.link("non", no_node)
        solo_node = ConvNode("solo", "Tu es plutôt joueur solo, genre RPG, aventures…", topic="jeux solo")
        multi_node = ConvNode("multi", "Tu es plutôt joueur multi, compétitif ou coopératif.", topic="jeux multi")
        yes_node.link("solo", solo_node)
        yes_node.link("multi", multi_node)
        solo_leaf = ConvNode("solo_leaf", "Conclusion : Tu es un aventurier solitaire 😎", topic="profil solo")
        multi_leaf = ConvNode("multi_leaf", "Conclusion : Tu es un joueur social et compétitif 🎮", topic="profil multi")
        solo_node.link("ok", solo_leaf)
        multi_node.link("ok", multi_leaf)
        return root
    def start(self, user_id: int) -> ConvNode:
        self.user_positions[str(user_id)] = self.root.id
        return self.root
    def reset(self, user_id: int):
        self.user_positions[str(user_id)] = self.root.id
    def current_node(self, user_id: int) -> ConvNode | None:
        node_id = self.user_positions.get(str(user_id))
        return self.node_index.get(node_id)
    def respond(self, user_id: int, answer: str) -> ConvNode | None:
        current = self.current_node(user_id) or self.start(user_id)
        answer = answer.lower().strip()
        for expected, child in current.children:
            if answer == expected:
                self.user_positions[str(user_id)] = child.id
                return child
        return None
    def topic_exists(self, topic: str) -> bool:
        topic = topic.lower().strip()
        def dfs(node: ConvNode):
            if (node.topic and topic in node.topic.lower()) or topic in node.text.lower():
                return True
            return any(dfs(child) for _, child in node.children)
        return dfs(self.root)
    def serialize(self):
        return {"positions": self.user_positions}
    def deserialize(self, data: dict):
        self.user_positions = data.get("positions", {})

conversation_manager = Conversation()

SAVE_FILE = "data.json"

def save_all():
    data = {
        "histories": history_manager.serialize(),
        "conversation": conversation_manager.serialize()
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Données sauvegardées.")

def load_all():
    if not os.path.exists(SAVE_FILE):
        print("Aucune sauvegarde trouvée, on démarre à zéro.")
        return
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    history_manager.deserialize(data.get("histories", {}))
    conversation_manager.deserialize(data.get("conversation", {}))
    print("Données chargées depuis", SAVE_FILE)


class MyBot(commands.Bot):
    async def setup_hook(self):
        asyncio.create_task(self.autosave_task())

    async def autosave_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            save_all()
            await asyncio.sleep(60)

bot = MyBot(command_prefix="!", intents=intents)
bot.remove_command("help") 


def get_command_list_message(bot_instance: commands.Bot) -> str:
    cmds = []
    prefix = bot_instance.command_prefix
    for cmd in bot_instance.commands:
        if cmd.help:
            cmds.append(f"{prefix}{cmd.name} - {cmd.help}")
        else:
            cmds.append(f"{prefix}{cmd.name}")
            
    return "Voici les commandes disponibles :\n" + "\n".join(cmds)


@bot.event
async def on_ready():
    load_all()
    print(f"Connecté en tant que {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    if message.content == bot.command_prefix:
        command_list = get_command_list_message(bot)
        await message.channel.send(command_list)
        return

    history_manager.record(message.author.id, message.content)

    await bot.process_commands(message)


@bot.command(name="commands", aliases=["cmds"])
async def list_commands(ctx: commands.Context):
    """Affiche toutes les commandes du bot"""
    command_list = get_command_list_message(bot)
    await ctx.send(command_list)


@bot.command()
async def last(ctx: commands.Context):
    """Affiche la dernière commande envoyée"""
    cmd = history_manager.last(ctx.author.id)
    await ctx.send(f"Ta dernière commande : `{cmd}`" if cmd else "Aucune commande dans ton historique.")


@bot.command()
async def history(ctx: commands.Context):
    """Affiche l'historique des commandes (max 20 dernières)"""
    cmds = history_manager.all(ctx.author.id)
    if not cmds:
        await ctx.send("Ton historique est vide.")
        return
    formatted = "\n".join(f"- {c}" for c in cmds[-20:])
    await ctx.send(f"Voici ton historique (max 20 dernières lignes) :\n```\n{formatted}```")


@bot.command()
async def clearhistory(ctx: commands.Context):
    """Vide ton historique"""
    history_manager.clear(ctx.author.id)
    await ctx.send("Ton historique a été vidé.")


@bot.command()
async def help(ctx: commands.Context):
    """Démarre ou continue une conversation"""
    node = conversation_manager.start(ctx.author.id)
    await ctx.send(node.text)


@bot.command()
async def answer(ctx: commands.Context, *, user_answer: str):
    """Répond à la conversation en cours"""
    node = conversation_manager.respond(ctx.author.id, user_answer)
    if node:
        await ctx.send(node.text)
    else:
        await ctx.send("Je n'ai pas compris ta réponse pour ce chemin. Essaie autre chose.")


@bot.command()
async def reset(ctx: commands.Context):
    """Réinitialise la conversation en cours"""
    conversation_manager.reset(ctx.author.id)
    node = conversation_manager.current_node(ctx.author.id)
    await ctx.send("Discussion réinitialisée.")
    if node:
        await ctx.send(node.text)


@bot.command()
async def speakabout(ctx: commands.Context, *, topic: str):
    """Vérifie si le bot peut parler d'un sujet (dans l'arbre de conversation)"""
    exists = conversation_manager.topic_exists(topic)
    await ctx.send("oui" if exists else "non")


@bot.command()
async def ping(ctx: commands.Context):
    """Teste la réactivité du bot (Latence)"""
    await ctx.send(f"Pong 🏓 | Latence: **{round(bot.latency * 1000)}ms**")


@bot.command()
async def stats(ctx: commands.Context):
    """Affiche le nombre total de messages/commandes que tu as envoyé"""
    all_cmds = history_manager.all(ctx.author.id)
    await ctx.send(f"Tu as envoyé **{len(all_cmds)}** messages/commandes depuis ta première connexion au bot.")


@bot.command()
async def quote(ctx: commands.Context):
    """Affiche une citation aléatoire"""
    quotes = [
        "Le succès, c’est tomber sept fois, se relever huit.",
        "Chaque grand voyage commence par un premier pas.",
        "Le code ne ment jamais, les commentaires parfois."
    ]
    await ctx.send(random.choice(quotes))


if __name__ == "__main__":
    if TOKEN == "exemple":
        print("ERREUR: Veuillez remplacer 'exemple' par votre token Discord réel dans la variable TOKEN.")
    else:
        bot.run(TOKEN)