# #理解
# #就是电源适配器的原理吧，将本来不兼容的接口类能够工作
# #这个是类实现方式
# #例子
# #假如一个插座类输出脚是3脚的，而台灯需要的是两脚插座，现在就需要一个Adapter实现适配插座
# #Adaptee
# class socket(object):
#     def Trigle(self):
#         print( 'power supply')
#     #target
# class tableLamp(object):
#     def needTwo(self):
#         pass
#     #adapter
# class Adapter(tableLamp,socket):
#     def needTwo(self):
#         self.Trigle()
#     #client
# if __name__=='__main__':
#     lamp=Adapter()
#     lamp.needTwo()
import transformers
print(transformers.__version__)