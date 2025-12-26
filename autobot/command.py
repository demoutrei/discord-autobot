from collections.abc import Coroutine
from discord import AutoModAction, Guild, Member, Thread
from discord.abc import GuildChannel
from inspect import iscoroutinefunction, Parameter, Signature, signature
from typing import Any, get_origin, Self, Union


class AutomodCommand:
  async def __call__(self: Self, execution: AutoModAction) -> None:
    if not isinstance(execution, AutoModAction): raise TypeError(f"execution: Must be an instance of {AutoModAction.__name__}; not {execution.__class__.__name__}")
    if not self.callback: raise ValueError(f"No callback provided for command {self.name!r}")
    callback_signature: Signature = signature(self.callback)
    args: dict[str, Any] = dict()
    for name in callback_signature.parameters:
      parameter: Parameter = callback_signature.parameters[name]
      if get_origin(parameter.annotation) is Union:
        if any([arg in (GuildChannel, Thread) for arg in parameter.annotation.__args__]): args[name]: Union[GuildChannel, Thread] = execution.channel
      elif parameter.annotation in (GuildChannel, Thread):
        if isinstance(execution.channel, (GuildChannel, Thread, None)): args[name]: Union[GuildChannel, Thread] = execution.channel
      elif parameter.annotation == str: args[name]: str = execution.content
      elif parameter.annotation == Guild: args[name]: Guild = execution.guild
      elif parameter.annotation == Member: args[name]: Member = execution.member
    await self.callback(**args)
  
  
  def __init__(self: Self, *, name: str, callback: Coroutine, keyword: str) -> None:
    if not isinstance(name, str): raise TypeError(f"name: Must be an instance of {str.__name__}; not {name.__class__.__name__}")
    if not name.strip(): raise ValueError("name: Must not be an empty string")
    if not iscoroutinefunction(callback): raise TypeError(f"callback: Must be a coroutine")
    if not isinstance(keyword, str): raise TypeError(f"keyword: Must be an instance of {str.__name__}; not {keyword.__class__.__name__}")
    if not keyword.strip(): raise ValueError(f"keyword: Must not be an empty string")
    keyword: str = keyword.strip()
    if 60 < len(keyword): raise ValueError(f"keyword: Can only be up to 60 characters in length")
    self.__keyword: str = keyword
    self.__name: str = name
    self.callback: Coroutine = callback


  @property
  def keyword(self: Self) -> str:
    return self.__keyword


  @property
  def name(self: Self) -> str:
    return self.__name