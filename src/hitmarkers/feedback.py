# -*- coding: utf-8 -*-

# Hitmarkers Add-on for Anki
#
# Copyright (C) 2017-2020  Aristotelis P. <https://glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Visual feedback
"""

from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

from aqt import mw

try:
    from aqt.sound import av_player
    from anki.sound import SoundOrVideoTag

    legacy_play = None
except (ImportError, ModuleNotFoundError):
    from anki.sound import play as legacy_play

    av_player = None


_lab: Optional[QLabel] = None
_timer: Optional[QTimer] = None


def closeConfirm():
    global _lab, _timer
    if _lab:
        try:
            _lab.deleteLater()
        except:  # noqa: E722
            pass
        _lab = None
    if _timer:
        _timer.stop()
        _timer = None


def confirm(image_path: str, audio_path: str, period: int):
    global _timer, _lab
    if mw is None:
        return
    parent = mw
    closeConfirm()

    if Path(image_path).is_file():

        lab = QLabel(parent=parent)
        img = QPixmap(image_path).scaledToWidth(64, mode=Qt.SmoothTransformation)
        lab.setPixmap(img)
        lab.setAttribute(Qt.WA_TranslucentBackground, True)
        lab.setAutoFillBackground(False)
        lab.setWindowFlags(
            Qt.ToolTip | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint  # type: ignore
        )
        center = parent.frameGeometry().center()
        qp = QPoint(img.width() * 0.5, img.height() * 0.5)  # type: ignore
        lab.move(center - qp)

        lab.show()
        _timer = mw.progress.timer(period, closeConfirm, False)
        _lab = lab

    if Path(audio_path).is_file():
        if av_player:
            # Delay audio playback to prevent reviewer from stopping playback
            # on showQuestion
            mw.progress.timer(
                1, lambda: av_player.play_file(filename=audio_path), False
            )
        else:
            legacy_play(audio_path)
