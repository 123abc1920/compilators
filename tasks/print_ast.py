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
        func_name = node[1]
        params = []
        if len(node) > 2 and node[2] and node[2][0] == "params":
            params = node[2][1]
        print(
            f"{current_prefix}function {func_name}({', '.join(str(p) for p in params)})"
        )
        if len(node) > 3 and node[3]:
            print_ast_from_tuples(node[3], level + 1, True, child_prefix)

    elif node_type == "params":
        params_str = ", ".join(str(p) for p in node[1]) if node[1] else ""
        print(f"{current_prefix}({params_str})")

    elif node_type == "block":
        print(f"{current_prefix}block")
        for i, stmt in enumerate(node[1]):
            print_ast_from_tuples(stmt, level + 1, i == len(node[1]) - 1, child_prefix)

    elif node_type == "return":
        print(f"{current_prefix}return")
        if node[1]:
            print_ast_from_tuples(node[1], level + 1, True, child_prefix)

    elif node_type == "assign":
        print(f"{current_prefix}assign {node[1]}")
        print_ast_from_tuples(node[2], level + 1, True, child_prefix)

    elif node_type == "call":
        print(f"{current_prefix}call {node[1]}")
        if len(node) > 2 and node[2]:
            for i, arg in enumerate(node[2]):
                print_ast_from_tuples(
                    arg, level + 1, i == len(node[2]) - 1, child_prefix
                )

    elif node_type == "binop":
        op = node[1]
        if op == "and":
            print(f"{current_prefix}and")
        elif op == "or":
            print(f"{current_prefix}or")
        elif op == "not":
            print(f"{current_prefix}not")
            print_ast_from_tuples(node[2], level + 1, True, child_prefix)
            return
        else:
            print(f"{current_prefix}{op}")
        print_ast_from_tuples(node[2], level + 1, False, child_prefix)
        if len(node) > 3:
            print_ast_from_tuples(node[3], level + 1, True, child_prefix)

    elif node_type == "var":
        print(f"{current_prefix}{node[1]}")

    elif node_type == "number":
        print(f"{current_prefix}{node[1]}")

    elif node_type == "string":
        print(f'{current_prefix}"{node[1]}"')

    elif node_type == "boolean":
        print(f"{current_prefix}{'true' if node[1] else 'false'}")

    elif node_type == "nil":
        print(f"{current_prefix}nil")

    elif node_type == "for":
        print(f"{current_prefix}for {node[1]} =", end=" ")
        if isinstance(node[2], tuple):
            if node[2][0] == "number":
                print(node[2][1], end=" ")
            elif node[2][0] == "var":
                print(node[2][1], end=" ")
            else:
                print("?", end=" ")
        else:
            print(node[2], end=" ")
        print("to", end=" ")
        if isinstance(node[3], tuple):
            if node[3][0] == "number":
                print(node[3][1])
            elif node[3][0] == "var":
                print(node[3][1])
            else:
                print("?")
        else:
            print(node[3])
        print_ast_from_tuples(node[4], level + 1, True, child_prefix)

    elif node_type == "while":
        print(f"{current_prefix}while", end=" ")
        condition = node[1]

        if isinstance(condition, tuple):
            cond_type = condition[0]

            if cond_type == "binop":
                op = condition[1]
                if op in ["and", "or"]:
                    print(f"{op}", end=" ")
                    if isinstance(condition[2], tuple):
                        if condition[2][0] == "binop":
                            nested_op = condition[2][1]
                            print(f"{nested_op}", end=" ")
                            if isinstance(condition[2][2], tuple):
                                if condition[2][2][0] == "var":
                                    print(condition[2][2][1], end=" ")
                                elif condition[2][2][0] == "number":
                                    print(condition[2][2][1], end=" ")
                            if isinstance(condition[2][3], tuple):
                                if condition[2][3][0] == "var":
                                    print(condition[2][3][1], end=" ")
                                elif condition[2][3][0] == "number":
                                    print(condition[2][3][1], end=" ")
                        elif condition[2][0] == "var":
                            print(condition[2][1], end=" ")
                        elif condition[2][0] == "number":
                            print(condition[2][1], end=" ")
                        elif condition[2][0] == "boolean":
                            print("true" if condition[2][1] else "false", end=" ")
                        else:
                            print("?", end=" ")
                    else:
                        print(condition[2], end=" ")
                    if len(condition) > 3 and condition[3]:
                        if isinstance(condition[3], tuple):
                            if condition[3][0] == "boolean":
                                print("true" if condition[3][1] else "false")
                            elif condition[3][0] == "var":
                                print(condition[3][1])
                            elif condition[3][0] == "number":
                                print(condition[3][1])
                            else:
                                print("?")
                        else:
                            print(condition[3])
                    else:
                        print()
                else:
                    print(f"{op}", end=" ")
                    if isinstance(condition[2], tuple):
                        if condition[2][0] == "var":
                            print(condition[2][1], end=" ")
                        elif condition[2][0] == "number":
                            print(condition[2][1], end=" ")
                        elif condition[2][0] == "boolean":
                            print("true" if condition[2][1] else "false", end=" ")
                        else:
                            print("?", end=" ")
                    else:
                        print(condition[2], end=" ")
                    if len(condition) > 3 and condition[3]:
                        if isinstance(condition[3], tuple):
                            if condition[3][0] == "var":
                                print(condition[3][1])
                            elif condition[3][0] == "number":
                                print(condition[3][1])
                            elif condition[3][0] == "boolean":
                                print("true" if condition[3][1] else "false")
                            else:
                                print("?")
                        else:
                            print(condition[3])
                    else:
                        print()

            elif cond_type == "boolean":
                print("true" if condition[1] else "false")
            elif cond_type == "var":
                print(condition[1])
            elif cond_type == "number":
                print(condition[1])
            else:
                print("?")
        else:
            print("?")

        if len(node) > 2 and node[2]:
            print_ast_from_tuples(node[2], level + 1, True, child_prefix)

    elif node_type == "repeat":
        print(f"{current_prefix}repeat")
        if len(node) > 1 and node[1]:
            print_ast_from_tuples(node[1], level + 1, False, child_prefix)
        print(f"{child_prefix}until", end=" ")

        if len(node) > 2:
            condition = node[2]
            if isinstance(condition, tuple):
                cond_type = condition[0]

                if cond_type == "binop":
                    print(f"{condition[1]}", end=" ")
                    if isinstance(condition[2], tuple):
                        if condition[2][0] == "var":
                            print(condition[2][1], end=" ")
                        elif condition[2][0] == "number":
                            print(condition[2][1], end=" ")
                        elif condition[2][0] == "boolean":
                            print("true" if condition[2][1] else "false", end=" ")
                        else:
                            print("?", end=" ")
                    else:
                        print(condition[2], end=" ")
                    if len(condition) > 3 and condition[3]:
                        if isinstance(condition[3], tuple):
                            if condition[3][0] == "var":
                                print(condition[3][1])
                            elif condition[3][0] == "number":
                                print(condition[3][1])
                            elif condition[3][0] == "boolean":
                                print("true" if condition[3][1] else "false")
                            else:
                                print("?")
                        else:
                            print(condition[3])
                    else:
                        print()
                elif cond_type == "boolean":
                    print("true" if condition[1] else "false")
                elif cond_type == "var":
                    print(condition[1])
                elif cond_type == "number":
                    print(condition[1])
                else:
                    print("?")
            else:
                print("?")
        else:
            print("?")

    elif node_type == "break":
        print(f"{current_prefix}break")

    elif node_type == "continue":
        print(f"{current_prefix}continue")

    elif node_type == "if":
        print(f"{current_prefix}if")

        conditions_blocks = node[1]
        else_block = node[2] if len(node) > 2 else None

        for i, (cond, block) in enumerate(conditions_blocks):
            is_last_cond = i == len(conditions_blocks) - 1 and else_block is None

            if i == 0:
                cond_prefix = child_prefix + ("└─ " if is_last_cond else "├─ ")
                print(f"{cond_prefix}then", end=" ")
            else:
                cond_prefix = child_prefix + ("└─ " if is_last_cond else "├─ ")
                print(f"{cond_prefix}elseif", end=" ")

            if isinstance(cond, tuple):
                cond_type = cond[0]
                if cond_type == "binop":
                    print(f"{cond[1]}", end=" ")
                    if isinstance(cond[2], tuple):
                        if cond[2][0] == "var":
                            print(cond[2][1], end=" ")
                        elif cond[2][0] == "number":
                            print(cond[2][1], end=" ")
                        elif cond[2][0] == "boolean":
                            print("true" if cond[2][1] else "false", end=" ")
                        else:
                            print("?", end=" ")
                    else:
                        print(cond[2], end=" ")
                    if len(cond) > 3 and cond[3]:
                        if isinstance(cond[3], tuple):
                            if cond[3][0] == "var":
                                print(cond[3][1])
                            elif cond[3][0] == "number":
                                print(cond[3][1])
                            elif cond[3][0] == "boolean":
                                print("true" if cond[3][1] else "false")
                            else:
                                print("?")
                        else:
                            print(cond[3])
                    else:
                        print()
                elif cond_type == "boolean":
                    print("true" if cond[1] else "false")
                elif cond_type == "var":
                    print(cond[1])
                elif cond_type == "number":
                    print(cond[1])
                else:
                    print("?")
            else:
                print("?")

            block_child_prefix = child_prefix + ("   " if is_last_cond else "│  ")
            if block:
                print_ast_from_tuples(
                    block, level + 2, is_last_cond, block_child_prefix
                )

        if else_block:
            print(f"{child_prefix}└─ else")
            print_ast_from_tuples(else_block, level + 2, True, child_prefix + "   ")

    elif node_type == "table":
        print(f"{current_prefix}table")
        if len(node) > 1 and node[1]:
            for i, elem in enumerate(node[1]):
                print_ast_from_tuples(
                    elem, level + 1, i == len(node[1]) - 1, child_prefix
                )

    elif node_type == "index":
        table_name = node[1]
        print(f"{current_prefix}{table_name}[", end="")
        if len(node) > 2 and node[2]:
            index = node[2]
            if isinstance(index, tuple):
                if index[0] == "var":
                    print(f"{index[1]}]")
                elif index[0] == "number":
                    print(f"{index[1]}]")
                elif index[0] == "string":
                    print(f'"{index[1]}"]')
                else:
                    print("?]")
            else:
                print(f"{index}]")
        else:
            print("?]")

    elif node_type == "cast":
        print(f"{current_prefix}cast to {node[1]}")
        if len(node) > 2 and node[2]:
            print_ast_from_tuples(node[2], level + 1, True, child_prefix)

    elif node_type == "unary":
        print(f"{current_prefix}{node[1]}")
        if len(node) > 2 and node[2]:
            print_ast_from_tuples(node[2], level + 1, True, child_prefix)

    elif node_type == "args":
        print(f"{current_prefix}args")
        if len(node) > 1 and node[1]:
            for i, arg in enumerate(node[1]):
                print_ast_from_tuples(
                    arg, level + 1, i == len(node[1]) - 1, child_prefix
                )

    elif node_type == "field":
        print(f"{current_prefix}{node[1]}.{node[2]}")

    else:
        print(f"{current_prefix}[DEBUG unknown type: {node_type}]")
        print(f"{current_prefix}{node}")
