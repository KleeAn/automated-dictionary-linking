# ================================================================
# Script for executing a 2-step pipeline that maps lexical units
# to beverage terms of a drinking vocabulary using large language models
# from ollama.
# ================================================================

from pathlib import Path
from script_9_4_3_01_ollama_mapping_basiskonzepte import run_mapping_basiskonzepte
from script_9_4_3_02_ollama_mapping_begriffe import run_mapping_begriffe   
import time

# ----------------------------------------
# Configuration
# ----------------------------------------
CONFIG = {
    "input_folder": Path("input"),         
    "output_folder": Path("output"),
    "json_vocab": Path("input/getränke_vokabular.json"), #"input/getränke_vokabular_nur_OT.json"
    "model_name": "llama3.3:70b",
    "files_to_process": None,     # None = all TSVs in input_folder
    "prompts": {
        "basiskonzepte": Path("input/getränke_concepts_prompt.txt"),
        "begriffe": Path("input/getränke_terms_prompt.txt") 
    },
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
    # Step 1: Mapping Basiskonzepte
    # ------------------------------------------------------------
    print("Step 1: Mapping Basiskonzepte...")
    
    # If no files specified, take all TSVs from input_folder
    if files_to_process is None:
        files_to_process = [f.name for f in input_folder.glob("*.tsv")]
    
    prompt_basis = load_prompt(config["prompts"]["basiskonzepte"])
    files_basis = run_mapping_basiskonzepte(
        files=files_to_process,
        input_folder=input_folder,
        output_folder=output_folder,
        json_path=json_vocab,
        model_name=model_name,
        prompt_text=prompt_basis,
    )
    
    
    # Files for step 2
    basis_files_names = [f.name for f in files_basis]
    #basis_files_names = ["A_Getränke_basiskonzepte.tsv"]
    # ------------------------------------------------------------
    # Step 2: Mapping terms
    # ------------------------------------------------------------
    print("Step 2: Mapping terms...")
    prompt_terms = load_prompt(config["prompts"]["begriffe"])
    files_terms = run_mapping_begriffe(
        files=basis_files_names,
        input_folder=output_folder,
        json_path=json_vocab,
        model_name=model_name,
        prompt_text=prompt_terms,
    )
    
    print("\n=== Pipeline completed ===")
    
    print("Generated files:")
    for f in files_terms:
        print(f" - {f}")

    return files_terms
    


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

