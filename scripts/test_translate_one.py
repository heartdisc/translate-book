#!/usr/bin/env python3
import sys
import os
import subprocess
import json

from gen_prompts_for_batch import get_args

def main():
    temp_dir = "/Users/shinosuke/Documents/Ebooks/Robot-Proof_When_Machines_Have_All_the_Answers_Build_Better_People_-_Dr_Vivienne_Ming_temp"
    chunk = "chunk0001.md"
    
    prompt = get_args(temp_dir, chunk)
    
    print("Prompt generated. Length:", len(prompt))
    print("Running agy --print...")
    
    # We can pass the prompt via stdin or as an argument
    # Let's pass via stdin if agy supports it, or as argument. 
    # Let's check if we can pass it to stdin.
    cmd = ["/Users/shinosuke/.local/bin/agy", "--print", prompt]
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    print("Exit code:", res.returncode)
    print("STDOUT (first 500 chars):")
    print(res.stdout[:500])
    print("STDERR:")
    print(res.stderr)

if __name__ == "__main__":
    main()
