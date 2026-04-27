import discord
from discord.ext import commands
import sqlite3

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_balance(self, user_id):
        conn = sqlite3.connect('data/bot.db')
        c = conn.cursor()
        c.execute("SELECT balance FROM economy WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row is None:
            return None # يعني مستخدم جديد
        return row[0]

    def update_balance(self, user_id, amount):
        current = self.get_balance(user_id)
        conn = sqlite3.connect('data/bot.db')
        c = conn.cursor()
        if current is None:
            c.execute("INSERT INTO economy (user_id, balance) VALUES (?, ?)", (user_id, 10000 + amount))
        else:
            c.execute("UPDATE economy SET balance = ? WHERE user_id = ?", (current + amount, user_id))
        conn.commit()
        conn.close()

    def parse_amount(self, amount_str):
        try:
            if 'e' in amount_str.lower():
                base, exp = amount_str.lower().split('e')
                return int(base) * (10 ** int(exp))
            return int(amount_str)
        except:
            return None

    @commands.command(name="رصيد")
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        bal = self.get_balance(member.id)
        if bal is None:
            self.update_balance(member.id, 0)
            bal = 10000
            
        embed = discord.Embed(title="💰 رصيدك في البنك", description=f"**{bal:,}** دولار", color=discord.Color.gold())
        embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else "")
        await ctx.send(embed=embed)

    @commands.command(name="تحويل")
    async def transfer(self, ctx, member: discord.Member = None, amount_str: str = None):
        if member is None or amount_str is None or member.id == ctx.author.id:
            return await ctx.send("**الاستخدام:** `-تحويل @شخص المبلغ` (مثال: `-تحويل @Moayad 1e3`)")

        amount = self.parse_amount(amount_str)
        if amount is None or amount <= 0:
            return await ctx.send("❌ مبلغ غير صحيح!")

        sender_bal = self.get_balance(ctx.author.id) or 10000
        # ضريبة 5% على التحويل
        tax = int(amount * 0.05) 
        total_deduction = amount + tax

        if sender_bal < total_deduction:
            return await ctx.send(f"❌ رصيدك لا يكفي! المبلغ + الضريبة (5%) = **{total_deduction:,}**")

        self.update_balance(ctx.author.id, -total_deduction)
        self.update_balance(member.id, amount)

        embed = discord.Embed(color=discord.Color.green())
        embed.add_field(name="✅ تم التحويل بنجاح", value=f"**{amount:,}** دولار إلى {member.mention}", inline=False)
        embed.add_field(name="💸 الضريبة (5%)", value=f"**{tax:,}** دولار", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))