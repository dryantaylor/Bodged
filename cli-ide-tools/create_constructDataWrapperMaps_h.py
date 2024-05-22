import re
import glob, os
import sys

def get_componentData_or_None(file_loc):
    with open(file_loc,"r") as file:
      contents = file.read()
    return (re.search("struct\s+([\S]+)\s*\:\s*(?:public\s+)?\s*ComponentData",contents), 
            re.search("namespace\s+([\S]+)\s*{",contents))


if __name__ == "__main__":
    path = ""
    output_path = ""

    if len(sys.argv) == 1:
        print("Invalid arguments, use -h or --help for help")
        exit()
    elif sys.argv[1] in ["-h", "--help"]:
        print("Script to generate the constructDataWrapperMaps.h file for the MacGyver project from the .h files in the project directory")
        print("arguments: create_data_wrapper_maps.py <path to .h files> <output path if different>")
    elif sys.argv[1] in ["-d", "--defualt"]:
        path = "C:\\Users\\44791\\source\\repos\\macgyver_v1\\MacGyver"
        output_path = path + "\\constructDataWrapperMaps.h"
    elif len(sys.argv) == 2:
        path = sys.argv[1]
        output_path = path + "\\constructDataWrapperMaps.h"
    elif len(sys.argv) == 3:
        path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        print("Invalid arguments, use -h or --help for help")
        exit()
    
    matches = {}

    #find all h files which inherit from ComponentData to indicate they have a custom destructor

    os.chdir(path)
    for file in glob.glob("*.h"):
        component = get_componentData_or_None(path + "\\"+ file)
        #print(file + ": " + str(component))
        if component[0] is not None:
            matches[file] = [component[0].group(1), component[1].group(1)]

    #generate the destructors.h file
    contents = """
    #pragma once
    #include "componentDataWrapper.h"

    """

    #include all the needed header files
    for file in matches.keys():
        contents += "#include \"" + file + "\"\n"

    contents += """

    const std::map<std::size_t, const std::function<void(Macgyver::Components::ComponentData*)>>
    Macgyver::Components::ComponentDataWrapper::ComponentDataWrapper::destructors = {
        
    """
    #create the function map
    for match in matches.values():
        cls = match[0]
        namespace = match[1]
        contents += "\t{typeid(" +namespace+"::"+ cls + ").hash_code(), [](Macgyver::Components::ComponentData* data){delete static_cast<" +namespace+"::"+ cls+ "*>(data);}},\n"


    contents += "};"

    #create map of component names to use for debugging
    contents += """
    #ifdef _DEBUG
    const std::map<std::size_t, const std::string> 
    Macgyver::Components::ComponentDataWrapper::ComponentDataWrapper::typeHashToComponentNames = {
    """
    for match in matches.values():
        cls = match[0]
        namespace = match[1]
        contents += "\t{typeid(" +namespace+"::"+ cls + ").hash_code(), \""+namespace+"::"+ cls+ "\"},\n"

    contents += "};\n#endif\n"

    with open(output_path, "w") as file:
        file.write(contents)

    print("File created at: " + output_path)
