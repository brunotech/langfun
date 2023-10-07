# Copyright 2023 The Langfun Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Conversation history with FIFO support."""

from typing import Annotated, Tuple
import langfun.core as lf


class ConversationHistory(lf.Memory):
  """A memory that keeps tracking of the conversation history."""

  max_turns: Annotated[
      int | None,
      'Max number of conversation turns to keep. If None, there is no limit.',
  ] = None

  def _on_bound(self):
    super()._on_bound()
    self.reset()

  @property
  def turns(self) -> list[Tuple[lf.Message, lf.Message]]:
    """Return conversation turns."""
    return self._turns

  @property
  def messages(self) -> list[lf.Message]:
    """Return conversation messages."""
    messages = []
    for r in self.turns:
      messages.extend((r[0], r[1]))
    return messages

  def _recollect(self, **kwargs) -> lf.MemoryRecord:
    return lf.MemoryRecord(
        '\n'.join([f'{m.sender}: {m.text}' for m in self.messages]))

  def _remember(
      self,
      input_message: lf.Message,
      output_message: lf.Message | None = None,
      **kwargs
  ) -> None:
    if self.max_turns and self.max_turns == len(self._turns):
      self._turns.pop(0)
    self._turns.append((input_message, output_message))

  def _reset(self, **kwargs) -> None:
    self._turns = []
