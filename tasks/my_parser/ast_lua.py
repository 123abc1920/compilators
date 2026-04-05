def ast_to_tuple(node):
    if node is None:
        return None

    node_name = node.__class__.__name__.replace("Node", "")

    if node_name == "Prog":
        statements = [ast_to_tuple(stmt) for stmt in node.statements]
        return ("prog", statements)

    elif node_name == "Assign":
        value = ast_to_tuple(node.value)
        return ("assign", node.name, value)

    elif node_name == "AddExpr":
        left = ast_to_tuple(node.left)
        right = ast_to_tuple(node.right)
        return ("binop", node.op, left, right)

    elif node_name == "MulExpr":
        left = ast_to_tuple(node.left)
        right = ast_to_tuple(node.right)
        return ("binop", node.op, left, right)

    elif node_name == "Comparison":
        left = ast_to_tuple(node.left)
        right = ast_to_tuple(node.right)
        return ("binop", node.op, left, right)

    elif node_name == "OrExpr":
        left = ast_to_tuple(node.left)
        right = ast_to_tuple(node.right)
        return ("binop", "or", left, right)

    elif node_name == "AndExpr":
        left = ast_to_tuple(node.left)
        right = ast_to_tuple(node.right)
        return ("binop", "and", left, right)

    elif node_name == "NotExpr":
        expr = ast_to_tuple(node.expr)
        return ("binop", "not", expr, None)

    elif node_name == "Atom":
        if node.type == "number":
            return ("number", node.value)
        elif node.type == "string":
            return ("string", node.value)
        elif node.type == "literal":
            if node.value == "true":
                return ("boolean", True)
            elif node.value == "false":
                return ("boolean", False)
            else:
                return ("nil", None)
        elif node.type == "name":
            return ("var", node.value)

    elif node_name == "FunStmt":
        params = ast_to_tuple(node.params) if node.params else ("params", [])
        block = ast_to_tuple(node.block)
        return ("function", node.name, params, block)

    elif node_name == "Params":
        return ("params", node.params)

    elif node_name == "Block":
        statements = [ast_to_tuple(stmt) for stmt in node.statements]
        return ("block", statements)

    elif node_name == "ReturnStmt":
        expr = ast_to_tuple(node.expr)
        return ("return", expr)

    elif node_name == "PrintStmt":
        args = []
        if node.args:
            for arg in node.args.args:
                args.append(ast_to_tuple(arg))
        return ("call", "print", args)

    elif node_name == "CallFun":
        args = []
        if node.args:
            for arg in node.args.args:
                args.append(ast_to_tuple(arg))
        return ("call", node.name, args)

    elif node_name == "Table":
        elements = [ast_to_tuple(el) for el in node.elements]
        return ("table", elements)

    elif node_name == "TableElement":
        return ast_to_tuple(node.value)

    return ("unknown", str(node))
