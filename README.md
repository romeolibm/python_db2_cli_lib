# python_db2_cli_lib

A small python library of methods and classes you can use
to execute db2 queries and commands via the db2/db2pd cli interface.

This is useful if you need a quick way (no drivers needed)
to implement monitoring ant automation for a db2 database
but you can't or do not have the time to install the python
driver library or some information is only available to you 
from the db2 cli interface. 
 
TODO: Error handling! (this is an alpha version for now)

# Entry points

```python
class TextRequestResponseSubprocess:
    """
    A base class implementing the common algorithm for executing 
    request-response operations on child processes by using the
    stdin, stdout and stderr of the child process.
    Allows for provisions on handling interfaces designed for
    human beings (including a prompt and a text custom parser). 
    """
```
```python
class DB2CliSubprocess(TextRequestResponseSubprocess):
    """
    Call a db2 command then execute subsequent commands parse and 
    return results to the caller.
    """
```
```python
class DB2pdSubprocess(TextRequestResponseSubprocess):
    """
    Call a db2pd command then execute subsequent commands parse and 
    return results to the caller.
    """
```
# Example of usage

```python
def main():
    """    
    This is a library so this main method is only for running some tests 
    and try it out
    """
    configLogging(level='debug')
    from pprint import pprint
    proc = DB2CliSubprocess()
    try:
        proc.connect()
        
        info = proc.getSnapshotForApplication(proc.getMyApplHandle())
        pprint(info)
        
        rs = proc.query("select * from syscat.tables fetch first 10 rows only")
        pprint(rs)
    finally:
        proc.close()
```
