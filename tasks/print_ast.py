def print_ast_from_tuples(node, level=0, is_last=True, prefix=""):
    if level == 0:
        current_prefix = ""
    else:
        current_prefix = prefix + ("└─ " if is_last else "├─ ")

    child_prefix = prefix + ("   " if is_last else "│  ")

    if not isinstance(node, tuple):
        print(f"{current_prefix}{node}")
        return

    node_type = node[0]

    if node_type == "prog":
        print(f"{current_prefix}prog")
        for i, stmt in enumerate(node[1]):
            print_ast_from_tuples(stmt, level + 1, i == len(node[1]) - 1, child_prefix)

    elif node_type == "function":
        print(f"{current_prefix}function {node[1]} {node[2]}")
        print_ast_from_tuples(node[3], level + 1, True, child_prefix)

    elif node_type == "params":
        print(f"{current_prefix}params {node[1]}")

    elif node_type == "block":
        print(f"{current_prefix}block")
        for i, stmt in enumerate(node[1]):
            print_ast_from_tuples(stmt, level + 1, i == len(node[1]) - 1, child_prefix)

    elif node_type == "return":
        print(f"{current_prefix}return")
        print_ast_from_tuples(node[1], level + 1, True, child_prefix)

    elif node_type == "assign":
        print(f"{current_prefix}assign {node[1]}")
        print_ast_from_tuples(node[2], level + 1, True, child_prefix)

    elif node_type == "call":
        print(f"{current_prefix}call {node[1]}")
        for i, arg in enumerate(node[2]):
            print_ast_from_tuples(arg, level + 1, i == len(node[2]) - 1, child_prefix)

    elif node_type == "binop":
        print(f"{current_prefix}{node[1]}")
        print_ast_from_tuples(node[2], level + 1, False, child_prefix)
        print_ast_from_tuples(node[3], level + 1, True, child_prefix)

    elif node_type == "var":
        print(f"{current_prefix}{node[1]}")

    elif node_type == "number":
        print(f"{current_prefix}{node[1]}")

    elif node_type == "string":
        print(f'{current_prefix}"{node[1]}"')

    elif node_type == "boolean":
        print(f"{current_prefix}{node[1]}")

    elif node_type == "nil":
        print(f"{current_prefix}nil")

    else:
        if isinstance(node, tuple):
            if len(node) == 2:
                print(f"{current_prefix}{node[0]}")
                if isinstance(node[1], list):
                    for i, item in enumerate(node[1]):
                        print_ast_from_tuples(
                            item, level + 1, i == len(node[1]) - 1, child_prefix
                        )
                else:
                    print_ast_from_tuples(node[1], level + 1, True, child_prefix)
            else:
                print(f"{current_prefix}unknown: {node}")
        else:
            print(f"{current_prefix}unknown: {node}")
