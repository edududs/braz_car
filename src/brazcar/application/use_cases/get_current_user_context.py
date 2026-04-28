from __future__ import annotations

from dataclasses import dataclass

from src.brazcar.application.dto import CurrentUserContext
from src.brazcar.application.ports import CurrentUserContextProvider


@dataclass(frozen=True, slots=True)
class GetCurrentUserContext:
    provider: CurrentUserContextProvider

    def execute(self) -> CurrentUserContext:
        return self.provider.get_current_user_context()
