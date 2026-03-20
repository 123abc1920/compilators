# Generated from Lua.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .LuaParser import LuaParser
else:
    from LuaParser import LuaParser

# This class defines a complete generic visitor for a parse tree produced by LuaParser.

class LuaVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by LuaParser#prog.
    def visitProg(self, ctx:LuaParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#statement.
    def visitStatement(self, ctx:LuaParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#readStmt.
    def visitReadStmt(self, ctx:LuaParser.ReadStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#printStmt.
    def visitPrintStmt(self, ctx:LuaParser.PrintStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#argList.
    def visitArgList(self, ctx:LuaParser.ArgListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#callFun.
    def visitCallFun(self, ctx:LuaParser.CallFunContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#args.
    def visitArgs(self, ctx:LuaParser.ArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#returnStmt.
    def visitReturnStmt(self, ctx:LuaParser.ReturnStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#funStmt.
    def visitFunStmt(self, ctx:LuaParser.FunStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#params.
    def visitParams(self, ctx:LuaParser.ParamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#block.
    def visitBlock(self, ctx:LuaParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#table.
    def visitTable(self, ctx:LuaParser.TableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#tableEl.
    def visitTableEl(self, ctx:LuaParser.TableElContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#key.
    def visitKey(self, ctx:LuaParser.KeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#value.
    def visitValue(self, ctx:LuaParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#assign.
    def visitAssign(self, ctx:LuaParser.AssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#breakStmt.
    def visitBreakStmt(self, ctx:LuaParser.BreakStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#continueStmt.
    def visitContinueStmt(self, ctx:LuaParser.ContinueStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#ifStmt.
    def visitIfStmt(self, ctx:LuaParser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#forStmt.
    def visitForStmt(self, ctx:LuaParser.ForStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#repeatStmt.
    def visitRepeatStmt(self, ctx:LuaParser.RepeatStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#whileStmt.
    def visitWhileStmt(self, ctx:LuaParser.WhileStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#expr.
    def visitExpr(self, ctx:LuaParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#orExpr.
    def visitOrExpr(self, ctx:LuaParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#andExpr.
    def visitAndExpr(self, ctx:LuaParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#notExpr.
    def visitNotExpr(self, ctx:LuaParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#comparison.
    def visitComparison(self, ctx:LuaParser.ComparisonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#addExpr.
    def visitAddExpr(self, ctx:LuaParser.AddExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#mulExpr.
    def visitMulExpr(self, ctx:LuaParser.MulExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LuaParser#atom.
    def visitAtom(self, ctx:LuaParser.AtomContext):
        return self.visitChildren(ctx)



del LuaParser