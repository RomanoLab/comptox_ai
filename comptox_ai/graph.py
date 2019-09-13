class Graph:
    def __init__(self, driver, **kwargs):
        self.driver = driver

        # If node_labels is the empty list, we don't filter on node type
        self.node_mask = kwargs.get("node_mask", [])
        if isinstance(self.node_mask, str):
            self.node_labels = [self.node_labels]
 
