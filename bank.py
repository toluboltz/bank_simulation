import argparse
import socket
import sys
import os

# Bank server IP address and listening port
HOST = "localhost"
PORT = 8000


def is_positive(account_id):
    """Ensure account ID is a positive integer"""
    value = int(account_id)
    if value <= 0:
        raise argparse.ArgumentTypeError("Account ID must be a positive integer")
    return value


def is_file(parser, file):
    """Check if file exists"""
    if not os.path.isfile(file):
        parser.error(f"{file} does not exist or is not readable")
    else:
        return file


def run_client(args_str, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except Exception as e:
            print(f"Could not connect to server at {host}:{port}: {e}")
            sys.exit(1)
        s.sendall(args_str.encode())
        response = s.recv(4096)
        print(response.decode())


def main():
    parser = argparse.ArgumentParser(description='Command-line tool that simulates a simple banking system '
                                                 'where users can create accounts, deposit, withdraw, and check balances.')
    # subparsers to define each command
    subparsers = parser.add_subparsers(dest='command', required=True)

    # create-account <accountID>
    parser_create = subparsers.add_parser('create-account', help='Create a new bank account with'
                                                                 ' an initial balance of 0.00')
    parser_create.add_argument('account_id', type=is_positive, help='Account ID')

    # deposit <accountID> <amount>
    parser_deposit = subparsers.add_parser('deposit', help='Deposit a specified amount into the account.')
    parser_deposit.add_argument('account_id', type=int, help='Account ID')
    parser_deposit.add_argument('amount', type=float, help='Amount to Deposit')

    # withdraw <accountID> <amount>
    parser_withdraw = subparsers.add_parser('withdraw', help='Withdraw a specified amount from the account'
                                                             ' if sufficient funds are available.')
    parser_withdraw.add_argument('account_id', type=int, help='Account ID')
    parser_withdraw.add_argument('amount', type=float, help='Amount to Withdraw')

    # balance <accountID>
    parser_balance = subparsers.add_parser('balance', help='Print the current balance of the account.')
    parser_balance.add_argument('account_id', type=int, help='Account ID')

    # transfer <fromAccountID> <toAccountID> <amount>
    parser_transfer = subparsers.add_parser('transfer', help='Transfer a specified amount from one'
                                                             ' account to another, if funds are available.')
    parser_transfer.add_argument('from_account_id', type=int, help='Sender account ID')
    parser_transfer.add_argument('to_account_id', type=int, help='Receiver account ID')
    parser_transfer.add_argument('amount', type=float, help='Amount to transfer')

    # history <accountID>
    parser_history = subparsers.add_parser('history', help='View transaction history')
    parser_history.add_argument('accountID', type=str, help='Account ID')

    # save <filename>
    parser_save = subparsers.add_parser('save', help='Save account data to a file')
    parser_save.add_argument('filename', type=str, metavar='<filename>', help='Filename to save data')

    # load <filename>
    parser_load = subparsers.add_parser('load', help='Load account data from a file')
    parser_load.add_argument('filename', type=lambda f: is_file(parser, f), metavar='<filename>',
                             help='Filename to load data from')

    args = parser.parse_args()

    # convert argparse object to string for easy transfer to the server
    args_str = " ".join(str(val) for arg, val in vars(args).items())
    # print the arg_string
    # print(args_str)

    run_client(args_str, HOST, PORT)


if __name__ == '__main__':
    // Add comment
    main()
