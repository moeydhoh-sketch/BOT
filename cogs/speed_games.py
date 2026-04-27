import discord
from discord.ext import commands
import random
import asyncio

class SpeedGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="اسرع")
    async def fast_type(self, ctx):
        words = ["تفاحة", "سيارة", "حاسوب", "مدرسة", "طائرة", "ديسكورد", "برمجة", "ذكاء", "شجاع"]
        word = random.choice(words)
        
        embed = discord.Embed(title="⌨️ لعبة السرعة!", description=f"أول من يكتب الكلمة التالية يفوز:\n# **{word}**", color=discord.Color.blue())
        embed.set_footer(text="لديك 50 ثانية فقط!")
        await ctx.send(embed=embed)
        
        def check(m):
            return m.channel == ctx.channel and m.content.strip() == word

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=50.0)
            await ctx.send(f"🎉 مبروك {msg.author.mention}! كنت أسرع واحد وفزت باللعبة!")
        except asyncio.TimeoutError:
            await ctx.send("⏰ انتهى الوقت! لم يستطع أحد كتابة الكلمة.")

async def setup(bot):
    await bot.add_cog(SpeedGames(bot))