import os
import subprocess
def createDocker(rootPath, folderPath, tagList, buildServer, buildWorker, buildTrigger, buildDemo, push):

    if not tagList:
        print("you must add tags")
        return

    workerTagList = []
    serverTagList = []
    triggerTagList = []
    demoTagList = []
    dev = False
    for tag in tagList:
        if tag.lower() == "dev":
            dev = True
        if tag is None or tag == "" or tag == "latest":
            serverTagList.append("furthrresearch/furthrmind-server-v1:latest")
            workerTagList.append("furthrresearch/furthrmind-worker-v1:latest")
            triggerTagList.append("furthrresearch/furthrmind-trigger-server-v1:latest")
            demoTagList.append("furthrresearch/furthrmind-demo-server-v1:latest")
        elif tag == "demo":
            demoTagList.append("furthrresearch/furthrmind-demo-server-v1:latest")
        else:
            serverTagList.append(f"furthrresearch/furthrmind-server-v1:{tag}")
            workerTagList.append(f"furthrresearch/furthrmind-worker-v1:{tag}")
            triggerTagList.append(f"furthrresearch/furthrmind-trigger-server-v1:{tag}")


    dockerServerCommand = f"docker build . -f docker/Dockerfile "
    dockerPushServerCommandList = []
    for tag in serverTagList:
        dockerServerCommand += f"-t {tag} "
        dockerPushServerCommandList.append(f"docker push {tag}")

    dockerWorkerCommand = f"docker build . -f docker/Dockerfile_Worker "
    dockerPushWorkerCommandList = []
    for tag in workerTagList:
        dockerWorkerCommand += f"-t {tag} "
        dockerPushWorkerCommandList.append(f"docker push {tag}")

    dockerTriggerCommand = f"docker build . -f docker/Dockerfile_TriggerServer "
    dockerPushTriggerCommandList = []
    for tag in triggerTagList:
        dockerTriggerCommand += f"-t {tag} "
        dockerPushTriggerCommandList.append(f"docker push {tag}")

    dockerDemoCommand = f"docker build . -f docker/Dockerfile_Demo "
    dockerPushDemoCommandList = []
    for tag in demoTagList:
        dockerDemoCommand += f"-t {tag} "
        dockerPushDemoCommandList.append(f"docker push {tag}")

    commandList = [
        f"cd {rootPath}"]

    if buildServer:
        commandList.append(f"{dockerServerCommand}")

    if buildWorker:
        commandList.append(f"{dockerWorkerCommand}")

    if buildTrigger:
        commandList.append(f"{dockerTriggerCommand}")
        # "python docker/CreateDockerBat.py",
        # f"cd docker",
        # f"./createDocker.bat"
        # f"docker build . -f Dockerfile -t furthrresearch/furthrmind-server-v1:{tag}",
        # f"docker push furthrresearch/furthrmind-server-v1:{tag}",

    if buildDemo:
        commandList.append(f"{dockerDemoCommand}")

    if push:
        if buildServer:
            for command in dockerPushServerCommandList:
                commandList.append(command)

        if buildWorker:
            for command in dockerPushWorkerCommandList:
                commandList.append(command)

        if buildTrigger:
            for command in dockerPushTriggerCommandList:
                commandList.append(command)
        if demoTagList:
            for command in dockerPushDemoCommandList:
                commandList.append(command)

    # batFile = f"{folderPath}/build.bat"
    shFile = f"{folderPath}/build.sh"

    with open(shFile, "w+") as f:
        pass

    for command in commandList:
        with open(shFile, "a") as f:
            f.write(f"{command}\n")

    # subprocess.run(totalCommand)
    # stdin, stdout, stderr = client.exec_command(totalCommand)
    # waitForCommand(stdout, stderr)

    import random
    rnd1 = random.randint(1, 9)
    rnd2 = random.randint(1, 9)
    result = rnd1 * rnd2

    answer = input(
        f"build server: {buildServer}\n"
        f"build worker: {buildWorker}\n"
        f"build trigger: {buildTrigger}\n"
        f"push: {push}\n"
        f"Tags: {tagList}\n"
                   f"Is that correct? What is {rnd1}x{rnd2}?: ")
    answerCorrect = False
    try:
        if int(answer) == result:
            answerCorrect = True
    except:
        pass
    if answerCorrect:
        # os.system(f'chmod +x {shFile}')
        subprocess.call(["sh", shFile])



if __name__ == "__main__":

    filePath = os.path.abspath(__file__)
    filePath = filePath.replace("\\", "/")
    folderPath = filePath.replace("/build_docker_wsl.py", "")
    rootPath = filePath.replace("/docker/build_docker_wsl.py", "")

    import sys

    if os.path.join(rootPath, "tests") in sys.path:
        sys.path.remove(os.path.join(rootPath, "tests"))
    config_file = os.path.join(rootPath, "config.py")

    sys.path.insert(0, config_file)
    sys.path.insert(0, rootPath)

    print(os.getcwd())
    import config

    tagList = []
    version_list = config.SERVER_VERSION.split(".")
    main_version = f"{version_list[0]}.{version_list[1]}"
    tagList.extend([
        "latest", f"{config.SERVER_VERSION}", main_version
    ])
    tagList.append("demo")
    
    tagList.append("dev")
    
    buildServer = True
    buildWorker = True
    buildTrigger = False
    buildDemo = True  # only build if tag == "Demo" or "latest"

    push = True

    createDocker(rootPath, folderPath,tagList, buildServer, buildWorker, buildTrigger, buildDemo, push)

