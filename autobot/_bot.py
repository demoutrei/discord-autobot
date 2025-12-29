from ._tree import AutomodTree
from .command import AutomodCommand
from discord import AutoModAction
from discord.ext.commands import Bot
from traceback import print_exc
from typing import Optional, Self


class AutoBot(Bot):
  def __init__(self: Self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.__automod_tree: AutomodTree = AutomodTree(self)
    self.automod = self.__automod_tree.command


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