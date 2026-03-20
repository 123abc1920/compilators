# Generated from Lua.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .LuaParser import LuaParser
else:
    from LuaParser import LuaParser

# This class defines a complete listener for a parse tree produced by LuaParser.
class LuaListener(ParseTreeListener):

    # Enter a parse tree produced by LuaParser#prog.
    def enterProg(self, ctx:LuaParser.ProgContext):
        pass

    # Exit a parse tree produced by LuaParser#prog.
    def exitProg(self, ctx:LuaParser.ProgContext):
        pass


    # Enter a parse tree produced by LuaParser#statement.
    def enterStatement(self, ctx:LuaParser.StatementContext):
        pass

    # Exit a parse tree produced by LuaParser#statement.
    def exitStatement(self, ctx:LuaParser.StatementContext):
        pass


    # Enter a parse tree produced by LuaParser#readStmt.
    def enterReadStmt(self, ctx:LuaParser.ReadStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#readStmt.
    def exitReadStmt(self, ctx:LuaParser.ReadStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#printStmt.
    def enterPrintStmt(self, ctx:LuaParser.PrintStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#printStmt.
    def exitPrintStmt(self, ctx:LuaParser.PrintStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#argList.
    def enterArgList(self, ctx:LuaParser.ArgListContext):
        pass

    # Exit a parse tree produced by LuaParser#argList.
    def exitArgList(self, ctx:LuaParser.ArgListContext):
        pass


    # Enter a parse tree produced by LuaParser#callFun.
    def enterCallFun(self, ctx:LuaParser.CallFunContext):
        pass

    # Exit a parse tree produced by LuaParser#callFun.
    def exitCallFun(self, ctx:LuaParser.CallFunContext):
        pass


    # Enter a parse tree produced by LuaParser#args.
    def enterArgs(self, ctx:LuaParser.ArgsContext):
        pass

    # Exit a parse tree produced by LuaParser#args.
    def exitArgs(self, ctx:LuaParser.ArgsContext):
        pass


    # Enter a parse tree produced by LuaParser#returnStmt.
    def enterReturnStmt(self, ctx:LuaParser.ReturnStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#returnStmt.
    def exitReturnStmt(self, ctx:LuaParser.ReturnStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#funStmt.
    def enterFunStmt(self, ctx:LuaParser.FunStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#funStmt.
    def exitFunStmt(self, ctx:LuaParser.FunStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#params.
    def enterParams(self, ctx:LuaParser.ParamsContext):
        pass

    # Exit a parse tree produced by LuaParser#params.
    def exitParams(self, ctx:LuaParser.ParamsContext):
        pass


    # Enter a parse tree produced by LuaParser#block.
    def enterBlock(self, ctx:LuaParser.BlockContext):
        pass

    # Exit a parse tree produced by LuaParser#block.
    def exitBlock(self, ctx:LuaParser.BlockContext):
        pass


    # Enter a parse tree produced by LuaParser#table.
    def enterTable(self, ctx:LuaParser.TableContext):
        pass

    # Exit a parse tree produced by LuaParser#table.
    def exitTable(self, ctx:LuaParser.TableContext):
        pass


    # Enter a parse tree produced by LuaParser#tableEl.
    def enterTableEl(self, ctx:LuaParser.TableElContext):
        pass

    # Exit a parse tree produced by LuaParser#tableEl.
    def exitTableEl(self, ctx:LuaParser.TableElContext):
        pass


    # Enter a parse tree produced by LuaParser#key.
    def enterKey(self, ctx:LuaParser.KeyContext):
        pass

    # Exit a parse tree produced by LuaParser#key.
    def exitKey(self, ctx:LuaParser.KeyContext):
        pass


    # Enter a parse tree produced by LuaParser#value.
    def enterValue(self, ctx:LuaParser.ValueContext):
        pass

    # Exit a parse tree produced by LuaParser#value.
    def exitValue(self, ctx:LuaParser.ValueContext):
        pass


    # Enter a parse tree produced by LuaParser#assign.
    def enterAssign(self, ctx:LuaParser.AssignContext):
        pass

    # Exit a parse tree produced by LuaParser#assign.
    def exitAssign(self, ctx:LuaParser.AssignContext):
        pass


    # Enter a parse tree produced by LuaParser#breakStmt.
    def enterBreakStmt(self, ctx:LuaParser.BreakStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#breakStmt.
    def exitBreakStmt(self, ctx:LuaParser.BreakStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#continueStmt.
    def enterContinueStmt(self, ctx:LuaParser.ContinueStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#continueStmt.
    def exitContinueStmt(self, ctx:LuaParser.ContinueStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#ifStmt.
    def enterIfStmt(self, ctx:LuaParser.IfStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#ifStmt.
    def exitIfStmt(self, ctx:LuaParser.IfStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#forStmt.
    def enterForStmt(self, ctx:LuaParser.ForStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#forStmt.
    def exitForStmt(self, ctx:LuaParser.ForStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#repeatStmt.
    def enterRepeatStmt(self, ctx:LuaParser.RepeatStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#repeatStmt.
    def exitRepeatStmt(self, ctx:LuaParser.RepeatStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#whileStmt.
    def enterWhileStmt(self, ctx:LuaParser.WhileStmtContext):
        pass

    # Exit a parse tree produced by LuaParser#whileStmt.
    def exitWhileStmt(self, ctx:LuaParser.WhileStmtContext):
        pass


    # Enter a parse tree produced by LuaParser#expr.
    def enterExpr(self, ctx:LuaParser.ExprContext):
        pass

    # Exit a parse tree produced by LuaParser#expr.
    def exitExpr(self, ctx:LuaParser.ExprContext):
        pass


    # Enter a parse tree produced by LuaParser#orExpr.
    def enterOrExpr(self, ctx:LuaParser.OrExprContext):
        pass

    # Exit a parse tree produced by LuaParser#orExpr.
    def exitOrExpr(self, ctx:LuaParser.OrExprContext):
        pass


    # Enter a parse tree produced by LuaParser#andExpr.
    def enterAndExpr(self, ctx:LuaParser.AndExprContext):
        pass

    # Exit a parse tree produced by LuaParser#andExpr.
    def exitAndExpr(self, ctx:LuaParser.AndExprContext):
        pass


    # Enter a parse tree produced by LuaParser#notExpr.
    def enterNotExpr(self, ctx:LuaParser.NotExprContext):
        pass

    # Exit a parse tree produced by LuaParser#notExpr.
    def exitNotExpr(self, ctx:LuaParser.NotExprContext):
        pass


    # Enter a parse tree produced by LuaParser#comparison.
    def enterComparison(self, ctx:LuaParser.ComparisonContext):
        pass

    # Exit a parse tree produced by LuaParser#comparison.
    def exitComparison(self, ctx:LuaParser.ComparisonContext):
        pass


    # Enter a parse tree produced by LuaParser#addExpr.
    def enterAddExpr(self, ctx:LuaParser.AddExprContext):
        pass

    # Exit a parse tree produced by LuaParser#addExpr.
    def exitAddExpr(self, ctx:LuaParser.AddExprContext):
        pass


    # Enter a parse tree produced by LuaParser#mulExpr.
    def enterMulExpr(self, ctx:LuaParser.MulExprContext):
        pass

    # Exit a parse tree produced by LuaParser#mulExpr.
    def exitMulExpr(self, ctx:LuaParser.MulExprContext):
        pass


    # Enter a parse tree produced by LuaParser#atom.
    def enterAtom(self, ctx:LuaParser.AtomContext):
        pass

    # Exit a parse tree produced by LuaParser#atom.
    def exitAtom(self, ctx:LuaParser.AtomContext):
        pass



del LuaParser