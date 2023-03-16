from handle_nifti import color as c

class cow:
    def __init__(self, name=None):
        self.name = name
        if self.name is None:
            self.name = "Anonymous because you didn't give me a name!"
        intro = [f'\|/         (__)                           ',
                f"     `\------(oo)      Mooh, I'm {self.name}",
                f"       ||    (__)                           ",
                f"       ||w--||     \|/                      ",
                f"   \|/                                      "]
        print(c.CBLUE, '\n'.join(intro), c.ENDC)

    def moo_your_name(self):
        print("Moo, I'm a cow called " + self.name + "!")

    def moo(self, n=1):
        print(f"Mo{'o'*int(n)}h!")
    def moo2(self, n):
        for i in range(n):
            self.moo(int(i))

    def sit(self):
        cow = [f'            /( ,,,,, )\        ',
               f'           _\,;;;;;;;,/_       ',
               f'        .-"; ;;;;;;;;; ;"-.    ',
               f"        '.__/`_ / \ _`\__.'    ",
               f"           | (')| |(') |       ",
               f'           | .--' '--. |       ',
               f'           |/ o     o \|       ',
               f'           |           |       ',
               f'          / \ _..=.._ / \      ',
               f"         /:. '._____.'   \     ",
               f"        ;::'    / \      .;    ",
               f'        |     _|_ _|_   ::|    ',
               f"      .-|     '==o=='    '|-.  ",
               f'     /  |  . /       \    |  | ',
               f'     |  | ::|         |   | .| ',
               f"     |  (  ')         (.  )::| ",
               f'     |: |   |; U U U ;|:: | `| ',
               f"     |' |   | \ U U / |'  |  | ",
               f'     ##V|   |_/`"""`\_|   |V## ',
               f"       ##V##         ##V##')   "]
        print(c.CBLUE, '\n'.join(cow), c.ENDC)

    def ass(self):
        ass = [f'                        ,     ,     ',
               f"                    ___('-&&&-')__  ",
               f"                   '.__./     \__.' ",
               f"       _     _     _ .-'  6  6 \    ",
               f"    /` `--'( ('--` `\         |     ",
               f"    /        ) )      \ \ _   _|    ",
               f"   |        ( (        | (0_._0)    ",
               f"   |         ) )       |/ '---'      ",
               f"   |        ( (        |\_          ",
               f"   |         ) )       |( \,        ",
               f"    \       ((`       / )__/        ",
               f"     |     /:))\     |   d          ",
               f"     |    /:((::\    |              ",
               f"     |   |:::):::|   |              ",
               f"     /   \::&&:::/   \              ",
               f"     \   /;U&::U;\   /              ",
               f"      | | | u:u | | |               ",
               f"      | | \     / | |               ",
               f"      | | _|   | _| |               ",
               f'      / |""`   `""/ \               ',
               f"     | __|       | __|              ",
               f"     `""""`      `""""`',            "]
        print(c.CBLUE, '\n'.join(ass), c.ENDC)

    def milk(self):
        milk = [f'-=Milk Map Milk=-        ',
                f"           _____       ",
                f"          j_____j      ",
                f"         /_____/_\     ",
                f"         |_(~)_| |     ",
                f'         | )"( | |     ',
                f"         |(@_@)| |     ",
                f"         |_____|,''    "]
        print(c.CBLUE, '\n'.join(milk), c.ENDC)



