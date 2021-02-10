
#!/usr/bin/env python
import os
import subprocess

DIR = os.path.dirname(__file__)
UNSUPPORTED_VERSIONS = [
    # python2
    "0.2",
    "0.3",
    "0.4",
    "0.5",
    "0.6",
    "0.7",
    "0.8",
    "1.0",
    "1.1",
    "1.2",
    "1.3",
    "1.4",
    "1.5",
    "6.0",
    "18.0",
    "18.1",
    "19.0",
    "19.1",
    "19.2",
    "19.3",
    "20.0",
    # "20.1",
    # "20.2",
    # "20.3",
    # "21.0",
]

if __name__ == "__main__":
    subprocess.check_call(["curl", "https://bootstrap.pypa.io/get-pip.py", "-o", "untracked_get-pip.py"])
    stdout = subprocess.check_output(["{}/get_versions.py".format(DIR), "pip"])
    versions = stdout.decode("utf-8").split("\n")
    versions_check = [
        version for version in versions 
        if 
            (version.count(".") == 1)
            and ("b" not in version)
            and (version not in UNSUPPORTED_VERSIONS)
    ][::-1]
    print("checking versions: \n" + "\n".join(versions_check))

    for version in versions_check:
        if version in UNSUPPORTED_VERSIONS:
            continue
        print("=========== checking {}".format(version))
        subprocess.check_call(["python", "untracked_get-pip.py"])
        subprocess.check_call(["pip", "install", "-U", "pip=={}".format(version)])
        stdout = subprocess.check_output(["{}/run_tests.sh".format(DIR)])
        response = stdout.decode("utf-8")
        if "SUCCESS" not in response:
            raise ValueError("verions not supported {}".format(version))
