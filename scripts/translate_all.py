#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from gen_prompts_for_batch import get_args

def translate_chunk(temp_dir, chunk_id):
    chunk_filename = f"{chunk_id}.md"
    output_filename = f"output_{chunk_id}.md"
    meta_filename = f"output_{chunk_id}.meta.json"
    
    output_path = os.path.join(temp_dir, output_filename)
    meta_path = os.path.join(temp_dir, meta_filename)
    
    if os.path.exists(output_path) and os.path.exists(meta_path) and os.path.getsize(output_path) > 0:
        print(f"[{chunk_id}] Already translated. Skipping.")
        return chunk_id, True
        
    print(f"[{chunk_id}] Starting translation...")
    
    try:
        # Generate prompt using the skill logic (glossary and neighbors)
        prompt = get_args(temp_dir, chunk_filename)
        
        # Run agy --print with --dangerously-skip-permissions to ensure smooth execution
        cmd = ["/Users/shinosuke/.local/bin/agy", "--dangerously-skip-permissions", "--print", prompt]
        
        # Run with timeout to prevent hanging
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if res.returncode != 0:
            print(f"[{chunk_id}] Failed with exit code {res.returncode}. Error: {res.stderr}")
            return chunk_id, False
            
        translation = res.stdout.strip()
        if not translation:
            print(f"[{chunk_id}] Received empty output.")
            return chunk_id, False
            
        # Write translated file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translation)
            
        # Write default empty meta file
        meta_data = {
            "schema_version": 1,
            "new_entities": [],
            "alias_hypotheses": [],
            "attribute_hypotheses": [],
            "used_term_sources": [],
            "conflicts": []
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)
            
        # Record completion in run_state
        # Run: python3 run_state.py record <temp_dir> chunkXXXX
        # Let's call run_state.py as subprocess
        record_cmd = [
            "python3", 
            "/Users/shinosuke/Documents/Ebooks/skills/translate-book/scripts/run_state.py",
            "record",
            temp_dir,
            chunk_id
        ]
        sub_res = subprocess.run(record_cmd, capture_output=True, text=True)
        if sub_res.returncode != 0:
            print(f"[{chunk_id}] Warning: run_state record failed: {sub_res.stderr}")
            
        print(f"[{chunk_id}] Completed successfully.")
        return chunk_id, True
        
    except subprocess.TimeoutExpired:
        print(f"[{chunk_id}] Timed out after 300 seconds.")
        return chunk_id, False
    except Exception as e:
        print(f"[{chunk_id}] Exception occurred: {e}")
        return chunk_id, False

def main():
    temp_dir = "/Users/shinosuke/Documents/Ebooks/Robot-Proof_When_Machines_Have_All_the_Answers_Build_Better_People_-_Dr_Vivienne_Ming_temp"
    concurrency = 12
    
    # Read plan to see which chunk ids to translate
    plan_cmd = [
        "python3",
        "/Users/shinosuke/Documents/Ebooks/skills/translate-book/scripts/run_state.py",
        "plan",
        temp_dir
    ]
    res = subprocess.run(plan_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error getting plan: {res.stderr}")
        sys.exit(1)
        
    plan_data = json.loads(res.stdout)
    translation_chunk_ids = plan_data.get("translation_chunk_ids", [])
    
    print(f"Total chunks to translate: {len(translation_chunk_ids)}")
    if not translation_chunk_ids:
        print("Nothing to translate.")
        return
        
    success_count = 0
    failure_chunks = []
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(translate_chunk, temp_dir, cid): cid for cid in translation_chunk_ids}
        for future in as_completed(futures):
            cid = futures[future]
            try:
                chunk_id, success = future.result()
                if success:
                    success_count += 1
                else:
                    failure_chunks.append(chunk_id)
            except Exception as e:
                print(f"[{cid}] Future raised exception: {e}")
                failure_chunks.append(cid)
                
    print(f"\nTranslation run finished. Successful: {success_count}/{len(translation_chunk_ids)}")
    if failure_chunks:
        print(f"Failed chunks: {', '.join(failure_chunks)}")
        sys.exit(1)
    else:
        print("All chunks translated successfully!")

if __name__ == "__main__":
    main()
