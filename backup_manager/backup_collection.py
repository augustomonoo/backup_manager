from __future__ import annotations

import bisect
from collections import UserList, defaultdict
from typing import Dict, Set

from backup_manager.backup_file import BackupAction, BackupFile


class BackupCollection(UserList):
    """Manages a collection of backups"""

    data: list[BackupFile]

    def insort(self, backup: BackupFile) -> None:
        """Inserts a backup into the collection. Utilizes bisect.isort to maintain order

        Args:
            backup (BackupFile): the backup to add to the collection
        """
        bisect.insort(self.data, backup)

    def filter(
        self,
        action_set: Set[BackupAction] = set(BackupAction),
    ) -> BackupCollection:
        """Returns a new collection of backups that match the specified action list.

        Args:
            action_set (Set[BackupAction], optional): A set of actions to use as filter. Defaults to all available actions.

        Returns:
            list: A list of backups that match the specified action filter
        """
        data = [backup_file for backup_file in self if backup_file.action in action_set]

        return BackupCollection(data)

    def filter_unset(self) -> BackupCollection:
        return self.filter(set([BackupAction.UNSET]))

    def filter_keep(self) -> BackupCollection:
        return self.filter(set([BackupAction.KEEP]))

    def filter_delete(self) -> BackupCollection:
        return self.filter(set([BackupAction.DELETE]))

    def exclude(self, action_set: Set[BackupAction]) -> BackupCollection:
        return BackupCollection(
            [backup for backup in self if backup.action not in action_set]
        )

    def exclude_delete(self) -> BackupCollection:
        return self.exclude(set([BackupAction.DELETE]))

    def exclude_unset(self) -> BackupCollection:
        return self.exclude(set([BackupAction.UNSET]))

    def exclude_keep(self) -> BackupCollection:
        return self.exclude(set([BackupAction.KEEP]))

    def grouped_by_strftime(self, strfime: str) -> Dict[str, BackupCollection]:
        grouped = defaultdict(BackupCollection)
        for backup in self.data:
            grouped[backup.date.strftime(strfime)].append(backup)
        return grouped

    def grouped_by_year(self) -> Dict[str, BackupCollection]:
        return self.grouped_by_strftime("%Y")

    def grouped_by_month(self) -> Dict[str, BackupCollection]:
        return self.grouped_by_strftime("%Y-%m")

    def grouped_by_day(self) -> Dict[str, BackupCollection]:
        return self.grouped_by_strftime("%Y-%m-%d")

    def disk_usage(self) -> int:
        return sum([backup.size for backup in self])

    def disk_usage_after_actions(self) -> int:
        return sum([backup.size for backup in self.exclude_delete()])

    def apply_actions(self):
        for backup in self:
            backup.apply_action()
        self = self.filter_keep()
