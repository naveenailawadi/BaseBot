import shutil
import sys
import os


# set the filename
DIRECTORY = 'BaseBot'


def main(days):
    # get to the main folder
    os.chdir(f"../{DIRECTORY}")

    # run the verification script
    os.system(f"python verify.py {days}")

    # go back and compress it
    os.chdir('../')

    # compress it
    shutil.make_archive(DIRECTORY, 'zip', DIRECTORY)


if __name__ == '__main__':
    main(sys.argv[1])
