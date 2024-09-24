from datetime import datetime, timedelta, timezone
import sys
from PyQt5 import QtWidgets, QtCore, QtGui


def parse_announcement_file(filename):
    notifications = []
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            # Parse notifications
            parts = line.split('  ', 2)  # Split the line into 3 parts: time, course, and notification
            if len(parts) == 3:
                time_str, course, notification = parts
                time_str = time_str.strip().replace("Z", "+00:00")
                try:
                    time = datetime.fromisoformat(time_str)
                    notifications.append((time, course.strip(), notification.strip()))
                except ValueError:
                    print(f"Error parsing time for line: {line}")
    return notifications
def parse_assignment_file(filename):
    assignments = []
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            # Parse assignment deadlines
            # Split the line into 4 parts: time, course, assignment, and completed status
            parts = line.rsplit('  ', 3)
            # Limit the split to 4 parts from the right, notice the spliter is a double-space
            if len(parts) == 4:
                time_str, course, assignment, completed = parts
                try:
                    time = datetime.fromisoformat(time_str)
                    completed = completed.strip() == 'True'  # Convert 'True' or 'False' string to a boolean
                    assignments.append((time, course, assignment.strip(), completed))
                except ValueError:
                    print(f"Error parsing time for line: {line}")
    return assignments

# Function to filter notifications and assignments by date range
def filter_items(notifications, assignments):
    now = datetime.now(timezone.utc)
    past_2_days = now - timedelta(days=2)
    future_5_days = now + timedelta(days=5)

    # Filter notifications from the past 2 days
    recent_notifications = [(time, course, content) for time, course, content in notifications if past_2_days <= time <= now]

    # Filter assignments due in the next 5 days
    upcoming_assignments = [(time, course, assignment, completed) for time, course, assignment, completed in assignments if now <= time <= future_5_days]

    return recent_notifications, upcoming_assignments

def display_sticky_note(notifications, assignments):
    notes_num = len(notifications)+len(assignments)

    app = QtWidgets.QApplication(sys.argv)

    # 创建主窗口
    window = QtWidgets.QMainWindow()
    # 设置成工具窗口，防止在任务栏显示；并且使之呆在底部
    window.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnBottomHint)
    window.setAttribute(QtCore.Qt.WA_TranslucentBackground)#透明背景

    # 获取屏幕大小
    screen = app.primaryScreen().size()
    window_width = 400
    # 长度由提醒数决定，可以调整
    window_height = 70*notes_num
    # 设置窗口位置，x轴/y轴/宽度/高度，目前为屏幕右上角
    window.setGeometry(screen.width() - window_width - 160, 50, window_width, window_height)

    # 设置窗口样式
    window.setStyleSheet("background-color: rgba(255, 255, 255, 180); border-radius: 15px;")

    # 创建主widget，用于承载内容
    widget = QtWidgets.QWidget(window)
    layout = QtWidgets.QVBoxLayout(widget)

    # 设置作业标题
    assignments_label = QtWidgets.QLabel("Upcoming Assignments:")
    assignments_label.setStyleSheet("font-weight: bold; font-size: 14px; color: black;")
    layout.addWidget(assignments_label)

    # 显示每个作业
    for time, course, assignment, completed in assignments:
        time_str = time.strftime('%Y-%m-%d %H:%M:%S')
        assignment_text = f"{time_str}  {course} \nq {assignment}"
        assignment_label = QtWidgets.QLabel(assignment_text)
        color = "green" if completed else "red"
        assignment_label.setStyleSheet(f"font-size: 16px; color: {color};")
        layout.addWidget(assignment_label)

    # 分隔线
    separator = QtWidgets.QFrame()
    separator.setFrameShape(QtWidgets.QFrame.HLine)
    layout.addWidget(separator)

    # 设置通知标题
    notifications_label = QtWidgets.QLabel("Recent Notifications:")
    notifications_label.setStyleSheet("font-weight: bold; font-size: 14px; color: black;")
    layout.addWidget(notifications_label)

    # 显示每个通知
    for time, course, content in notifications:
        time_str = time.strftime('%Y-%m-%d %H:%M:%S')
        notification_text = f"{time_str}  {course} \n  {content}"
        notification_label = QtWidgets.QLabel(notification_text)
        notification_label.setStyleSheet("font-size: 16px; color: blue;")
        layout.addWidget(notification_label)

    # 调整窗口大小以适应内容
    widget.setLayout(layout)
    window.setCentralWidget(widget)

    # 显示窗口
    window.show()
    sys.exit(app.exec_())
# Function to display notifications and assignments on a sticky note with the required design


# Main function to run the app
def main():
    filename1 = 'announcement.txt'
    filename2 = 'assignment.txt'
    notifications=parse_announcement_file(filename1)
    assignments=parse_assignment_file(filename2)
    recent_notifications, upcoming_assignments = filter_items(notifications, assignments)
    display_sticky_note(recent_notifications, upcoming_assignments)

if __name__ == "__main__":
    main()
