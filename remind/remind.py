import smtplib
import sys
import json
from datetime import date, timedelta
import email.message


DutyGroups = {
    "cook": ({"Big Cook", "Little Cook", "Tiny Cook"}, {"Big Cook", "Little Cook"}, "today"),
    "clean": ({"Cleaner 1", "Cleaner 2", "Cleaner 3"}, {"Cleaner 1", "Cleaner 2"}, "tonight"),
    "fridge ninja": ({"Fridge Ninja"}, {}, "today"),
}


def dayDeltaString(dayDelta, todayText):
    if dayDelta == 0:
        return todayText
    elif dayDelta == 1:
        return "tomorrow"
    elif dayDelta == -1:
        return "yesterday"
    elif dayDelta > 1:
        return f"in {dayDelta} days"
    elif dayDelta < -1:
        return f"{-dayDelta} days ago"


mailserver = "outgoing.mit.edu"
from_addr = "yfnkm@mit.edu"


def sendReminder(to, task, mightBeCanceled):
    SERVER = mailserver
    TO = to + [from_addr, "yfncc@mit.edu"]

    message = email.message.Message()
    message['From'] = from_addr
    message['To'] = ";; ".join(TO)
    message['Subject'] = f"Reminder: you are signed up to {task}"

    payload = "mealplan.pikans.org"
    if mightBeCanceled:
        payload += "\n\nNOTE: not all shifts are filled, so dinner may be canceled"
    if not to: 
        payload += "\n\nIMPORTANT: contact yfncc since this email has no reciever and should not have been sent. They have a bug to hunt down :()"
    message.set_payload(payload)

    # Send the mail

    server = smtplib.SMTP(SERVER)
    server.sendmail(from_addr, TO, message.as_string())
    # print(f"sent reminder to {TO} from {from_addr} with message {message.as_string()}\n")

    server.quit()


# Returns whether any shifts are missing
def mightBeCanceled(data, day, group):
    try:
        dayAssignments = data["Assignments"][day]
        for duty in group[1]:
            try:
                assignee = dayAssignments[duty]
                if assignee in ["", "_"]:
                    return True
            except:
                return True
    except:
        return True
    return False


def toEmail(username):
    if username.__contains__('@'):
        return username
    else:
        return username + "@mit.edu"


def main():
    if len(sys.argv) != 4:
        print(
            f"wrong number of args: run {sys.argv[0]} <datapath> <duty> <daysOut>")
        return
    task = sys.argv[2]
    try:
        group = DutyGroups[task]
    except:
        print(f"No task {task}")
        return

    try:
        day_delta = int(sys.argv[3])
    except:
        print(f"invalid day delta {sys.argv[3]}, should be an integer")
        return

    with open(sys.argv[1]) as f:
        data = json.load(f)

    day = (date.today() + timedelta(days=day_delta)).isoformat()
    to = []
    # try:
    dayAssignments = data["Assignments"][day]
    for duty in group[0]:
        assignee = ""
        try:
            assignee = dayAssignments[duty]
        except:
            continue
        if assignee not in ["", "_"]:
            to += [toEmail(assignee)]
    taskText = task + " " + dayDeltaString(day_delta, group[2])
    sendReminder(to, taskText, mightBeCanceled(data, day, group))
    # except:
    #     print("Unable to load data from json file")


main()
