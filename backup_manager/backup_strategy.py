from abc import ABC, abstractclassmethod

from backup_manager.backup_collection import BackupCollection
from backup_manager.backup_file import BackupAction


class BackupStrategy(ABC):
    action: BackupAction = BackupAction.UNSET

    @abstractclassmethod
    def apply_on(self, collection: BackupCollection) -> BackupCollection:

        """Apply the strategy on the given collection.

        Args:
            collection (BackupCollection): the collection to apply the strategy on.

        Returns:
            BackupCollection: a new collection containing only the backups that got the strategy applied.
        """
        pass


class BasicStrategy(BackupStrategy):
    """Basic implementation of a strategy. Applies the same action to all backups"""

    def apply_on(self, collection: BackupCollection) -> BackupCollection:
        applied_backups = []
        for backup in collection.data:
            if backup.set_action(self.action):
                applied_backups.append(backup)
        return BackupCollection(applied_backups)


class KeepEverything(BasicStrategy):
    """Basic implementation of a backup strategy. Keeps everything."""

    action = BackupAction.KEEP


class DeleteEverything(BasicStrategy):
    """Sample implementation of a backup strategy. Deletes everything."""

    action = BackupAction.DELETE


class LastN(BackupStrategy):
    action = BackupAction.KEEP
    n: int

    def __init__(self, n: int = 7) -> None:
        self.n = n

    def apply_on(self, collection: BackupCollection) -> BackupCollection:
        applied_backups = []
        for backup in collection.filter_unset()[-self.n :]:
            if backup.set_action(self.action):
                applied_backups.append(backup)
        return BackupCollection(applied_backups)


class DeleteUnset(BackupStrategy):
    action = BackupAction.DELETE

    def apply_on(self, collection: BackupCollection) -> BackupCollection:
        applied_backups = []
        for backup in collection.filter_unset():
            if backup.set_action(self.action):
                applied_backups.append(backup)
        return BackupCollection(applied_backups)


class DayOfMonth(BackupStrategy):
    action = BackupAction.KEEP
    day: int

    def __init__(self, day: int = 1) -> None:
        self.day = day

    def apply_on(self, collection: BackupCollection) -> BackupCollection:
        """Applies action to backups that match being on the given day of the month.

        If the given day is outside of range (day 31 on a month with 30 days), the action is not applied.

        Args:
            collection (BackupCollection): the collection to apply the strategy on.

        Returns:
            BackupCollection: a new collection containing only the backups that got the strategy applied.
        """
        applied_backups = []
        for _month, month_collection in collection.grouped_by_month().items():
            for backup in month_collection:
                if backup.date.day == self.day:
                    if backup.set_action(self.action):
                        applied_backups.append(backup)
        return BackupCollection(applied_backups)


class LastOfNMonths(BackupStrategy):
    action: BackupAction = BackupAction.KEEP
    n: int

    def __init__(self, n: int = 12) -> None:
        self.n = n

    def apply_on(self, collection: BackupCollection) -> BackupCollection:
        applied_backups = []
        grouped_by_month = collection.grouped_by_month()
        months = sorted(grouped_by_month.keys())[-self.n :]
        for month in months:
            last_of_month = grouped_by_month[month][-1]
            if last_of_month.set_action(self.action):
                applied_backups.append(last_of_month)
        return BackupCollection(applied_backups)


class DeleteUnset(BackupStrategy):
    action = BackupAction.DELETE

    def apply_on(self, collection: BackupCollection) -> BackupCollection:
        applied_backups = []
        for backup in collection.filter_unset():
            if backup.set_action(self.action):
                applied_backups.append(backup)
        return BackupCollection(applied_backups)
