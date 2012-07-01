from javax.swing import JOptionPane

def info(frame, message):
    JOptionPane.showMessageDialog(frame,
        message, "Info", JOptionPane.INFORMATION_MESSAGE)

def error(frame, message):
    JOptionPane.showMessageDialog(frame,
        message, "Error", JOptionPane.ERROR_MESSAGE)

def warn(frame, message):
    JOptionPane.showMessageDialog(frame,
        message, "Warning", JOptionPane.WARNING_MESSAGE)

def yesNo(frame, message):
    n = JOptionPane.showConfirmDialog(frame,
        message, "Question", JOptionPane.YES_NO_OPTION)
    if n == JOptionPane.YES_OPTION:
        return True
    else:
        return False

