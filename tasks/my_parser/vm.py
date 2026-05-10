from my_parser.byte_code import Cmds, BytecodeCreator

class VM:
    def __init__(self, bytecode, constants=None, functions=None):
        self.bytecode = bytecode
        self.constants = constants or []
        self.functions = functions or {}
        self.pc = 0
        self.stack = []
        self.call_stack = [{}]
        self.running = True

    def run(self):
        while self.running and self.pc < len(self.bytecode):
            op = self.bytecode[self.pc]
            self.pc += 1

            if op == Cmds.PUSH:
                self.stack.append(self.bytecode[self.pc])
                self.pc += 1

            elif op == Cmds.PUSH_CONST:
                idx = self.bytecode[self.pc]
                self.pc += 1
                self.stack.append(self.constants[idx])

            elif op == Cmds.LOAD:
                name = self.bytecode[self.pc]
                self.pc += 1
                self.stack.append(self.call_stack[-1].get(name, 0))

            elif op == Cmds.STORE:
                name = self.bytecode[self.pc]
                self.pc += 1
                if self.stack:
                    self.call_stack[-1][name] = self.stack.pop()

            elif op == Cmds.ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    self.stack.append(a + b)
                else:
                    self.stack.append(str(a) + str(b))

            elif op == Cmds.SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)

            elif op == Cmds.MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)

            elif op == Cmds.DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a / b)

            elif op == Cmds.MOD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a % b)

            elif op == Cmds.UNARY_MINUS:
                a = self.stack.pop()
                self.stack.append(-a)

            elif op == Cmds.OR:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a or b)

            elif op == Cmds.AND:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a and b)

            elif op == Cmds.NOT:
                a = self.stack.pop()
                self.stack.append(not a)

            elif op == Cmds.LT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a < b)

            elif op == Cmds.GT:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a > b)

            elif op == Cmds.LTE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a <= b)

            elif op == Cmds.GTE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a >= b)

            elif op == Cmds.EQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a == b)

            elif op == Cmds.NEQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a != b)

            elif op == Cmds.JMP:
                target = self.bytecode[self.pc]
                self.pc = target

            elif op == Cmds.JMP_IF:
                cond = self.stack.pop()
                target = self.bytecode[self.pc]
                if cond:
                    self.pc = target
                else:
                    self.pc += 1

            elif op == Cmds.JMP_IF_NOT:
                cond = self.stack.pop()
                target = self.bytecode[self.pc]
                if not cond:
                    self.pc = target
                else:
                    self.pc += 1

            elif op == Cmds.CALL:
                name = self.bytecode[self.pc]
                self.pc += 1
                num_args = self.bytecode[self.pc]
                self.pc += 1

                func = self.functions.get(name)
                if not func:
                    raise RuntimeError(f"Функция '{name}' не определена")

                args = []
                for _ in range(num_args):
                    args.append(self.stack.pop())
                args.reverse()

                new_frame = {}
                for i, param in enumerate(func["params"]):
                    if i < len(args):
                        new_frame[param] = args[i]

                self.call_stack.append(new_frame)

                saved_pc = self.pc
                saved_bytecode = self.bytecode
                saved_constants = self.constants

                bc_creator = BytecodeCreator()
                func_bytecode, func_constants, _ = bc_creator.compile(func["block"])

                self.bytecode = func_bytecode
                self.constants = func_constants
                self.pc = 0
                ret_val = None

                while self.pc < len(self.bytecode):
                    sub_op = self.bytecode[self.pc]
                    self.pc += 1

                    if sub_op == Cmds.RET:
                        ret_val = self.stack.pop() if self.stack else None
                        break
                    elif sub_op == Cmds.PUSH:
                        self.stack.append(self.bytecode[self.pc])
                        self.pc += 1
                    elif sub_op == Cmds.PUSH_CONST:
                        idx = self.bytecode[self.pc]
                        self.pc += 1
                        self.stack.append(self.constants[idx])
                    elif sub_op == Cmds.LOAD:
                        name = self.bytecode[self.pc]
                        self.pc += 1
                        self.stack.append(self.call_stack[-1].get(name, 0))
                    elif sub_op == Cmds.STORE:
                        name = self.bytecode[self.pc]
                        self.pc += 1
                        if self.stack:
                            self.call_stack[-1][name] = self.stack.pop()
                    elif sub_op == Cmds.ADD:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                            self.stack.append(a + b)
                        else:
                            self.stack.append(str(a) + str(b))
                    elif sub_op == Cmds.SUB:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a - b)
                    elif sub_op == Cmds.MUL:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a * b)
                    elif sub_op == Cmds.DIV:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a / b)
                    elif sub_op == Cmds.MOD:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a % b)
                    elif sub_op == Cmds.UNARY_MINUS:
                        a = self.stack.pop()
                        self.stack.append(-a)
                    elif sub_op == Cmds.OR:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a or b)
                    elif sub_op == Cmds.AND:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a and b)
                    elif sub_op == Cmds.NOT:
                        a = self.stack.pop()
                        self.stack.append(not a)
                    elif sub_op == Cmds.LT:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a < b)
                    elif sub_op == Cmds.GT:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a > b)
                    elif sub_op == Cmds.LTE:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a <= b)
                    elif sub_op == Cmds.GTE:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a >= b)
                    elif sub_op == Cmds.EQ:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a == b)
                    elif sub_op == Cmds.NEQ:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        self.stack.append(a != b)
                    elif sub_op == Cmds.JMP:
                        target = self.bytecode[self.pc]
                        self.pc = target
                    elif sub_op == Cmds.JMP_IF:
                        cond = self.stack.pop()
                        target = self.bytecode[self.pc]
                        if cond:
                            self.pc = target
                        else:
                            self.pc += 1
                    elif sub_op == Cmds.JMP_IF_NOT:
                        cond = self.stack.pop()
                        target = self.bytecode[self.pc]
                        if not cond:
                            self.pc = target
                        else:
                            self.pc += 1
                    elif sub_op == Cmds.PRINT:
                        cnt = self.bytecode[self.pc]
                        self.pc += 1
                        values = []
                        for _ in range(cnt):
                            if self.stack:
                                values.append(self.stack.pop())
                        values.reverse()
                        print(" ".join(str(v) for v in values))
                    elif sub_op == Cmds.READ:
                        val = input()
                        try:
                            val = int(val)
                        except:
                            try:
                                val = float(val)
                            except:
                                pass
                        self.stack.append(val)
                    elif sub_op == Cmds.MAKE_TABLE:
                        size = self.bytecode[self.pc]
                        self.pc += 1
                        table = []
                        for _ in range(size):
                            if self.stack:
                                table.append(self.stack.pop())
                        table.reverse()
                        self.stack.append(table)
                    elif sub_op == Cmds.HALT:
                        break

                self.call_stack.pop()
                self.bytecode = saved_bytecode
                self.constants = saved_constants
                self.pc = saved_pc
                self.stack.append(ret_val)

            elif op == Cmds.PRINT:
                cnt = self.bytecode[self.pc]
                self.pc += 1
                values = []
                for _ in range(cnt):
                    if self.stack:
                        values.append(self.stack.pop())
                values.reverse()
                print(" ".join(str(v) for v in values))

            elif op == Cmds.READ:
                val = input()
                try:
                    val = int(val)
                except:
                    try:
                        val = float(val)
                    except:
                        pass
                self.stack.append(val)

            elif op == Cmds.MAKE_TABLE:
                size = self.bytecode[self.pc]
                self.pc += 1
                table = []
                for _ in range(size):
                    if self.stack:
                        table.append(self.stack.pop())
                table.reverse()
                self.stack.append(table)

            elif op == Cmds.HALT:
                self.running = False