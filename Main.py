import os
import discord
import requests
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Flask keep_alive pour Replit
app = Flask('')

@app.route('/')
def home():
    return "Bot actif !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()  # Lance le serveur Flask

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

queue = []

# 🔁 Liste des URLs à ping
ping_urls = [
    "https://46d1ad0e-bafd-4f5c-bd7c-90f6b4e49db0-00-eaj2ewrcbyrt.janeway.replit.dev"
]

# 🔁 Tâche de ping régulière
@tasks.loop(seconds=120)
async def ping_loop():
            for url in ping_urls:
                try:
                    requests.get(url)
                    print(f"✅ Ping envoyé à : {url}")
                except Exception as e:
                    print(f"⚠️ Erreur lors du ping vers {url} : {e}")
            pass

@bot.tree.command(name="joinqueue", description="Rejoindre la file d'attente du scrim Brawl Stars")
async def joinqueue(interaction: discord.Interaction):
    user = interaction.user
    if user in queue:
        await interaction.response.send_message("Tu es déjà dans la file d'attente !", ephemeral=True)
        return
    queue.append(user)
    await interaction.response.send_message(f"{user.mention} rejoint la file d'attente. ({len(queue)}/6)")
    if len(queue) >= 6:
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
        }
        for member in queue[:6]:
            overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        channel = await guild.create_text_channel(
            name="scrim-brawlstars",
            overwrites=overwrites,
            reason="Création d'un salon de scrim Brawl Stars"
        )
        await channel.send(f"Bienvenue aux joueurs : {', '.join(member.mention for member in queue[:6])} ! Préparez votre scrim.")
        del queue[:6]

@bot.tree.command(name="leavequeue", description="Quitter la file d'attente du scrim")
async def leavequeue(interaction: discord.Interaction):
    user = interaction.user
    if user in queue:
        queue.remove(user)
        await interaction.response.send_message("Tu as quitté la file d'attente.", ephemeral=True)
    else:
        await interaction.response.send_message("Tu n'es pas dans la file d'attente.", ephemeral=True)

@bot.tree.command(name="queue", description="Afficher la file d'attente actuelle")
async def show_queue(interaction: discord.Interaction):
    if not queue:
        await interaction.response.send_message("La file d'attente est vide.", ephemeral=True)
        return
    mentions = ', '.join(user.mention for user in queue)
    await interaction.response.send_message(f"File d'attente actuelle ({len(queue)} joueur(s)) : {mentions}")

@bot.tree.command(name="resetqueue", description="Vider la file d'attente (admin uniquement)")
async def reset_queue(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return
    queue.clear()
    await interaction.response.send_message("La file d'attente a été réinitialisée.")

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que Glory power league")
    try:
        synced = await bot.tree.sync()
        print(f"🔧 Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation : {e}")
    ping_loop.start()  # On lance la tâche de ping ici

bot.run(os.getenv("DISCORD_TOKEN_BOT1"))
