"""Private, server-side settings for the standalone survey reader."""
from __future__ import annotations

import argparse
import os
from pathlib import Path


_src = Path(__file__).resolve().parent.parent
_source_checkout = _src.name == "src" and (_src.parent / "pyproject.toml").is_file()
# A wheel keeps mutable settings and reading jobs in the launch directory.
DIRECTORY = _src.parent if _source_checkout else Path.cwd()
PRIVATE_ENV = DIRECTORY / ".env.local"
KEYS = (
    "DEEPSEEK_API_KEY", "KET_MINERU_API_TOKEN", "KET_DEEPSEEK_BASE_URL",
    "KET_CHAT_MODEL", "KET_MINERU_MODEL",
)


class ConfigError(ValueError):
    """A configuration error safe to report without exposing provider values."""


def _user_environment(names):
    if os.name != "nt":
        return {}
    import winreg

    result = {}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as user:
            for name in names:
                try:
                    value, kind = winreg.QueryValueEx(user, name)
                except OSError:
                    continue
                if kind in (winreg.REG_SZ, winreg.REG_EXPAND_SZ) and isinstance(value, str):
                    result[name] = value
    except OSError:
        pass
    return result


def _selected_file(path):
    values = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            name, separator, value = line.strip().partition("=")
            if separator and name.strip() in KEYS:
                value = value.strip()
                if len(value) > 1 and value[0] == value[-1] and value[0] in ("'", '"'):
                    value = value[1:-1]
                if value:
                    values[name.strip()] = value
    return values


def load_service_env():
    """Fill missing process settings from this installation and the Windows user."""
    stored = _selected_file(PRIVATE_ENV)
    missing = [name for name in KEYS if not os.environ.get(name) and name not in stored]
    for name, value in {**_user_environment(missing), **stored}.items():
        if not os.environ.get(name) and value:
            os.environ[name] = value


def copy_existing():
    """One-time import from the current environment and KESearch's private loader."""
    if PRIVATE_ENV.exists():
        raise ConfigError("独立配置已存在。")
    for name, value in _user_environment(KEYS).items():
        if value and not os.environ.get(name):
            os.environ[name] = value
    loader = DIRECTORY.parent / "code" / "backend" / "local_config.py"
    if _source_checkout and loader.is_file():
        from importlib.util import module_from_spec, spec_from_file_location

        spec = spec_from_file_location("kesearch_private_loader", loader)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        module.load_local_ai_env()
    settings = {name: os.environ[name].strip() for name in KEYS if os.environ.get(name, "").strip()}
    if not all(name in settings for name in ("DEEPSEEK_API_KEY", "KET_MINERU_API_TOKEN")):
        raise ConfigError("现有配置中缺少 DeepSeek 或 MinerU 凭据。")
    if not settings.get("KET_CHAT_MODEL", "").lower().startswith("deepseek"):
        settings.pop("KET_CHAT_MODEL", None)
    if any("\r" in value or "\n" in value for value in settings.values()):
        raise ConfigError("服务配置含有无效换行。")
    # Exclusive creation also prevents two invocations from overwriting one another.
    fd = os.open(PRIVATE_ENV, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output:
            output.writelines(f"{key}={value}\n" for key, value in settings.items())
    except BaseException:
        PRIVATE_ENV.unlink(missing_ok=True)
        raise


def main(argv=None):
    cli = argparse.ArgumentParser(description="将已有 DeepSeek 与 MinerU 配置复制到此工作台的本机私有配置。")
    cli.add_argument("--copy-existing", action="store_true", required=True)
    cli.parse_args(argv)
    try:
        copy_existing()
    except ConfigError as exc:
        cli.exit(1, f"配置导入未完成：{exc}\n")
    except (OSError, UnicodeError):
        cli.exit(1, "本地配置文件无法读写。\n")
    print("DeepSeek 与 MinerU 配置已导入。")


if __name__ == "__main__":
    main()
