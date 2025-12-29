from .command import AutomodCommand
from .enums import TriggerType
from collections.abc import Coroutine
from datetime import timedelta
from discord import AutoModRule, AutoModRuleAction, AutoModRuleEventType, AutoModRuleTriggerType, AutoModTrigger, Guild, NotFound
from discord.ext.commands import Bot
from typing import Optional, Self


class AutomodTree:
  def __init__(self: Self, bot: Bot) -> None:
    if not isinstance(bot, Bot): raise TypeError(f"bot: Must be an instance of {Bot.__name__}; not {bot.__class__.__name__}")
    self.__command_map: dict[str, AutomodCommand] = dict()
    self.__rule_id_map: dict[int, int] = dict()
    self.bot: Bot = bot


  def add_command(self: Self, command: AutomodCommand) -> None:
    if not isinstance(command, AutomodCommand): raise TypeError(f"command: Must be an instance of {AutomodCommand.__name__}; not {command.__class__.__name__}")
    if command.trigger in self.__command_map: raise ValueError(f"command: Command with keyword {command.trigger!r} already exists")
    self.__command_map[command.trigger]: AutomodCommand = command


  def command(self: Self, trigger: str, *, name: Optional[str] = None, trigger_ype: TriggerType = TriggerType.keyword) -> AutomodCommand:
    def wrapper(function: Coroutine) -> AutomodCommand:
      command_name: str = name or function.__name__
      command: AutomodCommand = AutomodCommand(name = command_name, callback = function, trigger = trigger, trigger_type = trigger_type)
      self.add_command(command)
      return command
    return wrapper


  async def disable(self: Self, command: AutomodCommand, *, guild: Guild) -> None:
    await self.toggle(command, guild = guild, active = False)


  async def enable(self: Self, command: AutomodCommand, *, guild: Guild) -> None:
    await self.toggle(command, guild = guild, active = True)


  async def fetch_rule(self: Self, guild: Guild) -> Optional[AutoModRule]:
    if not isinstance(guild, Guild): raise TypeError(f"guild: Must be an instance of {Guild.__name__}; not {guild.__class__.__name__}")
    if guild.id in self.__rule_id_map:
      try:
        rule: AutoModRule = await guild.fetch_automod_rule(self.__rule_id_map[guild.id])
        if rule.name != "AutoBot": return None
        return rule
      except NotFound: return None
    for automod_rule in await guild.fetch_automod_rules():
      if automod_rule.name == "AutoBot":
        self.__rule_id_map[guild.id]: int = automod_rule.id
        return automod_rule


  def get_command(self: Self, trigger: str) -> Optional[AutomodCommand]:
    if not isinstance(trigger, str): raise TypeError(f"trigger: Must be an instance of {str.__name__}; not {trigger.__class__.__name__}")
    return self.__command_map.get(trigger)


  async def toggle(self: Self, *commands: tuple[AutomodCommand], guild: Guild, active: bool) -> None:
    if not commands: raise ValueError("commands: Must provide at least one automod command")
    for index, command in enumerate(commands):
      if not isinstance(command, AutomodCommand): raise TypeError(f"commands.{index}: Must be an instance of {AutomodCommand.__name__}; not {command.__class__.__name__}")
    if 1_000 < len(commands): raise ValueError("commands: Maximum of 1000 commands per guild")
    if not isinstance(guild, Guild): raise TypeError(f"guild: Must be an instance of {Guild.__name__}; not {guild.__class__.__name__}")
    if not isinstance(active, bool): raise TypeError(f"active: Must be an instance of {bool.__name__}; not {active.__class__.__name__}")
    rule: Optional[AutoModRule] = await self.fetch_rule(guild)
    if not rule:
      rule: AutoModRule = await guild.create_automod_rule(
        name = "AutoBot",
        event_type = AutoModRuleEventType.message_send,
        trigger = AutoModTrigger(
          type = AutoModRuleTriggerType.keyword,
          keyword_filter = [command.trigger for command in commands if command.trigger_type is TriggerType.keyword],
          regex_patterns = [command.trigger for command in commands if command.trigger_type is TriggerType.regex]
        ),
        actions = [
          AutoModRuleAction(
            duration = timedelta()
          )
        ],
        enabled = True,
        reason = "Autobot automod commands"
      )
      self.__rule_id_map[guild.id]: int = rule.id
    elif 10 < (len(rule.trigger.regex_patterns) + len([command for command in commands if command.trigger_type is TriggerType.regex])): raise ValueError("commands: Maximum of 10 active regex patterns")
    if active:
      trigger: AutoModTrigger = AutoModTrigger(
        keyword_filter = [keyword for keyword in rule.trigger.keyword_filter] + [command.trigger for command in commands if command.trigger_type is TriggerType.keyword and command.trigger not in rule.trigger.keyword_filter],
        regex_patterns = [pattern for pattern in rule.trigger.regex_patterns] + [command.trigger for command in commands if command.trigger_type is TriggerType.regex and command.trigger not in rule.trigger.regex_patterns]
      )
    else:
      trigger: AutoModTrigger = AutoModTrigger(
        keyword_filter = [keyword for keyword in rule.trigger.keyword_filter if keyword not in [command.trigger for command in commands if command.trigger_type is TriggerType.keyword]],
        regex_patterns = [pattern for pattern in rule.trigger.regex_patterns if pattern not in [command.trigger for command in commands if command.trigger_type is TriggerType.regex]]
      )
    await rule.edit(trigger = trigger)