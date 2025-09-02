class Logger:
    def __init__(self):
        self._logs = []

    def log(self, string: str):
        self._logs.append(string)
        print(string + "\n")

    def get_all_logs(self) -> str:
        return "\n".join(self._logs)

    def save_to_file(self, file_path: str):
        with open(file_path, "w") as f:
            f.write(self.get_all_logs())