import os

import pathspec
from treelib.tree import Tree


def get_master_gitignore_spec(start_path):
    """
    Collects .gitignore patterns from the starting path and
    creates a single PathSpec for efficient checking.
    Explicitly adds .git ignore patterns.
    """
    all_patterns = []
    gitignore_path = os.path.join(start_path, ".gitignore")
    try:
        with open(gitignore_path, "r", encoding="utf-8") as file:
            # Filter out comments and empty lines
            all_patterns.extend(
                [
                    line.strip()
                    for line in file
                    if line.strip() and not line.strip().startswith("#")
                ]
            )
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Warning: Could not read .gitignore at {gitignore_path}: {e}")

    # Remove git related files
    all_patterns.append(".git/")  # Matches the directory itself and its contents
    all_patterns.append(".git/*")
    all_patterns.append(".gitignore")
    all_patterns.append("README.md")

    return pathspec.PathSpec.from_lines("gitwildmatch", all_patterns)


def is_ignored(full_path, base_path_abs, gitignore_spec):
    """
    Checks if a given full_path should be ignored based on the PathSpec.
    The path passed to spec.match_file must be relative to base_path_abs.
    """
    # Ensure full_path is within base_path_abs
    if not full_path.startswith(base_path_abs):
        return False

    # Get the path relative to the base_path_abs, and normalize separators
    relative_path = os.path.relpath(full_path, base_path_abs).replace(os.sep, "/")

    # The base_path_abs itself should never be ignored (represented by '.')
    if relative_path == ".":
        return False

    # Pathspec, like Git, often needs a trailing slash to correctly match directory patterns
    # (e.g., 'build/' matches only a directory named 'build', not a file).
    if os.path.isdir(full_path) and not relative_path.endswith("/"):
        relative_path += "/"

    return gitignore_spec.match_file(relative_path)


def read_file_content(filepath):
    """
    Reads the content of a text file. Handles common encoding errors.
    Returns content string or a placeholder if it's a binary file or unreadable.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, "r", encoding="latin-1") as f:  # Fallback to latin-1
                return f.read()
        except Exception:
            return "[Binary File or Unreadable Content]"
    except Exception as e:
        return f"[Error Reading File: {e}]"


def get_directory_tree_and_contents(startpath):
    """
    Builds the directory tree structure using treelib,
    ignoring files and directories specified in .gitignore files,
    and storing the content of each file.
    Returns the treelib Tree object and a dictionary of file paths to contents.
    """
    startpath_abs = os.path.abspath(startpath)

    gitignore_spec = get_master_gitignore_spec(startpath_abs)

    tree = Tree()
    # Determine the name to use for the root folder in the output paths (e.g., "my_project")
    display_root_name = os.path.basename(startpath_abs)
    if not display_root_name:  # Handles cases like '/' or 'C:\' on Windows
        display_root_name = startpath_abs  # Use the full path as the name

    tree.create_node(display_root_name, startpath_abs)  # Identifier is full path

    file_contents_map = {}  # To store 'ROOT_DIR/relative/path/to/file' -> content

    for root, dirs, files in os.walk(startpath_abs):
        current_node_id = root  # The parent node for files/dirs in the current 'root'

        # Filter directories and prune `dirs` in-place for os.walk
        filtered_dirs = []
        for d in sorted(dirs):  # Sort for consistent output order
            dir_full_path = os.path.join(root, d)
            if not is_ignored(dir_full_path, startpath_abs, gitignore_spec):
                # Add to treelib if not ignored (add trailing slash for visual distinction)
                tree.create_node(d + "/", dir_full_path, parent=current_node_id)
                filtered_dirs.append(d)  # Keep this directory for os.walk to traverse

        dirs[:] = filtered_dirs  # Crucial: Prune directories to visit by os.walk

        # Filter files and store content
        for f in sorted(files):  # Sort for consistent output order
            file_full_path = os.path.join(root, f)
            if not is_ignored(file_full_path, startpath_abs, gitignore_spec):
                file_content = read_file_content(file_full_path)

                tree.create_node(
                    f, file_full_path, parent=current_node_id, data=file_content
                )

                # Store content in map for later output
                relative_path_segment = os.path.relpath(
                    file_full_path, startpath_abs
                ).replace(os.sep, "/")

                # Construct the full display path, like "ROOT_DIR/relative/path/to/file"
                if (
                    relative_path_segment == "."
                ):  # If the file is directly in the startpath (e.g., "my_project/file.txt")
                    display_filepath_key = f"{display_root_name}/{f}"
                else:  # For files in subdirectories (e.g., "my_project/src/file.py")
                    display_filepath_key = (
                        f"{display_root_name}/{relative_path_segment}"
                    )

                file_contents_map[display_filepath_key] = file_content

    return tree, file_contents_map


def prompt(dir):
    tree_obj, file_contents_data = get_directory_tree_and_contents(dir)

    result = "Folder structure\n"
    result += "```\n"
    result += tree_obj.show(stdout=False)
    result += "\n```\n"

    # --- Print Contents of Each File ---
    for relative_filepath, content in sorted(file_contents_data.items()):
        result += f"File: {relative_filepath}\n"
        result += "```\n"
        result += content.strip()
        result += "\n```\n\n"

    return result
