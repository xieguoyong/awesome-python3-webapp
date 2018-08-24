from collections import namedtuple

Result = namedtuple('Result', 'count average')

# 子生成器
def averager():
    total = 0.0
    count = 0
    average = None
    while True:
        # main 函数发送数据到这里 
        print("in averager, before yield")
        term = yield
        if term is None: # 终止条件
            break
        total += term
        count += 1
        average = total/count

    print("in averager, return result")
    return Result(count, average) # 返回的Result 会成为grouper函数中yield from表达式的值


# 委派生成器
def grouper(results, key):
     # 这个循环每次都会新建一个averager 实例，每个实例都是作为协程使用的生成器对象
    while True:
        print("in grouper, before yield from averager, key is ", key)
        results[key] = yield from averager()
        print("in grouper, after yield from, key is ", key)


# 调用方
def main(data):
    results = {}
    for key, values in data.items():
        # group 是调用grouper函数得到的生成器对象
        group = grouper(results, key)
        print("\ncreate group: ", group)
        next(group) #预激 group 协程。
        print("pre active group ok")
        for value in values:
            # 把各个value传给grouper 传入的值最终到达averager函数中；
            # grouper并不知道传入的是什么，同时grouper实例在yield from处暂停
            print("send to %r value %f now"%(group, value))
            group.send(value)
        # 把None传入groupper，传入的值最终到达averager函数中，导致当前实例终止。然后继续创建下一个实例。
        # 如果没有group.send(None)，那么averager子生成器永远不会终止，委派生成器也永远不会在此激活，也就不会为result[key]赋值
        print("send to %r none"%group)
        group.send(None)
    print(results)
    print("report result: ")
    report(results)


# 输出报告
def report(results):
    for key, result in sorted(results.items()):
        group, unit = key.split(';')
        print('{:2} {:5} averaging {:.2f}{}'.format(result.count, group, result.average, unit))


data = {
    'girls;kg':[40, 41, 42, 43, 44, 54],
    'girls;m': [1.5, 1.6, 1.8, 1.5, 1.45, 1.6],
    'boys;kg':[50, 51, 62, 53, 54, 54],
    'boys;m': [1.6, 1.8, 1.8, 1.7, 1.55, 1.6],
}

if __name__ == '__main__':
    main(data) 