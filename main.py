import argparse
from pathlib import Path
from typing import Dict, List

from backup_manager.backup_collection import BackupCollection
from backup_manager.backup_file import BackupFile
from backup_manager.backup_strategy import (
    BackupStrategy,
    DeleteUnset,
    LastN,
    LastOfNMonths,
)
from samples import setup_samples


def apply_strategies(collection: BackupCollection, strategies: List[BackupStrategy]):
    for strategy in strategies:
        strategy.apply_on(collection)


def fancy_print(collection_name: str, collection: BackupCollection):
    modified = collection.exclude_unset()
    untouched = collection.filter_unset()
    to_keep = collection.filter_keep()
    to_delete = collection.filter_delete()
    disk_usage = collection.disk_usage()
    disk_usage_after_actions = collection.disk_usage_after_actions()
    disk_usage_reduction = disk_usage / disk_usage_after_actions
    print(f"Collection: {collection_name}")
    print(f"Total backups: {len(collection)}")
    print(f"Modified backups: {len(modified)}")
    print(f"Untouched backups: {len(untouched)}")
    print(f"To keep: {len(to_keep)}")
    print(f"To delete: {len(to_delete)}")
    print(f"Disk usage: {disk_usage} bytes")
    print(f"Disk usage after actions: {disk_usage_after_actions} bytes")
    print(f"Disk usage reduction: {disk_usage_reduction:.2f}x")


def find_backup_files(path, glob_filter="**/*.tar"):
    backups = []
    for file_path in path.glob(glob_filter):
        backups.append(BackupFile.from_path(file_path))
    return backups


def build_collections_from_backup_file_list(
    backup_file_list: List[BackupFile],
) -> Dict[str, BackupCollection]:
    collections: Dict[str, BackupCollection] = {}
    for backup_file in backup_file_list:
        collection_name = backup_file.guess_collection_from_filename()
        if collection_name not in collections:
            collections[collection_name] = BackupCollection()
        collections[collection_name].insort(backup_file)
    return dict(collections)


def main(path: Path, extensions: List[str], recursive: bool, dry_run: bool):
    backups = []
    for extension in extensions:
        glob = f"*.{extension}"
        if recursive:
            glob = "**/" + glob
        backups.extend(find_backup_files(path, glob))

    collections = build_collections_from_backup_file_list(backups)
    strategies = [LastN(n=7), LastOfNMonths(n=12), DeleteUnset()]
    for collection_name, collection in collections.items():
        apply_strategies(collection, strategies)
        fancy_print(collection_name, collection)
        print("=" * 10)
        if not dry_run:
            collection.apply_actions()


def parse_args():
    parser = argparse.ArgumentParser(description="Backup manager")
    parser.add_argument("backup_path", type=Path, help="Path to backup folder")
    parser.add_argument(
        "-e",
        "--extension",
        type=str,
        help="File extensions to process. Pass multiple times to add more than one extension",
        action="append",
        required=True,
    )
    parser.add_argument(
        "-r",
        "--recursive",
        help="Process subfolders in path",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        help="Dry run. Don't delete anything",
        action="store_true",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(
        path=args.backup_path,
        extensions=args.extension,
        recursive=args.recursive,
        dry_run=args.dry_run,
    )
