import re


class Bind:
    @classmethod
    def isBind(self, s: str) -> bool:
        return re.match("^bind \S+ .+", s)

    def updatecmd(self, s: str) -> None:
        self.bindcmd = s
    def copy(self):
        return Bind(str(self))
    def __str__(self) -> str:
        return "bind " + self.bindkey + " " + self.bindcmd

    def __init__(self, s: str) -> None:
        m = re.match("^bind (\S+) (.+)", s)
        if m:
            self.bindkey = m.group(1)
            self.bindcmd = m.group(2)
            if self.bindcmd[-1] == "\n":
                self.bindcmd = self.bindcmd[:-1]
        else:
            raise Exception("not a bind")

    def nested(self):
        cmd = " " + self.bindcmd + " "
        for i in range(4, 0, -1):
            cmd = cmd.replace("\\" * ((1 << i) - 1), "\\" * ((1 << i + 1) - 1))
        cmd = cmd.replace(' "', ' \\"')
        cmd = cmd.replace('" ', '\\"')
        return Bind("bind " + self.bindkey + cmd)
