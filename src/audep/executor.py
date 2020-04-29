import logging
import fabric2


class Executor:
    """
    动作执行器
    """

    def __init__(self, host, password, debug):
        try:
            self._host = host
            self._password = password
            self._debug = debug
            self._error = -10000
            if debug:
                print(f"[DEBUG MODE]: connect host {host}")
            self._mc = fabric2.Connection(host, connect_kwargs={'password': password}, connect_timeout=5)
            return
        except Exception as e:
            logging.error("Template unexpected error:".format(e))
        self._mc = None

    @property
    def value(self):
        return self._mc

    @property
    def error(self):
        return self._error

    def sudo(self, cmd):
        """
        """
        try:
            if self._debug:
                print(f"[DEBUG MODE]: execute sudo {cmd}")
                return self._error
            elif self._mc:
                result = self._mc.sudo(cmd, hide=True)
                if result:
                    logging.debug(f"execute sudo stdout: {result.stdout}")
                    return result.return_code
        except Exception as e:
            logging.error("executor sudo error:".format(e))
        return self._error - 1

    def run(self, cmd):
        """
        """
        try:
            if self._debug:
                print(f"[DEBUG MODE]: execute run {cmd}")
                return self._error
            elif self._mc:
                result = self._mc.run(cmd, hide=True)
                if result:
                    logging.debug(f"execute run stdout: {result.stdout}")
                    return result.return_code
        except Exception as e:
            logging.error("executor run error:".format(e))
        return self._error - 1

    def local(self, cmd):
        """
        """
        try:
            if self._debug:
                print(f"[DEBUG MODE]: execute local {cmd}")
                return self._error
            elif self._mc:
                result = self._mc.local(cmd, hide=True)
                if result:
                    logging.debug(f"execute local stdout: {result.stdout}")
                    return result.return_code
        except Exception as e:
            logging.error("executor local error:".format(e))
        return self._error - 1

    def put(self, lpath, rpath):
        """
        """
        try:
            if self._debug:
                print(f"[DEBUG MODE]: execute put {lpath} {rpath}")
                return self._error
            elif self._mc:
                result = self._mc.put(lpath, rpath)
                if result:
                    return 0
        except Exception as e:
            logging.error("executor put error:".format(e))
        return self._error - 1

    def get(self, rpath, lpath):
        """
        """
        try:
            if self._debug:
                print(f"[DEBUG MODE]: execute get {rpath} {lpath}")
                return self._error
            elif self._mc:
                result = self._mc.get(rpath, lpath)
                if result:
                    return 0
        except Exception as e:
            logging.error("executor get error:".format(e))
        return self._error - 1


if __name__ == "__main__":
    # execute only if run as a script
    pass
