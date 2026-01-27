"""
config_loader.py

YAML configuration loader and validator.
"""

from __future__ import annotations

import pathlib
from typing import Any, Dict, Tuple

import yaml


class ConfigError(Exception):
    """Raised whenever the configuration file is missing required fields or has invalid data."""


class ConfigLoader:
    """
    Loads and validates a YAML configuration file.

    Usage:
        loader = ConfigLoader()
        config = loader.load_config("path/to/config.yml")
    """

    _REQUIRED_FIELDS: Dict[Tuple[str, ...], type] = {
        ("github", "token"): str,
        ("github", "repo"): str,
        ("policy", "mode"): str,
        ("security", "enabled"): bool,
        ("standards", "enabled"): bool,
        ("license", "enabled"): bool,
        ("ai", "enabled"): bool,
        ("ai", "model"): str,
    }

    _VALID_POLICY_MODES = {"ADVISORY", "WARNING", "BLOCKING"}

    _DEFAULTS: Dict[Tuple[str, ...], Any] = {
        ("policy", "mode"): "ADVISORY",
        ("security", "enabled"): True,
        ("standards", "enabled"): True,
        ("license", "enabled"): True,
        ("ai", "enabled"): False,
        ("ai", "model"): "gpt-4",
    }

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def load_config(self, path: str | pathlib.Path) -> Dict[str, Any]:
        """
        Load a YAML configuration file, apply defaults, and validate its contents.

        Args:
            path: Path to the YAML configuration file.

        Returns:
            A fully validated configuration dictionary.

        Raises:
            ConfigError: If the configuration is invalid or incomplete.
        """
        raw_config = self._parse_yaml(path)
        self._apply_defaults(raw_config)
        self._validate_required_fields(raw_config)
        self._validate_policy_mode(raw_config)
        return raw_config

    # --------------------------------------------------------------------- #
    # Internal Helpers
    # --------------------------------------------------------------------- #
    def _parse_yaml(self, path: str | pathlib.Path) -> Dict[str, Any]:
        p = pathlib.Path(path)

        if not p.is_file():
            raise ConfigError(f"Configuration file not found: {p}")

        try:
            with p.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
                if not isinstance(data, dict):
                    raise ConfigError("Top-level YAML structure must be a mapping.")
                return data
        except yaml.YAMLError as exc:
            raise ConfigError(f"Failed to parse YAML: {exc}") from exc

    def _apply_defaults(self, config: Dict[str, Any]) -> None:
        for field_path, default_value in self._DEFAULTS.items():
            node = config
            for key in field_path[:-1]:
                node = node.setdefault(key, {}) if isinstance(node, dict) else None
                if node is None:
                    break
            if node is not None:
                node.setdefault(field_path[-1], default_value)

    def _validate_required_fields(self, config: Dict[str, Any]) -> None:
        for field_path, expected_type in self._REQUIRED_FIELDS.items():
            value = self._get_nested_value(config, field_path)
            if value is None:
                joined = ".".join(field_path)
                raise ConfigError(f"Missing required field: {joined}")

            if not isinstance(value, expected_type):
                joined = ".".join(field_path)
                actual_type = type(value).__name__
                expected_name = expected_type.__name__
                raise ConfigError(
                    f"Invalid type for field {joined}: expected {expected_name}, got {actual_type}"
                )

    def _validate_policy_mode(self, config: Dict[str, Any]) -> None:
        mode = self._get_nested_value(config, ("policy", "mode"))
        if mode not in self._VALID_POLICY_MODES:
            allowed = ", ".join(sorted(self._VALID_POLICY_MODES))
            raise ConfigError(f"Invalid policy.mode '{mode}'. Allowed values: {allowed}")

    # --------------------------------------------------------------------- #
    # Static Helpers
    # --------------------------------------------------------------------- #
    @staticmethod
    def _get_nested_value(data: Dict[str, Any], path: Tuple[str, ...]) -> Any | None:
        node: Any = data
        for key in path:
            if not isinstance(node, dict):
                return None
            node = node.get(key)
            if node is None:
                return None
        return node
