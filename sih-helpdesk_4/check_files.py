import os

print("--- DIAGNOSTIC START ---")
current_folder = os.getcwd()
print(f"Current Working Directory: {current_folder}")

files = os.listdir(current_folder)
print("\nFiles found in this folder:")
found_ai = False
for f in files:
    print(f" - {f}")
    if "ai_engine" in f:
        found_ai = True

print("\n------------------------")
if found_ai:
    print("[OK] SUCCESS: 'ai_engine' file found. Check the exact name above.")
else:
    print("[ERROR] ERROR: 'ai_engine.py' is NOT in this folder.")
    print("Please move the file here: " + current_folder)
print("--- DIAGNOSTIC END ---")