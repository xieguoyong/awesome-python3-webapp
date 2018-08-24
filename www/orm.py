# -*- coding:utf-8 -*-
"""
时间：2018年7月9号
day3:ORM 对象关系映射：通俗说就是将一个数据库表映射为一个类
"""
import asyncio, logging
import aiomysql


def log(sql, args=()):
    """
    定义一个log方法，用于打印执行的SQL
    """
    logging.info('SQL: %s', sql)


async def create_pool(loop, **kw):
    """
    创建数据库连接池，每个HTTP请求都可以从连接池中直接获取数据库连接;
    使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。
    """
    logging.info('create database connection pool...')
    # 设置全局私有变量，仅内部可访问
    global __pool
    # await 调用协程函数并返回结果
    __pool = await aiomysql.create_pool(
        # 获取kw中的host的值，如果没有则填充为localhost，其他key同理
        host = kw.get('host', 'localhost'),
        port = kw.get('port', 3306),
        password = kw['password'],
        user = kw['user'],
        db = kw['db'],
        charset = kw.get('charset', 'utf8'),
        autocommit = kw.get('autocommit', True),
        maxsize = kw.get('maxsize', 10),
        minsize= kw.get('minsize', 1),
        loop = loop    # 这个不理解有什么用？
    )

async def select(sql, args, size=None):
    """
    协程：select查询操作
    size为默认参数，默认值为None,指定返回的查询结果数
    """
    # 先调用log函数打印出select语句
    log(sql, args)
    global __pool   # 这里为什么要再声明一次？？
    # 从连接池返回一个数据库连接；这里用到了with...as，会自动调用close()关闭连接
    async with __pool.get() as conn:    # 这个get方法怎么来的？
        # 使用cursor 以dict类型返回查询结果
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 执行查询语句。执行前先将sql语句中的占位符？换成mysql中采用的占位符%s
            await cur.execute(sql.replace('?', '%s'), args or ())  # 这里 or()怎么理解？？
            if size:
                # 如果传入size参数，则通过fetchmany()获取最多指定(size)数量的记录
                rs = await cur.fetchmany(size)
            else:
                # 通过fetchall()获取所有记录
                rs = await cur.fetchall()
        logging.info('rows returned: %s', len(rs))
        return rs


async def execute(sql, args, autocommit=True):
    """
    协程：INSERT、UPDATE、DELETE操作
    execute()函数和select()函数所不同的是，cursor对象不返回结果集，而是通过rowcount返回结果数。
    """
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:  # 这里为什么要作这个判断，什么情况下autocommit会非True??
            await conn.begin()    # 这里begin()方法怎么来的？？
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:  # 这里为什么又一次判断？？
                await conn.conmmit()
        except BaseException as e:
            if not autocommit:  # 这里又为什么判断了一次？？
                await conn.rollback()
            raise
        return affected

def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)


class Field (object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):
    def __init__(self, name=None, primary=False, default=0):
        super().__init__(name, 'bigint', primary, default)

class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)

class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键
                    if primaryKey:
                        raise StandardError('Duplicate primary key for field: %s' % k)
        