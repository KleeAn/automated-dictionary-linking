# ================================================================
# Script for executing a 2-step pipeline that maps lexical units
# to drinking vocabulary concepts using large language models from ollama.
# ================================================================

from pathlib import Path
from script_9_4_1_01_ollama_mapping_wurzelkonzepte import run_mapping_wurzelkonzepte
from script_9_4_1_02_ollama_mapping_basiskonzepte import run_mapping_basiskonzepte
import time

# ----------------------------------------
# Configuration
# ----------------------------------------
CONFIG = {
    "input_folder": Path("input"),         
    "output_folder": Path("output"),
    "json_vocab": Path("input/trinken_vokabular.json"), #Path("input/trinken_vokabular_nur_OT.json"),
    "model_name": "llama3.3:70b", #"llama3.1:8b", #"deepseek-r1:32b", #"deepseek-r1:70b", #"qwen2.5:32b", #"qwen2.5:72b"
    "files_to_process": None,     # None = all TSVs in input_folder
    "prompts": {
        "basiskonzepte": Path("input/basiskonzepte_prompt_3a.txt"),
        "wurzelkonzepte": Path("input/wurzelkonzepte_prompt_4b.txt")
    },
    "with_terms": True   # True to pass the terms for the concept names 
}


# Ensure output folder exists
CONFIG["output_folder"].mkdir(parents=True, exist_ok=True)

# ================================================================
# Load prompt from file
# ================================================================
def load_prompt(prompt_path: Path) -> str:
    abs_path = Path(__file__).parent / prompt_path
    with open(abs_path, 'r', encoding='utf-8') as f:
        prompt_text = f.read()
    
    print(f"\n--- Loaded prompt from {prompt_path} ---")
    print(prompt_text[:500])
    print("--- End of prompt preview ---\n")
    
    return prompt_text
    
# ----------------------------------------
# Pipeline execution
# ----------------------------------------
def run_pipeline(config: dict):
    print("=== Starting Pipeline ===")

    input_folder = config["input_folder"]
    output_folder = config["output_folder"]
    json_vocab = config["json_vocab"]
    model_name = config["model_name"]
    files_to_process = config["files_to_process"]

    
    # ------------------------------------------------------------
    # Step 1: Mapping Wurzelkonzepte
    # ------------------------------------------------------------
   
    
    print("Step 1: Mapping Wurzelkonzepte...")
    prompt_root = load_prompt(config["prompts"]["wurzelkonzepte"])
    root_files = run_mapping_wurzelkonzepte(
        input_folder=input_folder,
        output_folder=output_folder,
        json_path=json_vocab,
        model_name=model_name,
        files_to_process=files_to_process,
        prompt_text=prompt_root
    )
    
    
    # Files for step 2
    root_files_names = [f.name for f in root_files]

    # ------------------------------------------------------------
    # Step 2: Mapping Basiskonzepte
    # ------------------------------------------------------------
    print("Step 2: Mapping Basiskonzepte...")
    prompt_basis = load_prompt(config["prompts"]["basiskonzepte"])
    files_basis = run_mapping_basiskonzepte(
        files=root_files_names,
        input_folder=output_folder,
        json_path=json_vocab,
        model_name=model_name,
        prompt_text=prompt_basis,
        with_terms=config["with_terms"]
    )
    
    print("\n=== Pipeline completed ===")
    
    print("Generated files:")
    for f in files_basis:
        print(f" - {f}")

    return files_basis
    


# ================================================================
# Standalone execution
# ================================================================
if __name__ == "__main__":
    # get runtime
    start_time = time.time()
    run_pipeline(CONFIG)
    end_time = time.time()

    elapsed = end_time - start_time
    minutes, seconds = divmod(elapsed, 60)
    print(f"\n=== Script runtime: {elapsed:.2f} seconds // {int(minutes)} min {seconds:.2f} sec ===")

