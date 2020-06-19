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
        
        rs = proc.query("select TABSCHEMA,TABNAME,CARD \
        from syscat.tables \
        where TABSCHEMA like 'SYS%' \
        fetch first 10 rows only")
        pprint(rs)
    finally:
        proc.close()
```
```log
DEBUG:main:Start logging pid:28713
DEBUG:main:Exec process cmd:['db2', '-td@']
DEBUG:main:>>(c) Copyright IBM Corporation 1993,2007
DEBUG:main:>>Command Line Processor for DB2 Client 11.1.0
DEBUG:main:>>
DEBUG:main:>>You can issue database manager commands and SQL statements from the command 
DEBUG:main:>>prompt. For example:
DEBUG:main:>>    db2 => connect to sample
DEBUG:main:>>    db2 => bind sample.bnd
DEBUG:main:>>
DEBUG:main:>>For general help, type: ?.
DEBUG:main:>>For command help, type: ? command, where command can be
DEBUG:main:>>the first few keywords of a database manager command. For example:
DEBUG:main:>> ? CATALOG DATABASE for help on the CATALOG DATABASE command
DEBUG:main:>> ? CATALOG          for help on all of the CATALOG commands.
DEBUG:main:>>
DEBUG:main:>>To exit db2 interactive mode, type QUIT at the command prompt. Outside 
DEBUG:main:>>interactive mode, all commands must be prefixed with 'db2'.
DEBUG:main:>>To list the current command option settings, type LIST COMMAND OPTIONS.
DEBUG:main:>>
DEBUG:main:>>For more detailed help, refer to the Online Reference Manual.
DEBUG:main:>>
DEBUG:main:>>>db2 => 
DEBUG:main:<<<list database directory@
DEBUG:main:>>
DEBUG:main:>> System Database Directory
DEBUG:main:>>
DEBUG:main:>> Number of entries in the directory = 3
DEBUG:main:>>
DEBUG:main:>>Database 1 entry:
DEBUG:main:>>
DEBUG:main:>> Database alias                       = WLPDB
DEBUG:main:>> Database name                        = WLPDB
DEBUG:main:>> Local database directory             = /home/romeol
DEBUG:main:>> Database release level               = 14.00
DEBUG:main:>> Comment                              =
DEBUG:main:>> Directory entry type                 = Indirect
DEBUG:main:>> Catalog database partition number    = 0
DEBUG:main:>> Alternate server hostname            =
DEBUG:main:>> Alternate server port number         =
DEBUG:main:>>
DEBUG:main:>>Database 2 entry:
DEBUG:main:>>
DEBUG:main:>> Database alias                       = SAMPTGT
DEBUG:main:>> Database name                        = SAMPTGT
DEBUG:main:>> Local database directory             = /home/romeol
DEBUG:main:>> Database release level               = 14.00
DEBUG:main:>> Comment                              =
DEBUG:main:>> Directory entry type                 = Indirect
DEBUG:main:>> Catalog database partition number    = 0
DEBUG:main:>> Alternate server hostname            =
DEBUG:main:>> Alternate server port number         =
DEBUG:main:>>
DEBUG:main:>>Database 3 entry:
DEBUG:main:>>
DEBUG:main:>> Database alias                       = SAMPLE
DEBUG:main:>> Database name                        = SAMPLE
DEBUG:main:>> Local database directory             = /home/romeol
DEBUG:main:>> Database release level               = 14.00
DEBUG:main:>> Comment                              =
DEBUG:main:>> Directory entry type                 = Indirect
DEBUG:main:>> Catalog database partition number    = 0
DEBUG:main:>> Alternate server hostname            =
DEBUG:main:>> Alternate server port number         =
DEBUG:main:>>
DEBUG:main:>>>db2 => 
DEBUG:main:<<<connect to WLPDB@
DEBUG:main:>>
DEBUG:main:>>   Database Connection Information
DEBUG:main:>>
DEBUG:main:>> Database server        = DB2/LINUXX8664 11.1.0
DEBUG:main:>> SQL authorization ID   = ROMEOL
DEBUG:main:>> Local database alias   = WLPDB
DEBUG:main:>>
DEBUG:main:>>>db2 => 
DEBUG:main:<<<values mon_get_application_handle@
DEBUG:main:>>
DEBUG:main:>>1                   
DEBUG:main:>>--------------------
DEBUG:main:>>                 590
DEBUG:main:>>
DEBUG:main:>>  1 record(s) selected.
DEBUG:main:>>
DEBUG:main:>>>db2 => 
DEBUG:main:<<<get snapshot for application agentid 590@
DEBUG:main:>>
DEBUG:main:>>            Application Snapshot
DEBUG:main:>>
DEBUG:main:>>Application handle                         = 590
DEBUG:main:>>Application status                         = UOW Waiting
DEBUG:main:>>Status change time                         = Not Collected
DEBUG:main:>>Application code page                      = 1208
DEBUG:main:>>Application country/region code            = 1
DEBUG:main:>>DUOW correlation token                     = *LOCAL.romeol.200619191014
DEBUG:main:>>Application name                           = db2bp
DEBUG:main:>>Application ID                             = *LOCAL.romeol.200619191014
DEBUG:main:>>Sequence number                            = 00002
DEBUG:main:>>TP Monitor client user ID                  =
DEBUG:main:>>TP Monitor client workstation name         =
DEBUG:main:>>TP Monitor client application name         =
DEBUG:main:>>TP Monitor client accounting string        =
DEBUG:main:>>
DEBUG:main:>>Connection request start timestamp         = 06/19/2020 15:10:14.165034
DEBUG:main:>>Connect request completion timestamp       = 06/19/2020 15:10:16.060270
DEBUG:main:>>Application idle time                      = Not Collected
DEBUG:main:>>CONNECT Authorization ID                   = ROMEOL
DEBUG:main:>>Client login ID                            = romeol
DEBUG:main:>>Configuration NNAME of client              = oc3245253518.ibm.com
DEBUG:main:>>Client database manager product ID         = SQL11010
DEBUG:main:>>Process ID of client application           = 28724
DEBUG:main:>>Platform of client application             = LINUXAMD64
DEBUG:main:>>Communication protocol of client           = Local Client
DEBUG:main:>>
DEBUG:main:>>Inbound communication address              = *LOCAL.romeol
DEBUG:main:>>
DEBUG:main:>>Database name                              = WLPDB
DEBUG:main:>>Database path                              = /home/romeol/romeol/NODE0000/SQL00003/MEMBER0000/
DEBUG:main:>>Client database alias                      = WLPDB
DEBUG:main:>>Input database alias                       =
DEBUG:main:>>Last reset timestamp                       =
DEBUG:main:>>Snapshot timestamp                         = 06/19/2020 15:10:16.366197
DEBUG:main:>>Authorization level granted                =
DEBUG:main:>>   User authority:
DEBUG:main:>>      DBADM authority
DEBUG:main:>>      SECADM authority
DEBUG:main:>>      DATAACCESS authority
DEBUG:main:>>      ACCESSCTRL authority
DEBUG:main:>>   Group authority:
DEBUG:main:>>      SYSADM authority
DEBUG:main:>>      CREATETAB authority
DEBUG:main:>>      BINDADD authority
DEBUG:main:>>      CONNECT authority
DEBUG:main:>>      IMPLICIT_SCHEMA authority
DEBUG:main:>>Coordinator member number                  = 0
DEBUG:main:>>Current member number                      = 0
DEBUG:main:>>Coordinator agent process or thread ID     = 449
DEBUG:main:>>Current Workload ID                        = 1
DEBUG:main:>>Agents stolen                              = 0
DEBUG:main:>>Agents waiting on locks                    = 0
DEBUG:main:>>Maximum associated agents                  = 1
DEBUG:main:>>Priority at which application agents work  = 0
DEBUG:main:>>Priority type                              = Dynamic
DEBUG:main:>>
DEBUG:main:>>Lock timeout (seconds)                     = -1
DEBUG:main:>>Locks held by application                  = 0
DEBUG:main:>>Lock waits since connect                   = 0
DEBUG:main:>>Time application waited on locks (ms)      = Not Collected
DEBUG:main:>>Deadlocks detected                         = Not Collected
DEBUG:main:>>Lock escalations                           = 0
DEBUG:main:>>Exclusive lock escalations                 = 0
DEBUG:main:>>Number of Lock Timeouts since connected    = 0
DEBUG:main:>>Total time UOW waited on locks (ms)        = Not Collected
DEBUG:main:>>
DEBUG:main:>>Total sorts                                = 0
DEBUG:main:>>Total sort time (ms)                       = Not Collected
DEBUG:main:>>Total sort overflows                       = 0
DEBUG:main:>>
DEBUG:main:>>Buffer pool data logical reads             = 450
DEBUG:main:>>Buffer pool data physical reads            = 103
DEBUG:main:>>Buffer pool temporary data logical reads   = 0
DEBUG:main:>>Buffer pool temporary data physical reads  = 0
DEBUG:main:>>Buffer pool data writes                    = 0
DEBUG:main:>>Buffer pool index logical reads            = 610
DEBUG:main:>>Buffer pool index physical reads           = 201
DEBUG:main:>>Buffer pool temporary index logical reads  = 0
DEBUG:main:>>Buffer pool temporary index physical reads = 0
DEBUG:main:>>Buffer pool index writes                   = 0
DEBUG:main:>>Buffer pool xda logical reads              = 0
DEBUG:main:>>Buffer pool xda physical reads             = 0
DEBUG:main:>>Buffer pool temporary xda logical reads    = 0
DEBUG:main:>>Buffer pool temporary xda physical reads   = 0
DEBUG:main:>>Buffer pool xda writes                     = 0
DEBUG:main:>>Total buffer pool read time (milliseconds) = 657
DEBUG:main:>>Total buffer pool write time (milliseconds)= 0
DEBUG:main:>>Time waited for prefetch (ms)              = 0
DEBUG:main:>>Unread prefetch pages                      = 0
DEBUG:main:>>Direct reads                               = 58
DEBUG:main:>>Direct writes                              = 0
DEBUG:main:>>Direct read requests                       = 10
DEBUG:main:>>Direct write requests                      = 0
DEBUG:main:>>Direct reads elapsed time (ms)             = 34
DEBUG:main:>>Direct write elapsed time (ms)             = 0
DEBUG:main:>>
DEBUG:main:>>Number of SQL requests since last commit   = 0
DEBUG:main:>>Commit statements                          = 1
DEBUG:main:>>Rollback statements                        = 0
DEBUG:main:>>Dynamic SQL statements attempted           = 1
DEBUG:main:>>Static SQL statements attempted            = 1
DEBUG:main:>>Failed statement operations                = 0
DEBUG:main:>>Select SQL statements executed             = 1
DEBUG:main:>>Xquery statements executed                 = 0
DEBUG:main:>>Update/Insert/Delete statements executed   = 0
DEBUG:main:>>DDL statements executed                    = 0
DEBUG:main:>>Inactive stmt history memory usage (bytes) = 0
DEBUG:main:>>Internal automatic rebinds                 = 0
DEBUG:main:>>Internal rows deleted                      = 0
DEBUG:main:>>Internal rows inserted                     = 0
DEBUG:main:>>Internal rows updated                      = 0
DEBUG:main:>>Internal commits                           = 1
DEBUG:main:>>Internal rollbacks                         = 0
DEBUG:main:>>Internal rollbacks due to deadlock         = 0
DEBUG:main:>>Binds/precompiles attempted                = 0
DEBUG:main:>>Rows deleted                               = 0
DEBUG:main:>>Rows inserted                              = 0
DEBUG:main:>>Rows updated                               = 0
DEBUG:main:>>Rows selected                              = 1
DEBUG:main:>>Rows read                                  = 282
DEBUG:main:>>Rows written                               = 0
DEBUG:main:>>
DEBUG:main:>>UOW log space used (Bytes)                 = Not Collected
DEBUG:main:>>Previous UOW completion timestamp          = Not Collected
DEBUG:main:>>Elapsed time of last completed uow (sec.ms)= Not Collected
DEBUG:main:>>UOW start timestamp                        = Not Collected
DEBUG:main:>>UOW stop timestamp                         = Not Collected
DEBUG:main:>>UOW completion status                      = Not Collected
DEBUG:main:>>
DEBUG:main:>>Open remote cursors                        = 0
DEBUG:main:>>Open remote cursors with blocking          = 0
DEBUG:main:>>Rejected Block Remote Cursor requests      = 0
DEBUG:main:>>Accepted Block Remote Cursor requests      = 1
DEBUG:main:>>Open local cursors                         = 0
DEBUG:main:>>Open local cursors with blocking           = 0
DEBUG:main:>>Total User CPU Time used by agent (s)      = 0.027321
DEBUG:main:>>Total System CPU Time used by agent (s)    = 0.000000
DEBUG:main:>>Host execution elapsed time                = Not Collected
DEBUG:main:>>
DEBUG:main:>>Package cache lookups                      = 1
DEBUG:main:>>Package cache inserts                      = 1
DEBUG:main:>>Application section lookups                = 4
DEBUG:main:>>Application section inserts                = 1
DEBUG:main:>>Catalog cache lookups                      = 47
DEBUG:main:>>Catalog cache inserts                      = 38
DEBUG:main:>>Catalog cache overflows                    = 0
DEBUG:main:>>Catalog cache high water mark              = 0
DEBUG:main:>>
DEBUG:main:>>Workspace Information
DEBUG:main:>>
DEBUG:main:>>
DEBUG:main:>>Most recent operation                      = Static Commit
DEBUG:main:>>Most recent operation start timestamp      = Not Collected
DEBUG:main:>>Most recent operation stop timestamp       = Not Collected
DEBUG:main:>>Agents associated with the application     = 1
DEBUG:main:>>Number of hash joins                       = 0
DEBUG:main:>>Number of hash loops                       = 0
DEBUG:main:>>Number of hash join overflows              = 0
DEBUG:main:>>Number of small hash join overflows        = 0
DEBUG:main:>>Number of OLAP functions                   = 0
DEBUG:main:>>Number of OLAP function overflows          = 0
DEBUG:main:>>
DEBUG:main:>>Memory usage for application:
DEBUG:main:>>
DEBUG:main:>>  Memory Pool Type                         = Application Heap
DEBUG:main:>>     Current size (bytes)                  = 131072
DEBUG:main:>>     High water mark (bytes)               = 131072
DEBUG:main:>>     Configured size (bytes)               = 1048576
DEBUG:main:>>
DEBUG:main:>>Agent process/thread ID                    = 449
DEBUG:main:>>  Agent Lock timeout (seconds)             = -1
DEBUG:main:>>  Memory usage for agent:
DEBUG:main:>>
DEBUG:main:>>    Memory Pool Type                       = Other Memory
DEBUG:main:>>       Current size (bytes)                = 458752
DEBUG:main:>>       High water mark (bytes)             = 655360
DEBUG:main:>>       Configured size (bytes)             = 10360905728
DEBUG:main:>>>db2 => 
{'Accepted Block Remote Cursor requests': '1',
 'Agents stolen': '0',
 'Agents waiting on locks': '0',
 'Application ID': '*LOCAL.romeol.200619191014',
 'Application code page': '1208',
 'Application country/region code': '1',
 'Application handle': '590',
 'Application name': 'db2bp',
 'Application section inserts': '1',
 'Application section lookups': '4',
 'Application status': 'UOW Waiting',
 'Binds/precompiles attempted': '0',
 'Buffer pool data logical reads': '450',
 'Buffer pool data physical reads': '103',
 'Buffer pool data writes': '0',
 'Buffer pool index logical reads': '610',
 'Buffer pool index physical reads': '201',
 'Buffer pool index writes': '0',
 'Buffer pool temporary data logical reads': '0',
 'Buffer pool temporary data physical reads': '0',
 'Buffer pool temporary index logical reads': '0',
 'Buffer pool temporary index physical reads': '0',
 'Buffer pool temporary xda logical reads': '0',
 'Buffer pool temporary xda physical reads': '0',
 'Buffer pool xda logical reads': '0',
 'Buffer pool xda physical reads': '0',
 'Buffer pool xda writes': '0',
 'CONNECT Authorization ID': 'ROMEOL',
 'Catalog cache high water mark': '0',
 'Catalog cache inserts': '38',
 'Catalog cache lookups': '47',
 'Catalog cache overflows': '0',
 'Client database alias': 'WLPDB',
 'Client database manager product ID': 'SQL11010',
 'Client login ID': 'romeol',
 'Commit statements': '1',
 'Communication protocol of client': 'Local Client',
 'Configuration NNAME of client': 'oc3245253518.ibm.com',
 'Connect request completion timestamp': '06/19/2020 15:10:16.060270',
 'Connection request start timestamp': '06/19/2020 15:10:14.165034',
 'Coordinator agent process or thread ID': '449',
 'Coordinator member number': '0',
 'Current Workload ID': '1',
 'Current member number': '0',
 'DDL statements executed': '0',
 'DUOW correlation token': '*LOCAL.romeol.200619191014',
 'Database name': 'WLPDB',
 'Database path': '/home/romeol/romeol/NODE0000/SQL00003/MEMBER0000/',
 'Direct read requests': '10',
 'Direct reads': '58',
 'Direct reads elapsed time (ms)': '34',
 'Direct write elapsed time (ms)': '0',
 'Direct write requests': '0',
 'Direct writes': '0',
 'Dynamic SQL statements attempted': '1',
 'Exclusive lock escalations': '0',
 'Failed statement operations': '0',
 'Inactive stmt history memory usage (bytes)': '0',
 'Inbound communication address': '*LOCAL.romeol',
 'Internal automatic rebinds': '0',
 'Internal commits': '1',
 'Internal rollbacks': '0',
 'Internal rollbacks due to deadlock': '0',
 'Internal rows deleted': '0',
 'Internal rows inserted': '0',
 'Internal rows updated': '0',
 'Lock escalations': '0',
 'Lock timeout (seconds)': '-1',
 'Lock waits since connect': '0',
 'Locks held by application': '0',
 'Maximum associated agents': '1',
 'Number of Lock Timeouts since connected': '0',
 'Number of SQL requests since last commit': '0',
 'Open local cursors': '0',
 'Open local cursors with blocking': '0',
 'Open remote cursors': '0',
 'Open remote cursors with blocking': '0',
 'Package cache inserts': '1',
 'Package cache lookups': '1',
 'Platform of client application': 'LINUXAMD64',
 'Priority at which application agents work': '0',
 'Priority type': 'Dynamic',
 'Process ID of client application': '28724',
 'Rejected Block Remote Cursor requests': '0',
 'Rollback statements': '0',
 'Rows deleted': '0',
 'Rows inserted': '0',
 'Rows read': '282',
 'Rows selected': '1',
 'Rows updated': '0',
 'Rows written': '0',
 'Select SQL statements executed': '1',
 'Sequence number': '00002',
 'Snapshot timestamp': '06/19/2020 15:10:16.366197',
 'Static SQL statements attempted': '1',
 'Time waited for prefetch (ms)': '0',
 'Total System CPU Time used by agent (s)': '0.000000',
 'Total User CPU Time used by agent (s)': '0.027321',
 'Total buffer pool read time (milliseconds)': '657',
 'Total buffer pool write time (milliseconds)': '0',
 'Total sort overflows': '0',
 'Total sorts': '0',
 'Unread prefetch pages': '0',
 'Update/Insert/Delete statements executed': '0',
 'Xquery statements executed': '0',
 'agent[449].Agent Lock timeout (seconds)': '-1',
 'agent[449].mem.Other_Memory.Configured size (bytes)': '10360905728',
 'agent[449].mem.Other_Memory.Current size (bytes)': '458752',
 'agent[449].mem.Other_Memory.High water mark (bytes)': '655360',
 'mem.Application_Heap.Configured size (bytes)': '1048576',
 'mem.Application_Heap.Current size (bytes)': '131072',
 'mem.Application_Heap.High water mark (bytes)': '131072',
 'wki.Agents associated with the application': '1',
 'wki.Most recent operation': 'Static Commit',
 'wki.Number of OLAP function overflows': '0',
 'wki.Number of OLAP functions': '0',
 'wki.Number of hash join overflows': '0',
 'wki.Number of hash joins': '0',
 'wki.Number of hash loops': '0',
 'wki.Number of small hash join overflows': '0'}
DEBUG:main:<<<select TABSCHEMA,TABNAME,CARD         from syscat.tables         where TABSCHEMA like 'SYS%'         fetch first 10 rows only@
DEBUG:main:>>
DEBUG:main:>>TABSCHEMA                                                                                                                        TABNAME                                                                                                                          CARD                
DEBUG:main:>>-------------------------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------- --------------------
DEBUG:main:>>SYSIBM                                                                                                                           SYSTABLES                                                                                                                                          -1
DEBUG:main:>>SYSIBM                                                                                                                           SYSCOLUMNS                                                                                                                                         -1
DEBUG:main:>>SYSIBM                                                                                                                           SYSINDEXES                                                                                                                                         -1
DEBUG:main:>>SYSIBM                                                                                                                           SYSVIEWS                                                                                                                                           -1
DEBUG:main:>>SYSIBM                                                                                                                           SYSVIEWDEP                                                                                                                                         -1
DEBUG:main:>>SYSIBM                                                                                                                           SYSPLAN                                                                                                                                            -1
DEBUG:main:>>SYSIBM                                                                                                                           SYSPLANDEP                                                                                                                                         -1
DEBUG:main:>>SYSIBM                                                                                                                           SYSSECTION                                                                                                                                         -1
DEBUG:main:>>SYSIBM                                                                                                                           SYSSTMT                                                                                                                                            -1
DEBUG:main:>>SYSIBM                                                                                                                           SYSDBAUTH                                                                                                                                          -1
DEBUG:main:>>
DEBUG:main:>>  10 record(s) selected.
DEBUG:main:>>
DEBUG:main:>>>db2 => 
{'names': ['TABSCHEMA', 'TABNAME', 'CARD'],
 'rows': [['SYSIBM', 'SYSTABLES', '-1'],
          ['SYSIBM', 'SYSCOLUMNS', '-1'],
          ['SYSIBM', 'SYSINDEXES', '-1'],
          ['SYSIBM', 'SYSVIEWS', '-1'],
          ['SYSIBM', 'SYSVIEWDEP', '-1'],
          ['SYSIBM', 'SYSPLAN', '-1'],
          ['SYSIBM', 'SYSPLANDEP', '-1'],
          ['SYSIBM', 'SYSSECTION', '-1'],
          ['SYSIBM', 'SYSSTMT', '-1'],
          ['SYSIBM', 'SYSDBAUTH', '-1']],
 'sizes': [128, 128, 20]}
```
