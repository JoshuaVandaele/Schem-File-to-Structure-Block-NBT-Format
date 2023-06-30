import argparse
import os
import re
from math import floor

from nbtlib import CompoundSchema, File, load, schema
from nbtlib.tag import Compound, Int, List, String

SCHEMATIC_VERSION = 2586


def structure_schema() -> CompoundSchema:
    """Generate a structure schema.

    Returns:
        CompoundSchema: The structure schema.
    """
    return schema(
        "Structure",
        {
            "DataVersion": Int,
            "author": String,
            "size": List[Int],
            "palette": List[
                schema(
                    "State",
                    {
                        "Name": String,
                        "Properties": Compound,
                    },
                )
            ],
            "blocks": List[
                schema(
                    "Block",
                    {
                        "state": Int,
                        "pos": List[Int],
                        "nbt": Compound,
                    },
                )
            ],
        },
    )()


def get_schematic_size(worldedit: File) -> dict[str, int]:
    """Gets the size of a worldedit schematic file.

    Args:
        worldedit (File): The worldedit schematic file.

    Returns:
        dict[str, int]: A dictionary containing the size of the schematic in the x, y, and z directions.
    """
    return {
        "x": int(worldedit["Length"]),
        "y": int(worldedit["Height"]),
        "z": int(worldedit["Width"]),
    }


def initiate_schema(worldedit: File) -> CompoundSchema:
    """Initiates a structure file.

    Args:
        worldedit (File): The worldedit schematic file to base the structure file off of.

    Returns:
        CompoundSchema: The structure file.
    """
    nbt_schematic: CompoundSchema = structure_schema()
    nbt_schematic["DataVersion"] = SCHEMATIC_VERSION
    nbt_schematic["palette"] = []
    nbt_schematic["blocks"] = []
    nbt_schematic["author"] = "Folfy_Blue"

    size: dict[str, int] = get_schematic_size(worldedit)

    nbt_schematic["size"] = [size["x"], size["y"], size["z"]]
    return nbt_schematic


def get_block_palette(worldedit: File) -> dict[int, str]:
    """Gets the block palette from a worldedit schematic file and returns it as a dictionary.

    Args:
        worldedit (File): The worldedit schematic file.

    Returns:
        dict[int, int]: A dictionary of block palette entries.
    """
    return {int(v): k for k, v in dict(worldedit["Palette"]).items()}


def process_block_palette(
    nbt_schematic: CompoundSchema, byte_palette: dict[int, str]
) -> tuple[CompoundSchema, dict[str, int]]:
    """Processes the block palette from a worldedit palette and returns it in a structure file format.

    Args:
        nbt_schematic (CompoundSchema): The structure file.
        byte_palette (dict): The block palette.

    Returns:
        tuple[CompoundSchema, dict]: A tuple containing the structure file and the new palette.
    """
    new_palette = {}
    for _palette, block in byte_palette.items():
        block_name, block_properties = re.findall(r"(minecraft:\w+)(\[.+\])?", block)[0]
        block_properties = re.findall(r"((\w+)=(\w+))", block_properties)
        bp = {}
        for block_property in block_properties:
            bp[block_property[1]] = String(block_property[2])
        if len(bp) > 0:
            nbt_schematic["palette"].append({"Name": block_name, "Properties": bp})
        else:
            nbt_schematic["palette"].append({"Name": block_name})
        new_palette[block] = len(nbt_schematic["palette"]) - 1

    return nbt_schematic, new_palette


def process_block_entities(worldedit: File) -> dict[str, Compound]:
    """Processes block entities from a worldedit schematic file and returns them as a dictionary.

        Args:
    worldedit (nbtlib.File): The worldedit schematic file.

            Returns:
    dict[str, Compound]: A dictionary of block entities.
    """
    block_entities = {}
    for data in worldedit["BlockEntities"].copy():
        # Create a copy so we do not modify the worldedit file accidentally
        data = data.copy()
        key = f"{int(data['Pos'][0])} {int(data['Pos'][1])} {int(data['Pos'][2])}"
        data["id"] = data["Id"]
        del data["Id"]
        del data["Pos"]
        block_entities[key] = data
    return block_entities


def process_blocks(
    worldedit: File,
    nbt_schematic: CompoundSchema,
    byte_palette: dict[int, str],
    new_palette: dict[str, int],
    block_entities: dict[str, Compound] = {},
) -> CompoundSchema:
    """Processes blocks from a worldedit schematic file and returns them in a structure file format.

    Args:
        worldedit (File): The worldedit schematic file.
        nbt_schematic (CompoundSchema): The structure file.
        byte_palette (dict[int, str]): The old block palette from world edit.
        new_palette (dict[str, int]): The new block palette to use.
        block_entities (dict[str, Compound], optional): The block entities. If empty, they will be devoid of nbt. Defaults to {}.

    Returns:
        CompoundSchema: The structure file.
    """
    size: dict[str, int] = get_schematic_size(worldedit)

    for i in range(block_count := len(worldedit["BlockData"])):
        x = floor((i % (size["z"] * size["x"])) % size["z"])
        y = floor(i / (size["z"] * size["x"]))
        z = floor((i % (size["z"] * size["x"])) / size["z"])
        key: str = f"{x} {y} {z}"

        block_id = int(worldedit["BlockData"][i])

        try:
            block: str = byte_palette[block_id]
        except KeyError:
            block: str = byte_palette[0]
            print(
                f"We couldn't process the block at {key}: Block {block_id} doesn't exist. Defaulting to block 0 ({block})."
            )

        if key in block_entities:
            nbt_schematic["blocks"].append(
                {
                    "state": new_palette[block],
                    "pos": [x, y, z],
                    "nbt": block_entities[key],
                }
            )
        else:
            nbt_schematic["blocks"].append(
                {"state": new_palette[block], "pos": [x, y, z]}
            )
        print(
            f"Processed {i} / {block_count} blocks. ({round(i / block_count * 100, 2)} %)",
            end="\r",
        )
    return nbt_schematic


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts WorldEdit schematic files to Minecraft Structure files."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to the input schematic file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default=None,
        help="Path to the output nbt file.",
    )
    parser.add_argument(
        "-f",
        "--folder",
        action="store_true",
        default=False,
        help="Whether to treat the input path as a file or a folder.",
    )
    args = parser.parse_args()

    if args.folder:
        # input_path is a directory
        try:
            input_files = [
                file_path
                for f in os.listdir(args.input)
                if os.path.isfile(file_path := os.path.join(args.input, f))
            ]
            if not args.output:
                args.output = args.input

            os.makedirs(args.output, exist_ok=True)

            output_files = [
                os.path.join(args.output, f"{os.path.splitext(f)[0]}.nbt")
                for f in os.listdir(args.input)
                if os.path.isfile(os.path.join(args.input, f))
            ]
            print(output_files)
        except FileNotFoundError:
            print(f"Folder '{args.input}' not found.")
            exit(1)
    elif not os.path.isfile(args.input):
        # input_path doesn't exist
        print(f"File '{args.input}' not found.")
        exit(1)
    else:
        # input_path is a file
        input_files = [args.input]
        if not args.output:
            filename, file_extension = os.path.splitext(args.input)
            args.output = f"{filename}.nbt"
        output_files = [args.output]

    for i in range(len(input_files)):
        input_file = input_files[i]
        output_file = output_files[i]
        print(f"Processing {input_file}...")

        try:
            with load(input_file) as worldedit:
                nbt_schematic: CompoundSchema = initiate_schema(worldedit)

                block_entities = process_block_entities(worldedit)

                byte_palette = get_block_palette(worldedit)

                nbt_schematic, new_palette = process_block_palette(
                    nbt_schematic, byte_palette
                )

                nbt_schematic = process_blocks(
                    worldedit, nbt_schematic, byte_palette, new_palette, block_entities
                )
        except Exception as e:
            print(f"An error occurred while processing {input_file}: {repr(e)}")
            continue
        print("\nDone! Saving...")
        try:
            File({"": Compound(nbt_schematic)}, gzipped=True).save(output_file)
        except FileNotFoundError:
            print(f"Folder '{args.output}' not found. Could not save {output_file}.")
            continue
        print(f"Saved to {output_file}")
