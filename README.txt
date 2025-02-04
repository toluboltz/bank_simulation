Operation
-------
- This is a command-line program that simulates a simple banking system where users can create accounts, deposit, withdraw, check balances etc.
- The program utilizes Inter-Process Communication (IPC) using sockets and argparse.
- The program is made up of a server (bank_server.py) and a client (bank.py).
- The server script maintains the banking system in memory and listens for client commands while the client script connects to the bank server and sends commands.
- The server runs on "localhost" port "8000"

Usage
-----
1. Start the Server:
   Open a terminal and run:
       python bank_server.py
2. The server will start and listen for client connections.
3. Run Client Commands:
   In a separate terminal, run one command at a time. For example:
       python bank.py create-account 1001
       python bank.py deposit 1001 500
       python bank.py withdraw 1001 200
       python bank.py balance 1001
       python bank.py transfer 1001 1002 100

Each command connects to the server, sends the request, and prints the response.
This separation allows for the server and client to run independently, storing all account information in memory.

For more information, run: python bank.py -h

Additional features
-------------------
- Implement multi-threading using "threading" module to handle concurrent clients (or threads).
- Utilize pickle module to persist account data to a file and load it on subsequent executions (e.g., save <filename> and load <filename> ).
- Add a history command to display a list of transactions (deposits, withdrawals, transfers) for a particular account.
- Utilize decimal module to accurately handle financial transactions


Third-party package(s)
-----------------
See requirements.txt