import discord
from discord.ext import commands
import random

class FindTheBallView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=15.0)
        self.winning_position = random.randint(0, 2)
        self.author = None
        self.guessed = False

    @discord.ui.button(label="الصندوق 1 📦", style=discord.ButtonStyle.secondary, row=0)
    async def box1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 0)

    @discord.ui.button(label="الصندوق 2 📦", style=discord.ButtonStyle.secondary, row=0)
    async def box2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 1)

    @discord.ui.button(label="الصندوق 3 📦", style=discord.ButtonStyle.secondary, row=0)
    async def box3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 2)

    async def check_answer(self, interaction: discord.Interaction, chosen_index):
        if self.guessed:
            await interaction.response.send_message("لقد تم اختيار صندوق بالفعل!", ephemeral=True)
            return

        self.guessed = True
        for child in self.children:
            child.disabled = True

        if chosen_index == self.winning_position:
            embed = discord.Embed(title="🎉 كرة حظ!", description=f"**{interaction.user.mention} وجد الكرة!** أنت محظوظ!", color=discord.Color.green())
        else:
            embed = discord.Embed(title="❌ خسرت!", description=f"**{interaction.user.mention} لم يجد الكرة!** الكرة كانت في الصندوق رقم {self.winning_position + 1}.", color=discord.Color.red())

        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        embed = self.message.embeds[0]
        embed.description = f"⏰ انتهى الوقت! الكرة كانت في الصندوق رقم **{self.winning_position + 1}**."
        await self.message.edit(embed=embed, view=self)


class TriviaGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="اين_الكرة", aliases=["ball", "حظ"])
    async def where_is_the_ball(self, ctx):
        embed = discord.Embed(
            title="🎾 أين الكرة؟",
            description="اختر أحد الصناديق الثلاثة! واحد فقط يحتوي على الكرة. هل حظك موفق؟",
            color=discord.Color.blurple()
        )
        view = FindTheBallView()
        view.author = ctx.author
        message = await ctx.send(embed=embed, view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(TriviaGames(bot))