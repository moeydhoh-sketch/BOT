import discord
from discord.ext import commands
import random
import asyncio

class WYRView(discord.ui.View):
    def __init__(self, option1, option2, author):
        super().__init__(timeout=30.0) # ينتهي التصويت بعد 30 ثانية
        self.option1 = option1
        self.option2 = option2
        self.author = author
        self.votes1 = 0
        self.votes2 = 0
        self.voted_users = set()

    @discord.ui.button(label="الخيار الأول 🔴", style=discord.ButtonStyle.danger)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voted_users:
            await interaction.response.send_message("لقد قمت بالتصويت بالفعل!", ephemeral=True)
            return
        
        self.votes1 += 1
        self.voted_users.add(interaction.user.id)
        await interaction.response.send_message("تم تسجيل تصويتك للخيار الأول!", ephemeral=True)

    @discord.ui.button(label="الخيار الثاني 🔵", style=discord.ButtonStyle.primary)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voted_users:
            await interaction.response.send_message("لقد قمت بالتصويت بالفعل!", ephemeral=True)
            return
        
        self.votes2 += 1
        self.voted_users.add(interaction.user.id)
        await interaction.response.send_message("تم تسجيل تصويتك للخيار الثاني!", ephemeral=True)

    async def on_timeout(self):
        # عند انتهاء الوقت، تعطيل الأزرار وعرض النتيجة
        for child in self.children:
            child.disabled = True
        
        total_votes = self.votes1 + self.votes2
        if total_votes == 0:
            result_text = "لم يقم أحد بالتصويت!"
        else:
            pct1 = (self.votes1 / total_votes) * 100
            pct2 = (self.votes2 / total_votes) * 100
            result_text = f"🔴 **{self.option1}**: {pct1:.1f}% ({self.votes1} أصوات)\n🔵 **{self.option2}**: {pct2:.1f}% ({self.votes2} أصوات)"

        embed = self.message.embeds[0]
        embed.clear_fields()
        embed.add_field(name="📊 النتائج النهائية", value=result_text, inline=False)
        
        await self.message.edit(embed=embed, view=self)

class WouldYouRather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="خيروك", aliases=["wyr", "لوخيروك"])
    async def would_you_rather(self, ctx, category: str = None):
        data = self.bot.data.get("would_you_rather", {})
        
        if not data:
            await ctx.send("خطأ: لا توجد بيانات للأسئلة!")
            return

        # إذا حدد المستخدم فئة معينة
        if category:
            category = category.replace("_", " ")
            if category not in data:
                await ctx.send(f"الفئة غير موجودة! الفئات المتاحة: {', '.join(data.keys())}")
                return
            questions = data[category]
        else:
            # اختيار فئة عشوائية
            category = random.choice(list(data.keys()))
            questions = data[category]

        # اختيار سؤال عشوائي
        question = random.choice(questions)
        option1 = question["option1"]
        option2 = question["option2"]

        # تصميم الـ Embed
        embed = discord.Embed(
            title="🤔 لو خيروك بين...",
            description=f"**🔴 {option1}**\nأو\n**🔵 {option2}**",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"الفئة: {category} | الوقت المتبقي للتصويت: 30 ثانية")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else "")

        view = WYRView(option1, option2, ctx.author)
        message = await ctx.send(embed=embed, view=view)
        view.message = message # حفظ الرسالة لتحديثها لاحقاً

async def setup(bot):
    await bot.add_cog(WouldYouRather(bot))