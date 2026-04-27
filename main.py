import discord
from discord.ext import commands
import json
import os
import asyncio
import sqlite3
from dotenv import load_dotenv

# تحميل المتغيرات البيئية (لقراءة التوكن بطريقة آمنة)
load_dotenv()

# إعداد الصلاحيات المطلوبة للبوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# تعريف البوت مع البريفكس (-)
bot = commands.Bot(command_prefix='-', intents=intents, help_command=None)

# إعداد قاعدة البيانات (SQLite)
def setup_db():
    conn = sqlite3.connect('data/bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS economy (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 10000)''')
    c.execute('''CREATE TABLE IF NOT EXISTS channels (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)''')
    conn.commit()
    conn.close()

setup_db()

# دالة لقراءة أسئلة JSON
def load_questions():
    try:
        with open('data/questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

bot.data = load_questions()

# فحص القناة المحددة لمنع البوت من الرد خارجها
@bot.check
async def globally_check_channel(ctx):
    if ctx.guild is None:
        return True
    conn = sqlite3.connect('data/bot.db')
    c = conn.cursor()
    c.execute("SELECT channel_id FROM channels WHERE guild_id = ?", (ctx.guild.id,))
    row = c.fetchone()
    conn.close()
    if row and row[0] != ctx.channel.id:
        return False
    return True

@bot.event
async def on_ready():
    print(f'✅ تم تسجيل الدخول كـ {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'✅ تم تحميل أوامر السلاش: {len(synced)}')
    except Exception as e:
        print(f'❌ خطأ في السلاش: {e}')

# أمر السلاش لتحديد القناة
@bot.tree.command(name="set-channel", description="حدد القناة التي سيعمل فيها البوت فقط")
@discord.app_commands.checks.has_permissions(administrator=True)
async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    conn = sqlite3.connect('data/bot.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO channels (guild_id, channel_id) VALUES (?, ?)", (interaction.guild.id, channel.id))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ تم تحديد القناة {channel.mention} كالقناة الوحيدة للبوت!", ephemeral=False)

# أمر الأوامر والمساعدة
@bot.command(name="اوامر", aliases=["أوامر", "مساعدة", "help"])
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 قائمة أوامر البوت الترفيهي",
        description="مرحباً بك! إليك جميع الأوامر المتاحة للعب والتحدي:",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else "")
    
    # فئة الإعدادات
    embed.add_field(
        name="⚙️ إعدادات الإدارة",
        value="`/set-channel` - تحديد القناة الوحيدة لعمل البوت (للإداريين فقط)",
        inline=False
    )
    
    # فئة الأوامر المالية
    embed.add_field(
        name="💰 الأوامر المالية والاقتصاد",
        value="`-رصيد` - لمعرفة رصيدك الحالي (يبدأ بـ 10,000)\n"
              "`-تحويل @شخص المبلغ` - لتحويل مبلغ لشخص (ضريبة 5%)\n"
              "`مثال:` `-تحويل @Moayad 1e3`",
        inline=False
    )
    
    # فئة ألعاب السرعة والتحدي
    embed.add_field(
        name="⚡ ألعاب السرعة والتحدي",
        value="`-اسرع` - لعبة سرعة الكتابة (أول من يكتب الكلمة يفوز)\n"
              "`-اكس @شخص` - تحدي شخص في لعبة إكس أو (X-O)\n"
              "`-زر @شخص المبلغ` - تحدي شخص في لعبة الضغط السريع برهان مالي",
        inline=False
    )
    
    # فئة الألعاب الترفيهية
    embed.add_field(
        name="🤔 ألعاب ترفيهية واجتماعية",
        value="`-خيروك` - سحب سؤال لو خيروك مع تصويت تفاعلي",
        inline=False
    )
    
    embed.set_footer(text="💡 نظام الأرقام السريع: 1e1 = 10 | 1e2 = 100 | 1e3 = 1,000 | 1e6 = 1,000,000")
    
    await ctx.send(embed=embed)

# تحميل الـ Cogs تلقائياً من مجلد cogs
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'✅ تم تحميل: {filename}')
            except Exception as e:
                print(f'❌ فشل تحميل {filename}: {e}')

async def main():
    async with bot:
        await load_cogs()
        # قراءة التوكن من البيئة السرية (لن يعمل محلياً إلا إذا وضعته في ملف .env)
        TOKEN = os.getenv("TOKEN")
        if TOKEN is None:
            print("❌ خطأ: التوكن غير موجود! تأكد من وضعه في متغيرات البيئة (Environment Variables)")
            return
        await bot.start(TOKEN)

# تشغيل البوت
if __name__ == "__main__":
    asyncio.run(main())