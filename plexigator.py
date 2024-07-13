import os
import sqlite3

# Path to the Plex SQLite database
PLEX_DB_PATH = '/opt/projects/plexigator/database/databaseBackup.db'

# Directory containing your TV shows
TV_SHOWS_DIR = '/opt/media/tv.shows'

def get_plex_tv_shows(db_path):
    # Connect to the Plex database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute a query to get the list of file paths from the media_parts table
    cursor.execute('''
        SELECT file
        FROM media_parts
        WHERE file LIKE '/opt/media/tv.shows/%'
    ''')

    # Fetch all results and extract folder names and their full paths
    plex_tv_shows = {}
    for row in cursor.fetchall():
        file_path = row[0]
        folder_path = os.path.dirname(file_path)
        folder_name = os.path.basename(folder_path)
        plex_tv_shows[folder_name] = folder_path

    # Close the connection
    conn.close()

    return plex_tv_shows

def get_local_tv_shows(directory):
    # Get the list of directories in the TV shows directory
    return {name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))}

def main():
    # Get Plex TV shows list
    plex_tv_shows = get_plex_tv_shows(PLEX_DB_PATH)
    
    # Get local TV shows list
    local_tv_shows = get_local_tv_shows(TV_SHOWS_DIR)

    # Find the differences
    plex_tv_show_names = set(plex_tv_shows.keys())
    not_in_plex = local_tv_shows - plex_tv_show_names
    not_in_local = plex_tv_show_names - local_tv_shows

    # Print results
    if not_in_plex:
        print("Folders not recognized by Plex:")
        for show in sorted(not_in_plex):
            print(show)
    else:
        print("All local folders are recognized by Plex.")
    
    if not_in_local:
        print("\nTV shows in Plex but not in local folders:")
        for show in sorted(not_in_local):
            print(f"{show}: {plex_tv_shows[show]}")
    else:
        print("\nAll Plex TV shows are present in local folders.")

if __name__ == "__main__":
    main()
