import socket
import threading
import pickle  # for serializing and de-serializing the account info & history

from decimal import Decimal, getcontext  # to accurately handle financial transactions

# set decimal context
getcontext().prec = 2

# Bank server IP address and listening port
HOST = "localhost"
PORT = 8000


def is_number(amount):
    """Helper function to check if amount is a number and convert to Decimal data type for accurate floating-point arithmetic"""
    try:
        amount = float(amount)
    except ValueError:
        return "Error: Amount must be a number."
    return Decimal(amount)


class Bank:
    def __init__(self):
        self.accounts = {}  # dictionary to store account info (accountID and balance) in memory
        self.history = {}  # store transaction history for each account
        self._lock = threading.Lock()  # lock to prevent race conditions

    def create_account(self, account_id):
        with self._lock:
            if account_id in self.accounts:
                return "Error: Account already exists."
            self.accounts[account_id] = Decimal(0.00)
            self.history[account_id] = []
            return "Account created."

    def deposit(self, account_id, amount):
        amount = is_number(amount)
        if amount <= 0:
            return "Error: Deposit amount must be positive."
        with self._lock:
            if account_id not in self.accounts:
                return "Error: Account does not exist."
            self.accounts[account_id] += amount
            self.history[account_id].append(f"Deposited {amount:.2f}")
            return "Deposit successful."

    def withdraw(self, account_id, amount):
        amount = is_number(amount)
        if amount <= 0:
            return "Error: Withdrawal amount must be positive."
        with self._lock:
            if account_id not in self.accounts:
                return "Error: Account does not exist."
            if self.accounts[account_id] < amount:
                return "Error: Insufficient funds."
            self.accounts[account_id] -= amount
            self.history[account_id].append(f"Withdrew {amount:.2f}")
            return "Withdrawal successful."

    def balance(self, account_id):
        with self._lock:
            if account_id not in self.accounts:
                return "Error: Account does not exist."
            return f"Current balance: {self.accounts[account_id]:.2f}"

    def transfer(self, from_account, to_account, amount):
        amount = is_number(amount)
        if amount <= 0:
            return "Error: Transfer amount must be positive"
        with self._lock:
            if from_account not in self.accounts:
                return "Error: From account does not exist."
            if to_account not in self.accounts:
                return "Error: To account does not exist."
            if self.accounts[from_account] < amount:
                return "Error: Insufficient funds."
            self.accounts[from_account] -= amount
            self.accounts[to_account] += amount
            self.history[from_account].append(f"Transferred {amount:.2f} to {to_account}")
            self.history[to_account].append(f"Received {amount:.2f} from {from_account}")
            return "Transfer successful."

    def get_history(self, account_id):
        with self._lock:
            if account_id not in self.history:
                return "Error: Account does not exist."
            if not self.history[account_id]:
                return "No transactions yet."
            return "\n".join(self.history[account_id])

    def save(self, filename):
        with self._lock:
            try:
                with open(filename, 'wb') as f:
                    pickle.dump({'accounts': self.accounts, 'history': self.history}, f)
                return "Data saved successfully."
            except Exception as e:
                return f"Error saving data: {e}"

    def load(self, filename):
        with self._lock:
            try:
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                self.accounts = data.get('accounts', {})
                self.history = data.get('history', {})
                return "Data loaded successfully."
            except Exception as e:
                return f"Error loading data: {e}"


def handle_client(conn, addr, bank):
    with conn:
        try:
            data = conn.recv(4096)
            if not data:
                return
            command_str = data.decode().strip()
            # print(command_str)
            tokens = command_str.split()  # split the command string
            # print(tokens)
            if not tokens:
                response = "Error: No command received."
            else:
                cmd = tokens[0].lower()
                if cmd == "create-account":
                    if len(tokens) != 2:
                        response = "Usage: create-account <accountID>"
                    else:
                        response = bank.create_account(tokens[1])
                elif cmd == "deposit":
                    if len(tokens) != 3:
                        response = "Usage: deposit <accountID> <amount>"
                    else:
                        response = bank.deposit(tokens[1], tokens[2])
                elif cmd == "withdraw":
                    if len(tokens) != 3:
                        response = "Usage: withdraw <accountID> <amount>"
                    else:
                        response = bank.withdraw(tokens[1], tokens[2])
                elif cmd == "balance":
                    if len(tokens) != 2:
                        response = "Usage: balance <accountID>"
                    else:
                        response = bank.balance(tokens[1])
                elif cmd == "transfer":
                    if len(tokens) != 4:
                        response = "Usage: transfer <fromAccountID> <toAccountID> <amount>"
                    else:
                        response = bank.transfer(tokens[1], tokens[2], tokens[3])
                elif cmd == "history":
                    if len(tokens) != 2:
                        response = "Usage: history <accountID>"
                    else:
                        response = bank.get_history(tokens[1])
                elif cmd == "save":
                    if len(tokens) != 2:
                        response = "Usage: save <filename>"
                    else:
                        response = bank.save(tokens[1])
                elif cmd == "load":
                    if len(tokens) != 2:
                        response = "Usage: load <filename>"
                    else:
                        response = bank.load(tokens[1])
                else:
                    response = "Error: Unknown command."
            conn.sendall(response.encode())
        except Exception as e:
            print(f"Error handling client {addr}: {e}")


def run_server(host, port):
    bank = Bank()  # instantiate a new bank object
    print(f"Bank server running on {host}:{port} ...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                # handle each client connection in a new thread
                # shutdown all threads when program terminates
                threading.Thread(target=handle_client, args=(conn, addr, bank), daemon=True).start()
            except KeyboardInterrupt:
                print("\nBank server shutting down...")
                break


def main():
    run_server(HOST, PORT)


if __name__ == '__main__':
    main()
