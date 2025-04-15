

aop_subtree_query = """
CALL apoc.path.spanningTree(
    878567,
    {
        relationshipFilter: "AOPINCLUDESKE|KEINCLUDEDINAOP|KEYEVENTTRIGGEREDBY|KEYEVENTTRIGGERS",
        maxLevel: 2
    })
YIELD path
RETURN path;
"""
# Note: 878567 is currently the node id for 