import re
import ipdb

from owlready2 import get_ontology

_OWL = get_ontology("http://www.w3.org/2002/07/owl#")

def safe_add_property(entity, prop, value):
    """Add a value to a property slot on a node.

    Importantly, the method below is compatible with both functional and
    non-functional properties. If a property is functional, it either
    creates a new list or extends an existing list.

    This function cuts down on boilerplate code considerably when setting
    many property values in the ontology.
    """
    if value is None:
        return
    if _OWL.FunctionalProperty in prop.is_a:
        setattr(entity, prop._python_name, value)
    else:
        if len(getattr(entity, prop._python_name)) == 0:
            setattr(entity, prop._python_name, [value])
        else:
            getattr(entity, prop._python_name).append(value)

def eval_list_field(list_string: str):
    """Convert a list from a Neo4j CSV dump into a Python list.

    In the Neo4j database dumps, lists are stored as strings. Therefore,
    in order to use them as lists, we need to evaluate the string representation.

    If list_string is passed as `nan`, we catch the TypeError and return the
    empty list.
    """
    try:
        list_eval = eval(list_string)
        return list_eval
    except TypeError:
        return []

def eval_list_field_delim(list_string: str, delim: str = "|"):
    """Same as `eval_list_field`, but accept a (required) delimiter.

    This is implemented as a separate function for speed considerations.
    
    Parameters
    ----------
    list_string : str
        The string to split into a list.
    delim : str
        A string to use as a delimiter.
    """
    try:
        return list_string.split(delim)
    except AttributeError:
        return []

def make_safe_property_label(label):
    """Convert the label ("name") of a property to a safe format.

    We follow the convention that only class names can begin with an uppercase letter.
    This can be explained using the following example: One of the 'pathways' in Hetionet
    is named "Disease", but Disease is already a class in the ontology. Therefore, there
    is no way to distinguish between these two entities in Python.

    This may have to be reevaluated later, if lowercasing entity names is leading to
    more problems down the line.
    """
    #safe = re.sub(r'[!@#$,()\'\"\[\]\{\}\|]', '', label)
    safe = re.sub(r'\W', '', label)
    safe = safe.replace(" ", "_").lower()
    
    return safe
