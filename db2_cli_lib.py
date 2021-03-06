"""
    @author: Romeo Lupascu
    @contact: romeol@ca.ibm.com
    @organization: IBM
    @since: 2020-06-18,2020-06-22
    @license: http://www.apache.org/licenses/LICENSE-2.0
    @version: 0.1
    @see: https://github.com/romeolibm/python_db2_cli_lib
    
     A small python library of methods and classes you can use
     to execute db2 queries and commands via the db2/db2pd cli interface.
     
     This is useful if you need a quick way (no drivers needed)
     to implement monitoring ant automation for a db2 database
     but you can't or do not have the time to install the python
     driver library or some information is only available to you 
     from the db2 cli interface. 
 
"""
import os, sys, subprocess, threading, re, StringIO, time, traceback
import logging
LGR = logging.getLogger("main")
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

def configLogging(file=None, level=None):
    if not level:
        return
    if type(level) == str:
        level = level.lower()
        level = LOG_LEVELS[level]
    logging.basicConfig(level=level)
    LGR.setLevel(level)
    if file:
        from logging import handlers
        handler = handlers.RotatingFileHandler(
            file, maxBytes=100000000, backupCount=10
        )
        handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        LGR.addHandler(handler)
    LGR.debug("Start logging pid:{0}".format(os.getpid()))

def getuserid(user_name):
    """
    Use 'id -u <user-name>' to get the user number (id) from a user name
    """
    return subprocess.Popen(
        ["id", "-u", user_name],
        stdout=subprocess.PIPE
    ).communicate()[0].strip().splitlines()[0].strip()

def get_db2sysc_user():
    """
    """
    return subprocess.Popen(
        ["ps", "-o", "user", "-C", "db2sysc"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip().splitlines()[1].strip()

def get_db2fmp_user():
    """
    """
    return subprocess.Popen(
        ["ps", "-o", "user", "-C", "db2fmp"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip().splitlines()[1].strip()
    

def get_db2diag_path():
    """
    Retrieve the current env db2 diagpath by using db2pd -diagpath
    """
    return subprocess.Popen(
        ["db2pd", "-diagpath"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip().splitlines()[-1:][0]

def get_db2sysc_pid():
    """
    Find the current PID for the DB2 engine process.
    ps -o pid -C db2sysc
    """
    return subprocess.Popen(
        ["ps", "-o", "pid", "-C", "db2sysc"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip().splitlines()[1].strip()

class TextIOProcessor(threading.Thread):
    """
    Read data from an input stream infile one char at the time.
    Store the char in a local line buffer and 
    if outfile is provided the char is immediately written.
    If a condition is provided for checking the current 
    line buffer it will be called.
    The time of last read is recorded and available for
    future analysis.
    """
    
    def __init__(self,
            infile,
            outfile=None,
            linehandler=None,
            inflightLineHandler=None,
            name=None
        ):
        threading.Thread.__init__(self)
        self.setName(name if name else "iosubprocessor")
        self.setDaemon(True)
        self.ignorablechars = "\r"
        self.eol = "\n"
        self.linehandler = linehandler
        self.inflightLineHandler = inflightLineHandler
        self.line = StringIO.StringIO()
        self.lastrdtime = None
        self.infile = infile
        self.outfile = outfile
        self.rlock = threading.RLock()
        self.closed = False
        
    def lockSelf(self):
        """
        Allow synchronized access to this object instance, use before accessing it.
        """
        while not self.rlock.acquire(True):
            pass
        
    def unlockSelf(self):
        """
        Allow synchronized access to this object instance, use after finish accessing it.
        """
        if self.rlock._is_owned():
            self.rlock.release()
            
    def setOutput(self, outfile):
        """
        Allow for new output files to be changed "on the fly" by the clients.
        """
        try:
            self.lockSelf()
            if self.outfile:
                self.outfile.flush()
                self.outfile.close()
            self.outfile = outfile
        finally:
            self.unlockSelf()
        
    def __writeOutput(self, c):
        try:
            self.lockSelf()
            if self.outfile:
                self.outfile.write(c)
        finally:
            self.unlockSelf()
                
    def close(self):
        """
        Close the output (not the input) and mark the object as closed.
        This will stop the thread loop
        """
        try:
            self.lockSelf()
            if self.outfile:
                self.outfile.flush()
                self.outfile.close()
            self.outfile = None
            self.closed = True
        finally:
            self.unlockSelf()
            
    def run(self):
        try:
            while not self.closed:
                c = self.infile.read(1)
                if not c:
                    time.sleep(0.2)
                    continue
                self.lastrdtime = time.time()
                if c in self.ignorablechars:
                    continue
                
                if c == self.eol:
                    if self.linehandler:
                        try:
                            self.linehandler(self.line.getvalue())
                        except Exception, e:
                            LGR.debug("<>{0}".format(s))
                            LGR.debug("lh-err:{0}".format(traceback.format_exc()))
                    # TODO: use an array or buffer instead
                    self.line = StringIO.StringIO()
                else:
                    self.line.write(c)
                    s = self.line.getvalue()
                    try:
                        if self.inflightLineHandler and self.inflightLineHandler(s):
                            LGR.debug(">>>{0}".format(s))
                            self.line = StringIO.StringIO()
                    except Exception, e:
                        LGR.debug("<<>{0}".format(s))
                        LGR.debug("plh-err:{0}".format(traceback.format_exc()))
                        
                self.__writeOutput(c)
        finally:
            LGR.debug("***Ending thread:{0}".format(self.name))

class TextRequestResponseSubprocessException(StandardError):
    """
    A base exception for all process response detected errors.
    Those errors are expected to be raised by the _errParser()
    method when processign the response from the child process.
    """
    def __init__(self, *args):
        StandardError.__init__(self, *args)
        
class TextRequestResponseSubprocess:
    """
    A base class implementing the common algorithm for executing 
    request-response operations on child processes by using the
    stdin, stdout and stderr of the child process.
    Allows for provisions on handling interfaces designed for
    human beings (including a prompt and a text custom parser). 
    """
    def __init__(self,
            cmdline ,
            promptDetectorMethod,
            responseParser=None,
            responseLineHandler=None,
            name=None
        ):
        self.name = name if name else "subprocess"
        self.promptDetectorMethod = promptDetectorMethod
        self.responseLineHandler = responseLineHandler
        self.responseParser = responseParser
        self.cmdline = cmdline
        self.endRequest = False
        self.stdoutErr = False
        self.response = []
        
        LGR.debug("Exec process cmd:{0}".format(repr(cmdline)))
        
        self.proc = subprocess.Popen(
            cmdline,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if not self.isAlive():
            raise Exception("Unable to start {0}".format(cmdline[0]))
        
        self.stdoutproc = TextIOProcessor(
            self.proc.stdout,
            linehandler=self.handleOutputLine,
            inflightLineHandler=self.handleInflightLine,
            name=self.name + ".stdout"
        )
        self.stdoutproc.start()
        
        self.stderrproc = TextIOProcessor(
            self.proc.stderr,
            linehandler=self.handleErrorLine,
            name=self.name + ".stderr"
        )
        self.stderrproc.start()
        
        if self.promptDetectorMethod:
            timeout = 10
            start = time.time()
            while not self.endRequest and ((time.time() - start) < timeout):
                time.sleep(0.2)

    def testForErrorState(self, line):
        """
        Some processes output error messages into the stdount instead of stderr.
        This method is called first for each stdout line and can switch
        the normal stdout line processing to the self.error line list.
        It must be redefined in a derived class.
        It must return true if an error start message was detected.
        """
        return False
        
    def isAlive(self):
        return self.proc.poll() is None
    
    def handleInflightLine(self, line):
        if self.promptDetectorMethod and self.promptDetectorMethod(line):
            self.endRequest = True
        return self.endRequest
    
    def handleOutputLine(self, line):
        LGR.debug(">>{0}".format(line))
        if self.stdoutErr:
            self.handleErrorLine(line)
            return        
        if self.testForErrorState(line):
            self.stdoutErr = True
            self.handleErrorLine(line)
            return
         
        if self.responseLineHandler:
            self.responseLineHandler(line)
        else:
            rt = type(self.response)
            if rt == list:
                self.response.append(line)
            elif (rt == dict) \
              and self.response.has_key('info') \
              and (type(self.response['info']) == list):
                self.response['info'].append(line)
        
    def handleErrorLine(self, line):
        self.error.append(line)
    
    def _outputParser(self):
        """
        Override in derived class to allow you to parse the response from the 
        process and present it ina structured object (whatever that is)
        """
        return self.responseParser(self.response) if self.responseParser else self.response 
    
    def _errParser(self):
        """
        Override in derived class to allow you to parse the stderr from the 
        process and present it in a structured object (whatever that is).
        By default this method is expected to raise an error derived from
        TextRequestResponseSubprocessException but it can be redefined
        to return an error object if the caller is able to distinguish
        error objects from normal response objects.
        """
        raise TextRequestResponseSubprocessException(*self.error)
    
    def getResponse(self, cmd, timeout=300, loopSleep=0.2):
        """
        Execute a request to the child thread listen/wait for a response on the
        stdout and stderr then when the prompt is found call the 
        output and error parser then return the result
        """
        if not self.isAlive():
            raise Exception("{0} process is disconnected!".format(self.name))
        self.request = cmd
        self.endRequest = False
        if self.response is None:
            self.response = []
        self.stdoutErr = False
        self.error = []
        
        LGR.debug("<<<{0}".format(str(cmd)))
        
        self.proc.stdin.write(cmd)
        self.proc.stdin.write(os.linesep)
        self.proc.stdin.flush()
        
        stime = time.time()
        while not self.endRequest:
            time.sleep(loopSleep)
            if (time.time() - stime) > timeout:
                raise Exception("Timeout")
        if self.error:
            return self._errParser()
        return self._outputParser()
    
    def close(self):
        if self.stdoutproc:
            self.stdoutproc.close()
        if self.stderrproc:
            self.stderrproc.close()

class SQLError(TextRequestResponseSubprocessException):
    def __init__(self, *args, **names):
        TextRequestResponseSubprocessException.__init__(self, *args)
        self.sqlCode = names.get('sqlCode', None)
        self.sqlState = names.get('sqlState', None)
    
    def __repr__(self):
        return "SQLError(sqlCode={0},sqlState={1},args={2})".format(
            self.sqlCode, self.sqlState, self.args
        )
    def __str__(self):
        return repr(self)
    
class DB2CliSubprocess(TextRequestResponseSubprocess):
    """
    Call a db2 command then execute subsequent commands parse and 
    return results to the caller.
    """
    QUERY_HDR_REC = re.compile("^-+(\s+-*)*$")
    ERROR_LINE_REC = re.compile("^SQL\d+N.*$", re.DOTALL)
    ERROR_CODE_REC = re.compile("SQL\d+N")
    ERROR_STATE_REC = re.compile("SQLSTATE\=\d+")
            
    def __init__(self, database=None, delimiter="@"):
        self.delimiter = delimiter
        self.trimColData = True
        TextRequestResponseSubprocess.__init__(self,
            ["db2", "-td" + delimiter],
            self.__promptDetector,
            name="db2subprocess"
        )
        
        if database:
            self.execStmt("connect to " + database + self.delimiter)
        
    def __promptDetector(self, line):
        return line == "db2 => "
    
    def testForErrorState(self, line):
        """
        Detect if this line is the start of an error message as 
        a SQLnnnnN ...pattern        
        """
        return DB2CliSubprocess.ERROR_LINE_REC.match(line)
    
    def _errParser(self):
        """
        Extract the SQL error number and SQL state from the message.
        """
        sqlCode = None
        sqlState = None
        for line in self.error:
            if not sqlCode:
                m = DB2CliSubprocess.ERROR_CODE_REC.search(line)
                if m:
                    sqlCode = -int(m.group()[3:-1])
            if not sqlState:
                m = DB2CliSubprocess.ERROR_STATE_REC.search(line)
                if m:
                    sqlState = m.group()[9:]
            
            if sqlCode and sqlState:
                break
        
        err = SQLError(sqlCode=sqlCode, sqlState=sqlState, *self.error)
        if self.returError:
            return err
        raise err
    
    def handleQueryOutputLine(self, line):
        """
        Handle lines returned by a query and build a result set.
        Is also able to save the rows in a file (csv by default)
        for result sets that may not fit in memory
        """
        if self.rq_begin:
            if DB2CliSubprocess.QUERY_HDR_REC.match(line):
                self.row_size = len(line)
                self.row_sizes = [len(x) for x in line.split()]
                self.response['sizes'] = self.row_sizes
                if self.last_line:
                    self.response["names"] = self.last_line.split()
                self.rq_begin = False
            self.last_line = line
        else:
            if len(line) == self.row_size:
                spos = 0
                rec = []
                for l in self.row_sizes:
                    col = line[spos:spos + l]
                    if self.trimColData:
                        col = col.strip()
                    rec.append(col)
                    spos = spos + l + 1
                if self.rowWriter:
                    self.rowWriter.writerow(rec)
                else:
                    self.response['rows'].append(rec)

    def parseKV(self, line):
        idx = line.find("=")
        if idx > 0:
            return line[:idx].strip(), line[idx + 1:].strip()
        return None, None
    
    def handleApplicationSnapshotLine(self, line):
        """
        Handle the output of the db2 get snapshot for application agentid <agent-id>
        """
        if self.rsState == 'start':
            if line.find('Application Snapshot') > 0:
                self.rsState = 'kv'
        elif self.rsState == 'kv':
            if not line:
                return
            
            k, v = self.parseKV(line)
            if k:
                if k == 'Agent process/thread ID':
                    self.section = ["agent[{0}]".format(v)]
                    return
                if k == 'Memory Pool Type':
                    self.section.append(v.replace(" ", "_"))
                    return
                if self.section:
                    k = ".".join(self.section) + '.' + k
                if v and not v == 'Not Collected':
                    self.response[k] = v
            elif line.startswith('Workspace Information'):
                self.section = ['wki']
            elif line.startswith('Memory usage for application'):
                self.section = ['mem']
            elif line.startswith('  Memory usage for agent:'):
                self.section.append("mem")
            
    def handleListDatabaseDirectoryExtractAliasLine(self, line):
        """
        Handle the output of the db2 'list database directory' command
        and only extract the database aliases 
        """
        line = line.strip()
        if not line:
            return
        k, v = self.parseKV(line)
        if not k:
            return
        if k == 'Database alias':
            self.response.append(v)
        
    def query(self, sql, rowWriter=None, rowReader=None):
        """
        Execute query statements that returns a result set.
        If a rowWriter is provided (any object with a method writerow(<iterable>)
        then the rows of the result will be written to it.
        If a rowReader is provided then it will be provided in the
        result map instead of the 'rows' list. 
        """
        try:
            self.responseLineHandler = self.handleQueryOutputLine
            self.rq_begin = True
            self.row_size = None
            self.last_line = None
            self.rowWriter = rowWriter
            self.returError = False
            self.response = {'rows':rowReader if rowReader else [], 'info':[]}
            return self.getResponse(sql + self.delimiter)
        finally:
            self.responseParser = None
            self.responseLineHandler = None
            
    def execStmt(self,
            sql,
            responseParser=None,
            responseLineHandler=None,
            useDelim=True,
            returError=False,
            responseObject=None
        ):
        """
        Execute and db2 statement or command that does not return any result sets.
        """
        try:
            self.returError = returError
            self.responseParser = responseParser
            self.responseLineHandler = responseLineHandler
            if not responseObject is None:
                self.response = responseObject
            else:
                self.response = []
            return self.getResponse(sql + (self.delimiter if useDelim else ""))
        finally:
            self.responseParser = None
            self.responseLineHandler = None
     
    def execCmd(self,
            sql,
            responseParser=None,
            responseLineHandler=None,
            responseObject=None
        ):
        """
        Execute and db2 command that does not return any result sets.
        """
        return self.execStmt(sql,
            responseParser,
            responseLineHandler,
            responseObject=responseObject
        )
     
    def getMyApplHandle(self):
        """
        Return the current application handle
        """
        rs = self.query("values mon_get_application_handle")
        rows = rs['rows']
        return rows[0][0].strip() if rows else None
        
    def getSnapshotForApplication(self, *appl_handle):
        """
        Execute a db2 get snapshot for application agentid <appl-handle>
        Parse the text output and present it in a map object containing 
        db2 standard naming parameters as keys.
        TODO: key set and name mappings
        """
        if len(appl_handle) == 0:
            return None
        rl = []
        for ah in appl_handle:
            self.rsState = 'start'
            self.section = None
            rl.append(self.execCmd(
                "get snapshot for application agentid " + str(ah),
                responseLineHandler=self.handleApplicationSnapshotLine,
                responseObject={}
            ))
        return rl if len(rl) > 1 else rl[0]
        
    def getDatabaseAliases(self):
        """
        Return all the known database aliases for this instance
        """
        self.section = None
        self.response = []
        return self.execCmd(
            "list database directory",
            responseLineHandler=self.handleListDatabaseDirectoryExtractAliasLine
        )
        
    def connect(self, dbalias=None):
        """
        Connect to a database alias or to the first database in the
        database directory if no alias is provided
        """
        if not dbalias:
            aliases = self.getDatabaseAliases()
            dbalias = aliases[0]
        self.execStmt("connect to " + dbalias)
    
class DB2pdSubprocess(TextRequestResponseSubprocess):
    """
    Call a db2pd command then execute subsequent commands parse and 
    return results to the caller.
    """
    ERROR_LINE_REC = re.compile("^Invalid\s+command.*$")
    
    def __init__(self):
        TextRequestResponseSubprocess.__init__(self,
            ["db2pd"],
            self.__promptDetector,
            self.__parseResponse
        )
    
    def testForErrorState(self, line):
        """
        Detect if this line is the start of an error message as 
        a SQLnnnnN ...pattern        
        """
        return DB2pdSubprocess.ERROR_LINE_REC.matches(line)

    def __promptDetector(self, line):
        return line == "db2pd> "
    
    def getLatches(self):
        """
        """
    
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
        
        # DDL, DML and query
        rc = proc.execStmt("""CREATE TABLE TEST_SCH.TEST_TBL 
(
    cname varchar(128),
    value varchar(256)
)
        """, returError=True)
        LGR.debug("Result:> {0}".format(rc))
        
        rc = proc.execStmt("""INSERT INTO TEST_SCH.TEST_TBL (cname,value) VALUES
('n1','v1'),
('n2','v2'),
('n3','v3'),
('n4','v4')
        """, returError=True)
        LGR.debug("Result:> {0}".format(rc))
        
        rs = proc.query("select * FROM TEST_SCH.TEST_TBL order by 1")
        LGR.debug("Result:{0}".format(repr(rs)))
        
        rc = proc.execStmt('DROP TABLE TEST_SCH.TEST_TBL', returError=True)
        LGR.debug("Result:> {0}".format(rc))
        
        # error handling
        try:
            rs = proc.query("select * from TEST_SCH.TEST_TBL")
            pprint(rs)
        except Exception, e:
            LGR.debug("!!!! Error:> {0}".format(traceback.format_exc()))
            # pprint(e)
            
        # using cli utilities
        info = proc.getSnapshotForApplication(proc.getMyApplHandle())
        pprint(info)
        
    finally:
        proc.close()
        
if __name__ == '__main__':
    main()
    
