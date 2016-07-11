#!/usr/bin/env python

import sys, string, copy

# configuration management
class Component:
    def __init__(self):
        self.__dict__["_attrs"] = {}

    def __getattr__(self, name):
        try:
            return self._attrs[str(name)]
        except KeyError:
            raise AttributeError("no such attribute: " + str(name) + "!")

    def __setattr__(self, name, value):
        self._attrs[str(name)] = value
        
    def __delattr__(self, name):
        try:
            del self._attrs[str(name)]
        except KeyError:
            raise AttributeError("no such attribute: " + str(name) + "!")

    def __str__(self):
        return self.__indent_str(0)

    def __indent_str(self, spaces_count):
        result = str(spaces_count) + "L+ Conject(\n"
        SPACES = " " * spaces_count
        for (k,v) in self._attrs.iteritems():
            result = result + (SPACES + "%s = %s\n" % (k, v.__indent_str(spaces_count + 1) if isinstance(v, Component) else str(v)))
        return result + SPACES + ")"

    def __setitem__(self, k, v):
        self.__dict__['_attrs'][k] = v

    def __copy__(self):
        newObj = Component()
        newObj.__dict__["_attrs"] = copy.copy(self._attrs)
        return newObj

    def mergePath(self, otherComponent):
        for (key, val) in otherComponent._attrs.iteritems():
          if key in self._attrs.keys():
            if isinstance(val, Component):
              if not isinstance(self._attrs[key], Component):
                self._attrs[key] = Component.buildComponentWithValues({'_' : self._attrs[key]}) 
              self._attrs[key].mergePath(val)
            else:
              self._attrs[key]['_'] = str(val)
          else:
            self._attrs[key] = val
        return

    @classmethod
    def buildComponentWithValues(cls, kwargs):
        _comp = Component()
        for (key, value) in kwargs.iteritems():
            _comp.__setattr__(key, value)
        return _comp

def __autovivify(key, val):
  if "." in key:
    (current_key, _, next_keys) = key.partition(".")
    nl = __autovivify(next_keys, val)
    return Component.buildComponentWithValues({current_key : __autovivify(next_keys, val)})
  else:
    if key == "":
      raise Exception("key is empty")
    return Component.buildComponentWithValues({key: val})

def conject(filePath):
    comp = Component()
    with open(filePath, "r") as fh:
        for line in filter(lambda ln: 0 <> len(ln) and not ln.startswith("#"), map(string.strip, fh.readlines())):
            (key, _, val) = map(string.strip, line.partition('=')) 
            if key == "" or val == "":
              sys.stderr.write("ignoring invalid line: %s\n" % line)
              continue
            else:
              comp.mergePath(__autovivify(key, val))
    return comp

