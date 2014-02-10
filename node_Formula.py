import bpy
from node_s import *
from util import *
from mathutils import Vector, Matrix
import parser
from math import sin, cos, tan, pi

class FormulaNode(Node, SverchCustomTreeNode):
    ''' Formula '''
    bl_idname = 'FormulaNode'
    bl_label = 'Formula'
    bl_icon = 'OUTLINER_OB_EMPTY'
    
    formula = bpy.props.StringProperty(name = 'formula', default='x*n[0]', update=updateNode)

    def draw_buttons(self, context, layout):
        layout.prop(self, "formula", text="formula")
        
    def init(self, context):
        self.inputs.new('StringsSocket', "X", "X")
        self.inputs.new('StringsSocket', "n[.]", "n[.]")
        self.outputs.new('StringsSocket', "Result", "Result")
   
    def check_slots(self, num):
        l = []
        if len(self.inputs)<num+1:
            return False
        for i, sl in enumerate(self.inputs[num:]):   
            if len(sl.links)==0:
                 l.append(i+num)
        if l:
            return l
        else:
            return False

    def update(self):
        # inputs
        ch = self.check_slots(1)
        if ch:
            for c in ch[:-1]:
                self.inputs.remove(self.inputs[ch[0]])
        
        if 'X' in self.inputs and self.inputs['X'].is_linked: 
            vecs = SvGetSocketAnyType(self,self.inputs['X'])
        else:
            vecs = [[0.0]]
        
        list_mult=[]
        for idx, multi in enumerate(self.inputs[1:]):   
            if multi.is_linked and \
                type(multi.links[0].from_socket) == StringsSocket:
                
                mult = SvGetSocketAnyType(self,multi)
                ch = self.check_slots(2)
                if not ch:
                    self.inputs.new('StringsSocket', 'n[.]', "n[.]")

                list_mult.extend(mult)
        if len(list_mult)==0:
            list_mult= [[0.0]]
        
        # outputs
        if 'Result' in self.outputs and self.outputs['Result'].is_linked:

           code_formula = parser.expr(self.formula).compile()
           r_=[]
           result=[]
           max_l = 0
           for list_m in list_mult:
               l1 = len(list_m)
               max_l=max(max_l,l1)
           max_l = max(max_l,len(vecs[0]))
           
           for list_m in list_mult:
               d = max_l - len(list_m)
               if d>0:
                   for d_ in range(d):
                       list_m.append(list_m[-1])

           lres = []
           for l in range(max_l):
               ltmp=[]
               for list_m in list_mult:
                   ltmp.append(list_m[l])
               lres.append(ltmp)
               
           r = self.inte(vecs,code_formula,lres)  
           
           result.extend(r)           
           SvSetSocketAnyType(self,'Result',result)
    
    def inte(self, l, formula, list_n, indx=0):
        if type(l) in [int, float]:
            x=X=l
            
            n=list_n[indx]
            N=n

            t = eval(formula)
        else:
            t = []
            for idx,i in enumerate(l):
                j = self.inte(i, formula, list_n, idx)
                t.append(j)
            if type(l)==tuple:
                t = tuple(t)
        return t
        

def register():
    bpy.utils.register_class(FormulaNode)
    
def unregister():
    bpy.utils.unregister_class(FormulaNode)

if __name__ == "__main__":
    register()