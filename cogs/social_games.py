import discord
from discord.ext import commands
import random

class SocialGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="حقيقة_جرأة", aliases=["tod"])
    async def truth_or_dare(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
            
        data = self.bot.data
        truths = data.get("truth_questions", ["وش أكبر غلطة سويتها؟"])
        dares = data.get("dare_questions", ["ارقص لمدة دقيقة!"])
        
        # اختيار نوع السؤال عشوائياً
        choice = random.choice(["حقيقة", "جرأة"])
        
        if choice == "حقيقة":
            question = random.choice(truths)
            color = discord.Color.blue()
            emoji = "🟦"
        else:
            question = random.choice(dares)
            color = discord.Color.red()
            emoji = "🟥"
            
        embed = discord.Embed(
            title=f"{emoji} {choice}!",
            description=f"**{member.mention}**, {question}",
            color=color
        )
        embed.set_footer(text=f"مطلوب من: {member.display_name}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SocialGames(bot))