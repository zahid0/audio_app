import os


class LocalStorageService:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def list_folders(self):
        return [
            {"id": f, "name": f}
            for f in os.listdir(self.root_dir)
            if os.path.isdir(os.path.join(self.root_dir, f))
        ]

    def list_files(self, folder_id=None):
        directory = os.path.join(self.root_dir, folder_id if folder_id else "")
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                relative_path = os.path.relpath(
                    os.path.join(root, filename), self.root_dir
                )
                files.append({"id": relative_path, "name": filename})
        return files

    def get_file(self, file_id):
        full_path = os.path.join(self.root_dir, file_id)
        with open(full_path, "rb") as f:
            return f.read()

    def download_media(self, file_id, buffer):
        full_path = os.path.join(self.root_dir, file_id)
        with open(full_path, "rb") as f:
            buffer.write(f.read())

    async def media_stream(self, file_id):
        full_path = os.path.join(self.root_dir, file_id)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {file_id} not found")
        with open(full_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
