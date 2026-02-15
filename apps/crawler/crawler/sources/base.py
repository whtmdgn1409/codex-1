from __future__ import annotations

from typing import Protocol

from crawler.sources.types import MatchPayload, MatchStatPayload, PlayerPayload, StandingPayload, TeamPayload


class DataSource(Protocol):
    def load_teams(self) -> list[TeamPayload]:
        ...

    def load_players(self) -> list[PlayerPayload]:
        ...

    def load_matches(self) -> list[MatchPayload]:
        ...

    def load_match_stats(self) -> list[MatchStatPayload]:
        ...

    def load_standings(self) -> list[StandingPayload]:
        ...
