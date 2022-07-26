import random
import discord
from discord.ext import commands, vbu, tasks
import asyncio
from datetime import datetime as dt, timedelta


class Draco(vbu.Cog):
    cat_trivia = {
        "What is the proper term for a group of kittens?": [
            "Kine",
            "Kettle",
            "Kaboodle",
            "Kindle",
        ],
        "All cats are born with what color eyes?": [
            "Green",
            "Black",
            "Pink",
            "Blue",
        ],
        "What percentage of a cat's bones are in its tail?": [
            "There are no bones in a cat's tail",
            "2%",
            "20%",
            "10%",
        ],
        "What is it called when a cat kneads the ground?": [
            "Sneegling",
            "Rubbing",
            "Kneading",
            "Snurgling",
        ],
        "How many different sounds can a cat make?": [
            "150",
            "10",
            "27",
            "100",
        ],
        "How many breeds of domestic cat are there worldwide?": [
            "280",
            "210",
            "140",
            "70",
        ],
        "What year was the first major cat show held in the United States?": [
            "1842",
            "1921",
            "1895",
            "1952",
        ],
        "What is the normal body temperature of a cat?": [
            "94 degrees",
            "106 degrees",
            "98 degrees",
            "102 degrees",
        ],
        "What breed of cat has a reputation for being cross-eyed?": [
            "Persian",
            "Egyptian Mau",
            "Himalayan",
            "Siamese",
        ],
        "If a male cat is both orange and black, he is probably ...?": [
            "Blind",
            "Schizophrenic",
            "Deaf",
            "Sterile",
        ],
        "What breed of cat has no tail?": [
            "La Perm",
            "Singapura",
            "Snowshoe",
            "Manx",
        ],
        "What breed of domestic cat has the longest fur?": [
            "Tonkinese",
            "Himalayan",
            "Sphynx",
            "Persian",
        ],
        "Which U. S. city had a cat for a mayor for almost 20 years?": [
            "Jacksboro, Texas",
            "Warm River, Idaho",
            "Gardner, Kansas",
            "Talkeetna, Alaska",
        ],
        "Which country has more cats per person than any other country in the world?": [
            "Djibouti",
            "Denmark",
            "United States",
            "New Zealand",
        ],
        "How many cats did Abraham Lincoln have in the White House?": [
            "1",
            "2",
            "3",
            "4",
        ],
        "What skill do cats develop when playing with yarn/toys?": [
            "Finding Food",
            "Socializing",
            "Mating",
            "Hunting",
        ],
        "What is a group of cats called?": [
            "Felis",
            "Chowder",
            "Cluster",
            "Clowder",
        ],
        "What is the extreme fear of cats called?": [
            "Consecotaleophobia",
            "Anatidaephobia",
            "Katsaridaphobia",
            "Ailurophobia",
        ],
        "What is the largest breed of cat?": [
            "Ragdoll",
            "British Shorthair",
            "Savananah",
            "Maine Coon",
        ],
        "What percent of people identify as cat people?": [
            "27.9%",
            "34.6%",
            "48.2%",
            "11.5%",
        ],
    }
    naps = []
    trivia_cooldown = []
    currently_petting = []
    trivia_time = None
    draco_worshippers = []
    # Start the loop when the cog is started

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.nap_loop.start()
        self.food_loop.start()
        self.trivia_loop.start()

    # When the cog is turned off, turn the loop off
    def cog_unload(self):
        self.nap_loop.cancel()
        self.food_loop.cancel()
        self.trivia_loop.cancel()

    # Every hour, everyone gets a cast as long as they have less than 50
    @tasks.loop(hours=24)
    async def nap_loop(self):
        print("started")
        for i in range(3):
            timestart = dt.utcnow() - timedelta(minutes=random.randint(600, 1440))
            timeend = timestart + timedelta(minutes=10)
            print(timestart, "\n", timeend)
            self.naps.append((timestart, timeend))

    # Wait until the bot is on and ready and not just until the cog is on
    @nap_loop.before_loop
    async def before_nap_loop(self):
        await self.bot.wait_until_ready()

    # Every hour, everyone gets a cast as long as they have less than 50

    @tasks.loop(hours=1)
    async def food_loop(self):
        print("started")
        async with vbu.Database() as db:
            user_info = await db("""SELECT * FROM draco_stats""")
            if dt.utcnow().hour > 20:
                for user in user_info:
                    if user['feed_time'] + timedelta(hours=15) < dt.utcnow() and user['affection_meter'] > 0:
                        affection_removed = round(.05 *
                                                  user['affection_meter'])
                        await db("""UPDATE draco_stats SET affection_meter = affection_meter - $2 WHERE user_id = $1""",
                                 user["user_id"],
                                 affection_removed)
        for user in user_info:
            if user['user_id'] in self.draco_worshippers and user['affection_meter'] < 150:
                self.draco_worshippers.remove(user['user_id'])

    # Wait until the bot is on and ready and not just until the cog is on

    @food_loop.before_loop
    async def before_food_loop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=10)
    async def trivia_loop(self):
        self.trivia_cooldown = []
        self.trivia_time = dt.utcnow() + timedelta(minutes=10)

    # Wait until the bot is on and ready and not just until the cog is on
    @trivia_loop.before_loop
    async def before_trivia_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def draco(self, ctx: commands.Context):
        love_message = None
        love = 0
        hat_dict = {
            "": {
                "idle": "https://cdn.discordapp.com/attachments/949503245640933418/965612573246496788/draco_idle-export.gif",
                "sleep": "https://cdn.discordapp.com/attachments/949503245640933418/961064266838982656/draco_sleep-export.gif",
                "hungry": "https://cdn.discordapp.com/attachments/949503245640933418/962448669024591882/draco_hungry.gif",
                "pet": "https://cdn.discordapp.com/attachments/949503245640933418/965463679514587176/draco_pet-export.gif",
                "stab": "https://cdn.discordapp.com/attachments/949503245640933418/962893569549553695/draco_stab.gif",
            },
            "_cowboy_hat": {
                "idle": "https://cdn.discordapp.com/attachments/949503245640933418/963731409065902090/draco_idle-export_cowboy_hat.gif",
                "sleep": "https://cdn.discordapp.com/attachments/949503245640933418/963731409657270312/draco_sleep-export_cowboy_hat.gif",
                "hungry": "https://cdn.discordapp.com/attachments/949503245640933418/963731408700981258/draco_hungry_cowboy_hat.gif",
                "pet": "https://cdn.discordapp.com/attachments/949503245640933418/963731409372074014/draco_pet-export_cowboy_hat.gif",
                "stab": "https://cdn.discordapp.com/attachments/949503245640933418/963731409942507520/draco_stab_cowboy_hat.gif",
            },
            "_astronaut_helmet": {
                "idle": "https://cdn.discordapp.com/attachments/949503245640933418/963743514548645888/draco_idle-export_astronaut_helmet.gif",
                "sleep": "https://cdn.discordapp.com/attachments/949503245640933418/965451977897177098/draco_sleep-export_astronaut_helmet.gif",
                "hungry": "https://cdn.discordapp.com/attachments/949503245640933418/963743513953067018/draco_hungry_astronaut_helmet.gif",
                "pet": "https://cdn.discordapp.com/attachments/949503245640933418/963743514817097748/draco_pet-export_astronaut_helmet.gif",
                "stab": "https://cdn.discordapp.com/attachments/949503245640933418/963743515450417152/draco_stab_astronaut_helmet.gif",
            },
            "_aqua_hat": {
                "idle": "https://cdn.discordapp.com/attachments/949503245640933418/965007793990037504/draco_idle-export_aqua_hat.gif",
                "sleep": "https://cdn.discordapp.com/attachments/949503245640933418/965451977658073088/draco_sleep-export_aqua_hat.gif",
                "hungry": "https://cdn.discordapp.com/attachments/949503245640933418/964733232719462480/draco_hungry_aqua_hat.gif",
                "pet": "https://cdn.discordapp.com/attachments/949503245640933418/965007794308776007/draco_pet-export_aqua_hat.gif",
                "stab": "https://cdn.discordapp.com/attachments/949503245640933418/964733234321702912/draco_stab_aqua_hat.gif",
            },
            "_crab_hat": {
                "idle": "https://cdn.discordapp.com/attachments/949503245640933418/965007301582917632/draco_idle-export_crab_hat.gif",
                "sleep": "https://cdn.discordapp.com/attachments/949503245640933418/965451978182377502/draco_sleep-export_crab_hat.gif",
                "hungry": "https://cdn.discordapp.com/attachments/949503245640933418/965007301343846460/draco_hungry_crab_hat.gif",
                "pet": "https://cdn.discordapp.com/attachments/949503245640933418/965007301876543549/draco_pet-export_crab_hat.gif",
                "stab": "https://cdn.discordapp.com/attachments/949503245640933418/965007302509854790/draco_stab_crab_hat.gif",
            },
            "_crown": {
                "idle": "https://cdn.discordapp.com/attachments/949503245640933418/965451417752068136/draco_idle-export_crown.gif",
                "sleep": "https://cdn.discordapp.com/attachments/949503245640933418/965451418834174012/draco_sleep-export_crown.gif",
                "hungry": "https://cdn.discordapp.com/attachments/949503245640933418/965451417345200128/draco_hungry_crown.gif",
                "pet": "https://cdn.discordapp.com/attachments/949503245640933418/965451418242797568/draco_pet-export_crown.gif",
                "stab": "https://cdn.discordapp.com/attachments/949503245640933418/965451419207491644/draco_stab_crown.gif",
            },
        }
        hat_choice = ""
        placement_year = (dt.utcnow() - timedelta(hours=1))
        async with vbu.Database() as db:
            user_info = await db("""SELECT * FROM draco_stats WHERE user_id = $1""",
                                 ctx.author.id
                                 )
            if not user_info:
                user_info = await db(f"""INSERT INTO draco_stats (user_id, pet_time, feed_time, affection_meter, hunt_time) VALUES ($1, $2, $2, 0, $2) RETURNING *""",
                                     ctx.author.id,
                                     placement_year)

        affection_points = user_info[0]["affection_meter"]
        pet_time = user_info[0]["pet_time"]
        feed_time = user_info[0]["feed_time"]
        hunt_time = user_info[0]["hunt_time"]
        affection_meter = discord.File(
            f"C:/Users/JT/Pictures/gift/affection_bar_{affection_points}.png")
        await ctx.send(file=affection_meter)

        sleeping_check = False
        draco_asleep = False
        if dt.utcnow().hour < 10:
            draco_asleep = True
            sleeping_check = True
        for x in self.naps:
            print(x[0], "\n", x[1])
            if dt.utcnow() > x[0] and dt.utcnow() < x[1]:
                draco_asleep = True
                sleeping_check = True
        print(dt.utcnow().hour)
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Pet Draco", custom_id="pet"
                ),
                discord.ui.Button(
                    label="Stop Petting", custom_id="stop_pet"
                ),
                discord.ui.Button(
                    label="Feed Draco", custom_id="feed_draco"
                ),
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Love On Draco (25 Affection)", custom_id="reward_1", style=discord.ButtonStyle.primary
                ),
                discord.ui.Button(
                    label="Draco Stabs Someone (50 Affection)", custom_id="reward_2", style=discord.ButtonStyle.primary
                ),
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Cat Trivia (75 Affection)", custom_id="reward_3", style=discord.ButtonStyle.success
                ),
                discord.ui.Button(
                    label="Change Draco's Hat (100 Affection)", custom_id="reward_4", style=discord.ButtonStyle.success
                ),
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Draco Hunts (125 Affection)", custom_id="reward_5", style=discord.ButtonStyle.danger
                ),
                discord.ui.Button(
                    label="Worship Draco (150 Affection)", custom_id="reward_6", style=discord.ButtonStyle.danger
                ),
            ),
            discord.ui.ActionRow(
                discord.ui.Button(
                    label="Check Affection", custom_id="check_affection"
                ),
                discord.ui.Button(
                    label="Click for Help!", custom_id="help"
                ),
            ),
        )

        draco_status = "idle"
        components.get_component("stop_pet").disable()
        components.get_component("feed_draco").disable()
        for i in range(25, 175, 25):
            if affection_points < i:
                reward_number = f"reward_{int(i/25)}"
                components.get_component(reward_number).disable()
        embed = discord.Embed(title='Draco The Beautiful Cat')
        if ctx.author.id in self.draco_worshippers:
            components.get_component('reward_6').disable()
        if sleeping_check:
            components.get_component("pet").disable()
            components.get_component("reward_1").disable()
            embed.add_field(name="Draco Is Sleeping",
                            value="Please check in later!")
            draco_status = "sleep"
        elif (feed_time + timedelta(hours=15)) < dt.utcnow():
            draco_status = "hungry"
            components.get_component("feed_draco").enable()
        embed.set_image(url=hat_dict[hat_choice][draco_status])
        embed.add_field(name="Draco Worshippers", value=", ".join([
            f"<@{i}>" for i in self.draco_worshippers]) + " love draco a lot!", inline=False)
        draco_message = await ctx.send(embed=embed, components=components, allowed_mentions=discord.AllowedMentions.none())

        def button_check(payload):
            if payload.message.id != draco_message.id:
                return False
            return payload.user.id == ctx.author.id

        while True:
            if dt.utcnow().hour < 10:
                draco_asleep = True
            chosen_button_payload = await self.bot.wait_for(
                "component_interaction", check=button_check,
            )
            chosen_button = (chosen_button_payload.component.custom_id.lower())
            new_embed = discord.Embed(title='Draco The Beautiful Cat')
            change_image_check = False
            if chosen_button not in ["check_affection", "help", "reward_2", "pet"]:
                await chosen_button_payload.response.defer_update()

            if chosen_button == 'pet':
                if not draco_asleep:
                    change_image_check = True
                    components.get_component("pet").disable()
                    components.get_component("stop_pet").enable()
                    draco_status = "pet"
                    if (pet_time + timedelta(minutes=10)) < dt.utcnow():
                        affection_points += 1
                        if affection_points > 150:
                            affection_points = 150
                        pet_time = dt.utcnow()
                        async with vbu.Database() as db:
                            await db("""UPDATE draco_stats SET affection_meter = $3, pet_time = $1 WHERE user_id = $2""",
                                     pet_time,
                                     ctx.author.id,
                                     affection_points)
                        await chosen_button_payload.response.send_message(
                            "Affection Gained!", ephemeral=True)
                    else:
                        relative_time = discord.utils.format_dt(
                            pet_time - timedelta(hours=3, minutes=50),
                            style="R",
                        )
                        await chosen_button_payload.response.send_message(
                            f"More affection {relative_time}", ephemeral=True)
                else:
                    await ctx.send("Draco is sleeping shhh")

            elif chosen_button == 'stop_pet':
                if not draco_asleep:
                    change_image_check = True
                    components.get_component("pet").enable()
                    components.get_component("stop_pet").disable()
                    if (feed_time + timedelta(hours=15)) < dt.utcnow():
                        draco_status = "hungry"
                        components.get_component("feed_draco").enable()
                    else:
                        draco_status = "idle"
                else:
                    await ctx.send("Draco is sleeping shhh")

            elif chosen_button == 'check_affection':

                affection_meter = discord.File(
                    f"C:/Users/JT/Pictures/gift/affection_bar_{affection_points}.png")
                await chosen_button_payload.response.send_message(
                    content=f"{affection_points}/150", file=affection_meter, ephemeral=True)

            elif chosen_button == 'feed_draco':
                if not draco_asleep:
                    feed_time = dt.utcnow()
                    change_image_check = True
                    draco_status = "idle"
                    async with vbu.Database() as db:
                        await db("""UPDATE draco_stats SET feed_time = $1 WHERE user_id = $2""",
                                 dt.utcnow(),
                                 ctx.author.id)
                    components.get_component("feed_draco").disable()
                    await ctx.send("Draco fed!")
                else:
                    await ctx.send("Draco is sleeping shhh")

            elif chosen_button == 'help':
                await chosen_button_payload.response.send_message("How affection works: when you pet Draco you start a 10 minute timer getting one point of affection, "
                                                                  "and at the end of that timer the next pet will start another timer and give another point of affection. "
                                                                  "When the time is between 6 AM EST and 8 PM EST, draco while meow for food if it hasn't been fed yet that "
                                                                  "day. If it's 4 PM EST and Draco still hasn't been feds, you will lose 5% of your affection point every hour "
                                                                  "until he goes to sleep at 8 PM EST (losing ~19.5% per day). Draco will also take 3 random 10 minute naps per "
                                                                  "day. Affection points unlock certain features of the bot. The first feature being love which gives you a button "
                                                                  "that can be spammed many times to get more affection. The next feature is stab, which lets you make draco stab "
                                                                  "someone you @. Next is trivia, which will let you try to answer a cat themed trivia question every ten minutes "
                                                                  "for a point of affection. Next is the ability to give draco a hat, ranging from a cowboy hat to an astronaut hat. "
                                                                  "After that Draco will now hunt for you, bringing back dead animals that increase affection based on the animal. "
                                                                  "This feature has a one hour cooldown while Draco rests. Lastly you can worship Draco, adding your @ to a list "
                                                                  "that everyone sees, as well as giving you access to a fancy crown hat. Be careful though, as these will be "
                                                                  "removed if you go under 150 affection.",
                                                                  ephemeral=True
                                                                  )

            elif chosen_button == "reward_1":
                if not draco_asleep:
                    love += 2
                    if love >= 110:
                        love = 110
                    love_embed = discord.Embed(title="Love")
                    love_embed.add_field(
                        name=f"{int(love/2)}/55", value="Keep Clicking the \"Love\" button to level the heart up (at full stacks, gain one point of affection)")
                    love_file = discord.File(
                        fp=f"C:\\Users\\JT\\Pictures\\gift\\love_{love}.png", filename=f"love_{love}.png")
                    love_embed.set_image(url=f"attachment://love_{love}.png")
                    if not love_message:
                        love_embed_message = await ctx.send(embed=love_embed)
                        love_message = await ctx.send(file=love_file)
                    else:
                        await love_message.delete()
                        await love_embed_message.edit(embed=love_embed)
                        love_message = await ctx.send(file=love_file)
                    if love >= 110:
                        affection_points = affection_points + 1
                        if affection_points > 150:
                            affection_points = 150
                        async with vbu.Database() as db:
                            await db("""UPDATE draco_stats SET affection_meter = $2 WHERE user_id = $1""",
                                     ctx.author.id,
                                     affection_points)
                        love = 0
                        await ctx.send("Affection Gained!")
                else:
                    await ctx.send("Draco is sleeping shhh")

            elif chosen_button == "reward_2":
                if not draco_asleep:
                    message = await chosen_button_payload.response.send_message("@ Who you want to stab?", ephemeral=True)

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel
                    try:
                        name_message = await self.bot.wait_for("message", timeout=60.0, check=check)
                        name = name_message.mentions
                    except asyncio.TimeoutError:
                        await ctx.send("Timed out asking for person to stab")
                    if name[0]:
                        change_image_check = True
                        new_embed.add_field(
                            name="Stabby Stabby", value=f"Draco stabbed {name[0].mention}!")
                        draco_status = "stab"
                        await ctx.send(f"You stabbed {name[0].mention}!", allowed_mentions=discord.AllowedMentions.none())
                    else:
                        await ctx.send("You forgot to @ someone, so Draco stabbed YOU!")
                else:
                    await ctx.send("Draco is sleeping shhh")

            elif chosen_button == "reward_3":
                if not draco_asleep:
                    if ctx.author.id in self.trivia_cooldown:
                        relative_time = discord.utils.format_dt(
                            self.trivia_time - timedelta(hours=(4)),
                            style="R",
                        )
                        await ctx.send(f"More trivia {relative_time}!")
                    else:
                        self.trivia_cooldown.append(ctx.author.id)

                        def trivia_button_check(payload):
                            if payload.message.id != trivia_message.id:
                                return False
                            return payload.user.id == ctx.author.id

                        trivia_question = random.choice(
                            list(self.cat_trivia.keys()))
                        choices = self.cat_trivia[trivia_question]
                        correct_choice = choices[3]
                        random.shuffle(choices)
                        trivia_components = discord.ui.MessageComponents(
                            discord.ui.ActionRow(
                                discord.ui.Button(
                                    label=choices[0], custom_id=choices[0]
                                ),
                                discord.ui.Button(
                                    label=choices[1], custom_id=choices[1]
                                ),
                                discord.ui.Button(
                                    label=choices[2], custom_id=choices[2]
                                ),
                                discord.ui.Button(
                                    label=choices[3], custom_id=choices[3]
                                ),
                            ),
                        )
                        trivia_message = await ctx.send(trivia_question, components=trivia_components)
                        try:
                            chosen_trivia_button_payload = await self.bot.wait_for(
                                "component_interaction", check=trivia_button_check, timeout=60
                            )
                            chosen_trivia_button = (
                                chosen_trivia_button_payload.component.custom_id)
                            await chosen_trivia_button_payload.response.defer_update()
                        except asyncio.TimeoutError:
                            chosen_trivia_button = "aaaa"

                        await trivia_message.delete()
                        if chosen_trivia_button == correct_choice:
                            affection_points += 1
                            if affection_points > 150:
                                affection_points = 150
                            async with vbu.Database() as db:
                                await db("""UPDATE draco_stats SET affection_meter = $2 WHERE user_id = $1""",
                                         ctx.author.id,
                                         affection_points)
                            await ctx.send("Correct! Affection Gained!")
                        else:
                            await ctx.send("Incorrect, no affection gained.")
                else:
                    await ctx.send("Draco is sleeping shhh")

            elif chosen_button == "reward_4":
                hat_options = ["None", "Cowboy Hat",
                               "Astronaut Helmet", "Aqua Hat", "Crab Hat"]
                if ctx.author.id in self.draco_worshippers:
                    hat_options.append("Crown")
                test_options = []

                # For each name that isnt "" add it as an option for the select menu
                for option in hat_options:
                    if option != "":
                        test_options.append(
                            discord.ui.SelectOption(
                                label=option, value=option.replace(" ", "_").lower())
                        )

                # Set the select menu with the options
                components_menu = discord.ui.MessageComponents(
                    discord.ui.ActionRow(
                        discord.ui.SelectMenu(
                            custom_id="hat_choice",
                            options=test_options,
                            placeholder="Select an option",
                        )
                    )
                )

                # Ask them what they want to do with component
                message = await ctx.send(
                    f"What hat would you like to give Draco?",
                    components=components_menu,
                )

                # If it's the correct message and author return true
                def check(payload):
                    if payload.message.id != message.id:
                        return False

                    # If its the wrong author send an ephemeral message
                    if payload.user.id != ctx.author.id:
                        self.bot.loop.create_task(
                            payload.response.send_message(
                                "You can't respond to this message!", ephemeral=True
                            )
                        )
                        return False
                    return True

                # If it works don't fail, and if it times out say that
                try:
                    payload = await self.bot.wait_for(
                        "component_interaction", check=check, timeout=60
                    )
                    await payload.response.defer_update()
                except asyncio.TimeoutError:
                    await ctx.send(
                        f"Timed out asking for hat to "
                        f"give Draco. <@{ctx.author.id}>"
                    )
                    hat_choice = hat_choice

                # Return what they chose
                await message.delete()
                if payload.values:
                    hat_choice = "_" + str(payload.values[0])
                if str(payload.values[0]) == "none":
                    hat_choice = ""
                change_image_check = True

            if chosen_button == "reward_5":
                if not draco_asleep:
                    if (hunt_time + timedelta(hours=1)) < dt.utcnow():
                        hunt_time = dt.utcnow()
                        animal_types = {
                            "mouse": 1,
                            "bird": 2,
                            "vole": 3,
                            "squirrel": 4,
                            "rabbit": 5,
                        }
                        animal_chosen = random.choice(
                            ["mouse", "bird", "squirrel", "rabbit", "vole"])
                        affection_gained = animal_types[animal_chosen]
                        hunt_message = f"Draco caught and brought you a {animal_chosen}. {affection_gained} affection gained!"
                        hunt_image = discord.File(
                            f"C:/Users/JT/Pictures/gift/{animal_chosen}.png", "animal.png")
                        await ctx.send(hunt_message, file=hunt_image)
                        affection_points += affection_gained
                        if affection_points > 150:
                            affection_points = 150
                        async with vbu.Database() as db:
                            await db("""UPDATE draco_stats SET affection_meter = $2, hunt_time = $3 WHERE user_id = $1""",
                                     ctx.author.id,
                                     affection_points,
                                     hunt_time)
                    else:
                        relative_time = discord.utils.format_dt(
                            hunt_time - timedelta(hours=(3)),
                            style="R",
                        )
                        await ctx.send(f"Draco is tired, hunt again {relative_time}")
                else:
                    await ctx.send("Draco is sleeping shhh")

            if chosen_button == 'reward_6':
                if not draco_asleep:
                    self.draco_worshippers.append(ctx.author.id)
                    await ctx.send("You now worship Draco! (access to a new 'crown' hat included)")
                    components.get_component('reward_6').disable()
                    await draco_message.edit(components=components)
                else:
                    await ctx.send("Draco is sleeping shhh")

            if change_image_check:
                new_embed.add_field(name="Draco Worshippers", value=", ".join([
                    f"<@{i}>" for i in self.draco_worshippers]) + " love draco a lot!", inline=False)
                new_embed.set_image(url=hat_dict[hat_choice][draco_status])
                await draco_message.edit(
                    embed=new_embed,
                    components=components,
                    allowed_mentions=discord.AllowedMentions.none()
                )


def setup(bot):
    bot.add_cog(Draco(bot))
