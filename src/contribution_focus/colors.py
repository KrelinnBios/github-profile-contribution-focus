"""Stable, high-contrast colors for repository rows."""

import colorsys
import hashlib


def generated_color(repository: str) -> str:
    digest = hashlib.sha256(repository.casefold().encode("utf-8")).digest()
    hue = int.from_bytes(digest[:2], "big") / 65535
    saturation = 0.72
    lightness = 0.50
    red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
    return f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"


def color_for(repository: str, colors: dict[str, str]) -> str:
    if repository in colors:
        return colors[repository]
    short_name = repository.rsplit("/", 1)[-1]
    if short_name in colors:
        return colors[short_name]
    return generated_color(repository)
