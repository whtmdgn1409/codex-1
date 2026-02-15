from __future__ import annotations

from crawler.config import load_source_config
from crawler.logging_utils import log_event
from crawler.sources.api_football import ApiFootballDataSource
from crawler.sources.base import DataSource
from crawler.sources.premier_league import PremierLeagueDataSource
from crawler.sources.sample_data import SampleDataSource


def get_data_source() -> DataSource:
    config = load_source_config()
    if config.source == "sample":
        log_event("INFO", "source.selected", source="sample")
        return SampleDataSource()
    if config.source in {"pl", "premierleague", "premier_league"}:
        log_event("INFO", "source.selected", source="premierleague")
        return PremierLeagueDataSource(config)
    if config.source in {"api_football", "api-football", "apifootball"}:
        log_event("INFO", "source.selected", source="api_football")
        return ApiFootballDataSource(config)
    raise ValueError(f"unsupported CRAWLER_DATA_SOURCE: {config.source}")
