# --- import --------------------------------------------------------------------------------------


import WrightTools as wt
import argparse


# --- define --------------------------------------------------------------------------------------
# Entry points from terminal

# Print a wt5 file tree
def wt_tree():
    parser = argparse.ArgumentParser(description="Print a given data tree.")

    # Add arguments
    parser.add_argument("path", type=str)
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose? False by default")
    parser.add_argument("--depth", "-d", "-L", type=int, default=9, help="depth to print (int)")
    parser.add_argument("internal_path", nargs="?", default="/")
    args = parser.parse_args()

    # Create the data/collection object
    obj = wt.open(args.path, edit_local=True)[args.internal_path]

    # Print the tree
    # If the wt5 is a data object, it doesn't take depth as a parameter
    if isinstance(obj, wt.Data):
        obj.print_tree(verbose=args.verbose)
    else:
        obj.print_tree(verbose=args.verbose, depth=args.depth)

def wt_convert():
    parser = argparse.ArgumentParser(description="Converts data units.")
    parser.add_argument('args', nargs='*')
    argsList = parser.parse_args().args
    #print(argsList)
    #i = argsList[0]

    # Perhaps more efficient way to do this is to loop backwards so I start with the units
    # Also use the other printer I used for the first assignment
    unitArgs = []
    units = {"nm", "wn", "eV", "meV", "Hz", "THz", "GHz"}
    for arg in argsList:
        if arg in units:
            unitArgs.append(arg)
    #print(unitArgs)

    # No destination units provided
    if len(unitArgs) == 1:
        for unit in units:
            if unit != unitArgs[0]:
                print(wt.units.converter(float(argsList[0]), unitArgs[0], unit), unit)
    else:
        for arg in argsList:
            if arg not in units:
                print(wt.units.converter(float(arg), unitArgs[0], unitArgs[1]))

    #print(wt.units.converter(float(argsList[0]), argsList[1], argsList[2]))