""" Config file to handle app configurations """
from environs import Env

DEBUG = True
env = Env()
env.read_env()