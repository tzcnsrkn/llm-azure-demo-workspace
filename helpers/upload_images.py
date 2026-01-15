import redis
import os

# ================= CONFIGURATION =================
# Redis Connection Details
REDIS_HOST = '<redis_cloud_host>'
REDIS_PORT = 11744
REDIS_DB = 0
REDIS_PASSWORD = '<password>'

# Use raw strings (r"...") for Windows to handle backslashes correctly
ROOT_FOLDER_PATH = r"..\marimo-mission\02\improvised\dataset_cleaned_by_model\bears"
# =================================================

def main():
    # 1. Connect to Redis
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=False
        )
        # Test connection
        r.ping()
        print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except redis.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
        return

    # 2. Wipe the Database
    print("Wiping Redis Database...")
    r.flushdb()
    print("Database wiped successfully.")

    # 3. Walk through folders and upload
    print(f"Scanning folder: {ROOT_FOLDER_PATH}")

    if not os.path.exists(ROOT_FOLDER_PATH):
        print(f"Error: The folder path does not exist: {ROOT_FOLDER_PATH}")
        return

    count = 0
    # os.walk will go through 'bears', then 'black', 'grizzly', 'teddy'
    for root, dirs, files in os.walk(ROOT_FOLDER_PATH):
        for file_name in files:
            # Construct full local file path
            full_path = os.path.join(root, file_name)

            # Create a Redis Key.
            # Strategy: Use the folder name (category) and filename.
            # Example: "bears:black:image01.jpg"

            # Get the relative path from the root folder (e.g., "black\image.jpg")
            rel_path = os.path.relpath(full_path, ROOT_FOLDER_PATH)

            # Normalize path separators to forward slashes for consistency in Redis keys
            # and replace spaces with underscores if preferred
            redis_key = "bears:" + rel_path.replace("\\", ":").replace("/", ":")

            try:
                # Read the file as binary
                with open(full_path, 'rb') as f:
                    file_data = f.read()

                # Upload to Redis
                # We use .set() for simple Key-Value storage
                r.set(redis_key, file_data)

                print(f"Uploaded: {redis_key} ({len(file_data)} bytes)")
                count += 1

            except Exception as e:
                print(f"   ❌ Failed to upload {file_name}: {e}")

    print(f"\nFinished! Uploaded {count} files to Redis.")

if __name__ == "__main__":
    main()
