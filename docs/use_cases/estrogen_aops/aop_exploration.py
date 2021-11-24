

aop_subtree_query = """
CALL apoc.path.spanningTree(
    848838,
    {
        relationshipFilter: "AOPINCLUDESKE|KEINCLUDEDINAOP|KEYEVENTTRIGGEREDBY|KEYEVENTTRIGGERS",
        maxLevel: 2
    })
YIELD path
RETURN path;
"""