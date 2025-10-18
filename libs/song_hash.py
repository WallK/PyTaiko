import configparser
import csv
import json
import sqlite3
import sys
import time
from pathlib import Path

from libs.tja import NoteList, TJAParser
from libs.utils import get_config, global_data


def diff_hashes_object_hook(obj):
    if "diff_hashes" in obj:
        obj["diff_hashes"] = {
            int(key): value
            for key, value in obj["diff_hashes"].items()
        }
    return obj

class DiffHashesDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=diff_hashes_object_hook, *args, **kwargs)

def read_tjap3_score(input_file: Path):
    score_ini = configparser.ConfigParser()
    score_ini.read(input_file)
    scores = [int(score_ini['HiScore.Drums']['HiScore1']),
              int(score_ini['HiScore.Drums']['HiScore2']),
              int(score_ini['HiScore.Drums']['HiScore3']),
              int(score_ini['HiScore.Drums']['HiScore4']),
              int(score_ini['HiScore.Drums']['HiScore5'])]
    clears = [int(score_ini['HiScore.Drums'].get('Clear0', 0)),
              int(score_ini['HiScore.Drums'].get('Clear1', 0)),
              int(score_ini['HiScore.Drums'].get('Clear2', 0)),
              int(score_ini['HiScore.Drums'].get('Clear3', 0)),
              int(score_ini['HiScore.Drums'].get('Clear4', 0))]
    if score_ini['HiScore.Drums']['PerfectRange'] != 25:
        return [0],[0], None
    if score_ini['HiScore.Drums']['GoodRange'] != 75:
        return [0],[0], None
    if score_ini['HiScore.Drums']['PoorRange'] != 108:
        return [0],[0], None
    if score_ini['HiScore.Drums']['Perfect'] != 0:
        good = score_ini['HiScore.Drums'].get('Perfect', 0)
        ok = score_ini['HiScore.Drums'].get('Great', 0)
        bad = score_ini['HiScore.Drums'].get('Miss', 0)
        return scores, clears, [good, ok, bad]
    else:
        return scores, clears, None

def build_song_hashes(output_dir=Path("cache")):
    if not output_dir.exists():
        output_dir.mkdir()
    song_hashes: dict[str, list[dict]] = dict()
    path_to_hash: dict[str, str] = dict()  # New index for O(1) path lookups
    output_path = Path(output_dir / "song_hashes.json")
    index_path = Path(output_dir / "path_to_hash.json")

    # Load existing data
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            song_hashes = json.load(f, cls=DiffHashesDecoder)
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            path_to_hash = json.load(f)

    saved_timestamp = 0.0
    current_timestamp = time.time()
    if (output_dir / 'timestamp.txt').exists():
        with open(output_dir / 'timestamp.txt', 'r') as f:
            saved_timestamp = float(f.read())

    tja_paths = get_config()["paths"]["tja_path"]
    all_tja_files: list[Path] = []
    for root_dir in tja_paths:
        root_path = Path(root_dir)
        all_tja_files.extend(root_path.rglob("*.tja"))

    global_data.total_songs = len(all_tja_files)
    files_to_process = []

    for tja_path in all_tja_files:
        tja_path_str = str(tja_path)
        current_modified = tja_path.stat().st_mtime
        if current_modified <= saved_timestamp:
            current_hash = path_to_hash.get(tja_path_str)
            if current_hash is not None:
                global_data.song_paths[tja_path] = current_hash
                continue
        current_hash = path_to_hash.get(tja_path_str)
        if current_hash is None:
            files_to_process.append(tja_path)
        else:
            files_to_process.append(tja_path)
            if current_hash in song_hashes:
                del song_hashes[current_hash]
            del path_to_hash[tja_path_str]


    # Prepare database connection for updates
    db_path = Path("scores.db")
    db_updates = []  # Store updates to batch process later

    # Process only files that need updating
    song_count = 0
    total_songs = len(files_to_process)
    if total_songs > 0:
        global_data.total_songs = total_songs

    for tja_path in files_to_process:
        tja_path_str = str(tja_path)
        current_modified = tja_path.stat().st_mtime
        tja = TJAParser(tja_path)
        all_notes = NoteList()
        diff_hashes = dict()
        
        try:
                for diff in tja.metadata.course_data:
                        diff_notes, _, _, _ = TJAParser.notes_to_position(TJAParser(tja.file_path), diff)
                        diff_hashes[diff] = tja.hash_note_data(diff_notes)
                        all_notes.play_notes.extend(diff_notes.play_notes)
                        all_notes.bars.extend(diff_notes.bars)
        except Exception as e:
                print(f"Failed to parse TJA {tja_path}: {e}")
                continue

        if all_notes == []:
            continue

        hash_val = tja.hash_note_data(all_notes)
        if hash_val not in song_hashes:
            song_hashes[hash_val] = []

        song_hashes[hash_val].append({
            "file_path": tja_path_str,
            "last_modified": current_modified,
            "title": tja.metadata.title,
            "subtitle": tja.metadata.subtitle,
            "diff_hashes": diff_hashes
        })

        # Update both indexes
        path_to_hash[tja_path_str] = hash_val
        global_data.song_paths[tja_path] = hash_val

        # Prepare database updates for each difficulty
        en_name = tja.metadata.title.get('en', '') if isinstance(tja.metadata.title, dict) else str(tja.metadata.title)
        jp_name = tja.metadata.title.get('jp', '') if isinstance(tja.metadata.title, dict) else ''

        score_ini_path = tja_path.with_suffix('.tja.score.ini')
        if score_ini_path.exists():
            imported_scores, imported_clears, _ = read_tjap3_score(score_ini_path)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            for i in range(len(imported_scores)):
                if i not in diff_hashes or imported_scores[i] == 0:
                    continue
                cursor.execute("SELECT score FROM scores WHERE hash = ?", (diff_hashes[i],))
                existing_record = cursor.fetchone()
                if existing_record and existing_record[0] >= imported_scores[i]:
                    continue
                if imported_clears[i] == 2:
                    bads = 0
                    clear = 2
                elif imported_clears[i] == 1:
                    bads = None
                    clear = 1
                else:
                    bads = None
                    clear = 0
                cursor.execute("""
                    INSERT OR REPLACE INTO scores (hash, en_name, jp_name, diff, score, clear, bad)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (diff_hashes[i], en_name, jp_name, i, imported_scores[i], clear, bads))
                if cursor.rowcount > 0:
                    action = "Added" if not existing_record else "Updated"
                    print(f"{action} entry for {en_name} ({i}) - Score: {imported_scores[i]}")
            conn.commit()
            conn.close()

        for diff, diff_hash in diff_hashes.items():
            db_updates.append((diff_hash, en_name, jp_name, diff))

        song_count += 1
        global_data.song_progress = song_count / total_songs

    # Update database with new difficulty hashes
    if db_updates and db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            for diff_hash, en_name, jp_name, diff in db_updates:
                # Update existing entries that match by name and difficulty
                cursor.execute("""
                    UPDATE scores
                    SET hash = ?
                    WHERE (en_name = ? AND jp_name = ?) AND diff = ?
                """, (diff_hash, en_name, jp_name, diff))
                if cursor.rowcount > 0:
                    print(f"Updated {cursor.rowcount} entries for {en_name} ({diff})")

            conn.commit()
            conn.close()
            print(f"Database update completed. Processed {len(db_updates)} difficulty hash updates.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error updating database: {e}")
    elif db_updates:
        print(f"Warning: scores.db not found, skipping {len(db_updates)} database updates")

    # Save both files
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(song_hashes, f, indent=2, ensure_ascii=False)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(path_to_hash, f, indent=2, ensure_ascii=False)
    with open(output_dir / 'timestamp.txt', 'w') as f:
        f.write(str(current_timestamp))

    return song_hashes

def process_tja_file(tja_file):
    """Process a single TJA file and return hash or None if error"""
    tja = TJAParser(tja_file)
    all_notes = NoteList()
    for diff in tja.metadata.course_data:
        notes, _, _, _ = TJAParser.notes_to_position(TJAParser(tja.file_path), diff)
        all_notes.play_notes.extend(notes.play_notes)
        all_notes.bars.extend(notes.bars)
    if all_notes == []:
        return ''
    hash = tja.hash_note_data(all_notes)
    return hash

def get_japanese_songs_for_version(csv_file_path, version_column):
    # Read CSV file and filter rows where the specified version column has 'YES'
    version_songs = []

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get(version_column, "NO") != "NO":
                version_songs.append(row)

    # Extract Japanese titles (JPTITLE column)
    title_column = "TITLE 【TITLE2】\nJPTITLE／「TITLE2」 より"
    japanese_titles = [row[title_column] for row in version_songs if title_column in row]

    japanese_titles = [name.split("\n") for name in japanese_titles]
    second_lines = [
        name[1] if len(name) > 1 else name[0] for name in japanese_titles
    ]

    all_tja_files = []
    direct_tja_paths = dict()
    text_files = dict()
    tja_paths = get_config()["paths"]["tja_path"]
    for root_dir in tja_paths:
        root_path = Path(root_dir)
        all_tja_files.extend(root_path.rglob("*.tja"))
    for tja in all_tja_files:
        tja_parse = TJAParser(tja)
        tja_name = tja_parse.metadata.title.get(
            "ja", tja_parse.metadata.title["en"]
        )
        if "【双打】" in tja_name:
            tja_name = tja_name.strip("【双打】")
            tja_name = tja_name.strip()
        if tja_name in direct_tja_paths:
            direct_tja_paths[tja_name].append(tja)
        else:
            direct_tja_paths[tja_name] = [tja]
    for title in second_lines:
        if "・・・" in title:
            title = title.replace("・・・", "…")
        if "..." in title:
            title = title.replace("・・・", "…")

        # Find all matching keys
        matches = []

        # Check for exact title match
        if title in direct_tja_paths:
            for path in direct_tja_paths[title]:
                matches.append((title, path))

        # Also check for partial matches with the first part before '／'
        title_prefix = title.split("／")[0]
        for key in direct_tja_paths:
            if key.startswith(title_prefix) and key != title:
                for path in direct_tja_paths[key]:
                    matches.append((key, path))

        if not matches:
            for key in direct_tja_paths:
                if title.lower() in key.lower() or key.lower() in title.lower():
                    for path in direct_tja_paths[key]:
                        matches.append((key, path))

        if not matches:
            from difflib import get_close_matches

            close_matches = get_close_matches(
                title, direct_tja_paths.keys(), n=3, cutoff=0.6
            )
            for close_match in close_matches:
                for path in direct_tja_paths[close_match]:
                    matches.append((close_match, path))

        if len(matches) == 1:
            path = matches[0][1]
        elif len(matches) > 1:
            print(
                f"Multiple matches found for '{title.split('／')[0]} ({title.split('／')[1] if len(title.split('／')) > 1 else ''})':"
            )
            for i, (key, path_val) in enumerate(matches, 1):
                print(f"{i}. {key}: {path_val}")
            choice = int(input("Choose number: ")) - 1
            path = matches[choice][1]
        else:
            path = Path(input(f"NOT FOUND {title}: "))
        hash = process_tja_file(path)
        tja_parse = TJAParser(Path(path))
        genre = Path(path).parent.parent.name
        if genre not in text_files:
            text_files[genre] = []
        text_files[genre].append(
            f"{hash}|{tja_parse.metadata.title['en'].strip()}|{tja_parse.metadata.subtitle['en'].strip()}"
        )
        print(f"Added {title}: {path}")
    for genre in text_files:
        if not Path(version_column).exists():
            Path(version_column).mkdir()
        if not Path(f"{version_column}/{genre}").exists():
            Path(f"{version_column}/{genre}").mkdir()
        with open(
            Path(f"{version_column}/{genre}/song_list.txt"),
            "w",
            encoding="utf-8-sig",
        ) as text_file:
            for item in text_files[genre]:
                text_file.write(item + "\n")
    return text_files


if len(sys.argv) > 1:
    get_japanese_songs_for_version(sys.argv[1], sys.argv[2])
