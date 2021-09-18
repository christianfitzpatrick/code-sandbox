'''
Utility structures for execution of remote code requests via Docker

Every code execution request is treated as a 'job' for a Docker container:
    - Interpreted jobs: The file is run directly in a container for its language's runtime

    - Compiled jobs: Docker builds an image for the request in which to compile the code
      and runs the output in a container
'''

import subprocess
import os
import tempfile

# File system parameters
HOST_DIR = os.path.abspath("tmp_src")
MNT_DIR = "/usr/src/app"


# Interpreted language runtimes
RUNTIMES = {
    "py": "python:latest python",
    "js": "node:latest node",
    "rb": "ruby:latest ruby"
}


# Docker run template
RUN_CMD = "docker run --rm -v {host}:{mnt} {runtime} {mnt}/{src}"

# Compilers
COMPILERS = {
    "c": "gcc"
}

# Dockerfile template
DOCKERFILE = '''
FROM {compiler}
COPY . {mnt}
WORKDIR {mnt}
RUN {compiler} -o {exe} tmp_src/{src}
CMD ["./{exe}"]
'''.strip()


# Docker build and run templates for compiled code
BUILD_CMD = "docker build -t {name} -f {tmp_dir}/dockerfiles/{dockerfile}  ."
RUN_EXECUTABLE_CMD = "docker run -it --rm {name}"


class DockerRunJob:
    ''' State and logic for a Docker run command. Used for interpreted implementations '''

    def __init__(self, src_file: str):
        self.src_file = src_file
        self.file_ext = self.src_file.split('.')[-1]
        self.runtime = RUNTIMES[self.file_ext]

    def generate_cmd(self) -> str:
        ''' generate docker run command from template '''
        return RUN_CMD.format(host=HOST_DIR, mnt=MNT_DIR, runtime=self.runtime, src=self.src_file)

    def run(self) -> str:
        ''' launch the docker run process '''
        docker_run_cmd = self.generate_cmd().split(' ')
        proc = subprocess.run(docker_run_cmd, check=True,
                              stdout=subprocess.PIPE)
        output = proc.stdout.decode().strip()
        os.remove(f'{HOST_DIR}/{self.src_file}')
        return output


class DockerBuildJob:
    ''' State and logic for a Docker build command. Used for compiled implementations '''

    def __init__(self, src_file: str, executable: str = 'main'):
        self.src_file = src_file
        self.file_ext = self.src_file.split('.')[-1]
        self.compiler = COMPILERS[self.file_ext]
        self.executable = executable

    def generate_dockerfile(self) -> str:
        ''' generate Dockerfile from template '''
        return DOCKERFILE.format(
            mnt=MNT_DIR, src=self.src_file, compiler=self.compiler, exe=self.executable)

    def build_and_run(self) -> str:
        ''' build an image for a container to compile and run code requests in '''

        with tempfile.NamedTemporaryFile(
                dir=f"{HOST_DIR}/dockerfiles", delete=False, suffix='.Dockerfile') as dockerfile:
            contents = str.encode(self.generate_dockerfile())
            dockerfile.write(contents)
            filename = os.path.split(dockerfile.name)[-1]

        build = BUILD_CMD.format(
            tmp_dir=HOST_DIR, dockerfile=filename, name='tmp-build')

        build_proc = subprocess.run(
            build, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if build_proc.returncode != 0:
            os.remove(f'{HOST_DIR}/dockerfiles/{filename}')
            return build_proc.stderr.decode().strip()

        run = RUN_EXECUTABLE_CMD.format(name='tmp-build')
        run_proc = subprocess.run(
            run, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        os.remove(f'{HOST_DIR}/dockerfiles/{filename}')
        os.remove(f'{HOST_DIR}/{self.src_file}')
        return run_proc.stdout.decode().strip()
