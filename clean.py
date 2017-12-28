from __future__ import print_function
import os
import shutil
import stat
import subprocess
import requests
from unipath import Path

def req():
    subprocess.run("pip install -r requirements.txt")
    os.system('cls')
req()

HOME = Path(os.path.dirname(os.path.abspath(__file__)))
UP = HOME.parent
BFG_URL = "http://repo1.maven.org/maven2/com/madgag/bfg/1.12.16/bfg-1.12.16.jar"
BFG = "java -jar %s\\bfg.jar" % HOME
files = []
folders = []
OPTIONS = []

def onerror(func, path, exc_info):
    """shutil error handler for read-only files"""
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        pass

def download():
    """downloads bfg version 1.12.16, renames is bfg.jar"""
    if not os.path.isfile(f"{HOME}\\bfg.jar"):
        r = requests.get(BFG_URL)
        with open(f'{HOME}/bfg.jar', 'wb+') as z:
            z.write(r.content)

def getinfo():
    """gets GitHub username, repo name, deletes old mirror and backup if they exist,
    makes new ones"""
    opt1 = False
    opt2 = False
    opt3 = False
    user = input("Enter GitHub UserName: ")
    repo = input("Enter repository name: ")
    os.chdir(UP)
    if os.path.isdir(f'{repo}.git'):
        shutil.rmtree(f'{repo}.git', onerror=onerror)
    if os.path.isdir(f'BKUP0{repo}.git'):
        shutil.rmtree(f'BKUP0{repo}.git', onerror=onerror)
    subprocess.call("git clone --mirror https://github.com/%s/%s.git BKUP0%s.git" \
    % (user, repo, repo))
    gettask(user=user, repo=repo, opt1=opt1, opt2=opt2, opt3=opt3, files=files, folders=folders)

def gettask(user, repo, opt1, opt2, opt3, files, folders):
    """gets the task"""
    task = input("1-Remove file 2-Remove folder 3-Replace text\nEnter #: ")
    if task in "123":
        if task is "1":
            opt1 = True
            remfile(user, repo, opt1, opt2, opt3, files, folders)
        if task is "2":
            opt2 = True
            remfold(user, repo, opt1, opt2, opt3, files, folders)
        if task is "3":
            opt3 = True
            reptext(user, repo, opt1, opt2, opt3, files, folders)
    else:
        print("Enter 1, 2, or 3")
        gettask(user, repo, opt1, opt2, opt3, files, folders)

def remfile(user, repo, opt1, opt2, opt3, files, folders):
    """removes a file from index, adds it to gitignore"""
    filepath = input("Enter path to file (ex: folder\\file.txt): ")
    realpth = Path(f"{UP}\\{repo}\\{filepath}")
    os.chdir(f"{repo}")
    filepath = filepath.replace('\\', '/')
    subprocess.run(f"git rm --cached {filepath}")
    with open('.gitignore', 'a') as f:
        f.write(f"{filepath}\n")
    subprocess.run("git add .gitignore")
    files.append(f"{realpth.name}")
    os.chdir(UP)
    ismore(user, repo, opt1, opt2, opt3, files, folders)

def remfold(user, repo, opt1, opt2, opt3, files, folders):
    """removes a folder from index, recursively including files, adds folder to gitignore"""
    folderpath = input("Enter path to folder (ex: files\\folder): ")
    realpth = Path(f"{UP}\\{repo}\\{folderpath}")
    os.chdir(f"{UP}\\{repo}")
    folderpath = folderpath.replace('\\', '/')
    subprocess.run(f"git rm --cached {folderpath}/ -r")
    with open('.gitignore', 'a') as f:
        f.write(f"{folderpath}/\n")
    subprocess.run("git add .gitignore")
    folders.append(f"{realpth.name}")
    os.chdir(UP)
    ismore(user, repo, opt1, opt2, opt3, files, folders)

def reptext(user, repo, opt1, opt2, opt3, files, folders):
    """replaces text in file,
    creates or adds to rep.txt, commits file, force push, removes from index"""
    filepath = input("Enter path to file containing text to replace (ex: folder\\file.txt): ")
    os.chdir(f"{repo}")
    filepath = filepath.replace('\\', '/')
    with open('.gitignore', 'a') as f:
        f.write(f"{filepath}\n")
    subprocess.run("git add .gitignore")
    words = input("Enter word/replacement combo (ex: password123/your-password-here): ")
    word = words.split('/')[0].strip()
    repl = words.split('/')[1].strip()
    with open(f'{HOME}/rep.txt', 'a+') as rep:
        rep.write(f'{word}==>{repl}\n')
    subprocess.run(f"sed -i 's/{word}/{repl}/g' {filepath}")
    subprocess.run(f"git add {filepath}")
    subprocess.run('git commit -m "replace text"')
    subprocess.run("git push")
    subprocess.run(f"git rm --cached {filepath}")
    subprocess.run(f"git add {filepath} -f")
    os.chdir(UP)
    ismore(user, repo, opt1, opt2, opt3, files, folders)

def commit(user, repo, opt1, opt2, opt3, files, folders):
    """queries git status, force pushes to all branches"""
    os.chdir(repo)
    subprocess.run("git status")
    msg = input("Your commit message: ")
    subprocess.run(f'git commit -m "{msg}"')
    user_choice = input("Ready to Push? (y/n) \
    Yes to push changes to all branches, or no to Skip. ")
    if user_choice.lower().startswith('y'):
        subprocess.run("git push -f --all")
        os.chdir(UP)
        bfg(user, repo, opt1, opt2, opt3, files, folders)
    else:
        os.chdir(UP)
        bfg(user, repo, opt1, opt2, opt3, files, folders)

def bfg(user, repo, opt1, opt2, opt3, files, folders):
    """makes another backup (deletes old one), runs the bfg-repo-cleaner"""
    if os.path.isdir(f'BKUP1{repo}.git'):
        shutil.rmtree(f'BKUP1{repo}.git', onerror=onerror)
    subprocess.run("git clone --mirror https://github.com/%s/%s.git" % (user, repo))
    subprocess.run("mkdir BKUP1%s.git" % repo)
    subprocess.run("robocopy %s.git BKUP1%s.git /E" % (repo, repo))
    OPT1 = "-D "+"{"+",".join(files)+"}"
    OPT2 = "--delete-folders {"+",".join(folders)+"}"
    OPT3 = "-rt %s\\rep.txt" % HOME
    if opt1 is True:
        OPTIONS.append(OPT1)
    if opt2 is True:
        OPTIONS.append(OPT2)
    if opt3 is True:
        OPTIONS.append(OPT3)
    BFGOPTS = " ".join(OPTIONS)
    print(f"BFG options: {BFGOPTS}")
    subprocess.run(r'%s %s %s.git | grep -v "You can\|make people\|give up"' \
    % (BFG, BFGOPTS, repo), shell=True)
    os.chdir(UP)
    clean(repo)

def ismore(user, repo, opt1, opt2, opt3, files, folders):
    """checks for more"""
    more = input("Is there more? (y/n) ")
    if more.lower() in 'yn':
        if more.lower().startswith('y'):
            gettask(user, repo, opt1, opt2, opt3, files, folders)
        if more.lower().startswith('n'):
            commit(user, repo, opt1, opt2, opt3, files, folders)
    else:
        print("Yes or no, please...")
        ismore(user, repo, opt1, opt2, opt3, files, folders)

def clean(repo):
    """clean up, prune empty commits,
    pushes, moves to regular repo and does a force pull (rebase)"""
    os.chdir('%s.git' % repo)
    subprocess.run("git reflog expire --expire=now --all")
    subprocess.run("git gc --prune=now --aggressive")
    subprocess.run("git filter-branch --prune-empty -f")
    subprocess.run("git push")
    os.chdir("../%s" % repo)
    subprocess.run("git pull --rebase -f")
    os.chdir(HOME)

def main():
    download()
    getinfo()
main()
