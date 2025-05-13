import discord


def get_channel(
    interaction: discord.Interaction | discord.Message,
) -> discord.TextChannel:
    channel = interaction.channel

    if not isinstance(channel, discord.TextChannel):
        raise TypeError("Interaction channel is not a TextChannel")

    return channel


def get_guild(interaction: discord.Interaction | discord.Message) -> discord.Guild:
    guild = interaction.guild

    if not isinstance(guild, discord.Guild):
        raise TypeError("Interaction has no guild")

    return guild


def get_guild_member(interaction: discord.Interaction) -> discord.Member:
    user = interaction.user

    if not isinstance(user, (discord.Member)):
        raise TypeError("Interaction user is not a guild member")

    return user
