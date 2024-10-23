import os,sys
import win32com.client
import subprocess
sys.path.append('./')

from llm.utils import get_green_logger
logger=get_green_logger()

def parse_lnk(path):
    logger.info(f'parsing lnk file from {path}')
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(path)
    result= shortcut.TargetPath
    logger.info(f'lnk file parsed, target path is {result}')
    return result


def start_exe(path):
    subprocess.Popen(path)