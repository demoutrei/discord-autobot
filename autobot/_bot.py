from ._tree import AutomodTree
from .command import AutomodCommand
from collections.abc import Coroutine
from discord import AutoModAction
from discord.ext.commands import Bot
from traceback import print_exc
from typing import Optional, Self


class AutoBot(Bot):
  def __init__(self: Self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.__automod_tree: AutomodTree = AutomodTree(self)
  
  
  def automod(self: Self, keyword: str, *, name: Optional[str] = None) -> AutomodCommand:
    def wrapper(function: Coroutine) -> AutomodCommand:
      command_name: str = name or function.__name__
      command: AutomodCommand = AutomodCommand(name = command_name, callback = function, keyword = keyword)
      self.automod_tree.add_command(command)
      return command
    return wrapper


  @property
  def automod_tree(self: Self) -> AutomodTree:
    return self.__automod_tree


  async def on_automod_action(self: Self, execution: AutoModAction) -> None:
    try:
      if not execution.matched_keyword: return
      if not await self.automod_tree.fetch_rule(execution.guild): return
      command: Optional[AutomodCommand] = self.automod_tree.get_command(execution.matched_keyword)
      if not command: return
      await command(execution)
    except: print_exc()