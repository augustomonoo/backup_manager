from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


class BackupAction(enum.Enum):
    """Enum for backup actions.
    UNSET: No action. This also means that the file is kept. This is the default.
    KEEP: Keep the file.
    DELETE: Delete the file.
    """

    UNSET = 0
    KEEP = 1
    DELETE = 2


@dataclass
class BackupFile:
    path: Path
    size: int
    date: datetime
    action: BackupAction = field(default=BackupAction.UNSET)

    @staticmethod
    def from_path(path: Path) -> BackupAction:
        """Create a BackupFile from a given path.

        Args:
            path (Path): The file Path

        Returns:
            [type]: The created BackupFile.
        """
        return BackupFile(
            path=path,
            size=path.stat().st_size,
            date=datetime.fromtimestamp(path.stat().st_mtime),
        )

    def guess_collection_from_filename(self) -> str:
        """Guess the collection name from the filename.

        Very specific to the backup name convention. Will be removed in the future.
        Returns:
            str: the guessed collection name.
        """
        if match := re.match(
            r"^(?P<collection>.*)_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\.tar$", self.path.name
        ):
            return match.group("collection")
        return self.path.parent.name

    def set_action(self, action: BackupAction, force: bool = False) -> bool:
        """Set the action for this file if it is UNSET. Use force change the action regardless.

        Args:
            action (BackupAction): the action to set.
            force (bool, optional): Force the action to be set. Defaults to False.

        Returns:
            bool: True if the action was set, False otherwise. Always true if force is True.
        """
        if force:
            self.action = action
            return True

        if self.action != BackupAction.UNSET:
            return False

        if action == self.action:
            return False

        self.action = action
        return True

    def apply_action(self):
        if self.action is BackupAction.DELETE:
            self.path.unlink()

    def __lt__(self, other):
        return self.date < other.date
