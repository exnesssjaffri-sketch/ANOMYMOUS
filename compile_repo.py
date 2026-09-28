#!/usr/bin/env python3
import compileall
import os

# Compile all Python files in the current directory and subdirectories
compileall.compile_dir(os.getcwd())