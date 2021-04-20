"""
Generic script runner with output capturing, sending email and retrying capabilities.

Configuration can be given via command line options or via environment variables.

The following configuration is available:
    --sender or PYRUN_SENDER             - the email address for the sender
    --recipients or PYRUN_RECIPIENTS     - the email addresses for the recipients, separated by comma
    --name or PYRUN_NAME                 - the name/id for the task/script
    --script or PYRUN_SCRIPT             - the path to entry point function for task (e.g.: foo.bar.app:main)

If both command line option and environment variable are provided, the value given to the command line option
will take precedence / high priority and will override the value set to the environment variable.

If you have command line arguments / options to be passed to the script / entry point, then you must separate
that with double dashes, for example:

pyrun foo.bar -- spam eggs --verbose

This will invoke foo.bar entry point, and it will pass ["spam", "eggs", "--verbose"] as command line arguments
to that script.

Everything before the double dashes are treated/parsed as command line options for the pyrun command.
"""
import argparse
import datetime
import getpass
import os
import smtplib
import socket
import subprocess
import sys
from email.message import EmailMessage
from enum import Enum
from typing import List, Dict, Tuple, Optional


def main():
    config = get_config()
    config["start"] = datetime.datetime.now()

    # run the script
    returncode, output = call(config["executable_call"])

    config["end"] = datetime.datetime.now()

    # send the email
    if should_send_email(config, returncode):
        config["elapsed"] = (config["end"] - config["start"]).seconds
        send_email(config, returncode, output)


def get_config(argv: List[str] = None):
    args = parse_args(argv=argv)

    sender = args.sender or env_var("SENDER")
    recipients = args.recipients or env_var("RECIPIENTS")
    name = args.name or env_var("NAME")
    send_email_on_failure = args.failure or env_var("FAILURE", "false").lower() in ["1", "true"]
    send_email_on_success = args.success or env_var("SUCCESS", "false").lower() in ["1", "true"]
    executable_call = args.executable_call

    recipients = [r.strip() for r in recipients.strip().split(",")]

    return {
        "sender": sender,
        "recipients": recipients,
        "name": name,
        "executable_call": executable_call,
        "send_email_on_failure": send_email_on_failure,
        "send_email_on_success": send_email_on_success,
    }


def parse_args(argv: List[str] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--sender", help="the email address for the sender")
    parser.add_argument("--recipients", help="the email addresses for the recipients, separated by comma")
    parser.add_argument("--name", help="the name/id for the task/script")
    parser.add_argument("-f", "--failure", action="store_true", help="send email on failures")
    parser.add_argument("-s", "--success", action="store_true", help="send email on successes")
    parser.add_argument("executable_call", nargs=argparse.REMAINDER,
                        help="the path to the entry point function for task (e.g.: foo.bar.app:main)")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    return args


def env_var(name, default=None) -> str:
    return os.getenv(f"PYRUN_{name}", default)


def should_send_email(config: Dict, returncode: int) -> bool:
    if returncode:
        return config["send_email_on_failure"]
    else:
        return config["send_email_on_success"]


def call(program_args: List[str]) -> Tuple[int, str]:
    try:
        output = subprocess.check_output(program_args, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output
    else:
        return 0, output


def format_dict(d: Dict, sep: str = ":") -> str:
    n = max(len(k) for k in d)
    lines = "\n".join((f"{k:<{n}} {sep} {v}" for k, v in d.items()))
    return lines


def send_email(config: Dict, output: str, returncode: int) -> None:
    status = "FAILED" if returncode else "SUCCEEDED"
    dt_fmt = "%d-%b-%Y %H:%M:%S"
    fields = {
        "Name": config["name"],
        "Executable call": " ".join(config["executable_call"]),
        "Return code": returncode,
        "Status": status,
        "Started at": config["start"].strftime(dt_fmt),
        "Finished at": config["end"].strftime(dt_fmt),
        "Total Runtime": "{:,.2f}".format(config["elapsed"]),
        "Username": getpass.getuser(),
        "Hostname": socket.gethostname(),
    }
    formatted_fields = format_dict(fields)
    body = f"<h1>{config['name']} - {status}</h1><br><pre>{formatted_fields}</pre><h2>Please check output attached.</h2>"
    _send_email(
        sender=config["sender"],
        recipients=config["recipients"],
        subject=f"Task: {config['name']} - {status}",
        body=body,
        html=True,
        priority=EmailPriority.HIGH if returncode else EmailPriority.NORMAL,
        attachments={"output.txt": output},
    )



class EmailPriority(str, Enum):
    LOW = "5"
    NORMAL = "3"
    HIGH = "1"


def _send_email(sender: str,
                recipients: List[str],
                subject: str,
                body: str,
                smtp_hostname: str = "localhost",
                attachments: Optional[Dict] = None,
                html: Optional[bool] = True,
                priority: Optional[EmailPriority] = EmailPriority.NORMAL,
                ):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["X-Priority"] = str(EmailPriority(priority))

    kwargs = {}
    if html:
        kwargs["subtype"] = "html"

    message.set_content(body, **kwargs)

    attachments = attachments or {}
    for filename, contents in attachments.items():
        message.add_attachment(contents, filename=filename)

    with smtplib.SMTP(smtp_hostname) as smtp:
        smtp.send_message(message)


if __name__ == '__main__':
    main()
