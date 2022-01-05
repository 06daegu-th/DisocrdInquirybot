import discord 
import asyncio 
from source import config
from datetime import datetime, timedelta
import os

user_command_time = {}
close_user_m = {}

async def go_message(client, message):
    ######################################## 문의봇 명령어 확인 부분 ########################################
    if message.content.startswith("#문의봇명령어"):
        embed = discord.Embed(title='문의봇 명령어 안내', color=0x50bcdf, timestamp=message.created_at)
        # embed.add_field(name="블랙리스트 등록", value='```!블랙 @유저태그```',inline=False)
        # embed.add_field(name="블랙리스트 제거", value='```!제거 @유저태그```',inline=False)
        embed.add_field(name="문의종료 방법", value='```!문의종료```',inline=False)
        embed.set_footer(text=" ⓒ 태형. All rights reserved", icon_url="https://cdn.discordapp.com/avatars/727076241777229854/fd20bae7647ba1aa6919d515c44f5287.png?size=128")
        await message.channel.send(embed=embed)
    ############################################ 문의 종료 부분 ############################################
    elif message.content.startswith("!문의종료"):
        channel = config.check_user_m2(message.channel.id, "")
        if not channel:
            await message.channel.purge(limit=1)
            a = await message.channel.send(embed=discord.Embed(title="ERROR", description="📢 이곳은 문의하는 채널이 아닙니다\n\n해당 메시지는 5초 뒤 삭제됩니다", color=0xff0000))
            await asyncio.sleep(5)
            await a.delete()
        else:
            close_user_m[channel] = 1
            await message.channel.send("3초 뒤 해당 유저의 문의가 종료됩니다")
            await asyncio.sleep(3)
            await message.channel.delete()
            config.delete_user(message.channel.id)
            file = discord.File(f"log/{channel}.txt")
            user = client.get_user(int(channel))
            log_channel = client.get_channel(int(config.config("log_channel")))
            embed = discord.Embed(title='SDRDev Korea 고객센터', description=f"{user.name}님 문의가 종료되었습니다 \n\n>**{user.name}**님의 질문(문의)를 통해 잘 되였을거라 믿습니다. \n\n > **더 궁금하게 있으시면 다시 여기로 연락주십시오. ", color=0x50bcdf, timestamp=message.created_at)
            embed.set_footer(text='SDRDev Korea 고객센터', icon_url=client.user.avatar_url)
            await user.send(embed=embed)
            now = datetime.now()
            embed = discord.Embed(title='{}'.format(now.strftime("%Y - %m - %d")), color=0x50bcdf, timestamp=message.created_at)
            embed.add_field(name="문의 종료 로그", value=f"문의한 유저 : <@{channel}>\n\n문의 종료 담당자 : <@{message.author.id}>", inline=True)
            embed.set_footer(text='ⓒ 태형. All rights reserved', icon_url=client.user.avatar_url)
            await log_channel.send(embed=embed)
            log = await log_channel.send(file=file)
            os.remove(f"log/{channel}.txt")
            config.check_count(channel)
            close_user_m[channel] = 0
    ############################################ 문의 답변 부분 ############################################
    else:
        user_id = config.check_user_m2(message.channel.id, "")
        if user_id:
            try:
                user = client.get_user(int(user_id))
                if user is None:
                    return await message.channel.send(embed=discord.Embed(title="ERROR", description="문의를 답변하던 중 알 수 없는 에러가 발생했습니다\n\n> ERROR CODE : 0002(NONE TYPE USER)", color=0xff0000))
            except Exception as e:
                return await message.channel.send(embed=discord.Embed(title="ERROR", description=f"문의를 답변하던 중 알 수 없는 에러가 발생했습니다\n\n> ERROR CODE : 0003({e}", color=0xff0000))
            if message.attachments:
                await message.add_reaction('♥️')
                await user.send(embed=discord.Embed(title="문의 답변", description=f"SDRDev Korea 고객센터 : {message.content}", color=0x50bcdf))
                await user.send(message.attachments[0].url)
                open(f"log/{user.id}.txt", 'a', encoding='utf-8 sig').write(f"SDRDev Korea 고객센터({message.author.name }) : {message.content} , {message.attachments[0].url}\n")
            else:
                await message.add_reaction('♥️')
                await user.send(embed=discord.Embed(title="문의 답변", description=f"SDRDev Korea 고객센터 : {message.content}", color=0x50bcdf))
                open(f"log/{user.id}.txt", 'a', encoding='utf-8 sig').write(f"SDRDev Korea 고객센터({message.author.name}) : {message.content}\n")

    ########################################문의 or 첫 문의 부분#########################################
    if message.guild is None:
        black, reason = config.check_black(message.author.id)
        if black == True:
            await message.channel.send(embed=discord.Embed(title="SDRDev Korea 문의 담당", description=f"안녕하세요 {message.author.name}님 당신은 '{reason}'의 사유로 블랙리스트에 등록되어 문의가 불가능합니다", color=0xff0000))
        else:
            user_id = config.check_user_m(message.author.id)
            try:
                close_user_m[message.author.id]
            except:
                close_user_m[message.author.id] = 0
            if close_user_m[message.author.id] == 1:
                return await message.channel.send(embed=discord.Embed(title="SDRDev Korea 고객센터", description=f"안녕하세요 {message.author.name}님 현재 전에 문의한 내용이 정리되고있습니다 잠시 후 다시 시도해주세요", color=0xff0000))
            if user_id == True: #새로운 문의자가 맞을경우
                now = datetime.now()
                try:
                    user_command_time[message.author.id]
                except:
                    user_command_time[message.author.id] = now - timedelta(seconds=5)
                if user_command_time[message.author.id] <= now:
                    if message.attachments:
                        user_command_time[message.author.id] = now + timedelta(seconds=5)
                        user_nick = ""
                        guild = client.get_guild(int(config.config("guild")))
                        guild2 = client.get_guild(int(config.config("guild2")))
                        user = guild.get_member(message.author.id)
                        if user.nick is None:
                            user_nick = message.author.name
                        else:
                            user_nick = user.nick
                        count, bool = config.check_url2(message.author.id)
                        list = ['🇨', '🇴', '🇱', '🇩']
                        for i in list:
                            await message.add_reaction(i)
                        channel = await guild2.create_text_channel(user_nick, category=client.get_channel(int(config.config("category"))))
                        if not bool:
                            embed = discord.Embed(title='SDRDev Korea 고객센터', color=0x50bcdf, timestamp=message.created_at)
                            embed.add_field(name="문의 접수", value=f"{message.author.name}님 문의접수가 완료되었습니다. 관리자의 응답을 기다려주세요\n\n 문의 내용 : {message.content}", inline=True)
                            embed.set_footer(text='SDRDev Korea 고객센터', icon_url=client.user.avatar_url)
                            embeda = discord.Embed(title='SDRDev Korea 고객센터', description="유저에게 문의가 도착했어요!" ,color=0x50bcdf, timestamp=message.created_at)
                            embeda.add_field(name="문의한 유저", value=f"{user_nick}", inline=False)
                            embeda.add_field(name="문의 내역 건수", value=f"```해당 유저는 0건의 문의 내역이 있습니다```", inline=False)
                            embeda.set_footer(text='SDRDev Korea 고객센터', icon_url=client.user.avatar_url)
                            await message.channel.send(embed=embed)
                            await channel.send(content="@everyone", embed=embeda)
                        else:
                            embed = discord.Embed(title='SDRDev Korea 고객센터', color=0x50bcdf, timestamp=message.created_at)
                            embed.add_field(name="문의 접수", value=f"{message.author.name}님 문의접수가 완료되었습니다. 관리자의 응답을 기다려주세요\n\n 문의 내용 : {message.content}", inline=True)
                            embed.set_footer(text='SDRDev Korea 고객센터', icon_url=client.user.avatar_url)
                            embeda = discord.Embed(title='SDRDev Korea 고객센터', description="유저에게 문의가 도착했어요!" ,color=0x50bcdf, timestamp=message.created_at)
                            embeda.add_field(name="문의한 유저", value=f"{user_nick}", inline=True)
                            embeda.add_field(name="문의 내역 건수", value=f"**{count}**건", inline=True)
                            embeda.set_footer(text='SDRDev Korea 고객센터', icon_url=client.user.avatar_url)
                            await message.channel.send(embed=embed)
                            await channel.send(content="@everyone", embed=embeda)
                        config.insert_user(message.author.id, channel.id)
                        await channel.send(embed=discord.Embed(title="문의", description=f"{user_nick} : {message.content}", color=0x50bcdf))
                        await channel.send(message.attachments[0].url)
                        open(f"log/{message.author.id}.txt", 'w', encoding='utf-8 sig').write(f"{user_nick} : {message.content} , {message.attachments[0].url}\n")
                    else:
                        user_command_time[message.author.id] = now + timedelta(seconds=5)
                        user_nick = ""
                        guild = client.get_guild(int(config.config("guild")))
                        guild2 = client.get_guild(int(config.config("guild2")))
                        user = guild.get_member(message.author.id)
                        if user.nick is None:
                            user_nick = message.author.name
                        else:
                            user_nick = user.nick
                        count, bool = config.check_url2(message.author.id)
                        list = ['🇨', '🇴', '🇱', '🇩']
                        for i in list:
                            await message.add_reaction(i)
                        channel = await guild2.create_text_channel(user_nick, category=client.get_channel(int(config.config("category"))))
                        if not bool:
                            embed = discord.Embed(title='SDRDev Korea 고객센터', color=0x50bcdf, timestamp=message.created_at)
                            embed.add_field(name="문의 접수", value=f"{message.author.name}님 문의접수가 완료되었습니다. 관리자의 응답을 기다려주세요\n\n 문의 내용 : {message.content}", inline=True)
                            embed.set_footer(text='SDRDev Korea 고객센터', icon_url=client.user.avatar_url)
                            embeda = discord.Embed(title='SDRDev Korea 고객센터', description="유저에게 문의가 도착했어요!" ,color=0x50bcdf, timestamp=message.created_at)
                            embeda.add_field(name="문의한 유저", value=f"{user_nick}", inline=False)
                            embeda.add_field(name="문의 내역 건수", value=f"```해당 유저는 0건의 문의 내역이 있습니다```", inline=False)
                            embeda.set_footer(text='SDRDev Korea 고객센터', icon_url=client.user.avatar_url)
                            await message.channel.send(embed=embed)
                            await channel.send(content="@everyone", embed=embeda)
                        else:
                            embed = discord.Embed(title='SDRDev Korea 고객센터', color=0x50bcdf, timestamp=message.created_at)
                            embed.add_field(name="문의 접수", value=f"{message.author.name}님 문의접수가 완료되었습니다. 관리자의 응답을 기다려주세요\n\n 문의 내용 : {message.content}", inline=True)
                            embed.set_footer(text='SDRDev Korea 고객센터', icon_url=client.user.avatar_url)
                            embeda = discord.Embed(title='SDRDev Korea 고객센터', description="유저에게 문의가 도착했어요!" ,color=0x50bcdf, timestamp=message.created_at)
                            embeda.add_field(name="문의한 유저", value=f"{user_nick}", inline=True)
                            embeda.add_field(name="문의 내역 건수", value=f"**{count}**건", inline=True)
                            embeda.set_footer(text='SDRDev Korea 고객센터', icon_url=client.user.avatar_url)
                            await message.channel.send(embed=embed)
                            await channel.send(content="@everyone", embed=embeda)
                        config.insert_user(message.author.id, channel.id)
                        await channel.send(embed=discord.Embed(title="문의", description=f"{user_nick} : {message.content}", color=0x50bcdf))
                        open(f"log/{message.author.id}.txt", 'w', encoding='utf-8 sig').write(f"{user_nick} : {message.content}\n")
                else:
                    check_time2 = user_command_time[message.author.id] - now
                    days = check_time2.days
                    hours = check_time2.seconds // 3600
                    minutes = check_time2.seconds // 60 - hours * 60
                    seconds = check_time2.seconds - hours * 3600 - minutes * 60
                    error_message = await message.reply(embed=discord.Embed(title="채팅 속도가 너무 빨라요!", description=f"첫 문의 후 다음 메시지는 {round(seconds, 1)}초 뒤에 다시 보낼 수 있어요!\n\n > 해당 메시지는 3초 뒤 삭제됩니다", color=0x50bcdf))
                    await asyncio.sleep(3)
                    return await error_message.delete()
            else:
                channel_id = config.check_user_m2(message.author.id, "channel")
                channel = client.get_channel(channel_id)
                user_nick = ""
                guild = client.get_guild(int(config.config("guild")))
                user = guild.get_member(message.author.id)
                if user.nick is None:
                    user_nick = message.author.name
                else:
                    user_nick = user.nick
                if message.attachments:
                    await message.add_reaction('♥️')
                    await channel.send(embed=discord.Embed(title="문의", description=f"{user_nick} : {message.content}", color=0x50bcdf))
                    await channel.send(message.attachments[0].url)
                    open(f"log/{message.author.id}.txt", 'a', encoding='utf-8 sig').write(f"{user_nick} : {message.content} , {message.attachments[0].url}\n")
                else:
                    await message.add_reaction('♥️')
                    await channel.send(embed=discord.Embed(title="문의", description=f"{user_nick} : {message.content}", color=0x50bcdf))
                    open(f"log/{message.author.id}.txt", 'a', encoding='utf-8 sig').write(f"{user_nick} : {message.content}\n")
