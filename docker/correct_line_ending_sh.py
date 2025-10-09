import os.path

currentFilePath = os.path.abspath(__file__)
dirPath = os.path.dirname(currentFilePath)

fileList = ["start.sh",
            "start_without_migrate.sh",
            "migrate.sh",
            "start_worker.sh"]

for file in fileList:
    filePath = f"{dirPath}/{file}"
    with open(filePath, "r") as f:
        content = f.read()
    content = content.replace(r"\r\n", r"\n")

    with open(filePath, "w+") as f:
        f.write(content)

