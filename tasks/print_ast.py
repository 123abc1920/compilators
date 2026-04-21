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

    elif node_type == "for":
        print(f"{current_prefix}for {node[1]} =", end=" ")
        temp_prefix = prefix + ("   " if is_last else "│  ")
        if isinstance(node[2], tuple):
            print(f"{node[2][1]}", end=" ")
        else:
            print(f"{node[2]}", end=" ")
        print("to", end=" ")
        if isinstance(node[3], tuple):
            print(f"{node[3][1]}")
        else:
            print(f"{node[3]}")
        print_ast_from_tuples(node[4], level + 1, True, child_prefix)

    elif node_type == "while":
        print(f"{current_prefix}while", end=" ")
        if isinstance(node[1], tuple) and node[1][0] == "binop":
            print(f"{node[1][1]}", end=" ")
            if isinstance(node[1][2], tuple):
                print(node[1][2][1], end=" ")
            else:
                print(node[1][2], end=" ")
            if isinstance(node[1][3], tuple):
                print(node[1][3][1])
            else:
                print(node[1][3])
        else:
            print("?")
        print_ast_from_tuples(node[2], level + 1, True, child_prefix)

    elif node_type == "repeat":
        print(f"{current_prefix}repeat")
        print_ast_from_tuples(node[1], level + 1, False, child_prefix)
        print(f"{child_prefix}until", end=" ")
        if isinstance(node[2], tuple) and node[2][0] == "binop":
            print(f"{node[2][1]}", end=" ")
            if isinstance(node[2][2], tuple):
                print(node[2][2][1], end=" ")
            else:
                print(node[2][2], end=" ")
            if isinstance(node[2][3], tuple):
                print(node[2][3][1])
            else:
                print(node[2][3])
        else:
            print("?")

    elif node_type == "break":
        print(f"{current_prefix}break")

    elif node_type == "continue":
        print(f"{current_prefix}continue")

    elif node_type == "if":
        print(f"{current_prefix}if")
        for i, (cond, block) in enumerate(node[1]):
            is_last_cond = i == len(node[1]) - 1 and node[2] is None
            cond_prefix = child_prefix + ("└─ " if is_last_cond else "├─ ")
            cond_child_prefix = child_prefix + ("   " if is_last_cond else "│  ")

            if i == 0:
                print(f"{cond_prefix}then", end=" ")
            else:
                print(f"{cond_prefix}elseif", end=" ")

            if isinstance(cond, tuple) and cond[0] == "binop":
                print(f"{cond[1]}", end=" ")
                if isinstance(cond[2], tuple):
                    print(cond[2][1], end=" ")
                else:
                    print(cond[2], end=" ")
                if isinstance(cond[3], tuple):
                    print(cond[3][1])
                else:
                    print(cond[3])
            else:
                print("?")

            print_ast_from_tuples(block, level + 2, is_last_cond, cond_child_prefix)

        if node[2] is not None:
            print(f"{child_prefix}└─ else")
            print_ast_from_tuples(node[2], level + 2, True, child_prefix + "   ")

    elif node_type == "table":
        print(f"{current_prefix}table")
        for i, elem in enumerate(node[1]):
            print_ast_from_tuples(elem, level + 1, i == len(node[1]) - 1, child_prefix)

    elif node_type == "field":
        print(f"{current_prefix}{node[1]}.{node[2]}")

    elif node_type == "unary":
        print(f"{current_prefix}{node[1]}")
        print_ast_from_tuples(node[2], level + 1, True, child_prefix)

    elif node_type == "args":
        print(f"{current_prefix}args")
        for i, arg in enumerate(node[1]):
            print_ast_from_tuples(arg, level + 1, i == len(node[1]) - 1, child_prefix)

    elif node_type == "if":
        print(f"{current_prefix}if")

        for i, (cond, block) in enumerate(node[1]):
            is_last_cond = i == len(node[1]) - 1 and node[2] is None

            if i == 0:
                cond_prefix = child_prefix + ("└─ " if is_last_cond else "├─ ")
                print(f"{cond_prefix}then", end=" ")
            else:
                cond_prefix = child_prefix + ("└─ " if is_last_cond else "├─ ")
                print(f"{cond_prefix}elseif", end=" ")

            if isinstance(cond, tuple):
                if cond[0] == "binop":
                    print(f"{cond[1]}", end=" ")

                    if isinstance(cond[2], tuple) and cond[2][0] in [
                        "var",
                        "number",
                        "string",
                        "boolean",
                    ]:
                        print(cond[2][1], end=" ")
                    else:
                        print("?", end=" ")

                    if isinstance(cond[3], tuple) and cond[3][0] in [
                        "var",
                        "number",
                        "string",
                        "boolean",
                    ]:
                        print(cond[3][1])
                    else:
                        print("?")
                elif cond[0] == "var":
                    print(cond[1])
                elif cond[0] == "number":
                    print(cond[1])
                elif cond[0] == "boolean":
                    print(cond[1])
                else:
                    print("?")
            else:
                print("?")

            block_child_prefix = child_prefix + ("   " if is_last_cond else "│  ")
            print_ast_from_tuples(block, level + 2, is_last_cond, block_child_prefix)

        if node[2] is not None:
            print(f"{child_prefix}└─ else")
            print_ast_from_tuples(node[2], level + 2, True, child_prefix + "   ")

    elif node_type == "break":
        print(f"{current_prefix}break")

    elif node_type == "continue":
        print(f"{current_prefix}continue")

    elif node_type == "index":
        print(f"{current_prefix}{node[1]}[", end="")
        index = node[2]
        if isinstance(index, tuple):
            if index[0] == "var":
                print(f"{index[1]}]")
            elif index[0] == "number":
                print(f"{index[1]}]")
            else:
                print("?]")
        else:
            print(f"{index}]")

    elif node_type == "cast":
        print(f"{current_prefix}cast to {node[1]}")
        print_ast_from_tuples(node[2], level + 1, True, child_prefix)

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
