def copy_from_src_to_dest(src: str, dest_dir: str, ignore=None) -> None:
    if os.path.isfile(src):
        logging.info(f"Copying {src} into {dest_dir}")
        shutil.copy(src, dest_dir)
    elif os.path.isdir(src):
        logging.info(f"Copying files in {src} into {dest_dir}")
        shutil.copytree(src, dest_dir, ignore=ignore, dirs_exist_ok=True)
    else:
        logging.warning(f"src: {src} not found")


def copy_compose_file(src_dir: str, dest_dir: str) -> None:
    logging.info(
        f"Copying docker-compose.**.yml files from {src_dir} into {dest_dir} non-recursively"
    )

    def ignore_non_compose_files(dir, files):
        return [
            f
            for f in files
            if not (os.path.isfile(os.path.join(dir, f)) and f.startswith("docker-compose."))
        ]

    copy_from_src_to_dest(src_dir, dest_dir, ignore=ignore_non_compose_files)


def execute_command(cmd: list[str]) -> subprocess.CompletedProcess:
    logging.info(f"\033[92m Executing command: {' '.join(cmd)} \033[0m")
    return subprocess.run(
        cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        encoding="utf-8",
        text=True,
        check=True,
    )


def load_properties(file_path: str, error: str) -> dict:
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return {
                key.strip(): value.strip()
                for line in file
                if line and not line.startswith("#")
                for key, value in [line.split("=", 1)]
            }
    else:
        logging.error(error)
        sys.exit(1)


def load_yaml(file_path: str, error: str) -> dict:
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            result = yaml.safe_load(file)
            return result
    else:
        logging.error(error)
        sys.exit(1)


def save_yaml(file_path: str, content: dict, error: str) -> None:
    if os.path.exists(file_path):
        with open(file_path, "w") as file:
            yaml.safe_dump(content, file, width=1000)
    else:
        logging.error(error)
        sys.exit(1)


def load_json(file_path: str, error: str) -> dict:
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            result = json.load(file)
            return result
    else:
        logging.error(error)
        sys.exit(1)


def save_json(file_path: str, content: dict, error: str) -> None:
    if os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(content, file, indent=2)
    else:
        logging.error(error)
        sys.exit(1)


def find_paths(src_dir: str, depth: int) -> list[str]:
    if depth < 1:
        return []

    pattern = "/*" * depth  # Create pattern with proper depth
    return [str(p) for p in Path(src_dir).glob(pattern[1:]) if p.is_dir()]


def find_files(root_dir: str, filter=None):
    for root, dirs, files in os.walk(root_dir, followlinks=True):
        files = filter(files) if filter else files
        for file in files:
            yield os.path.join(root, file)


def sanitize_docker_compose_files(path: str) -> None:
    logging.info(f"Sanitizing docker_compose files in {path}")

    def docker_compose_filter(files: list[str]):
        return [f for f in files if f.startswith("docker-compose") and f.endswith(".yml")]

    for file in find_files(path, filter=docker_compose_filter):
        content = load_yaml(file, f"{file} not found.")
        save_yaml(file, content, f"{file} not found.")

def rm_dest(path: str) -> None:
    if os.path.isfile(path):
        LOGGER.info(f"Removing file: {path}")
        os.remove(path)
    elif os.path.isdir(path):
        LOGGER.info(f"Removing directory and its contents: {path}")
        shutil.rmtree(path)
    else:
        LOGGER.debug(f"Path not found: {path}")
