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

from typing import NamedTuple, Optional

from anki.cards import Card
from aqt.gui_hooks import reviewer_did_answer_card
from aqt.reviewer import Reviewer
from aqt.utils import showWarning

from .consts import ADDON_NAME, PACKAGE_PATH, USER_FILES_PATH
from .feedback import confirm

# TODO?: configurable
_DEFAULT_MEDIA_SET = "hitmarkers"
_DEFAULT_DURATION = 200


class MediaPaths(NamedTuple):
    passed: str
    lapsed: str


def _get_media_paths(set_name: str, media_type: str) -> Optional[MediaPaths]:
    default_path = PACKAGE_PATH / media_type
    user_path = USER_FILES_PATH / media_type

    extension = "png" if media_type == "images" else "wav"

    for path in (default_path, user_path):
        path_passed = path / set_name / f"passed.{extension}"
        path_lapsed = path / set_name / f"lapsed.{extension}"

        if path_passed.is_file() or path_lapsed.is_file():
            return MediaPaths(str(path_passed), str(path_lapsed))

    return None


def on_answer_card(reviewer: Reviewer, card: Card, ease: int):
    image_set = _DEFAULT_MEDIA_SET
    audio_set = _DEFAULT_MEDIA_SET
    duration = _DEFAULT_DURATION

    image_paths = _get_media_paths(image_set, "images")
    sound_paths = _get_media_paths(audio_set, "sounds")

    if image_paths is None or sound_paths is None:
        showWarning(
            f"{ADDON_NAME} is not configured correctly: Could not find images or audio "
            f"for '{image_set}'' media set. Please reset the configuration to the "
            "defaults and try again. If that does not work, "
            "please redownload the add-on."
        )
        return

    if ease == 1:
        confirm(image_paths.lapsed, sound_paths.lapsed, duration)
    elif ease in (2, 3, 4):
        confirm(image_paths.passed, sound_paths.passed, duration)


def hook_into_reviewer():
    reviewer_did_answer_card.append(on_answer_card)
