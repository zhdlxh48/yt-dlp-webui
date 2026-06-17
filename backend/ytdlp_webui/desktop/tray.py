from __future__ import annotations

from collections.abc import Callable

import pystray
from PIL import Image, ImageDraw


def make_icon_image() -> Image.Image:
    image = Image.new("RGBA", (64, 64), (20, 24, 31, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((10, 14, 54, 50), radius=10, fill=(52, 211, 153, 255))
    draw.polygon([(28, 25), (28, 39), (41, 32)], fill=(20, 24, 31, 255))
    return image


class TrayApp:
    def __init__(
        self,
        open_dashboard: Callable[[], None],
        start_monitoring: Callable[[], None],
        stop_all: Callable[[], None],
        quit_app: Callable[[], None],
    ) -> None:
        self.open_dashboard = open_dashboard
        self.start_monitoring = start_monitoring
        self.stop_all = stop_all
        self.quit_app = quit_app
        self.icon = pystray.Icon(
            "yt-dlp-webui",
            make_icon_image(),
            "yt-dlp-webui",
            menu=pystray.Menu(
                pystray.MenuItem("대시보드 열기", self._open),
                pystray.MenuItem("감시 시작", self._start),
                pystray.MenuItem("전체 중지", self._stop),
                pystray.MenuItem("종료", self._quit),
            ),
        )

    def run(self) -> None:
        self.icon.run()

    def _open(self) -> None:
        self.open_dashboard()

    def _start(self) -> None:
        self.start_monitoring()

    def _stop(self) -> None:
        self.stop_all()

    def _quit(self) -> None:
        self.quit_app()
        self.icon.stop()
