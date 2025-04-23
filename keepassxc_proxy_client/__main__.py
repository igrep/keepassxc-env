import sys
import json
import base64
import time

import keepassxc_proxy_client
import keepassxc_proxy_client.protocol

USAGE = """usage: keepassxc_proxy_client

keepassxc_proxy_client create: Connects to a locally running keepassxc instance,
creates a new association with it (this will prompt a dialogue from keepassxc)
and prints it to stdout as JSON. Note that the public key that is printed is
secret and can allow anyone with access to your local machine access to all
passwords that are related to a URL, thus it should be stored safely.

keepassxc_proxy_client get <file> <url>: Reads a keepassxc association from
<file> and attempts to get the first password for <url>. Will exit with 1 if the
association is not valid for the running keepassxc instance or the no logins are
found for the given URL.

keepassxc_proxy_client await_get <file> <url>: Same as 'get' but retries every 10 seconds
when encountering connection errors. This is useful when KeePassXC is not yet running
or the database is locked.

keepassxc_proxy_client unlock <file>: Causes a running KeepassXC instance
to launch a dialogue window to allow the user to unlock a locked database.
If the database is already unlocked it has no effect.
"""


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help", "h"]:
        print(USAGE)
        sys.exit(0)

    command = sys.argv[1]

    if command == "create":
        connection = keepassxc_proxy_client.protocol.Connection()
        connection.connect()
        connection.associate()

        if not connection.test_associate():
            print(
                "For some reason the newly created association is invalid, this should not be happening")
            sys.exit(1)

        name, public_key = connection.dump_associate()
        out = {
            "name": name,
            "public_key": base64.b64encode(public_key).decode("utf-8")
        }
        print(json.dumps(out))
        sys.exit(0)

    elif command == "get":
        run_get()
    elif command == "await_get":
        run_await_get()
    elif command == "unlock":
        if len(sys.argv) < 3:
            print("Too few arguments provided, see --help for usage")
            sys.exit(1)

        associate_file = sys.argv[2]
        association = json.load(open(associate_file, "r"))

        connection = keepassxc_proxy_client.protocol.Connection()
        connection.connect()

        connection.load_associate(
            association["name"],
            base64.b64decode(association["public_key"].encode("utf-8"))
        )

        print(connection.test_associate(True))

        sys.exit(0)
    else:
        print("Unknown subcommand, see --help for usage")
        sys.exit(1)


def run_get():
    if len(sys.argv) < 4:
        print("Too little arguments provided, see --help for usage")
        sys.exit(1)

    associate_file = sys.argv[2]
    url = sys.argv[3]

    association = json.load(open(associate_file, "r"))
    connection = keepassxc_proxy_client.protocol.Connection()
    connection.connect()
    connection.load_associate(
        association["name"],
        base64.b64decode(association["public_key"].encode("utf-8"))
    )

    if not connection.test_associate():
        print("The loaded association is invalid")
        sys.exit(1)

    logins = connection.get_logins(url)
    if not logins:
        print("No logins found for the given URL")
        sys.exit(1)

    password = logins[0]["password"]
    print(password)


def run_await_get():
    """
    Retries the run_get function every 10 seconds when encountering specific errors.
    """
    retry_interval = 10  # seconds

    while True:
        try:
            run_get()
            break  # Exit the loop if run_get completes successfully
        except Exception as e:
            error_str = str(e)
            # Check for the specific connection error
            is_response_unsuccessful = isinstance(
                e,
                keepassxc_proxy_client.protocol.ResponseUnsuccesfulException,
            )
            is_connection_error =(
                    "Error: Connection could not be established to pipe org.keepassxc.KeePassXC.BrowserServer_" in error_str
                    and "指定されたファイルが見つかりません。" in error_str
            )
            if is_response_unsuccessful or is_connection_error:
                print(
                    f"KeePassXC not running or database locked. Retrying in {retry_interval} seconds...",
                    file=sys.stderr,
                )
                time.sleep(retry_interval)
                continue
            else:
                raise e

if __name__ == "__main__":
    main()