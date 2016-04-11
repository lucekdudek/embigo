import time

from django.contrib.auth.models import User


class ConnectedUsers:
    users_webs = {}
    users_unique = {}

    def get_unique(self):
        return self.users_unique

    def add(self, client_id, user):
        if client_id not in self.users_webs:
            self.users_webs[client_id] = user
            if user not in self.users_unique:
                self.users_unique[user] = [client_id]
            else:
                self.users_unique[user].append(client_id)
        print("\033[93mConnected users: %s\033[0m" % self.get_unique())

    def remove(self, client_id):
        time.sleep(5)
        if client_id in self.users_webs:
            user = self.users_webs[client_id]

            del self.users_webs[client_id]
            if user in self.users_unique:
                self.users_unique[user].remove(client_id)
                if len(self.users_unique[user]) == 0:
                    del self.users_unique[user]
        print("\033[93mConnected users: %s\033[0m" % self.get_unique())

    def is_online(self, username):
        user = User.objects.get(username=username)
        if user in self.users_unique:
            return True
        else:
            return False

    def get(self, client_id):
        if client_id in self.users_webs:
            return self.users_webs[client_id]
