from my_parser.byte_code import Cmds

class VM:
    def __init__(self, bytecode, constants=None):
        self.bytecode = bytecode
        self.constants = constants or []
        self.program_counter = 0
        self.stack = []
        self.variables = {}
        self.running = True
        
    def run(self):
        while self.running and self.program_counter < len(self.bytecode):
            op = self.bytecode[self.program_counter]
            self.program_counter += 1
            
            if op == Cmds.PUSH:
                value = self.bytecode[self.program_counter]
                self.program_counter += 1
                self.stack.append(value)
                
            elif op == Cmds.PUSH_CONST:
                const_idx = self.bytecode[self.program_counter]
                self.program_counter += 1
                self.stack.append(self.constants[const_idx])
                
            elif op == Cmds.STORE:
                var_name = self.bytecode[self.program_counter]
                self.program_counter += 1
                self.variables[var_name] = self.stack.pop()
                
            elif op == Cmds.LOAD:
                var_name = self.bytecode[self.program_counter]
                self.program_counter += 1
                self.stack.append(self.variables.get(var_name, 0))
                
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
                
            elif op == Cmds.PRINT:
                value = self.stack.pop()
                print(value)
                
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
                
            elif op == Cmds.HALT:
                self.running = False