import os
import pickle

PATH_TO_HERE = "\\".join(os.path.dirname(os.path.abspath(__file__)).split("\\")[:-1])

if __name__ == "__main__":
    # rename files
    with open("name_directory.pkl", "rb") as f:
        name_directory = pickle.load(f)
    print(os.listdir(f"../pdbFiles"))
    for file in os.listdir(f"../pdbFiles"):
        if file.endswith(".pdb") and (id := file.split(".")[0]).isdigit():
            file_name = name_directory.get(int(id))
            if file_name == None:
                print(f"Could not find name for {file}")
            else:
                try:
                    os.rename(f"../pdbFiles/{file}", f"../pdbFiles/{file_name}.pdb")
                except FileExistsError:
                    print(f"File {file_name}.pdb already exists")
                except Exception as e:
                    print(f"Error renaming {file}: {e}")
    #         if (id := file.split(".")[0]).isdigit():
    #             file_name = name_directory.get(int(id))
    #         else:
    #             continue
    #         if file_name == None:
    #             print(f"Could not find name for {file}")
    #         else:
    #             try:
    #                 os.rename(f"..\pdbFiles\{file}", f"..\pdbFiles\{file_name}.pdb")
    #             except FileExistsError:
    #                 print(f"File {file_name}.pdb already exists")
    #             except Exception as e:
    #                 print(f"Error renaming {file}: {e}")
