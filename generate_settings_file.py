import jinja2
import argparse
import os.path


parser = argparse.ArgumentParser(
    description="Generate settings.yaml or settings_slackbot.yaml"
)

parser.add_argument(
    "application",
    nargs="?",
    choices=["settings.yaml", "settings_slackbot.yaml"],
    default="settings.yaml",
    help="The kind of settings file you want to create."
)

parser.add_argument(
    "--log-dir",
    help="Directory to store logs in."
)

parsed = parser.parse_args()
choice = parsed.application
log_dir = parsed.log_dir
systemd_configfile = os.path.join(os.path.dirname(__file__), "settings.yaml")
slackbot_configfile = os.path.join(os.path.dirname(__file__), "settings_slackbot.yaml")

choices = dict()


if choice == "settings.yaml":
    add_more_units = True
    while add_more_units:
        unit = dict()
        # UNIT
        print("Which unit in systemd will you connect Slack to?")
        unit['unit'] = input("> ")

        # ALLOWED COMMANDS
        print("Which systemctl commands shall be available to Slack?")
        commands = {"status": True, "start": False, "stop": False,
                    "restart": False}
        finished = False
        while not finished:
            print("\n".join(["[" + ("X" if commands[cmd] else " ") + "] " + cmd
                             for cmd in commands]))
            print("Toggle which command? (Leave blank when done)")
            answer = input("> ").strip().lower()
            if answer in commands:
                commands[answer] = not commands[answer]
            elif not answer:
                finished = True
            else:
                print("Didn't recognize '%s'" % answer)
        unit['allowed_commands'] = [cmd for cmd in commands if commands[cmd]]

        # KEYWORD
        print("What must all messages for this Slackbot start with?")
        print("It should be something that you don't write by accident.")
        default_keyword = "." + unit['unit']
        print("Default: %s" % default_keyword)
        keyword = input("> ") or default_keyword

        # HELP
        print("Describe this Slackbot. End the description with a blank line.")
        help_lines = []
        answer = input("> ")
        while answer:
            help_lines.append(answer)
            answer = input("> ")
        unit['help'] = "\n".join(help_lines)

        # SLACK_CHANNEL
        print("On which channel in Slack should messages be posted?")
        print("Leave blank to post to whichever channel the user posted in.")
        unit['slack_channel'] = input("> ")

        # Add unit
        choices[keyword] = unit

        # More units?
        print("Do you want to connect Slack to more units? [yN]")
        add_more_units = True if input("> ").lower().strip() in ("y", "yes") else False

else:
    # SLACK
    print("Slack API Token?")
    choices['slack_token'] = input("> ")

    # LOGFILE
    choices['logfile'] = log_dir + "/application.log"

print("Generating the file...")

# Generate the files!
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
if choice == "settings.yaml":
    template = env.get_template("settings.yaml")
    with open(systemd_configfile, "w") as f:
        f.write(template.render(**choices))

else:
    template = env.get_template("settings_slackbot.yaml")
    with open(slackbot_configfile, "w") as f:
        f.write(template.render(**choices))
