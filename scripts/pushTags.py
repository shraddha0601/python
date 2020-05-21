import sys
import subprocess
import re
import os
from enum import Enum
from argparse import ArgumentParser

# TODO: Move it into separate project
# TODO: Push to github

MASTER_PATTERN = "v(\d+\.)?(\d+\.)?(\*|\d+)$"
CANDIDATE_PATTERN = "v(\d+\.)?(\d+\.)?(\*|\d+)-rc\.\d+$"

class SemanticVersion(Enum):
    MAJOR = 1
    MINOR = 2
    PATCH = 3

def releaseOrCandidateMatch(lastTag):
    if re.search(MASTER_PATTERN, lastTag):
        return "RELEASE"
    elif re.search(CANDIDATE_PATTERN, lastTag):
        return "CANDIDATE"


def calculateNextCandidateTag(tagList, sem_version):
    lastTag = tagList[-1]
    print("Last tag was: " + lastTag)
    version = releaseOrCandidateMatch(lastTag)

    if "RELEASE" == version:
        split = re.split("[v, ., -]", lastTag)
        if sem_version == SemanticVersion.PATCH:
            return "v" + split[1] + "." + split[2] + "." + str(int(split[3]) + 1) + "-rc.1"
        elif sem_version == SemanticVersion.MINOR:
            return "v" + split[1] + "." + str(int(split[2]) + 1) + "." + split[3]  + "-rc.1"
        elif sem_version == SemanticVersion.MAJOR:
            return "v" + str(int(split[1]) + 1) + "." + split[2] + "." + split[3]  + "-rc.1"

    elif "CANDIDATE" == version:
        split = re.split("[v, ., -]", lastTag)
        return "v" + split[1] + "." + split[2] + "." + split[3] + "-rc."  + str(int(split[5]) + 1)


def calculateNextReleaseTag(tagList, sem_version):
    lastTag = tagList[-1]
    print("Last tag was: " + lastTag)
    version = releaseOrCandidateMatch(lastTag)

    if "RELEASE" == version:
        split = re.split("[v, ., -]", lastTag)
        if sem_version == SemanticVersion.PATCH:
            return "v" + split[1] + "." + split[2] + "." + str(int(split[3]) + 1)
        elif sem_version ==SemanticVersion.MINOR:
            return "v" + split[1]  + "." + str(int(split[2]) + 1) + "." + split[3]
        elif sem_version == SemanticVersion.MAJOR:
            return "v" + str(int(split[1]) + 1) + "." + split[2] + "." + split[3]

    elif "CANDIDATE" == version:
        split = re.split("[v, ., -]", lastTag)
        return "v" + split[1] + "." + split[2] + "." + split[3]


def main(releaseOrCandidate, semantic, dir):
    call = subprocess.check_output(["git", "-C", dir, "tag"])
    tagList = []
    for line in call.splitlines():
        tag = line.decode('utf-8')
        tagList.append(tag)

    if len(tagList) == 0 and "release" == releaseOrCandidate:
        return "v0.0.1"
    elif len(tagList) == 0 and "candidate" == releaseOrCandidate:
        return "v0.0.1-rc.1"

    if "release" == releaseOrCandidate:
        tag = calculateNextReleaseTag(tagList, semantic)
    elif "candidate" == releaseOrCandidate:
        tag = calculateNextCandidateTag(tagList, semantic)
    else:
        raise Exception("Invalid option")

    print("Next tag: " + tag)
    return tag;


if __name__ == '__main__':

    parser = ArgumentParser(description= 'Calculate the next tag');
    parser.add_argument("-t", "--type", dest="type",
                    help="release or candidate", default='candidate')
    parser.add_argument("-s", "--semantic", dest="semantic", default='PATCH',
                    help="semantic version MAJOR/MINOR/PATCH")
    curDir = os.getcwd()
    parser.add_argument("-d", "--directory", dest="dir", default=curDir,
                        help="Full path to the Git repo")

    args = parser.parse_args()
    print(main(args.type, SemanticVersion[args.semantic], args.dir))

