import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ====== CONFIGURACIÓN ======
WELCOME_CHANNEL = 1441580090126368818      # canal donde se envía la bienvenida
GENERAL_CHANNEL = 1441580090126368818      # canal donde tendrá permisos de archivos
URL_SERVER = "lorest"                      # palabra clave de tu URL
RECOMMEND_1 = "<#1441580587117969468>"
RECOMMEND_2 = "<#1441568208137093172>"
# ===========================


@bot.event
async def on_ready():
    print(f"Bot listo como {bot.user}")


# ╔═══════════════════════════════╗
#   BIENVENIDA
# ╚═══════════════════════════════╝
@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(WELCOME_CHANNEL)
    if channel is None:
        return

    embed = discord.Embed(
        title="https://discord.gg/yUQUc3mS4f",
        description=f"""
👋 Welcome {member.mention}

> 🧟‍♂️ . url for pic perms  
> 🦇 . check **annc** & **faggots**

**Recommended channels:**
🔹 {RECOMMEND_1}
🔹 {RECOMMEND_2}

Members: **{member.guild.member_count}**
        """,
        colour=discord.Colour.dark_grey()
    )

    embed.set_thumbnail(url=(member.avatar.url if member.avatar else member.default_avatar.url))

    await channel.send(embed=embed)


# ╔═══════════════════════════════╗
#   DETECTAR URL EN ESTADO / BIO
# ╚═══════════════════════════════╝
@bot.event
async def on_member_update(before, after):
    texto = after.display_name.lower()

    if after.activity and isinstance(after.activity, discord.CustomActivity):
        if after.activity.name:
            texto += " " + after.activity.name.lower()

    if after.bio:
        texto += " " + after.bio.lower()

    if URL_SERVER.lower() not in texto:
        return

    print(f"{after} puso la URL, asignando permisos...")

    canal = after.guild.get_channel(GENERAL_CHANNEL)
    if canal:
        await canal.set_permissions(after, send_messages=True, attach_files=True)

    try:
        await after.send("Thanks for posting the server link; now you can send images in chat..")
    except:
        pass


# INICIO DEL BOT
bot.run(os.environ["TOKEN"])
