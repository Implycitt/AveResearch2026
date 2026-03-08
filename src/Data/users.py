class Users:

    def __init__(self) -> None:
        self.outFile = "./out/users.txt"
        self.users = self.readUsers()

    def readUsers(self) -> set:
        with open(self.outFile, 'r') as file:
            users = set(file.read().split('\n'))
        return users

    def writeUsers(self, userSet: set) -> None:
        with open(self.outFile, 'w') as file:
            for user in userSet:
                file.write(user + '\n')

    def writeUser(self, user: str) -> None:
        with open(self.outFile, 'w') as file:
            file.write(user + '\n')

