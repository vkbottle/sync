import os
import git
import shutil


PACKAGE_NAME = "vkbottle"
PACKAGE_ALT_NAME = "vkbottle_sync"
BOT_PATH = "vkbottle_sync/framework/bot/bot.py"
ABC_FRAMEWORK_PATH = "vkbottle_sync/framework/abc.py"
CLIENT_PATH = "vkbottle_sync/http/client/aiohttp.py"
CLIENT_ALT_PATH = "vkbottle_sync/http/client/requests.py"
CLIENT_NAME = "AiohttpClient"
CLIENT_ALT_NAME = "RequestsClient"
CLIENT_PACKAGE = ".aiohttp"
CLIENT_ALT_PACKAGE = ".requests"

REPLACEMENTS = [
    ("async ", ""),
    ("await ", ""),
    ("import vkbottle.", "import vkbottle_sync."),
    ("from vkbottle.", "from vkbottle_sync."),
    ("from vkbottle ", "from vkbottle_sync "),
    ("__aenter__", "__enter__"),
    ("__aexit__", "__exit__"),
    (CLIENT_NAME, CLIENT_ALT_NAME),
    (CLIENT_PACKAGE, CLIENT_ALT_PACKAGE),
]


def sync_reformat(file_path: str, alt_path: str, contents: dict):
    if not file_path.endswith(".py"):
        os.makedirs(alt_path, exist_ok=True)
        for n in os.listdir(file_path):
            sync_reformat(file_path + os.sep + n, alt_path + os.sep + n, contents)
        return

    alt_lines = []
    with open(file_path, "r") as file:
        for line in file:
            for (f, t) in REPLACEMENTS:
                line = line.replace(f, t)
            alt_lines.append(line)

    if alt_path == BOT_PATH:
        alt_lines = contents["bot"]
    elif alt_path == ABC_FRAMEWORK_PATH:
        alt_lines = contents["abc_framework"]

    with open(alt_path, "w") as file:
        file.writelines(alt_lines)


def build(setup_kwargs: dict):
    contents = {
        "abc_framework": open("sync_replacements/abc_framework.py").readlines(),
        "bot": open("sync_replacements/bot.py").readlines(),
        "client_alt": open("sync_replacements/client.py").read(),
    }

    git.Repo.clone_from("https://github.com/timoniq/vkbottle.git", "vkbottle_repo")
    shutil.move("vkbottle_repo/vkbottle", "./")

    shutil.rmtree("vkbottle_repo", ignore_errors=True)

    os.makedirs("vkbottle_sync", exist_ok=True)
    for file_name in os.listdir("vkbottle"):
        sync_reformat(
            "vkbottle" + os.sep + file_name, "vkbottle_sync" + os.sep + file_name, contents
        )

    os.remove(CLIENT_PATH)
    os.makedirs(os.sep.join(CLIENT_ALT_PATH.split(os.sep)[:-1]), exist_ok=True)
    with open(CLIENT_ALT_PATH, "w") as f:
        f.write(contents["client_alt"])

    shutil.rmtree("vkbottle", ignore_errors=True)
