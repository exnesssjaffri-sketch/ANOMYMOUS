import sys

with open('C:/Users/ALI HAIDER/OneDrive/Desktop/ANOMYMOUS/providers/registry.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[140:250], start=141):
        print(f"{i}: {line.rstrip()}")