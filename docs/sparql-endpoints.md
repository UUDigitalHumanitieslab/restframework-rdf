# SPARQL endpoints

## Defining endpoints in settings

You can define your project's SPARQL views as subclasses of `SPARQLUpdateAPIView` and `SPARQLQueryAPIView` and include urls for these views in your project.

To create a working view, you have to define the `graph` method in your subclass, which should return an instance of an rdflib `Graph` object.

For example, you could use a function to construct a graph like the following:

```python
def foo_graph():
    return Graph(...) # specify options
```

Note that you may want to use your configured store setting (see the [getting started guide](/getting-started)) in the graph constructor: `Graph(store = settings.RDFLIB_STORE)`

Your view can then be defined as

```python
class FooSPARQLQueryView:
    def graph(self):
        return foo_graph()

```

You may also want to add permissions to your views. For example:

```python
from rest_framework.permissions import IsAdminUser

class FooSPARQLUpdateView:
    permission_classes = (IsAdminUser,)
    def graph(self):
        return foo_graph()

```
